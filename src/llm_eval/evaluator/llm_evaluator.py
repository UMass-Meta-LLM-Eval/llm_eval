from textwrap import dedent

from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..model import create_model

class LLMEvaluator(BaseEvaluator):
    TEMPLATE = dedent('''
    Your task is to look at the following question, and based on the references
    provided, determine if the model's response is correct or incorrect.
    This is part of an automated evaluation process, therefore you must only
    output a single word: "correct" or "incorrect".

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
            self.TEMPLATE = dedent(eval_config['template']).strip()
        self._exact_match_evaluator = ExactMatchEvaluator({})
        self._doc = InfoDoc(**eval_config)

    def _format_prompt(self, question, references, response):
        return self.TEMPLATE.format(
            question=question,
            references='\n'.join(references),
            response=response)

    def evaluate(self, question, response, references, **kwargs):
        # If the response is an exact match, return True
        is_exact_match, _ = self._exact_match_evaluator.evaluate(question,
                                                                 response,
                                                                 references)
        if is_exact_match:
            return True, {'evaluation': 'correct',
                          'parsed_successfully': 'N/A'}

        # Provide the llm with the question, references, and response
        prompt = self._format_prompt(question, references, response)
        evaluation = self._model.predict(prompt).lower().strip()
        if evaluation.startswith('correct'):
            ev = True
            parsed_successfully = True
        elif evaluation.startswith('incorrect'):
            ev = False
            parsed_successfully = True
        else:
            ev = False
            parsed_successfully = False
        return ev, {'evaluation': evaluation,
                    'parsed_successfully': parsed_successfully}

    @property
    def config(self):
        return self._eval_config

    @property
    def hashval(self):
        return self._doc.doc_id
