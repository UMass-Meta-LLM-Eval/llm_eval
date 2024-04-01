def find_acceptable_answers_triviaqa(doc): 
    acceptable_answers = [doc['answer']['value']]

    aliases = doc['answer'].get('aliases', []) 
    acceptable_answers.extend(aliases)

    acceptable_answers = acceptable_answers[:10]

    return acceptable_answers
