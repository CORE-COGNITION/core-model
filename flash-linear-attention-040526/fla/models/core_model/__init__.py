# Copyright (c) 2023-2026, Songlin Yang, Yu Zhang, Zhiyuan Li
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# For a list of all contributors, visit:
#   https://github.com/fla-org/flash-linear-attention/graphs/contributors

from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

from fla.models.core_model.configuration_core_model import CoreModelConfig
from fla.models.core_model.modeling_core_model import CoreModelForCausalLM, CoreModelModel

AutoConfig.register(CoreModelConfig.model_type, CoreModelConfig, exist_ok=True)
AutoModel.register(CoreModelConfig, CoreModelModel, exist_ok=True)
AutoModelForCausalLM.register(CoreModelConfig, CoreModelForCausalLM, exist_ok=True)

__all__ = ['CoreModelConfig', 'CoreModelForCausalLM', 'CoreModelModel']
