# Copyright (c) 2023-2026, Songlin Yang, Yu Zhang, Zhiyuan Li
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# For a list of all contributors, visit:
#   https://github.com/fla-org/flash-linear-attention/graphs/contributors

from transformers.configuration_utils import PretrainedConfig


class CoreModelConfig(PretrainedConfig):
    model_type = 'core_model'
    keys_to_ignore_at_inference = ['past_key_values']

    def __init__(
        self,
        hidden_size: int = 128,
        num_heads: int = 4,
        head_dim: int = 32,
        learning_rule: str = 'delta',
        use_forget_gate: bool = True,
        num_hidden_layers: int = 6,
        norm_eps: float = 1e-6,
        use_cache: bool = True,
        pad_token_id: int | None = None,
        bos_token_id: int = 1,
        eos_token_id: int = 2,
        tie_word_embeddings: bool = False,
        initializer_range: float = 0.02,
        vocab_size: int = 32000,
        response_token_ids: list[int] | None = None,
        **kwargs,
    ):
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.learning_rule = learning_rule
        self.use_forget_gate = use_forget_gate

        self.num_hidden_layers = num_hidden_layers
        self.norm_eps = norm_eps
        self.use_cache = use_cache
        self.initializer_range = initializer_range

        self.vocab_size = vocab_size
        self.response_token_ids = response_token_ids

        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )
