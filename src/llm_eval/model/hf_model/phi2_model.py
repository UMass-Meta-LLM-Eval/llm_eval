from .base_hf_model import BaseHFModel

class Phi2Model(BaseHFModel):
    HF_ORG_NAME = 'microsoft'

    def _predict(self, prompt: str) -> str:
        if self._config.get('chat', False):
            prompt = f'Instruct: {prompt}\nOutput:'
        
        return super()._predict(prompt)
