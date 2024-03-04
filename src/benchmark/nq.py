import base64

from .base_benchmark import BaseBenchmark
from ..helpers import BenchmarkDoc
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator

class DummyNQBenchmark(BaseBenchmark):
    def __init__(self, bm_config: dict):
        self._config = bm_config
        self._dataset = [
            {
                'question': 'When was the last time anyone was on the moon?',
                'references': ['14 December 1972 UTC', 'December 1972']
            }
        ]

    def create_prompt(self, question, **kwargs):
        return f'Q. {question} A: '
    
    def run(self, model, db: BaseDatabase):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            prediction = model.predict(prompt)
            doc = BenchmarkDoc(self._config, model.config, prompt, prediction)
            db.add_doc('benchmark', 'nq_dummy', doc.get_hash(), doc.to_json())

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        scores = []
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            doc = BenchmarkDoc(self._config, model_cfg, prompt)
            key = doc.get_hash()
            doc = db.get_doc('benchmark', 'nq_dummy', key)
            doc = BenchmarkDoc.from_json(doc)
            prediction = doc.response
            result, info = evaluator.evaluate(item['question'], prediction,
                                        item['references'])
            eval_key = hex(evaluator.get_eval_key(key))
            doc.evaluation[eval_key] = {
                'evaluator': evaluator.config,
                'result': result,
                'info': info}
            db.add_doc('benchmark', 'nq_dummy', key, doc.to_json())
            scores.append(int(result))

        return sum(scores) / len(scores)
    
    def inspect_results(self, db: BaseDatabase, model_cfg: dict):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            doc = self._get_doc_from_db(db, model_cfg, prompt, 'nq_dummy')
            doc.inspect(item['question'], item['references'])
            if input() == 'q':
                break

    @property
    def config(self):
        return self._config
