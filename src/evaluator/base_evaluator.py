from abc import ABC, abstractmethod


class BaseEvaluator(ABC):

    @abstractmethod
    def evaluate(self, question, response, references, **kwargs)->bool:
        ...

    def evaluate_batch(self, questions, responses, references_list, **kwargs):
        return [self.evaluate(q, r, refs, **kwargs)
                for q, r, refs in zip(questions, responses, references_list)]
    
    @property
    @abstractmethod
    def config(self):
        ...


class DummyEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config

    def evaluate(self, question, response, references, **kwargs):
        return True
    
    @property
    def config(self):
        return self._eval_config
