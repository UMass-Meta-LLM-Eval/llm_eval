from .base_evaluator import BaseEvaluator, DummyEvaluator

classes = {
    'DummyEvaluator': DummyEvaluator,
    # Add new evaluators here
}

def create_evaluator(eval_config: dict):
    eval_cls = classes[eval_config['cls']]
    return eval_cls(eval_config)
