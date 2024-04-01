from .base_hf_model import BaseHFModel

class MistralModel(BaseHFModel):
    HF_ORG_NAME = 'mistralai'

    def _predict(self, prompt: str) -> str:
        if self._config.get('chat', False):
            prompt = f'<s>[INST]{prompt}[/INST]'
        
        return super()._predict(prompt)
