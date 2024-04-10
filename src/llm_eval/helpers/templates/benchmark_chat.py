from textwrap import dedent


class CHAT_SIMPLE:
    FEWSHOT: str = 'Q: {question}\nA: {answer}\n\n'
    """Simple fewshot template for chat models."""

    QUESTION: str = '{fewshot}Q: {question}\nA:'
    """Simple question template for chat models."""


class CHAT_V2:
    """V2 templates for chat models. Should work better with fewshot"""

    FEWSHOT: str = 'Q: {question}\nA: {answer}\n\n'
    """Fewshot template V2 for chat models."""
    
    QUESTION: str = dedent('''
    You are a part of a question answering benchmark. Look at the following 
    examples on how to answer the questions.

    ```
    {fewshot}
    ```

    Your task is to answer the following question. Remember to be concise and 
    only give the answer in a few words.

    Q: {question}
    A:''').strip()
    """Question template V2 for chat models."""
    
    QUESTION_ZERO_SHOT: str = dedent('''
    You are a part of a question answering benchmark. Your task is to answer 
    the following question. Remember to be concise and only give the answer in
    a few words.

    Q: {question}
    A:''').strip()
    """Zero-shot question template V2 for chat models."""