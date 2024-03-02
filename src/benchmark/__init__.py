"""Wrappers for the benchmarks."""

from .base_benchmark import BaseBenchmark, DummyBenchmark
from .mmlu import MMLUBenchmark
from .naturalquestions import NaturalQuestions

classes = {
    'DummyBenchmark': DummyBenchmark,
    'MMLUBenchmark': MMLUBenchmark,
    'NaturalQuestions' : NaturalQuestions
    # Add new benchmarks here
}

def create_benchmark(bm_config: dict):
    print('Loading Benchmark with config - ', bm_config)
    bm_cls = classes[bm_config['cls']]
    return bm_cls(bm_config)
