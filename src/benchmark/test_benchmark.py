from datasets import load_dataset
from numpy.random import Generator, PCG64

from .base_benchmark import BaseBenchmark
from ..helpers import BenchmarkDoc, NQAnswersHelper
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from tqdm import tqdm


class TestBenchmark(BaseBenchmark):
    BM_NAME = 'test_bm'
    FEWSHOT_TEMPLATE = 'Q: {question}\nA: {answer}\n\n'
    QUESTION_TEMPLATE = 'Q: {question}\nA:'
    QUESTIONS = [
        'who sings i felt the rains down in africa',
        'who sings system from queen of the damned',
        'what part of atlanta is gwinnett county in',
        'when did ty beanie babies first come out',
        'when did the british hand-over sovereignty of hong kong back to china'
    ]
    ANSWERS = [
        'Toto',
        'Chester Bennington of Linkin Park',
        'north central portion',
        '1993',
        '1 July 1997'
    ]

    def __init__(self, bm_config: dict):
        self._config = bm_config
        self._dataset = bm_config['dataset']
        self._fewshot_prefix = self._create_fewshot_examples()

    def _create_fewshot_examples(self):
        prompt = ''
        for q, a in zip(self.QUESTIONS, self.ANSWERS):
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, answer=a)
        return prompt

    def create_prompt(self, question, **kwargs):
        return self._fewshot_prefix + self.QUESTION_TEMPLATE.format(
            question=question)

    def run(self, model, db: BaseDatabase):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            prediction = model.predict(prompt).split('\n')[0]
            doc = BenchmarkDoc(self._config, model.config, prompt, prediction)
            db.add_doc('benchmark', self.BM_NAME, doc.get_hash(), doc.to_json())

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        scores = []
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            doc = BenchmarkDoc(self._config, model_cfg, prompt)
            key = doc.get_hash()
            doc = db.get_doc('benchmark', self.BM_NAME, key)
            doc = BenchmarkDoc.from_json(doc)
            prediction = doc.response
            result, info = evaluator.evaluate(item['question'], prediction,
                                        item['references'])
            eval_key = hex(evaluator.get_eval_key(key))
            doc.evaluation[eval_key] = {
                'evaluator': evaluator.config,
                'result': result,
                'info': info}
            db.add_doc('benchmark', self.BM_NAME, key, doc.to_json())
            scores.append(int(result))

        return sum(scores) / len(scores)

    def inspect_results(self, db: BaseDatabase, model_cfg: dict):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            key = BenchmarkDoc(self._config, model_cfg, prompt).get_hash()
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            doc.inspect(item['question'], item['references'])
            if input() == 'q':
                break

    @property
    def config(self):
        return self._config
