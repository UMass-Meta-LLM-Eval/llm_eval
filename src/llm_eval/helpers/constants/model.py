# HuggingFace Constants

HF_MAX_NEW_TOKENS = 64
"""Default maximum number of tokens to generate for a response."""

# OpenAI Constants

OAI_BATCH_PURPOSE = 'batch'
"""Purpose code for batch processing."""

OAI_BATCH_ENDPOINT = '/v1/chat/completions'
"""Endpoint for batch processing requests."""

OAI_BATCH_COMPLETION_WINDOW = '24h'
"""Default completion window for batch processing requests."""

OAI_BATCH_METHOD = 'POST'
"""HTTP method for batch processing requests."""

OAI_BATCH_SUCCESS = 'completed'
"""Status code for a successfully completed batch request."""
