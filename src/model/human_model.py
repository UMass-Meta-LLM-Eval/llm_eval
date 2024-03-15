from .base_model import BaseModel
from ..helpers.documents import InfoDoc

class HumanModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str) -> str:
        return input(prompt+'\n').strip()
    
    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
