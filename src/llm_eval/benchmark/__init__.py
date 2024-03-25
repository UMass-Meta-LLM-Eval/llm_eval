"""Wrappers for the benchmarks."""

import logging
logger = logging.getLogger(__name__)

from .base_benchmark import BaseBenchmark, DummyBenchmark
from .mmlu import MMLUBenchmark
from .naturalquestions import NaturalQuestionsBenchmark, DummyNQBenchmark
from .test_benchmark import TestBenchmark
from .triviaqa import TriviaQABenchmark

classes = {
    'DummyBenchmark': DummyBenchmark,
    'MMLUBenchmark': MMLUBenchmark,
    'NaturalQuestionsBenchmark' : NaturalQuestionsBenchmark,
    'DummyNQBenchmark': DummyNQBenchmark,
    'TestBenchmark': TestBenchmark,
    'TriviaQABenchmark': TriviaQABenchmark,
    # Add new benchmarks here
}

def create_benchmark(bm_config: dict) -> BaseBenchmark:
    bm_cls = classes[bm_config['cls']]
    return bm_cls(bm_config)
