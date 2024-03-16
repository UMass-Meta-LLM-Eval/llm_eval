from pathlib import Path
from .base_database import BaseDatabase
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()


class MongoDB(BaseDatabase):
    def __init__(self, db_params):
        """Initalize a MongoDBDatabase instance which stores data in a JSON file."""
        self.client = MongoClient(db_params['uri'])

    def get_doc(self, db_name: str, coll_name: str, doc_id):
        collection = self.client[db_name][coll_name]
        return collection.find_one({'_id': doc_id})
    
    def add_doc(self, db_name: str, coll_name: str, doc_id, doc):
        collection = self.client[db_name][coll_name]
        collection.update_one({'_id': doc_id}, {'$set': doc}, upsert=True)
    
    def update_doc(self, db_name: str, coll_name: str, doc_id, key, val):
        collection = self.client[db_name][coll_name]
        collection.find_one_and_update({'_id':doc_id},
                        { '$set': {key : val} })

    def doc_exists(self, db_name: str, coll_name: str, doc_id) -> bool:
        collection = self.client[db_name][coll_name]
        doc = collection.find_one({'_id': doc_id}, projection={'_id': 1})
        return doc is not None
