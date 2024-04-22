from textwrap import dedent

class EXTRACT_DEFAULT:
    ARGS = ['PROMPT', 'TAG']

    PROMPT = dedent('''
        You will be provided a question, some references, and a response from
        a language model. Your task in to extract the answer given by the
        language model from the response, while discarding any irrelevant
        information.

        The extracted answer should be enclosed in <extract> and </extract>
        tags. If the response contains multiple answers, you should append
        them into a single string inside the tags.
                    
        Make sure that the answer that you extract is a sub-string of the
        response. If no answer is present in the response, the extracted
        answer should be an empty string.
                    
        Question:
        ```
        {question}
        ```

        References:
        ```
        {references}
        ```

        Response:
        ```
        {response}
        ```
                    
        Give an explanation of how you determined which part of the model
        response in the answer, and then return the extracted answer enclosed
        in a <extract> and </extract> tag pair.
        ''').strip()
    
    TAG = 'extract'


class SPLIT_DEFAULT:
    ARGS = ['PROMPT', 'TAG']

    PROMPT = dedent('''
        You will be provided a question, some references, and a response from
        a language model that contains one or more answers to the question.
        Your task in to split the response into the individual answers. You
        can use the references to determine how to split the response. For
        example, if a refernce contains multiple entities, then those entities
        should not be split into separate answers, but if there are multiple
        references with different entities, then the response should be split
        into separate answers for each entity.

        Each answer should be enclosed in separate <split> and </split> tags.

        Question:
        ```
        {question}
        ```

        References:
        ```
        {references}
        ```

        Response:
        ```
        {response}
        ```
        ''').strip()
    
    TAG = 'split'

class MATCH_DEFAULT:
    ARGS = ['PROMPT', 'POS', 'NEG']

    PROMPT = dedent('''
        You will be provided a question, an answer, and a reference. Your task
        is to determine if the answer matches the reference. If the answer
        matches the reference, you should respond with "MATCH", otherwise you
        should respond with "NO MATCH".

        Your response should be in all caps and should not contain any other
        information.

        Question:
        ```
        {question}
        ```

        Answer:
        ```
        {answer}
        ```

        Reference:
        ```
        {reference}
        ```
        ''').strip()

    POS = 'MATCH'

    NEG = 'NO MATCH'
