import evaluate

from .base_evaluator import BaseEvaluator

class HFEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._evaluator = evaluate.load(self.EVAL_NAME)

    def _evaluate(self, response, references):
        return self._evaluator(references=references, predictions=response)

    @property
    def config(self):
        return self._eval_config


class BLEUEvaluator(HFEvaluator):
    EVAL_NAME = 'bleu'

    def evaluate(self, question, response, references, **kwargs):
        threshold = self.config.get('threshold', 1.0)
        eval = self._evaluate(response, references)
        return eval['bleu'] >= threshold, eval