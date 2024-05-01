from datetime import datetime
from .. import logger
from .io import truncate_response, extract_from_tag
from .config_utils import load_config, validate_config, log_config


def create_job_id() -> str:
    """Create a unique job ID based on the current time."""
    dt_curr_str = datetime.now().strftime('%Y%m%d-%H%M%S%z')
    return f'INTERACTIVE_{dt_curr_str}'
