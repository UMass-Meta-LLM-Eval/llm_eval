import os
import torch
from transformers import pipeline, AutoTokenizer

from .base_model import BaseModel

class LlamaModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        self.tokenizer = AutoTokenizer.from_pretrained(
            self._config['model'], token=os.getenv('HF_TOKEN'))

        self.pipeline = pipeline('text-generation',
                                  model=self._config['model'],
                                  torch_dtype=torch.float16,
                                  device_map='auto')

    def _predict(self, prompt: str) -> str:
        sequences = self.pipeline(
            prompt,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=32)
        response = sequences[0]['generated_text']
        if response.startswith(prompt):
            response = response[len(prompt):]
        return response.strip()

    @property
    def config(self) -> dict:
        return self._config
