import textwrap
from termcolor import colored

from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc
from ..helpers.constants.db import BENCHMARK


VALID_INPUTS = ['y', 'n', 'yy', 'nn', 'y?', 'n?']


def _get_human_eval(question, response, references) -> tuple[bool, dict]:
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

    # Get a valid user input
    user_input = ''
    while user_input not in VALID_INPUTS:
        user_input = input().lower()
        if user_input not in VALID_INPUTS:
            print('Invalid input. Please enter one of',
                    {', '.join(f"'{i}'" for i in VALID_INPUTS)})
    print()

    # Return the result
    success = user_input in ['yy','y', 'y?']
    info = {'confident': user_input in ['yy','nn', 'y', 'n'],
            'exact_match': False}
    return success, info


class HumanEvaluator(BaseEvaluator):
    """Evaluator that asks a human to evaluate the response."""

    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._exact_match_evaluator = ExactMatchEvaluator({})
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
        return _get_human_eval(question, response, references)

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
