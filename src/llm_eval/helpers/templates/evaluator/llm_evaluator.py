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