import base64
from abc import ABC, abstractmethod
from ..helpers import InfoDoc

class BaseModel(ABC):
    @abstractmethod
    def __init__(self, model_config: dict):
        ...

    def predict(self, prompt:str , b64_input: bool = False, b64_output: bool = False):
        if b64_input:
            prompt = base64.b64decode(prompt).decode('utf-8')
        prediction = self._predict(prompt)
        if b64_output:
            prediction = prediction.encode('utf-8')
            prediction = base64.b64encode(prediction).decode('utf-8')
        return prediction

    @abstractmethod
    def _predict(self, prompt: str) -> str:
        """Return a prediction given a prompt."""
        ...

    @property
    @abstractmethod
    def config(self) -> dict:
        """Return the model's configuration."""

    @property
    @abstractmethod
    def hashval(self) -> str:
        """Return the SHA256 hash of the model's configuration as a base64
        string."""


class DummyModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        self.prefix = model_config['prefix']
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str) -> str:
        return self.prefix + prompt
    
    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
