from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from ..database.dummy_mongodb import DummyMongoDB

class BaseEvaluator(ABC):

    @abstractmethod
    def evaluate(self, question, response, references, **kwargs)->Tuple[bool, Dict[str, Any]]:
        ...

    def evaluate_batch(self, questions, responses, references_list, **kwargs):
        return [self.evaluate(q, r, refs, **kwargs)
                for q, r, refs in zip(questions, responses, references_list)]
    
    @property
    @abstractmethod
    def config(self):
        ...


class DummyEvaluator(BaseEvaluator):
    def __init__(self, eval_config: dict, mongo_db:DummyMongoDB):
        self._eval_config = eval_config
        self._mongo_db = mongo_db

    def evaluate(self, question, response, references, **kwargs):
        doc = self._mongo_db.get_doc("db_name", "coll_name", "doc_id")

        print("Question:", doc['question'])
        print("Response:", doc['response'])
        print("Accepted Answers:", doc['accepted_answers'])

        user_input = ''
        while user_input not in ['y', 'n', 'yy', 'nn']:
            user_input = input("Enter yy/nn/y/n :").lower()
            if user_input not in ['y', 'n', 'yy', 'nn']:
                print("Invalid input. Please enter 'y', 'n', 'yy', or 'nn'.")

        success = user_input in ['yy','y']
        result = {
            'input': user_input,
        }

        return success, result

    @property
    def config(self):
        return self._eval_config
