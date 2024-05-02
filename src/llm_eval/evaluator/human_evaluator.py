import textwrap
from termcolor import colored

from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..helpers.constants.db import BENCHMARK
from ..helpers.constants.evaluator import (VALID_HUMAN_INPUTS, POS_LABELS,
                                           HIGH_CONFIDENCE_LABELS, ERROR_CODES)
from ..helpers.misc import parse_error_codes
from . import logger


def _parse_input(user_input: str) -> tuple[bool, bool, bool, str]:
    """Parse the user input for a human evaluator.
    Human input should be the evaluation string. Returns a tuple with the
    following elements:
    - parsed: whether the input is valid
    - success: whether the response is correct
    - confident: whether the user is confident in their response
    - parsing_error: an error message if the input is invalid
    """
    # Check if the input is valid
    if user_input not in VALID_HUMAN_INPUTS:
        return False, False, False, 'Invalid evaluation. Please enter one ' \
            f'of {", ".join(f"{i}" for i in VALID_HUMAN_INPUTS)}'
    
    # Parse the evaluation
    is_pos = user_input in POS_LABELS
    is_high_confidence = user_input in HIGH_CONFIDENCE_LABELS
    return True, is_pos, is_high_confidence, ''


def _parse_input_with_error_codes(user_input: str
                                  ) -> tuple[bool, bool, bool, list, str]:
    """
    Parse the user input for a human evaluator including error codes.
    Human input should be of the form: `<pos_evaluation>` or
    `<neg_evaluation> <error_codes>`. Returns a tuple with the following
    elements:
    - parsed: whether the input is valid
    - success: whether the response is correct
    - confident: whether the user is confident in their response
    - error_codes: the error codes for the response
    - parsing_error: an error message if the input is invalid"""

    # Split the user input into the error evaluation and error codes
    user_input = user_input.strip().split()
    if len(user_input) == 0:
        return False, False, False, [], 'No input provided'
    
    # Parse the evaluation
    if user_input[0] not in VALID_HUMAN_INPUTS:
        return False, False, False, [], 'Invalid evaluation. Please enter ' \
            f'one of {", ".join(f"{i}" for i in VALID_HUMAN_INPUTS)}'
    
    is_high_confidence = user_input[0] in HIGH_CONFIDENCE_LABELS

    # Return the parsed input if positive evaluation
    if user_input[0] in POS_LABELS:
        # In this case there should be no error codes
        if len(user_input) > 1:
            return False, False, False, [], 'Error codes should not be ' \
                'provided for positive evaluations'
        
        # Valid positive evaluation
        return True, True, is_high_confidence, [], ''
    
    # Parse the error codes
    if len(user_input) == 1:
        return False, False, False, [], 'Error codes not provided'
    if len(user_input) > 2:
        return False, False, False, [], 'Too many arguments provided'
    
    # Check if the error codes are valid
    parsed_codes, unknown_codes = parse_error_codes(user_input[1])
    if unknown_codes != '':
        return False, False, False, [], f'Unknown error codes: {unknown_codes}'
    
    # Valid negative evaluation
    return True, False, is_high_confidence, parsed_codes, ''


def _get_human_eval(question, response, references, **kwargs
                    ) -> tuple[bool, dict]:
    """Ask a human to evaluate the response."""

    # Provide the user with the question, references, and response
    print(colored('Question  :\n', 'red'),
            textwrap.indent(colored(question, 'blue'), '  '))
    print(colored('References:', 'red'))
    for ref in references:
        print(textwrap.indent(ref, '  '))
    print(colored('Response  :\n', 'red'),
            textwrap.indent(colored(response, 'green'), '  '))
    print(colored('Evaluation:', 'red'))

    # Ask the user to evaluate the response
    input_valid = False
    if kwargs.get('error_analysis', False):
        while not input_valid:
            logger.info('Please evaluate the response. In case of an error, '
                        'valid error codes are: %s', ', '.join(
                            f'{k} ({v})' for k, v in ERROR_CODES.items()))
            user_input = input().lower()
            input_valid, success, confident, error_codes, parsing_error = \
                _parse_input_with_error_codes(user_input)
            if not input_valid:
                print(parsing_error)
        return success, {'confident': confident, 'exact_match': False,
                         'error_codes': error_codes}
    else:
        while not input_valid:
            user_input = input().lower()
            input_valid, success, confident, parsing_error = \
                _parse_input(user_input)
            if not input_valid:
                print(parsing_error)
        return success, {'confident': confident, 'exact_match': False}


class HumanEvaluator(BaseEvaluator):
    """Evaluator that asks a human to evaluate the response."""

    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._exact_match_evaluator = ExactMatchEvaluator({})
        self._error_analysis: bool = eval_config.get('error_analysis', False)
        self._doc = InfoDoc(**eval_config)

    def evaluate(self, question, response, references, **kwargs):
        # If the response is an exact match, return True
        is_exact_match, _ = self._exact_match_evaluator.evaluate(question,
                                                                 response,
                                                                 references)
        # Return True if the response is an exact match
        if is_exact_match:
            return True, {'confident': True, 'exact_match': True}

        # Otherwise, ask a human to evaluate the response
        return _get_human_eval(question, response, references,
                               error_analysis=self._error_analysis)

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id


class MultiHumanEvaluator(BaseEvaluator):
    """Evaluator that asks a human to evaluate the response."""

    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._doc = InfoDoc(cls='MultiHumanEvaluator',
                            name=eval_config['name'])

    def evaluate(self, question, response, references, **kwargs):
        self_answer = None

        human_eval_keys = [InfoDoc(**d).doc_id
                           for d in self._eval_config['human-evals']]
        answer_requested_keys = []

        for key in human_eval_keys:
            # Key of human eval we want to double-check
            human_eval = kwargs['doc'].evaluation[key]

            # Add `other-humans` if it doesn't exist, this is where
            # our evaluation will be stored
            if 'other-humans' not in human_eval['info']:
                human_eval['info']['other-humans'] = {}
            
            print(self.hashval, human_eval['info']['other-humans'])
            # No need to double-check if the human was confident
            if human_eval['info']['confident']:
                continue
            
            # If we have already double-checked this human, save the result
            # (so that there is no need to ask the human to get the same
            # result again), then skip to the next human evaluation
            elif self.hashval in human_eval['info']['other-humans']:
                self_answer = human_eval['info']['other-humans'][self.hashval]
            
            # Add to the list of unanswered human evaluations with low
            # confidence
            else:
                answer_requested_keys.append(key)
        
        # If we have any human evaluations to double-check, and we haven't
        # already double-checked for some other human evaluation, ask the
        # human to evaluate the response
        if len(answer_requested_keys)>0 and self_answer is None:
            result, info = _get_human_eval(question, response, references)
            self_answer = {'result': result, 'info': info}

        # Save the result of the evaluation for all the requested evaluations
        for key in answer_requested_keys:
            kwargs['doc'].evaluation[key][
                'info']['other-humans'][self.hashval] = self_answer
        
        # Update the document in the database
        kwargs['db'].update_doc(BENCHMARK, kwargs['bm_name'],
                                kwargs['doc'].doc_id, 'evaluation',
                                kwargs['doc'].evaluation)
        
        # Returning None signals the benchmark that this evaluation does
        # not need to be saved as its own evaluation
        return None, None

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id
