"""Constants for the evaluator module and supporting helper functions."""

TRUNCATE = 'truncate'
"""The key for the truncation configuration."""

EXTRACT = 'extract'
"""The key for the extraction tag."""

VALID_HUMAN_INPUTS = ['y', 'n', 'yy', 'nn', 'y?', 'n?']
"""The valid inputs for a human evaluator."""

POS_LABELS = ['y', 'yy', 'y?']
"""The positive labels for a human evaluator."""

HIGH_CONFIDENCE_LABELS = ['y', 'n', 'yy', 'nn']
"""The high confidence labels for a human evaluator."""

ERROR_CODES = {
    'N': 'No answer',
    'I': 'Incorrect entity',
    'M': 'Too many entities',
    'F': 'Too few entities',
    'U': 'Under-specified',
    'C': 'Answer cut-off',
    'O': 'Other'}
"""The error codes and their descriptions when evaluating a response
as incorrect."""
