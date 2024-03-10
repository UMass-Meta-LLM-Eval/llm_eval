import base64
from src.helpers.nqanswers import NQAnswersHelper
from src.helpers.utils import Utilities
from src.model import create_model
from .base_evaluator import BaseEvaluator
from datasets import load_dataset

class LLMEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config
        self.judge_llm = create_model(self._eval_config['model'])
        self.utils = Utilities()

        self.FEWSHOT_TEMPLATE = 'Question -\n{question}\n\nReferences -\n{reference}\n\nAnswer -\n{answer}\n\nEvaluation - {evaluation}'
        self.JUDGE_LLM_TEMPLATE = 'Answer in True/False if the Answer is correct based on Question and References -\n\n{FEW_SHOT}\n\n{QUESTION}'
        self.FEW_SHOT = self._create_few_shot_nq_examples(1)

    def _create_few_shot_nq_examples(self, num_fewshot: int):
        self.nqhelper = NQAnswersHelper()
        self._dataset = load_dataset('natural_questions',
                                     trust_remote_code=True)
        rng = self.utils._get_rng(self._eval_config.get('seed', 0))

        if num_fewshot > 0:
            fewshot_idxs = rng.choice(
                len(self._dataset['train']),
                size=1000*num_fewshot, replace=False).tolist()
        else:
            fewshot_idxs = []

        # Find fewshot examples with short answers from the training set
        fewshot_examples = []
        i = 0
        for idx in fewshot_idxs:
            if i >= num_fewshot:
                break

            row = self._dataset['train'][idx]
            answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(answers['short_answers']) == 0 or len(answers['short_answers']) == 1:
                continue

            fewshot_examples.append((row['question']['text'],
                                     answers['short_answers']))
            i += 1

        # Warn if not enough fewshot examples are found
        if len(fewshot_examples) != num_fewshot:
            print(f'Warning: Fewshot examples requested: '
                  f'{num_fewshot}, but '
                  f'{len(fewshot_examples)} found.')
            

        # Create the prompt prefix
        prompt = ''
        for (q, a) in fewshot_examples:
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, reference='\n'.join(a), answer=a[0], evaluation='True')

        return prompt
    
    def _create_judge_llm_prompt(self, question, response, references):
        question_template = self.FEWSHOT_TEMPLATE.format(question=question, reference='\n'.join(references), answer=response, evaluation='')
        return self.JUDGE_LLM_TEMPLATE.format(FEW_SHOT=self.FEW_SHOT, QUESTION=question_template)

    def evaluate(self, question, response, references, **kwargs):       
        response = base64.b64decode(response).decode('utf-8')
        prompt = self._create_judge_llm_prompt(question, response, references)
        response = self.judge_llm.predict(prompt)
        if response == 'True':
            return True, {}
        elif response == 'False':
            return False, {}
        else:
            return False, {'response':response}

    @property
    def config(self):
        return self._eval_config