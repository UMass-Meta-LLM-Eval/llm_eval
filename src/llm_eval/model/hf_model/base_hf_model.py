import os
import torch
from transformers import pipeline, AutoTokenizer

from ..base_model import BaseModel
from ...helpers.documents import InfoDoc

class BaseHFModel(BaseModel):
    """Base class for all HuggingFace models."""

    HF_ORG_NAME = ''
    """Name of the organization that provides the model."""

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
        
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str) -> str:
        sequences = self.pipeline(
            prompt,
            eos_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=self._config.get('max_new_tokens', 32))
        response = sequences[0]['generated_text']
        if response.startswith(prompt):
            response = response[len(prompt):]
        return response.strip()

    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
