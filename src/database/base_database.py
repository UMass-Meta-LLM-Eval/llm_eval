from abc import ABC, abstractmethod

class BaseDatabase(ABC):
    @abstractmethod
    def __init__(self, name, db_params):
        ...

    @abstractmethod
    def get_doc(self, db_name, coll_name, doc_id):
        ...

    @abstractmethod
    def add_doc(self, db_name, coll_name, doc_id, doc):
        ...
    

class DummyDatabase(ABC):
    def __init__(self, name, db_params):
        self._name = name
        self._db_params = db_params

    def get_doc(self, db_name, coll_name, doc_id):
        return {'text': 'dummy text'}
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        pass
