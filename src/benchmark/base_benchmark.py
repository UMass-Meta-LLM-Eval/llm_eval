from abc import ABC, abstractmethod
from ..helpers import BenchmarkDoc
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator

class BaseBenchmark(ABC):
    @abstractmethod
    def __init__(self, bm_config: dict):
        """Initialize the benchmark with the given configuration.
        The implementation should load the dataset and any other necessary
        resources."""
        ...

    
    @abstractmethod
    def create_prompt(self, question, **kwargs):
        """Create a prompt for the given question. The can be used to format
        the question in a way that the model can understand, adding context or
        few-shot learning examples. The kwargs can be used to pass any
        additional information needed to create the prompt."""
        ...

    @abstractmethod
    def run(self, model_config, db: BaseDatabase):
        """Run the benchmark with the given model configuration and store the
        results in the given database."""
        ...

    @abstractmethod
    def compute_results(self, db: BaseDatabase, evaluator: BaseEvaluator):
        """Compute the results of the benchmark using the given evaluator that
        will judge if the model's predictions are correct. The results will be
        stored in the given database."""
        ...

    @property
    @abstractmethod
    def config(self):
        """Return the benchmark's configuration."""
        ...


class DummyBenchmark(BaseBenchmark):
    def __init__(self, bm_config: dict):
        self._config = bm_config
        self._dataset = [
            {'question': "What is the capital of France?", 'references': ["Paris"]},
            {'question': "What is 2+2?", 'references': ["4", "four"]},
        ]

    def create_prompt(self, question, **kwargs):
        return question

    def run(self, model, db: BaseDatabase):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            prediction = model.predict(prompt)
            doc = BenchmarkDoc(self._config, model.config,
                               item['question'], prompt, prediction)
            db.add_doc('benchmark', 'test', hash(doc), doc.to_json())

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        scores = []
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            doc = BenchmarkDoc(self._config, model_cfg, item['question'],
                               prompt, None)
            key = hash(doc)
            doc = db.get_doc('benchmark', 'test', key)
            prediction = doc['response']
            success, result = evaluator.evaluate(item['question'], prediction, item['references'])
            doc['evaluation'].append({
                'evaluator': evaluator.config,
                'result': result})
            db.add_doc('benchmark', 'test', key, doc)
            if success:
                scores.append(1)

        return sum(scores) / len(scores)
    
    @property
    def config(self):
        return self._config
