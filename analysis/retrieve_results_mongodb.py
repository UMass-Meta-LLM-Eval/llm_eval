from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

mongodburi = 'MONGODBURI1'
db_name = 'evaluation_prod'
coll_name = 'naturalquestions'

uri = os.getenv('MONGODBURI1')
client = MongoClient(uri)
collection = client[db_name][coll_name]

results = []

for record in collection.find():
    results.append(record)

print(results)