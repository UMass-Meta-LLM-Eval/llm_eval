from .base_evaluator import BaseEvaluator, DummyEvaluator
from .classic_evaluator import (ExactMatchEvaluator, ContainsMatchEvaluator,
                                ContainsWordsEvaluator)

classes = {
    'DummyEvaluator': DummyEvaluator,
    'ExactMatchEvaluator': ExactMatchEvaluator,
    'ContainsMatchEvaluator': ContainsMatchEvaluator,
    'ContainsWordsEvaluator': ContainsWordsEvaluator,
    # Add new evaluators here
}

def create_evaluator(eval_config: dict):
    eval_cls = classes[eval_config['cls']]
    return eval_cls(eval_config)
