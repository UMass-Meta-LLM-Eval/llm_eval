import re
import string

from . import logger

def _get_truncation_logic(logic):
    if not logic or logic == 'newline':
        return {
            'until': ['\n']
        }
    elif logic == 'skip':
        return {}
    elif logic == 'newlinequestion':
        return {
            'until': ['\nQ:']
        }
    elif logic == 'newlinequestion2':
        return {
            'until': ['\nQuestion:']
        }
    elif logic == 'eleutherai':
        return {
        'until': ['\n', '.', ','],
        'remove': ['punctuation', 'whitespace'],
        'ignore_regex': ['\\b(?: The the An | A |The | a |an )'],
        'ignore_case': True
    }
    else:
        raise ValueError('Not a Valid Truncation Logic!')


def truncate_response(config, response) -> str:
    """
    Truncates a response based on the given configuration.

    Parameters:
        config (dict): A dictionary containing truncation configuration.
        response (str): The response string to be truncated.

    Returns:
        str: The truncated response string.
    """
    logic = config.get('truncate', 'newline')
    logger.debug('Truncation Logic: %s', logic)
    config_trunc = _get_truncation_logic(logic)
    
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