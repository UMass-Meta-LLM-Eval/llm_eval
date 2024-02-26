"""Wrappers for the LLMs."""

from .base_model import BaseModel, DummyModel
from .llama_model import LlamaModel

classes = {
    'DummyModel': DummyModel,
    'LlamaModel': LlamaModel,
    # Add new models here
}

def create_model(model_config: dict):
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
