from textwrap import dedent
import re

from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..model import create_model
from ..helpers.templates.evaluator import staged_llm_evaluator as templates
from ..helpers.constants.logging import UPDATE
from ..helpers.misc import extract_from_tag
from . import logger

class StagedLLMEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._model = create_model(eval_config['model_config'])

        # Set the extract, split, and match templates
        self._set_template('extract')
        self._set_template('split')
        self._set_template('match')
        
        self._exact_match_evaluator = ExactMatchEvaluator({})
        self._doc = InfoDoc(**eval_config)
        
    def _set_template(self, template_type: str):
        try:
            template_name = self._eval_config[f'{template_type}_template'
                                              ].upper()
            logger.log(UPDATE, '%s template name for staged LLM evaluator: %s',
                    template_type, template_name)
            template = getattr(templates, template_name)
        except KeyError as e:
            logger.error('%s template name not provided for '
                         'staged LLM evaluator.', template_type)
            raise ValueError(f'{template_type} template name not provided for '
                             'staged LLM Evaluator.') from e
        except AttributeError as e:
            logger.error('Template `%s` not found for staged LLM evaluator.',
                         template_name)
            raise ValueError('Invalid template name for staged LLM Evaluator: '
                             f'{template_name}') from e

        for arg in template.ARGS:
            set_arg = f'{template_type}_{arg}'.upper()
            setattr(self, set_arg, getattr(template, arg))
            logger.info('Set `self.%s` to `%s.%s`',
                        set_arg, template_name, arg)

    def _extract(self, question, references, response) -> tuple[str, dict]:
        """Extract the actual answer from the response."""
        prompt = self.EXTRACT_PROMPT.format(question=question,
                                              references='\n'.join(references),
                                              response=response)
        eval_response = self._model.predict(prompt)
        extracted = extract_from_tag(eval_response, self.EXTRACT_TAG)
        extracted = extracted if extracted is not None else ''
        return extracted.strip(), {'extract_response': eval_response}

    def _split(self, question, references, response) -> tuple[list[str], dict]:
        """Split the response into multiple answers."""
        if response == '':
            return [], ''
        
        prompt = self.SPLIT_PROMPT.format(question=question,
                                            references='\n'.join(references),
                                            response=response)
        eval_response = self._model.predict(prompt)
        split = extract_from_tag(eval_response, self.SPLIT_TAG,
                            multi_ok=True)
        split = [] if split is None else split
        split = [s.strip() for s in split]
        return split, {'split_response': eval_response}

    def _match(self, question, answer, reference) -> tuple[bool, dict]:
        """Match the answer to a reference."""
        prompt = self.MATCH_PROMPT.format(question=question,
                                            answer=answer,
                                            reference=reference)
        response = self._model.predict(prompt).lower().strip()
        if response.startswith(self.MATCH_POS.lower()):
            return True, {'match_response': response}
        elif response.startswith(self.MATCH_NEG.lower()):
            return False, {'match_response': response}
        else:
            logger.warning('Invalid matching response from the model: %s',
                           response)
            return False, {'match_response': response}

    def _evaluate(self, question, response, references) -> tuple[bool, dict]:
        """Evaluate the response to a question using multiple stages."""
        extracted, info = self._extract(question, references, response)
        answers, ans_info = self._split(question, references, extracted)
        info.update(ans_info)
        
        # No actual answer found in the response
        if len(answers) == 0:
            return False, info
        
        # Every answer must match one of the references
        all_match_info = {}
        for answer in answers:
            matched = False
            all_match_info[answer] = {}
            for reference in references:
                is_match, match_info = self._match(question, answer, reference)
                all_match_info[answer][reference] = match_info
                if is_match:
                    matched = True
                    break
            if not matched:
                info.update(all_match_info)
                return False, info

        # All answers are correct
        info.update(all_match_info)
        return True, info

    def evaluate(self, question, response, references, **kwargs):
        # If the response is an exact match, return True
        is_exact_match, _ = self._exact_match_evaluator.evaluate(question,
                                                                 response,
                                                                 references)
        if is_exact_match:
            return True, {'evaluation': 'correct',
                          'parsed_successfully': 'N/A'}

        # Evaluate the response using the staged LLM evaluator
        return self._evaluate(question, response, references)

    @property
    def config(self):
        return self._eval_config

    @property
    def hashval(self):
        return self._doc.doc_id
