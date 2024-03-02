from .base_evaluator import BaseEvaluator

class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config

    def evaluate(self, question, response, references, **kwargs):
        cased = self.config.get('cased', True)
        if cased:
            return response in references, {}
        else:
            return response.lower() in [ref.lower() for ref in references], {}

    @property
    def config(self):
        return self._eval_config

class ContainsMatchEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config

    def evaluate(self, question, response, references, **kwargs):
        cased = self.config.get('cased', True)
        if cased:
            return any(ref in response for ref in references), {}
        else:
            return any(ref.lower() in response.lower() for ref in references), {}

    @property
    def config(self):
        return self._eval_config
    
class ContainsWordsEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict):
        self._eval_config = eval_config

    def evaluate(self, question, response, references, **kwargs):
        cased = self.config.get('cased', True)
        if cased:
            all_words = response.split()
        else:
            all_words = response.lower().split()

        for ref in references:
            words = ref.split() if cased else ref.lower().split()
            if all(word in all_words for word in words):
                return True, {}
        return False, {}
    
    @property
    def config(self):
        return self._eval_config
