import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

from .base_model import BaseModel
from ..helpers.documents import InfoDoc
from ..helpers.constants.model import HF_MAX_NEW_TOKENS
from . import logger

class BaseHFModel(BaseModel):
    """Base class for all HuggingFace models."""

    @property
    def HF_ORG_NAME(self) -> str:
        """Name of the organization that provides the model."""
        raise NotImplementedError('HF_ORG_NAME must be set in a '
                                  'derived class.')

    def __init__(self, model_config: dict):
        self._config = model_config

        try:
            model_name = self._config['model']
        except KeyError as e:
            logger.error('Model name not found for HF Model.')
            raise ValueError('Model name not found for HF Model.') from e

        if '/' not in model_name:
            model_name = f'{self.HF_ORG_NAME}/{model_name}'

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=os.getenv('HF_TOKEN'),
            trust_remote_code=True)
        self.pipeline = pipeline('text-generation',
                                  model=model_name,
                                  tokenizer=self.tokenizer,
                                  torch_dtype=torch.float16,
                                  device_map='auto',
                                  token=os.getenv('HF_TOKEN'),
                                  trust_remote_code=True)
        
        self._terminators = self.tokenizer.eos_token_id
        
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str, **kwargs) -> str:
        chat = kwargs.get('chat', self._config.get('chat', False))
        if chat:
            messages = [{'role': 'user', 'content': prompt}]
            prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)

        sequences = self.pipeline(
            prompt,
            eos_token_id=self._terminators,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=self._config.get('max_new_tokens',
                                            HF_MAX_NEW_TOKENS),
            return_full_text=False,
            do_sample=False)

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

    def __init__(self, model_config: dict):
        raise ValueError('Phi2Model is not working correctly in this '
                         'version of the code.')
        
class BAAIModel(BaseHFModel):
    HF_ORG_NAME = 'BAAI'

    def __init__(self, model_config: dict):
        self._config = model_config
        self.starttoken = '<s>'

        model_name = self._config['model']
        if '/' not in model_name:
            model_name = f'{self.HF_ORG_NAME}/{model_name}'

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=os.getenv('HF_TOKEN'))
        self.pipeline = AutoModelForCausalLM.from_pretrained(model_name,
                                  torch_dtype=torch.float16,
                                  device_map='auto')

        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str) -> str:
        sequences = self.pipeline.generate(
            **self.tokenizer(prompt, return_tensors='pt').to('cuda'),
            max_new_tokens=self._config.get('max_new_tokens',
                                            HF_MAX_NEW_TOKENS),
            do_sample=False)
        response = self.tokenizer.decode(sequences[0])

        if response.startswith(self.starttoken):
            response = response[len(self.starttoken):].strip()

        if response.startswith(prompt):
            response = response[len(prompt):]
        return response.strip()
