class TriviaQaAnswersHelper:

    def __init__(self):
        ...

    def findAcceptableAnswersforTriviaQA(self, doc : object): 
        acceptable_answers = [doc['answer']['value']]

        aliases = doc['answer'].get('aliases', []) 
        acceptable_answers.extend(aliases)

        acceptable_answers = acceptable_answers[:10]

        return acceptable_answers
