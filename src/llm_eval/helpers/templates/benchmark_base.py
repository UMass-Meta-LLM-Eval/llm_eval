class BASE_SIMPLE:
    FEWSHOT: str = 'Q: {question}\nA: {answer}\n\n'
    """Simple fewshot template for base models."""

    QUESTION: str = '{fewshot}Q: {question}\nA:'
    """Simple question template for base models."""

    QUESTION_ZERO_SHOT: str = 'Q: {question}\nA:'
    """Simple zero-shot question template for base models."""


class BASE_MMLU:
    FEWSHOT: str = 'Question: {question}\nResponse: {answer}\n\n'
    """Simple MMLU fewshot template for base models."""

    QUESTION: str = '{fewshot}Question: {question}\nResponse:'
    """Simple MMLU question template for base models."""

    QUESTION_ZERO_SHOT: str = 'Question: {question}\nResponse:'
    """Simple MMLU zero-shot question template for base models."""