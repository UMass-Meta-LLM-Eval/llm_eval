"""Wrappers for the LLMs."""

from .base_model import BaseModel, DummyModel
from .llama_model import LlamaModel
# from dotenv import load_dotenv
# load_dotenv()
import os

classes = {
    'DummyModel': DummyModel,
    'LlamaModel': LlamaModel,
    # Add new models here
}

def create_model(model_config: dict):
    print('Loading LLM with config - ', model_config)
    print('HF Home set to - ', os.getenv('HF_HOME'))
    print('HF Token set to - ', os.getenv('HF_TOKEN'))
    model_cls = classes[model_config['cls']]
    return model_cls(model_config)
