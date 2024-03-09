from pathlib import Path
from .base_database import BaseDatabase
from pymongo import MongoClient
import base64
from dotenv import load_dotenv
import os
load_dotenv()


class MongoDB(BaseDatabase):
    def __init__(self):
        """Initalize a MongoDBDatabase instance which stores data in a JSON file."""
        self.client = self.startMongoDB()
        print('MongoDB Atlas connected')

    def startMongoDB(self):
        uri = os.getenv('MONGO_URI')
        if not uri:
            raise ValueError("MongoDB Atlas URI not found. Please check your .env file.")
        client = MongoClient(uri)
        return client

    def _save_data(self, db_name, coll_name, data):
        collection = self.client[db_name][coll_name]
        collection.insert_one(data)

    def get_doc(self, db_name, coll_name):
        collection = self.client[db_name][coll_name]
        results = []
        for record in collection.find():
            hashid = list(record.keys())[1]
            record[hashid]['response'] = base64.b64decode(record[hashid]['response'].decode("utf-8"))
            results.append(record)
        return results
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        doc['response'] = base64.b64encode(doc['response'].encode("utf-8"))
        data = {hex(doc_id):doc}
        self._save_data(db_name, coll_name, data)


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
