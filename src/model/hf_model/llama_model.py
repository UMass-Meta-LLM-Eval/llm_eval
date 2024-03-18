from .base_hf_model import BaseHFModel

class LlamaModel(BaseHFModel):
    HF_ORG_NAME = 'meta-llama'

    def _predict(self, prompt: str) -> str:
        if self._config.get('chat', False):
            prompt = f'[INST]{prompt}[/INST]'
        
        return super()._predict(prompt)
