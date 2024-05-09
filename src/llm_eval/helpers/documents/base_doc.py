from abc import ABC, abstractmethod
import hashlib
import json
import base64

class BaseDoc(ABC):
    @abstractmethod
    def to_json(self):
        ...

    def _encode(self) -> bytes:
        s = json.dumps(self.to_json(), sort_keys=True)
        return s.encode('utf-8')

    @staticmethod
    def str_to_b64_str(s: str) -> str:
        return base64.b64encode(s.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def b64_str_to_str(b: str) -> str:
        return base64.b64decode(b).decode('utf-8')
    
    @property
    def doc_id(self) -> str:
        """Return the SHA256 hash of the object as a base64 string."""
        # TODO: Use the helper function create_hash instead of this
        hashval = hashlib.sha256(self._encode()).digest()
        return base64.b64encode(hashval).decode('utf-8')
    
    @classmethod
    @abstractmethod
    def from_json(cls, json_obj: dict):
        ...
