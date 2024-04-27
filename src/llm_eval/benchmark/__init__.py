"""Wrappers for the benchmarks."""

import logging
logger = logging.getLogger('benchmark')

from .base_benchmark import BaseBenchmark, DummyBenchmark
from .mmlu import MMLUBenchmark
from .naturalquestions import NaturalQuestionsBenchmark
from .triviaqa import TriviaQABenchmark

classes = {
    'DummyBenchmark': DummyBenchmark,
    'MMLUBenchmark': MMLUBenchmark,
    'NaturalQuestionsBenchmark' : NaturalQuestionsBenchmark,
    'TriviaQABenchmark': TriviaQABenchmark,
    # Add new benchmarks here
}

def create_benchmark(bm_config: dict) -> BaseBenchmark:
    bm_cls = classes[bm_config['cls']]
    return bm_cls(bm_config)
