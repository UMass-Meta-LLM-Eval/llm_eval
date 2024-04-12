import evaluate

from .base_evaluator import BaseEvaluator
from ..helpers import InfoDoc

class HFEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._evaluator = evaluate.load(self.EVAL_NAME)
        self._doc = InfoDoc(**eval_config)

    def _evaluate(self, response, references, **kwargs):
        return self._evaluator.compute(references=[references],
                                       predictions=[response],
                                       **kwargs)

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id


class BLEUEvaluator(HFEvaluator):
    # NOTE: DOES NOT WORK PROPERLY. DO NOT USE!!!
    EVAL_NAME = 'bleu'

    def evaluate(self, question, response, references, **kwargs):
        threshold = self.config.get('threshold', 1.0)
        evaluation = self._evaluate(response, references)
        return evaluation['bleu'] >= threshold, eval
    

class BERTEvaluator(HFEvaluator):
    EVAL_NAME = 'bertscore'

    def evaluate(self, question, response, references, **kwargs):
        threshold = self.config.get('threshold', 0.5)
        evaluation = self._evaluate(response, references,
                                    lang=self.config.get('lang'),
                                    model_type=self.config.get(
                                        'model_type',
                                        'distilbert-base-uncased'))
        return evaluation['f1'][0] >= threshold, evaluation
