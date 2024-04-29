def find_acceptable_answers_triviaqa(doc): 
    acceptable_answers = [doc['answer']['value']]

    aliases = doc['answer'].get('aliases', []) 
    acceptable_answers.extend(aliases)

    # Returning all references here and then filtering them (if needed)
    # in the benchmark class
    return acceptable_answers
