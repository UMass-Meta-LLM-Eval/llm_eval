from abc import ABC, abstractmethod

class BaseDatabase(ABC):
    @abstractmethod
    def __init__(self, name, db_params):
        ...

    @abstractmethod
    def get_doc(self, db_name: str, coll_name: str, doc_id):
        ...

    @abstractmethod
    def add_doc(self, db_name: str, coll_name: str, doc_id, doc):
        ...

    @abstractmethod
    def update_doc(self, db_name: str, coll_name: str, doc_id, key, val):
        ...

    @abstractmethod
    def doc_exists(self, db_name: str, coll_name: str, doc_id) -> bool:
        ...

    def iter_collection(self, db_name, coll_name):
        raise NotImplementedError("This database does not support "
                                  "iterating over collections.")
    

class DummyDatabase(ABC):
    def __init__(self, name, db_params):
        self._name = name
        self._db_params = db_params

    def get_doc(self, db_name, coll_name, doc_id):
        return {'text': 'dummy text'}
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        pass

    def doc_exists(self, db_name, coll_name, doc_id) -> bool:
        return True
