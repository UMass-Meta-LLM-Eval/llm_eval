from datasets import load_dataset
import base64

from .base_benchmark import BaseBenchmark
from ..helpers import BenchmarkDoc, NQAnswersHelper
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from tqdm import tqdm

class NaturalQuestions(BaseBenchmark):

    def __init__(self, bm_config: dict):
        self._config = bm_config
        self.nqhelper = NQAnswersHelper()

    def create_prompt(self, row: dict):
        return row['input']+self.PROMPT_SUFFIX.format(**row)

    def run(self, model, db: BaseDatabase):
        dataset = load_dataset("natural_questions", split='validation')
        for i in tqdm(range(len(dataset))):
            row = dataset[i]
            prompt = row['question']['text']
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            prediction = model.predict(prompt, b64_output=True)
            doc = BenchmarkDoc(bm_config=self._config, model_config=model.config,
                                question=prompt, prompt=prompt, response=prediction,acceptable_answers=acceptable_answers)
            db.add_doc('benchmark', 'naturalquestions', hash(doc), doc.to_json())

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
       results = db.get_doc('benchmark', 'naturalquestions')
       print('Retrieved Results - ', len(results))

    @property
    def config(self):
        return self._config
