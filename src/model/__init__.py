"""Wrappers for the LLMs."""

from .base_model import BaseModel, DummyModel
from .llama_model import LlamaModel
from .human_model import HumanModel
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel

classes = {
    'DummyModel': DummyModel,
    'LlamaModel': LlamaModel,
    'HumanModel': HumanModel,
    'OpenAIModel': OpenAIModel,
    'AnthropicModel': AnthropicModel,
    # Add new models here
}

def create_model(model_config: dict) -> BaseModel:
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
