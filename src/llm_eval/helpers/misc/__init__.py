from datetime import datetime
from .. import logger
from .io import truncate_response, extract_from_tag
from .config_utils import (load_config, validate_config, log_config,
                           configs_to_jsonl)
from ..constants.evaluator import ERROR_CODES


def create_job_id() -> str:
    """Create a unique job ID based on the current time."""
    dt_curr_str = datetime.now().strftime('%Y%m%d-%H%M%S%z')
    return f'INTERACTIVE_{dt_curr_str}'


def parse_error_codes(error_codes: str) -> tuple[list, str]:
    """Parse a string of error codes into a list of error codes and a
    string of unknown error codes."""

    # Split the error codes into a list
    error_code_list = list(set(e.upper() for e in error_codes))

    # Check if the error codes are valid
    errors, unknown = [], ''
    for error in error_code_list:
        if error in ERROR_CODES:
            errors.append(ERROR_CODES[error])
        else:
            unknown += error

    return errors, unknown
