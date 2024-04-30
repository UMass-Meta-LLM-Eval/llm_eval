"""Helper functions and classes for benchmarks."""


class NQAnswersHelper:
    def findAnswerSpanBasedOnTokens(self, doc : object, start : int, end : int
                                    ):
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
        short_answers, long_answers = set(), []

        for ans in doc["annotations"]["short_answers"]:
            if ans['text'] != []:
                short_answers = short_answers.union(set(ans['text']))
            elif ans["start_token"] != [] and ans["end_token"] != []: 
                short_answers.add(self.findAnswerSpanBasedOnTokens(
                    doc, ans["start_token"],ans["end_token"]))
        short_answers = list(filter(None, short_answers))
        short_answers.sort()
        acceptable_answers['short_answers'] = short_answers

        for ans in doc["annotations"]["long_answer"]:
            if ans["start_token"] != [] and ans["end_token"] != []:
                long_answers.append(self.findAnswerSpanBasedOnTokens(
                    doc, ans["start_token"],ans["end_token"]))
        long_answers = list(filter(None, long_answers))
        if long_answers != []:
            acceptable_answers['long_answers'] = long_answers

        if -1 not in doc['annotations']['yes_no_answer']:
            acceptable_answers['y/n'] = doc['annotations']['yes_no_answer']

        return acceptable_answers


def find_acceptable_answers_triviaqa(doc): 
    acceptable_answers = [doc['answer']['value']]

    aliases = doc['answer'].get('aliases', []) 
    acceptable_answers.extend(aliases)

    # Returning all references here and then filtering them (if needed)
    # in the benchmark class
    return acceptable_answers
