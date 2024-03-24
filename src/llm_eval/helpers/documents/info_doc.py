from .base_doc import BaseDoc


class InfoDoc(BaseDoc):
    def __init__(self, **kwargs):
        self._dict = kwargs

    def to_json(self):
        return self._dict
    
    @classmethod
    def from_json(cls, json_obj: dict):
        return cls(**json_obj)


def cfg_to_hash(cfg: dict) -> str:
    """Create the base64 encoded SHA256 hash of a JSON serializable
    config dictionary."""
    doc = InfoDoc(**cfg)
    return doc.doc_id
