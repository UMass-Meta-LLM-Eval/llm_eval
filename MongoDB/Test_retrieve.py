from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
#client = MongoClient('mongodb://gypsum-gpu089.unity.rc.umass.edu:27017/')

def retrieve_bechmarks_results(benchmark):
    db = client[benchmark]
    collection = db['results']
    results = []
    for record in collection.find():
        results.append(record)
    return results


print(retrieve_bechmarks_results('MMLU_results'))
print(retrieve_bechmarks_results('nq_results'))