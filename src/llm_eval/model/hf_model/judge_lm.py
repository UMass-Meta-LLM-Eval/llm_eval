from .base_hf_model import BaseHFModel
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from ...helpers.documents import InfoDoc

class JudgeLM(BaseHFModel):
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
            max_new_tokens=self._config.get('max_new_tokens', 32))
        response = self.tokenizer.decode(sequences[0])

        if response.startswith(self.starttoken):
            response = response[len(self.starttoken):].strip()
        
        if response.startswith(prompt):
            response = response[len(prompt):]
        return response.strip()
