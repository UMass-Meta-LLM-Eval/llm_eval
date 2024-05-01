"""Wrappers for the LLMs."""

import logging
logger = logging.getLogger('model')

from .base_model import BaseModel, DummyModel, ConstantModel, ReferenceModel
from .hf_model import HFModel, LlamaModel, MistralModel, Phi2Model, BAAIModel
from .human_model import HumanModel
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel

classes = {
    'DummyModel': DummyModel,
    'ConstantModel': ConstantModel,
    'HFModel': HFModel,
    'LlamaModel': LlamaModel,
    'MistralModel': MistralModel,
    'Phi2Model': Phi2Model,
    'HumanModel': HumanModel,
    'OpenAIModel': OpenAIModel,
    'AnthropicModel': AnthropicModel,
    'BAAIModel': BAAIModel,
    'ReferenceModel': ReferenceModel,
    # Add new models here
}

def create_model(model_config: dict = None, **kwargs) -> BaseModel:
    """Create a model from a config dictionary."""
    model_config = kwargs if model_config is None else model_config
    logger.info(f'Creating model of class: {model_config["cls"]}')
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
