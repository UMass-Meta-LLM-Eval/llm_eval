class BASE_SIMPLE:
    FEWSHOT: str = 'Q: {question}\nA: {answer}\n\n'
    """Simple fewshot template for base models."""

    QUESTION: str = '{fewshot}Q: {question}\nA:'
    """Simple question template for base models."""
