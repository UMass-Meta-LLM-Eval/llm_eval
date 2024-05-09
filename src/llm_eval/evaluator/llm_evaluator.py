from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..model import create_model
from ..helpers.templates.evaluator import llm_evaluator as templates
from ..helpers.constants.logging import UPDATE
from ..helpers.misc import extract_from_tag
from . import logger


class LLMEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._model = create_model(eval_config['model_config'])
        
        # Get the template name from the config
        try:
            template_name = eval_config['template']
        except KeyError as e:
            logger.error('Template name not found for LLM evaluator.')
            raise ValueError('Template name not found for '
                             'LLM Evaluator.') from e
        logger.log(UPDATE, 'Template name for LLM Evaluator: %s',
                   template_name)

        # Set the template to the specified template
        try:
            self.TEMPLATE = getattr(templates, template_name).PROMPT
        except AttributeError as e:
            logger.error('Template `%s` not found for LLM evaluator.',
                         template_name)
            raise ValueError('Invalid template name for LLM Evaluator: '
                             f'{template_name}') from e

        self._exact_match_evaluator = ExactMatchEvaluator({})
        self._doc = InfoDoc(**eval_config)

    def _format_prompt(self, question, references, response):
        return self.TEMPLATE.format(
            question=question,
            references='\n'.join(references),
            response=response)

    def evaluate(self, question, response, references, **kwargs):
        # Check if the response is an exact match
        is_exact_match, _ = self._exact_match_evaluator.evaluate(question,
                                                                 response,
                                                                 references)

        # Provide the llm with the question, references, and response
        prompt = self._format_prompt(question, references, response)
        evaluation = self._model.predict(prompt).lower().strip()
        ev, confident, parsed_successfully = self._parse_eval(evaluation)
        return ev, {'evaluation': evaluation,
                    'parsed_successfully': parsed_successfully,
                    'exact_match': is_exact_match,
                    'confident': confident}

    def _parse_eval(self, eval_str: str) -> tuple[bool, bool, bool]:
        if eval_str.startswith('correct'):
            ev, confident, parsed_successfully = True, True, True
        elif eval_str.startswith('incorrect'):
            ev, confident, parsed_successfully = False, True, True
        elif eval_str.startswith('maybe correct'):
            ev, confident, parsed_successfully = True, False, True
        elif eval_str.startswith('maybe incorrect'):
            ev, confident, parsed_successfully = False, False, True
        else:
            ev, confident, parsed_successfully = False, None, False
        return ev, confident, parsed_successfully

    @property
    def config(self):
        return self._eval_config

    @property
    def hashval(self):
        return self._doc.doc_id

    def exit(self, message: str = None):
        del self._model
        super().exit(message)


class LLMExtractEvaluator(LLMEvaluator):
    def __init__(self, eval_config: dict):
        super().__init__(eval_config)
        try:
            self._extract_tag = eval_config['eval_tag']
        except KeyError as e:
            logger.error('Evaluation tag not found for LLM Extract Evaluator.')
            raise ValueError('Evaluation tag not found for '
                             'LLM Extract Evaluator.') from e

    def _format_prompt(self, question, references, response):
        return self.TEMPLATE.format(
            question=question,
            references='\n'.join(references),
            response=response,
            extract_tag=self._extract_tag)
    
    def _parse_eval(self, eval_str: str) -> tuple[bool, bool, bool]:
        extracted = extract_from_tag(eval_str, self._extract_tag)
        if extracted is not None:
            eval_str = extracted

        return super()._parse_eval(eval_str)
