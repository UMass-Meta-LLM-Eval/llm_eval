import os

from transformers import AutoTokenizer
import torch
from transformers import pipeline


from .base_model import BaseModel

class LlamaModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        self.prefix = model_config['prefix']
        print('Loading Model - ', self._config['model'])
        self.tokenizer = AutoTokenizer.from_pretrained(
            self._config['model'], use_auth_token=True)

        self.pipeline = pipeline('text-generation',
                                  model=self._config['model'],
                                  torch_dtype=torch.float16,
                                  device_map='auto')

    def predict(self, prompt:str , b64_input: bool = False, b64_output: bool = False) -> str:
        sequences = self.pipeline(
            prompt,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_length=256)
        response = sequences[0]['generated_text']
        if response.startswith(prompt):
            response = response[len(prompt):]
        return response.strip()

    def _predict(self, prompt: str) -> str:
        return self.prefix + prompt

    @property
    def config(self) -> dict:
        return self._config
