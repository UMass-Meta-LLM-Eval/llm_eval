from pathlib import Path
import json
from .base_database import BaseDatabase


class JSONDatabase(BaseDatabase):
    def __init__(self, name, db_dir):
        """Initalize a JSONDatabase instance which stores data in a JSON file."""
        self._name = name
        self._db_dir = Path(db_dir)

    def _load_data(self, filename):
        file_loc = self._db_dir.joinpath(filename)
        if file_loc.exists():
            with open(file_loc, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        return data

    def _save_data(self, filename, data):
        file_loc = self._db_dir.joinpath(filename)
        file_loc.parent.mkdir(parents=True, exist_ok=True)
        with open(file_loc, 'w') as f:
            json.dump(data, f, indent=4)

    def get_doc(self, db_name, coll_name, doc_id):
        data = self._load_data(f'{db_name}/{coll_name}.json')
        return data[doc_id]
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        data = self._load_data(f'{db_name}/{coll_name}.json')

        data[doc_id] = doc
        self._save_data(f'{db_name}/{coll_name}.json', data)

    def doc_exists(self, db_name, coll_name, doc_id) -> bool:
        data = self._load_data(f'{db_name}/{coll_name}.json')
        return doc_id in data
