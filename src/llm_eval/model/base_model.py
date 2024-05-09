import base64
from abc import ABC, abstractmethod
from . import logger
from ..helpers import InfoDoc
from ..helpers.constants.logging import UPDATE

class BaseModel(ABC):
    @abstractmethod
    def __init__(self, model_config: dict):
        ...

    def predict(self, prompt:str , b64_input: bool = False,
                b64_output: bool = False, **kwargs):
        if b64_input:
            prompt = base64.b64decode(prompt).decode('utf-8')
        prediction = self._predict(prompt, **kwargs)
        if b64_output:
            prediction = prediction.encode('utf-8')
            prediction = base64.b64encode(prediction).decode('utf-8')
        return prediction

    @abstractmethod
    def _predict(self, prompt: str, **kwargs) -> str:
        """Return a prediction given a prompt."""

    @property
    @abstractmethod
    def config(self) -> dict:
        """Return the model's configuration."""

    @property
    @abstractmethod
    def hashval(self) -> str:
        """Return the SHA256 hash of the model's configuration as a base64
        string."""

    def exit(self, message: str = None):
        """Perform any necessary cleanup operations."""
        logger.log(UPDATE, 'Exiting model: `%s`. Message: %s',
                   self.config.get('name', 'UNKNOWN'),
                   message)

class DummyModel(BaseModel):
    """A dummy model that simply returns the prompt with a prefix and
    suffix added. The prefix and suffix are specified in the model
    configuration."""
    def __init__(self, model_config: dict):
        self._config = model_config
        self.prefix = model_config.get('prefix', '')
        self.suffix = model_config.get('suffix', '')
        logger.log(UPDATE, 'Dummy model created with prefix: `%s` and '
                   'suffix: `%s`', self.prefix, self.suffix)
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str, **kwargs) -> str:
        return self.prefix + prompt + self.suffix
    
    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
    

class ConstantModel(BaseModel):
    """A baseline model that always returns the same constant string. The
    constant string is specified in the model configuration."""
    def __init__(self, model_config: dict):
        self._config = model_config
        self.constant = model_config.get('constant',
                                         'This is a constant model.')
        logger.log(UPDATE, 'Constant model created with constant: `%s`',
                     self.constant)
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str, **kwargs) -> str:
        return self.constant
    
    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id


class ReferenceModel(BaseModel):
    """A baseline model that returns the first reference in the list of
    references as its prediction. Therefore, the prediction is always
    correct."""

    def __init__(self, model_config: dict):
        self._config = model_config
        logger.log(UPDATE, 'Reference model created.')
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str, **kwargs) -> str:
        return kwargs['references'][0]
    
    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
