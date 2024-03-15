import textwrap
from termcolor import colored

from .base_evaluator import BaseEvaluator
from .classic_evaluator import ExactMatchEvaluator
from ..helpers import InfoDoc

class HumanEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self._exact_match_evaluator = ExactMatchEvaluator({})
        self._doc = InfoDoc(**eval_config)

    def evaluate(self, question, response, references, **kwargs):
        # If the response is an exact match, return True
        is_exact_match, _ = self._exact_match_evaluator.evaluate(question,
                                                                 response,
                                                                 references)
        if is_exact_match:
            return True, {'confident': True}

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
        while user_input not in ['y', 'n', 'yy', 'nn']:
            user_input = input().lower()
            if user_input not in ['y', 'n', 'yy', 'nn']:
                print("Invalid input. Please enter 'y', 'n', 'yy', or 'nn'.")
        print()

        # Return the result
        success = user_input in ['yy','y']
        result = {'confident': user_input in ['yy','nn']}
        return success, result

    @property
    def config(self):
        return self._eval_config
    
    @property
    def hashval(self):
        return self._doc.doc_id
