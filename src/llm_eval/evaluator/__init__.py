"""Wrappers for the evaluators."""

import logging
logger = logging.getLogger('evaluator')

from .base_evaluator import BaseEvaluator, DummyEvaluator
from .classic_evaluator import (ExactMatchEvaluator, ContainsMatchEvaluator,
                                ContainsWordsEvaluator)
from .human_evaluator import HumanEvaluator, MultiHumanEvaluator
from .llm_evaluator import LLMEvaluator, LLMExtractEvaluator
from .hf_evaluator import BERTEvaluator
from .staged_llm_evaluator import StagedLLMEvaluator

classes = {
    'DummyEvaluator': DummyEvaluator,
    'ExactMatchEvaluator': ExactMatchEvaluator,
    'ContainsMatchEvaluator': ContainsMatchEvaluator,
    'ContainsWordsEvaluator': ContainsWordsEvaluator,
    'HumanEvaluator': HumanEvaluator,
    'LLMEvaluator': LLMEvaluator,
    'BERTEvaluator': BERTEvaluator,
    'MultiHumanEvaluator': MultiHumanEvaluator,
    'StagedLLMEvaluator': StagedLLMEvaluator,
    'LLMExtractEvaluator': LLMExtractEvaluator,
    # Add new evaluators here
}

def create_evaluator(eval_config: dict) -> BaseEvaluator:
    eval_cls = classes[eval_config['cls']]
    return eval_cls(eval_config)
