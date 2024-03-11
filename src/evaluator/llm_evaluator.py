from textwrap import dedent

from .base_evaluator import BaseEvaluator
from ..model import create_model

class LLMEvaluator(BaseEvaluator):
    TEMPLATE = dedent('''
    Question:
    {question}

    References:
    {references}

    Model Response:
    {response}

    Evaluation (correct/incorrect):
    ''').strip()
    
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._model = create_model(eval_config['model_config'])
        if 'template' in eval_config:
            self.TEMPLATE = eval_config['template']

    def _format_prompt(self, question, references, response):
        return self.TEMPLATE.format(
            question=question,
            references='\n'.join(references),
            response=response)

    def evaluate(self, question, response, references, **kwargs):
        prompt = self._format_prompt(question, references, response)
        evaluation = self._model.predict(prompt).lower().strip()
        return evaluation.startswith('correct'), {'evaluation': evaluation}

    @property
    def config(self):
        return self._eval_config
