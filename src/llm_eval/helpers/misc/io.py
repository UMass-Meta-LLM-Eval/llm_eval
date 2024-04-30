import re
import string

from . import logger


TRUNCATION_LOGIC: dict[str, dict] = {
    'newline': {
        'until': ['\n']},
    'skip': {},
    'newlinequestion': {
        'until': ['\nQ:']},
    'newlinequestion2': {
        'until': ['\nQuestion:']},
    'eleutherai': {
        'until': ['\n', '.', ','],
        'remove': ['punctuation', 'whitespace'],
        'ignore_regex': ['\\b(?: The the An | A |The | a |an )'],
        'ignore_case': True}}
"""Dictionary containing presets for truncation of response strings."""

DEFAULT_TRUNCATION_LOGIC = 'newline'

def truncate_response(response, logic) -> str:
    """
    Truncates a response based on the given configuration.

    Parameters:
        response (str): The response string to be truncated.
        logic (str): The truncation logic to be used.

    Returns:
        str: The truncated response string.
    """
    if logic is None:
        logger.warning('Truncation configuration not found. Using default '
                       'truncation logic: %s', DEFAULT_TRUNCATION_LOGIC)
        logic = DEFAULT_TRUNCATION_LOGIC
    logger.debug('Truncation Logic: %s', logic)
    try:
        config_trunc = TRUNCATION_LOGIC[logic]
    except KeyError as e:
        logger.error('Invalid truncation logic: %s', logic)
        raise ValueError(f'Could not find truncation logic: {logic}') from e
    
    # Skip Truncation if no configuration provided
    if config_trunc == {}:
        return response.strip()

    # Truncate based on specified characters until their occurrence
    if config_trunc.get('until', False):
        min_index = len(response)
        until_chars = config_trunc.get('until')
        for char in until_chars:
            index = response.find(char)
            if index != -1:
                min_index = min(min_index, index)
        response = response[:min_index]

    # Truncate based on removing regex patterns
    if config_trunc.get('ignore_regex', False):
        ignore_regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in config_trunc.get('ignore_regex', [])]
        for pattern in ignore_regex_patterns:
            response = pattern.sub(' ', response)

    # Truncate based on removing specified characters
    if config_trunc.get('remove', False):
        for remove_logic in config_trunc.get('remove'):
            if remove_logic == 'punctuation':
                for char in string.punctuation:
                    response = response.replace(char, '')
            elif remove_logic == 'whitespace':
                response = response.strip()
                response = response.replace('\t', ' ')
                response = re.sub(r'\s+', ' ', response)
    
    # Ignore case if specified
    if config_trunc.get('ignore_case', False):
        response = response.lower()

    return response.strip()


def extract_from_tag(input_str: str, tag: str, multi_ok: bool = False):
        pattern = f'<{tag}>(.*?)</{tag}>'
        matches: list[str] = re.findall(pattern, input_str, re.DOTALL)

        # No matches found
        if len(matches) == 0:
            return None
        
        # Return all matches if multi_ok is True
        if multi_ok:
            return matches
        
        # Return the first match if multi_ok is False
        if len(matches) > 1:
            logger.warning('Multiple matches found for tag `%s` in response. '
                           'Returning the first match.', tag)
        return matches[0]
