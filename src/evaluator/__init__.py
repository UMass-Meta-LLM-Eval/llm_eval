from .base_evaluator import BaseEvaluator, DummyEvaluator
from .classic_evaluator import (ExactMatchEvaluator, ContainsMatchEvaluator,
                                ContainsWordsEvaluator)
from .human_evaluator import HumanEvaluator
from .llm_evaluator import LLMEvaluator

classes = {
    'DummyEvaluator': DummyEvaluator,
    'ExactMatchEvaluator': ExactMatchEvaluator,
    'ContainsMatchEvaluator': ContainsMatchEvaluator,
    'ContainsWordsEvaluator': ContainsWordsEvaluator,
    'HumanEvaluator': HumanEvaluator,
    'LLMEvaluator': LLMEvaluator,
    # Add new evaluators here
}

def create_evaluator(eval_config: dict) -> BaseEvaluator:
    eval_cls = classes[eval_config['cls']]
    return eval_cls(eval_config)
