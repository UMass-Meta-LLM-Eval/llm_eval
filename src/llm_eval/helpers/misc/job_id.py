from datetime import datetime

def create_job_id() -> str:
    """Create a unique job ID based on the current time."""
    dt_curr_str = datetime.now().strftime('%Y%m%d-%H%M%S%z')
    return f'INTERACTIVE_{dt_curr_str}'
