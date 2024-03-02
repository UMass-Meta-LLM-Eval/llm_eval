class NQAnswersHelper:

    def __init__(self):
        ...

    def findAnswerSpanBasedOnTokens(self, doc : object, start : int, end : int):
        answer_start = start
        answer_end = end
        answer_span = doc["document"]["tokens"]["token"][
            answer_start:answer_end
        ]
        answer_is_html = doc["document"]["tokens"]["is_html"][
            answer_start:answer_end
        ]
        answer_chars = [
            tok
            for (tok, is_html) in zip(answer_span, answer_is_html)
            if not is_html
        ]
        answer = " ".join(answer_chars)
        return answer

    def findAcceptableAnswersforNQ(self, doc : object):   
        acceptable_answers = {}
        short_answers, long_answers = [], []

        for ans in doc["annotations"]["short_answers"]:
            if ans['text'] != []:
                short_answers += ans['text']
            elif ans["start_token"] != [] and ans["end_token"] != []: 
                short_answers.append(self.findAnswerSpanBasedOnTokens(doc, ans["start_token"],ans["end_token"]))
        short_answers = list(filter(None, short_answers))
        if short_answers != []:
            acceptable_answers['short_answers'] = short_answers

        for ans in doc["annotations"]["long_answer"]:
            if ans["start_token"] != [] and ans["end_token"] != []:
                long_answers.append(self.findAnswerSpanBasedOnTokens(doc, ans["start_token"],ans["end_token"]))
        long_answers = list(filter(None, long_answers))
        if long_answers != []:
            acceptable_answers['long_answers'] = long_answers

        if -1 not in doc['annotations']['yes_no_answer']:
            acceptable_answers['y/n'] = doc['annotations']['yes_no_answer']

        return acceptable_answers

# dataset = load_dataset("natural_questions", split='validation')
# for i, row in enumerate(dataset):
#     print(i)
#     acceptable_answers = findAcceptableAnswersforNaturalQuestions(row)
#     if acceptable_answers == {}:
#         print(row['question']['text'], "\n")