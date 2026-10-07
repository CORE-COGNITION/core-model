# Reference PyTorch implementation of the delta_value rule (CoreModel, --learning_rule delta_value).
#
# Update rule (per token, on the matrix state S in R^{K x V}):
#
#   S~_t = Diag(exp(g_t)) S_{t-1}
#   S_t  = S~_t + k_t (beta_t * (v_t - S~_t^T k_t))^T
#   o_t  = S_t^T q_t * scale
#
# `beta_t in R^V` is a learning rate per value channel on the prediction error, `g_t in R^K` the channel-wise
# log-decay. Every value channel j follows a scalar delta rule S_t[:, j] = (I - beta_tj k_t k_t^T) S~_t[:, j] + ...

import torch


def naive_recurrent_delta_value(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    g: torch.Tensor,
    beta: torch.Tensor,
    scale: float | None = None,
    initial_state: torch.Tensor | None = None,
    output_final_state: bool = False,
):
    """Token-by-token reference (differentiable, keeps the input dtype).

    Args:
        q, k: [B, T, H, K] (already L2-normalised). v, beta: [B, T, H, V]. g: log-decay [B, T, H, K].
        initial_state: optional [B, H, K, V].

    Returns:
        o [B, T, H, V], final state [B, H, K, V] or None.
    """
    B, T, H, K = k.shape
    V = v.shape[-1]
    if scale is None:
        scale = K ** -0.5
    S = k.new_zeros(B, H, K, V) if initial_state is None else initial_state.to(k.dtype)
    o = []
    for t in range(T):
        S = S * g[:, t].exp().unsqueeze(-1)
        e = v[:, t] - (k[:, t].unsqueeze(-1) * S).sum(-2)                 # prediction error [B, H, V]
        S = S + k[:, t].unsqueeze(-1) * (beta[:, t] * e).unsqueeze(-2)
        o.append((q[:, t].unsqueeze(-1) * S).sum(-2) * scale)
    return torch.stack(o, dim=1), (S if output_final_state else None)
