"""Wrappers for the LLMs."""

from .base_model import BaseModel, DummyModel
from .hf_model import (FalconModel, GemmaModel, LlamaModel, MistralModel,
                       OlmoModel, Phi2Model, VicunaModel, ZephyrModel)
from .human_model import HumanModel
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel

classes = {
    'DummyModel': DummyModel,
    'FalconModel': FalconModel,
    'GemmaModel': GemmaModel,
    'LlamaModel': LlamaModel,
    'MistralModel': MistralModel,
    'OlmoModel': OlmoModel,
    'Phi2Model': Phi2Model,
    'VicunaModel': VicunaModel,
    'ZephyrModel': ZephyrModel,
    'HumanModel': HumanModel,
    'OpenAIModel': OpenAIModel,
    'AnthropicModel': AnthropicModel,
    # Add new models here
}

def create_model(model_config: dict) -> BaseModel:
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
