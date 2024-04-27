from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..model import create_model
from ..helpers.templates.evaluator import llm_evaluator as templates
from ..helpers.constants.logging import UPDATE
from . import logger


class LLMEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._model = create_model(eval_config['model_config'])
        
        # Get the template name from the config
        template_name = eval_config.get('template', 'DEFAULT').upper()
        logger.log(UPDATE, 'Template name: %s', template_name)

        # Set the template to the specified template
        if hasattr(templates, template_name):
            self.TEMPLATE = getattr(templates, template_name).PROMPT
        else:
            logger.log(UPDATE, 'Template `%s` not found. Using default '
                       'template.', template_name)
            self.TEMPLATE = templates.DEFAULT.PROMPT

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
        if evaluation.startswith('maybe correct'):
            confident = False
            ev = True
            parsed_successfully = True
        elif evaluation.startswith('maybe incorrect'):
            confident = False
            ev = False
            parsed_successfully = True
        elif evaluation.startswith('correct'):
            confident = True
            ev = True
            parsed_successfully = True
        elif evaluation.startswith('incorrect'):
            confident = True
            ev = False
            parsed_successfully = True
        else:
            confident = None
            ev = False
            parsed_successfully = False
        return ev, {'evaluation': evaluation,
                    'parsed_successfully': parsed_successfully,
                    'exact_match': is_exact_match,
                    'confident': confident}

    @property
    def config(self):
        return self._eval_config

    @property
    def hashval(self):
        return self._doc.doc_id
    
    def exit(self):
        del self._model
        super().exit()
