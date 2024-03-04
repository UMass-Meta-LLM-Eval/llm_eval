"""Wrappers for the LLMs."""

from .base_model import BaseModel, DummyModel
from .llama_model import LlamaModel
from .human_model import HumanModel

classes = {
    'DummyModel': DummyModel,
    'LlamaModel': LlamaModel,
    'HumanModel': HumanModel,
    # Add new models here
}

def create_model(model_config: dict) -> BaseModel:
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
