import evaluate

from .base_evaluator import BaseEvaluator
from ..helpers import InfoDoc

class HFEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._evaluator = evaluate.load(self.EVAL_NAME)
        self._doc = InfoDoc(**eval_config)

    def _evaluate(self, response, references):
        return self._evaluator(references=references, predictions=response)

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id


class BLEUEvaluator(HFEvaluator):
    EVAL_NAME = 'bleu'

    def evaluate(self, question, response, references, **kwargs):
        threshold = self.config.get('threshold', 1.0)
        eval = self._evaluate(response, references)
        return eval['bleu'] >= threshold, eval
