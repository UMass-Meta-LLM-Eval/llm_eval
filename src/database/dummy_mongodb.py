from .base_database import BaseDatabase

class DummyMongoDB(BaseDatabase):
    def __init__(self, name, db_params):
        self._name = name
        self._db_params = db_params

    def get_doc(self, db_name, coll_name, doc_id):
        return {
            'model': 'dummy',
            'question': 'When was the last time anyone was on the moon?',
            'prompt': 'Q. When was the last time anyone was on the moon? A: ',
            'response': 'VGhlIGxhc3QgdGltZSBhbnlvbmUgd2FzIG9uIHRoZSBtb29uIHdhcyBkdXJpbmcgdGhlIEFwb2xsbyAxNyBtaXNzaW9uIGluIERlY2VtYmVyIDE5NzI=',
            'accepted_answers' : ['14 December 1972 UTC', 'December 1972'],
        }
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        pass
