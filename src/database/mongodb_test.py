from src.database.mongodb import MongoDB

def DummyMongoDB():
    db = MongoDB()

    db.startMongoDB()

    test_db_name = 'test_db'
    test_collection_name = 'test_collection'

    doc_id = 1234
    test_doc = {
        'model': 'dummy',
        'question': 'When was the last time anyone was on the moon?',
        'prompt': 'Q. When was the last time anyone was on the moon? A: ',
        'response': 'VGhlIGxhc3QgdGltZSBhbnlvbmUgd2FzIG9uIHRoZSBtb29uIHdhcyBkdXJpbmcgdGhlIEFwb2xsbyAxNyBtaXNzaW9uIGluIERlY2VtYmVyIDE5NzI=',
        'accepted_answers' : ['14 December 1972 UTC', 'December 1972'],
    }

    # print('Adding document...')
    # db.add_doc(test_db_name, test_collection_name, doc_id, test_doc)
    
    print('Retrieving documents...')
    documents = db.get_doc(test_db_name, test_collection_name)
    print(documents)
    
if __name__ == '__main__':
    DummyMongoDB()