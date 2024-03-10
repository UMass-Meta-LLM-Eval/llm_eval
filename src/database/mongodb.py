from pathlib import Path
from .base_database import BaseDatabase
from pymongo import MongoClient
import base64
from dotenv import load_dotenv
import os
load_dotenv()


class MongoDB(BaseDatabase):
    def __init__(self, env, db_uri):
        """Initalize a MongoDBDatabase instance which stores data in a JSON file."""
        self.client = self.startMongoDB(db_uri)
        self.env = env
        
    def startMongoDB(self, db_uri):
        uri = os.getenv(db_uri)
        if not uri:
            raise ValueError("MongoDB Atlas URI not found. Please check your .env file.")
        client = MongoClient(uri)
        try:
            client.admin.command('ping')
            print("Connection to MongoDB Successful")
        except Exception as e:
            print(e)
        return client

    def _modify_db_name(self, db_name, env):
        return db_name+"_"+env

    def _save_data(self, db_name, coll_name, data):
        collection = self.client[db_name][coll_name]
        collection.insert_one(data)

    def get_doc(self, db_name, coll_name, doc_id):
        db_name = self._modify_db_name(db_name, self.env)
        collection = self.client[db_name][coll_name]
        results = []
        record = collection.find({ hex(doc_id) : {'$exists' : True} })
        for doc in record:
            results.append(doc)
        if len(results) == 0:
            return {}
        if len(results) > 1:
            print(results)
            return KeyError('Key with Duplicate Value found in Mongo DB - ', hex(doc_id)) 
        return results[0][hex(doc_id)]
    
    def add_doc(self, db_name, coll_name, doc_id, doc):
        db_name = self._modify_db_name(db_name, self.env)
        doc['response'] = base64.b64encode(doc['response'].encode("utf-8"))
        data = {hex(doc_id):doc}
        self._save_data(db_name, coll_name, data)
    
    def clean_db(self, db_name, coll_name):
        db_name = self._modify_db_name(db_name, self.env)
        collection = self.client[db_name][coll_name]
        return collection.delete_many({}) 


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
