from pymongo import MongoClient
import base64

client = MongoClient('mongodb://localhost:27017/')

def encoderesponseb64(response):
    return base64.b64encode(response.encode("utf-8"))

def decoderresponseb64(base64_bytes):
    return base64.b64decode(base64_bytes).decode('utf-8')

def retrieve_bechmarks_results(benchmark):
    db = client[benchmark]
    collection = db['results']
    results = []
    for record in collection.find():
        question = record['question']
        response = decoderresponseb64(record['response'])
        print('**', record['model']['name'], '\n', question, response, '**', '\n')

retrieve_bechmarks_results('mmlu')