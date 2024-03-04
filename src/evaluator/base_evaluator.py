from abc import ABC, abstractmethod
import base64
import hashlib
import json

class BaseEvaluator(ABC):

    @abstractmethod
    def evaluate(self, question, response, references, **kwargs)->tuple[bool, dict]:
        ...

    def evaluate_batch(self, questions, responses, references_list, **kwargs):
        return [self.evaluate(q, r, refs, **kwargs)
                for q, r, refs in zip(questions, responses, references_list)]
    
    def get_eval_key(self, key):
        self_str = json.dumps(self.config)
        return int(hashlib.sha256(
            (hex(key)+self_str).encode('utf-8')).hexdigest(), 16)
    
    @property
    @abstractmethod
    def config(self, key):
        ...


class DummyEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config

    def evaluate(self, question, response, references, **kwargs):
        return True, {}

    @property
    def config(self):
        return self._eval_config
