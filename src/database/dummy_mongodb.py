from abc import ABC, abstractmethod

class DummyMongoDB(ABC):
    def __init__(self, name, db_params):
        self._name = name
        self._db_params = db_params

    def get_doc(self, db_name, coll_name, doc_id):
        return {
            'model': 'dummy',
            'question': 'Q. When was the last time anyone was on the moon? A: ',
            'prompt': 'Q. When was the last time anyone was on the moon? A: ',
            'response': 'The last time anyone was on the moon was during the Apollo 17 mission in December 1972',
            'accepted_answers' : ['14 December 1972 UTC', 'December 1972'],
        }
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        pass
