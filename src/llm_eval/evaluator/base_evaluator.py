from abc import ABC, abstractmethod
import hashlib
import json

from ..helpers import InfoDoc

class BaseEvaluator(ABC):
    @abstractmethod
    def __init__(self, eval_config: dict):
        ...

    @abstractmethod
    def evaluate(self, question, response, references, **kwargs)->tuple[bool, dict]:
        ...

    def evaluate_batch(self, questions, responses, references_list, **kwargs):
        return [self.evaluate(q, r, refs, **kwargs)
                for q, r, refs in zip(questions, responses, references_list)]
    
    @property
    @abstractmethod
    def config(self, key):
        ...

    @property
    @abstractmethod
    def hashval(self) -> str:
        """Return the SHA256 hash of the evaluator's configuration as a base64
        string."""


class DummyEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._doc = InfoDoc(**eval_config)

    def evaluate(self, question, response, references, **kwargs):
        return True, {}

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id
