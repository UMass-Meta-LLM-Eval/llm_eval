from .base_doc import BaseDoc

class InfoDoc(BaseDoc):
    def __init__(self, **kwargs):
        self._dict = kwargs

    def to_json(self):
        return self._dict
    
    @classmethod
    def from_json(cls, json_obj: dict):
        return cls(**json_obj)
