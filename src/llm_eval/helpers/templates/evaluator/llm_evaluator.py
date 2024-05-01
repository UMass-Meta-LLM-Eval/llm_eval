from textwrap import dedent


class DEFAULT:
    PROMPT: str = dedent('''
    Your task is to look at the following question, and based on the references
    provided, determine if the model's response is correct or incorrect.
    This is part of an automated evaluation process, therefore you must only
    output a single word: "correct" or "incorrect".

    Question:
    {question}

    References:
    {references}

    Model Response:
    {response}

    Evaluation (correct/incorrect):
    ''').strip()


class DEFAULT_V2:
    PROMPT: str = dedent('''
    Your task is to look at the following question, and based on the references
    provided, determine if the model's response is correct or incorrect.
    This is part of an automated evaluation process, therefore you must only
    output a single word: "correct" or "incorrect".

    Question:
    ```
    {question}
    ```

    References:
    ```
    {references}
    ```

    Model Response:
    ```
    {response}
    ```

    Evaluation (correct/incorrect):
    ''').strip()


class HUMAN_GUIDELINES:
    PROMPT: str = dedent('''
    You will be given a question, a set of reference answers and the answer
    given by an LLM. Your task is to judge if the answer given by the LLM is
    correct, as if you were the LLMs teacher grading their exam. An answer
    should be counted as correct if it is semantically equivalent to (one of
    the) reference answers. In doing so, please follow the following
    guidelines (1-3):
    1. Underspecified answers (e.g. "December" instead of "December 20") should
    be marked incorrect
    2. Answers that have more information than requested (e.g. "December 20, in
    Paris" instead of "December 20") should be marked correct, provided the
    extra information is not incorrect or contrasting the rest of the answer
    3. Answers with unnecessary verbosity but correct answers should be marked
    correct (E.g. "Thanks for asking this question! The correct answer is: ...)
    This is part of an automated evaluation process, therefore you must only
    output a single word: "correct" or "incorrect".
    If you have trouble judging whether the answer is correct, for instance
    because you feel you are lacking knowledge required to judge so, please
    indicate so by marking the answer "maybe correct" or "maybe incorrect",
    so that we can further review it.
                                            
    Question:
    {question}

    References:
    {references}

    Model Response:
    {response}

    Evaluation (correct/incorrect):
    ''').strip()


class HUMAN_GUIDELINES_V2:
    PROMPT: str = dedent('''
    Review the Question and Examine the Reference: Carefully read and
    understand the question. Carefully read each of the reference provided for
    the question:
    Evaluate the LLM Response based on guidelines (1-4): 
    1. Given the model response, only consider the part(s) of the response
    answering the question, and ignore any extra text.
    2. When evaluating the language model's answer, evaluate True if it matches
    with at least one of the provided references otherwise False.
    3. An answer and reference pair is considered a match if they are
    semantically equivalent given the context of the question. This
    determination should not require world knowledge from the human, and if it
    does, consider it not a match. The answer must contain all the information
    of the reference for it to be considered a match.
    4. Considering there might be multiple correct answers, each answer must
    match with at least one reference for the response to be considered correct
    overall.
    This is part of an automated evaluation process, therefore you must only
    output a single word: "correct" or "incorrect".
                                         
    Question:
    {question}

    References:
    {references}

    Model Response:
    {response}

    Evaluation (correct/incorrect):
    ''').strip()


class TAG:
    PROMPT: str = dedent('''
    Your task is to look at the following question, and based on the references
    provided, determine if the model's response is correct or incorrect.
    First, you will provide a step-by-step evaluation of the model's response,
    and then provide the final answer of "correct" or "incorrect" inside
    <{extract_tag}> and </{extract_tag}> tags.
    For example, <{extract_tag}>correct</{extract_tag}> or
    <{extract_tag}>incorrect</{extract_tag}>. If you are not confident in your
    evaluation, you can answer with "maybe correct" or "maybe incorrect".

    Question:
    {question}

    References:
    {references}

    Model Response:
    {response}

    Evaluation (correct/incorrect):
    ''').strip()