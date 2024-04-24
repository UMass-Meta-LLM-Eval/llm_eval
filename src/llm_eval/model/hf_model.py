import os
import torch
from transformers import pipeline, AutoTokenizer

from .base_model import BaseModel
from ..helpers.documents import InfoDoc

class BaseHFModel(BaseModel):
    """Base class for all HuggingFace models."""

    @property
    def HF_ORG_NAME(self) -> str:
        """Name of the organization that provides the model."""
        raise NotImplementedError('HF_ORG_NAME must be set in a '
                                  'derived class.')

    def __init__(self, model_config: dict):
        self._config = model_config

        model_name = self._config['model']
        if '/' not in model_name:
            model_name = f'{self.HF_ORG_NAME}/{model_name}'

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=os.getenv('HF_TOKEN'))
        self.pipeline = pipeline('text-generation',
                                  model=model_name,
                                  tokenizer=self.tokenizer,
                                  torch_dtype=torch.float16,
                                  device_map='auto',
                                  token=os.getenv('HF_TOKEN'))
        
        self._terminators = self.tokenizer.eos_token_id
        
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str, chat:bool = None) -> str:
        chat = self._config.get('chat', False) if chat is None else chat
        if chat:
            messages = [{'role': 'user', 'content': prompt}]
            prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)

        sequences = self.pipeline(
            prompt,
            eos_token_id=self._terminators,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=self._config.get('max_new_tokens', 32),
            return_full_text=False)

        response: str = sequences[0]['generated_text']
        return response.strip()

    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id


class HFModel(BaseHFModel):
    """Generic class for loading a HuggingFace model that does not require
    any special code.
    
    This class does not support short names for models. The model name must
    be the full HuggingFace model name including the organization name.
    """


class LlamaModel(BaseHFModel):
    HF_ORG_NAME = 'meta-llama'
    def __init__(self, model_config: dict):
        super().__init__(model_config)
        if 'Meta-Llama-3' in self._config['model']:
            self._terminators = [
                self.tokenizer.eos_token_id,
                self.tokenizer.convert_tokens_to_ids('<|eot_id|>')]


class MistralModel(BaseHFModel):
    """Mistral model class for backward compatibility. Use HFModel instead
    since this model does not require any special code."""
    HF_ORG_NAME = 'mistralai'


class Phi2Model(BaseHFModel):
    HF_ORG_NAME = 'microsoft'

    def _predict(self, prompt: str) -> str:
        if self._config.get('chat', False):
            prompt = f'Instruct: {prompt}\nOutput:'
        
        return super()._predict(prompt)