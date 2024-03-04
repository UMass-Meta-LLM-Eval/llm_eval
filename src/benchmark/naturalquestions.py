from datasets import load_dataset
from numpy.random import Generator, PCG64

from .base_benchmark import BaseBenchmark
from ..helpers import BenchmarkDoc, NQAnswersHelper
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from tqdm import tqdm

class NaturalQuestionsBenchmark(BaseBenchmark):
    FEWSHOT_TEMPLATE = 'Q: {question}\nA: {answer}\n\n'
    QUESTION_TEMPLATE = 'Q: {question}\nA:'

    def __init__(self, bm_config: dict):
        self._config = bm_config
        self.nqhelper = NQAnswersHelper()
        self._dataset = load_dataset('natural_questions',
                                     trust_remote_code=True)
        self._fewshot_prefix = self._create_fewshot_examples(
            self._config.get('num_fewshot', 0))

    def _create_fewshot_examples(self, num_fewshot: int):
        rng = self._get_rng(self._config.get('seed', 0))

        if num_fewshot > 0:
            fewshot_idxs = rng.choice(
                len(self._dataset['train']),
                size=10*num_fewshot, replace=False).tolist()
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
            if len(answers['short_answers']) == 0:
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
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, answer=a[0])

        return prompt

    def create_prompt(self, question:int, **kwargs):
        prompt = self._fewshot_prefix + self.QUESTION_TEMPLATE.format(
            question=question)

        return prompt

    def _get_rng(self, seed: int):
        return Generator(PCG64(seed=seed))

    def run(self, model, db: BaseDatabase):
        rng = self._get_rng(self._config.get('seed', 0))

        # Shuffle the dataset (if sampling)
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(
                len(self._dataset['validation'])).tolist()
        else:
            total = len(self._dataset['validation'])
            shuffled_indices = range(total)

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=total)
        for i in shuffled_indices:
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(acceptable_answers['short_answers']) == 0:
                continue
            prediction = model.predict(prompt).split('\n')[0]
            doc = BenchmarkDoc(self._config, model.config, prompt,
                               response=prediction)
            db.add_doc('benchmark', 'naturalquestions', doc.get_hash(),
                       doc.to_json())
            pbar.update(1)
            if pbar.n >= total:
                break
        pbar.close()

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        rng = self._get_rng(self._config.get('seed', 0))

        # Shuffle the dataset (if sampling)
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(
                len(self._dataset['validation'])).tolist()
        else:
            total = len(self._dataset['validation'])
            shuffled_indices = range(total)

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=total)
        for i in shuffled_indices:
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(acceptable_answers['short_answers']) == 0:
                continue
            key = BenchmarkDoc(self._config, model_cfg, prompt).get_hash()
            doc = self._get_doc_from_db(db, 'naturalquestions', key)
            prediction = doc.response
            result = evaluator.evaluate(row['question']['text'], prediction,
                                        acceptable_answers['short_answers'])
            eval_key = hex(evaluator.get_eval_key(key))
            doc.evaluation[eval_key] = {
                'evaluator': evaluator.config,
                'result': result}
            db.add_doc('benchmark', 'naturalquestions', key, doc.to_json())
            pbar.update(1)
            if pbar.n >= total:
                break
        pbar.close()

    def inspect_results(self, db: BaseDatabase, model_cfg: dict):
        rng = self._get_rng(self._config.get('seed', 0))

        # Shuffle the dataset (if sampling)
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(
                len(self._dataset['validation'])).tolist()
        else:
            total = len(self._dataset['validation'])
            shuffled_indices = range(total)

        num_fewshot = self._config.get('num_fewshot', 0)
        n = 0
        for i in shuffled_indices:
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(acceptable_answers['short_answers']) == 0:
                continue
            key = BenchmarkDoc(self._config, model_cfg, prompt).get_hash()
            doc = self._get_doc_from_db(db, 'naturalquestions', key)
            doc.inspect(row['question']['text'],
                        acceptable_answers['short_answers'])
            n += 1
            if n >= total:
                break
            if input() == 'q':
                break

    @property
    def config(self):
        return self._config
