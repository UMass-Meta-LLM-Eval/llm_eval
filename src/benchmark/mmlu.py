from datasets import load_dataset
import base64

from .base_benchmark import BaseBenchmark
from ..helpers import BenchmarkDoc
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator

class MMLUBenchmark(BaseBenchmark):
    # SUBSETS = ['abstract_algebra', 'anatomy', 'astronomy', 'business_ethics',
    #            'clinical_knowledge', 'college_biology', 'college_chemistry',
    #            'college_computer_science', 'college_mathematics',
    #            'college_medicine', 'college_physics', 'computer_security',
    #            'conceptual_physics', 'econometrics', 'electrical_engineering',
    #            'elementary_mathematics', 'formal_logic', 'global_facts',
    #            'high_school_biology', 'high_school_chemistry',
    #            'high_school_computer_science', 'high_school_european_history',
    #            'high_school_geography', 'high_school_government_and_politics',
    #            'high_school_macroeconomics', 'high_school_mathematics',
    #            'high_school_microeconomics', 'high_school_physics',
    #            'high_school_psychology', 'high_school_statistics',
    #            'high_school_us_history', 'high_school_world_history',
    #            'human_aging', 'human_sexuality', 'international_law',
    #            'jurisprudence', 'logical_fallacies', 'machine_learning',
    #            'management', 'marketing', 'medical_genetics', 'miscellaneous',
    #            'moral_disputes', 'moral_scenarios', 'nutrition', 'philosophy',
    #            'prehistory', 'professional_accounting', 'professional_law',
    #            'professional_medicine', 'professional_psychology',
    #            'public_relations', 'security_studies', 'sociology',
    #            'us_foreign_policy', 'virology', 'world_religions']

    SUBSETS = ['abstract_algebra', 'anatomy']
    
    PROMPT_SUFFIX = ' Answer using Options A/B/C/D - A: {A}, B: {B}, C: {C}, D: {D}'

    def __init__(self, bm_config: dict):
        self._config = bm_config

    def create_prompt(self, row: dict):
        return row['input']+self.PROMPT_SUFFIX.format(**row)

    def run(self, model, db: BaseDatabase):
        for subset in self.SUBSETS:
            dataset = load_dataset("lukaemon/mmlu", subset)
            for row in dataset['test']:
                prompt = self.create_prompt(row)
                prediction = model.predict(prompt, b64_output=True)
                doc = BenchmarkDoc(self._config, model.config,
                                   row['input'], prompt, prediction)
                db.add_doc('benchmark', 'mmlu', hash(doc), doc.to_json())

    def compute_results(self, model_cfg: dict, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        scores = {}
        for subset in self.SUBSETS:
            scores[subset] = []
            dataset = load_dataset("lukaemon/mmlu", subset)
            for row in dataset['test']:
                prompt = self.create_prompt(row)
                doc = BenchmarkDoc(self._config, model_cfg, row['input'],
                                   prompt, None)
                key = hash(doc)
                doc = db.get_doc('benchmark', 'mmlu', key)
                prediction = doc['response']
                prediction = base64.b64decode(prediction).decode('utf-8')
                result = evaluator.evaluate(row['input'], prediction,
                                            [row['target']])
                doc['evaluation'].append({
                    'evaluator': evaluator.config,
                    'result': result})
                db.add_doc('benchmark', 'mmlu', key, doc)
                scores[subset].append(int(result))
            scores[subset] = sum(scores[subset]) / len(scores[subset])

        return scores
    
    @property
    def config(self):
        return self._config
