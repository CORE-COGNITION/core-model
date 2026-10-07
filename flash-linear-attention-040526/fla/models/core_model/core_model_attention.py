# Copyright (c) 2023-2026, Songlin Yang, Yu Zhang, Zhiyuan Li
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# For a list of all contributors, visit:
#   https://github.com/fla-org/flash-linear-attention/graphs/contributors

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch
import torch.nn as nn
from einops import rearrange
from torch.nn import functional as F

from fla.layers.utils import get_layer_cache, get_unpad_data, index_first_axis, pad_input, update_layer_cache
from fla.ops.delta_value import chunk_delta_value
from fla.ops.gla import chunk_gla, fused_recurrent_gla

if TYPE_CHECKING:
    from transformers.processing_utils import Unpack

    from fla.models.utils import Cache


class CoreModelAttention(nn.Module):
    """
    CoreModel memory layer: per head a fast-weight matrix ``M_t`` of shape
    ``[head_dim, head_dim]`` (keys x values), written by a gated learning rule
    at every token and read by a query.

    Shared by both rules (per head, ``d = head_dim``):

    - ``q_t = silu(q_proj(x_t))``, ``k_t = silu(k_proj(x_t))``, both L2-normalised
      per head before they touch the memory (``q_hat``, ``k_hat``);
    - ``v_t = x_t`` (identity value pathway, ``hidden_size == num_heads * head_dim``);
    - learning rate ``beta_t = sigmoid(b_proj(x_t))`` in ``(0, 1)^d``, one per channel;
    - decay ``D_t = diag(exp(log_alpha_t))`` with
      ``log_alpha_t = -exp(A_log) * softplus(a_proj(x_t) + dt_bias) <= 0`` per key
      channel (fine-grained forgetting as in Kimi Delta Attention). ``use_forget_gate=False`` sets
      ``D_t = I`` and drops ``a_proj``, ``A_log`` and ``dt_bias``.

    Write rules (``learning_rule``)::

        delta:    M_t = D_t M_{t-1} + k_hat_t (beta_t * (v_t - (D_t M_{t-1})^T k_hat_t))^T
        hebbian:  M_t = D_t M_{t-1} + k_hat_t (beta_t * v_t)^T

    ``'delta'`` stores a gated prediction error: ``beta_t`` is a learning rate per
    value channel on ``v_t`` minus what the memory retrieves for ``k_hat_t``, so every
    value channel ``j`` follows a scalar delta rule
    ``M_t[:, j] = (I - beta_tj k_hat_t k_hat_t^T) D_t M_{t-1}[:, j] + beta_tj v_tj k_hat_t``
    (symmetric, never expansive). ``'hebbian'`` drops the prediction: a pure gated
    outer-product write. Read-out: ``o_t = M_t^T q_hat_t * d**-0.5``, passed through
    unchanged.

    Kernels: ``chunk_delta_value`` (``fla.ops.delta_value``, ours) for ``'delta'`` on
    both the chunk and the token-by-token path, ``chunk_gla`` / ``fused_recurrent_gla``
    for ``'hebbian'``; q/k L2-norm and ``beta_t`` applied outside the kernels, decay
    per key channel. State per layer ``[N, num_heads, head_dim, head_dim]``.

    Args:
        hidden_size (int, Optional):
            The hidden size of the input, ``num_heads * head_dim``. Default: 128.
        head_dim (int, Optional):
            Key, value and read-out dim per head (kernel limit 256). Default: 32.
        num_heads (int, Optional):
            The number of heads. Default: 4.
        learning_rule (str, Optional):
            ``'delta'`` or ``'hebbian'`` (above). Default: ``'delta'``.
        use_forget_gate (bool, Optional):
            Input-dependent channel-wise decay of the memory. Default: ``True``.
        layer_idx (int, Optional):
            The index of the layer. Default: ``None``.
    """

    def __init__(
        self,
        hidden_size: int = 128,
        head_dim: int = 32,
        num_heads: int = 4,
        learning_rule: str = 'delta',
        use_forget_gate: bool = True,
        layer_idx: int = None,
        **kwargs,
    ) -> CoreModelAttention:
        super().__init__()

        assert 1 <= head_dim <= 256, f"head_dim must be in [1, 256] (kernel limit), got {head_dim}."
        assert learning_rule in ('delta', 'hebbian'), (
            f"learning_rule must be 'delta' or 'hebbian', got {learning_rule!r}."
        )
        assert hidden_size == num_heads * head_dim, (
            f"hidden_size ({hidden_size}) must equal num_heads * head_dim ({num_heads} * {head_dim}): "
            "identity value pathway and identity read-out."
        )

        self.hidden_size = hidden_size
        self.head_dim = head_dim
        self.num_heads = num_heads
        self.learning_rule = learning_rule
        self.use_forget_gate = use_forget_gate
        self.delta_chunk_size = 16
        self.layer_idx = layer_idx

        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.k_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        # Channel-wise learning rate beta_t.
        self.b_proj = nn.Linear(hidden_size, hidden_size, bias=False)

        if use_forget_gate:
            self.a_proj = nn.Linear(hidden_size, hidden_size, bias=False)
            A = torch.empty(hidden_size, dtype=torch.float32).uniform_(0, 16)
            self.A_log = nn.Parameter(torch.log(A))
            self.A_log._no_weight_decay = True
            dt_min = 0.001
            dt_max = 0.1
            dt_init_floor = 1e-4
            dt = torch.exp(
                torch.rand(hidden_size) * (math.log(dt_max) - math.log(dt_min))
                + math.log(dt_min),
            )
            dt = torch.clamp(dt, min=dt_init_floor)
            # Inverse of softplus: https://github.com/pytorch/pytorch/issues/72759
            inv_dt = dt + torch.log(-torch.expm1(-dt))
            self.dt_bias = nn.Parameter(inv_dt)
            self.dt_bias._no_weight_decay = True

        # Stashes for analysis, populated at every forward pass and not persisted:
        # the log decay and the learning rate as per-head channel means, [B, T, H]
        # (the full [B, T, H, head_dim] tensors are too large at packed-batch lengths).
        # stash_channels = True keeps the full tensors instead (analysis only, one sequence at a time).
        self.last_log_alpha: torch.Tensor | None = None
        self.last_beta: torch.Tensor | None = None
        self.stash_channels = False

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        past_key_values: Cache | None = None,
        use_cache: bool | None = False,
        output_attentions: bool | None = False,
        **kwargs: Unpack[dict],
    ) -> tuple[torch.Tensor, torch.Tensor | None, Cache | None]:
        if attention_mask is not None:
            assert len(attention_mask.shape) == 2, (
                "Expected attention_mask as a 0-1 matrix with shape [batch_size, seq_len] "
                "for padding purposes (0 indicating padding). "
                "Arbitrary attention masks of shape [batch_size, seq_len, seq_len] are not allowed."
            )

        batch_size, q_len, _ = hidden_states.shape
        # Hebbian: chunk kernel for training/long prefixes, fused recurrent for short inference steps (e.g. token-by-token
        # generation). The delta rule's chunk kernel serves both.
        mode = 'fused_recurrent' if (q_len <= 64 and not self.training) else 'chunk'

        last_state = get_layer_cache(self, past_key_values)

        cu_seqlens = kwargs.get('cu_seqlens')
        if cu_seqlens is None and attention_mask is not None:
            indices, cu_seqlens, _ = get_unpad_data(attention_mask[:, -q_len:])
            hidden_states = index_first_axis(rearrange(hidden_states, "b s ... -> (b s) ..."), indices).unsqueeze(0)

        q = F.silu(rearrange(self.q_proj(hidden_states), '... (h d) -> ... h d', d=self.head_dim))
        k = F.silu(rearrange(self.k_proj(hidden_states), '... (h d) -> ... h d', d=self.head_dim))
        v = rearrange(hidden_states.to(q.dtype), '... (h d) -> ... h d', d=self.head_dim)

        # Learning rate beta_t in (0, 1), [B, T, H, head_dim].
        beta = rearrange(self.b_proj(hidden_states).sigmoid(), '... (h d) -> ... h d', d=self.head_dim)

        # Log decay per key channel, fp32, [B, T, H, head_dim].
        if self.use_forget_gate:
            log_alpha = -torch.exp(self.A_log) * F.softplus(self.a_proj(hidden_states).float() + self.dt_bias.float())
            log_alpha = rearrange(log_alpha, '... (h d) -> ... h d', d=self.head_dim)
        else:
            log_alpha = hidden_states.new_zeros(*hidden_states.shape[:2], self.num_heads, self.head_dim, dtype=torch.float32)

        # Episodic state M_t starts at zero.
        recurrent_state = last_state['recurrent_state'] if last_state is not None else None

        q_in = F.normalize(q, p=2, dim=-1).to(q.dtype)
        k_in = F.normalize(k, p=2, dim=-1).to(k.dtype)
        if self.learning_rule == 'delta':
            # M_t = D_t M_{t-1} + k_hat (beta * (v - (D_t M_{t-1})^T k_hat))^T
            o, recurrent_state = chunk_delta_value(
                q=q_in,
                k=k_in,
                v=v,
                g=log_alpha,
                beta=beta,
                initial_state=recurrent_state,
                output_final_state=use_cache,
                cu_seqlens=cu_seqlens,
                chunk_size=self.delta_chunk_size,
            )
        else:
            # M_t = D_t M_{t-1} + k_hat (beta * v)^T
            v_in = (v * beta).to(v.dtype)
            gk = log_alpha.contiguous()
            if mode == 'chunk':
                o, recurrent_state = chunk_gla(
                    q=q_in,
                    k=k_in,
                    v=v_in,
                    g=gk,
                    initial_state=recurrent_state,
                    output_final_state=use_cache,
                    cu_seqlens=cu_seqlens,
                )
            else:
                o, recurrent_state = fused_recurrent_gla(
                    q=q_in,
                    k=k_in,
                    v=v_in,
                    gk=gk,
                    initial_state=recurrent_state,
                    output_final_state=use_cache,
                    cu_seqlens=cu_seqlens,
                )

        # Cache decay and learning rate for analysis (per-head channel means, or all channels).
        with torch.no_grad():
            if self.stash_channels:
                self.last_log_alpha = log_alpha.detach()
                self.last_beta = beta.float().detach()
            else:
                self.last_log_alpha = log_alpha.mean(-1).detach()
                self.last_beta = beta.float().mean(-1).detach()

        update_layer_cache(
            self,
            past_key_values,
            recurrent_state=recurrent_state,
            conv_state=None,
            offset=q_len,
        )

        o = rearrange(o, 'b t h d -> b t (h d)')
        if attention_mask is not None:
            o = pad_input(o.squeeze(0), indices, batch_size, q_len)

        return o, None, past_key_values
