import re
import inspect
import string

def getTruncationLogic(logic):
    if not logic or logic == 'newline':
        return {
            "until": ["\n"]
        }
    elif logic == 'skip':
        return {}
    elif logic == 'newlinequestion':
        return {
            "until": ["\nQ:"]
        }
    elif logic == 'eleutherai':
        return {
        "until": ["\n", ".", ","],
        "remove": ["punctuation", "whitespace"],
        "ignore_regex": ["\\b(?: The the An | A |The | a |an )"],
        "ignore_case": True
    }
    else:
        raise ValueError("Not a Valid Truncation Logic!")


def truncate_response(config, response) -> str:
    """
    Truncates a response based on the given configuration.

    Parameters:
        config (dict): A dictionary containing truncation configuration.
        response (str): The response string to be truncated.

    Returns:
        str: The truncated response string.
    """
    logic = config.get("truncate", None)
    config_trunc = getTruncationLogic(logic)
    
    # Skip Truncation if no configuration provided
    if config_trunc == {}:
        return response.strip()

    # Truncate based on specified characters until their occurrence
    if config_trunc.get("until", False):
        min_index = len(response)
        until_chars = config_trunc.get("until")
        for char in until_chars:
            index = response.find(char)
            if index != -1:
                min_index = min(min_index, index)
        response = response[:min_index]

    # Truncate based on removing regex patterns
    if config_trunc.get("ignore_regex", False):
        ignore_regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in config_trunc.get("ignore_regex", [])]
        for pattern in ignore_regex_patterns:
            response = pattern.sub(" ", response)

    # Truncate based on removing specified characters
    if config_trunc.get("remove", False):
        for remove_logic in config_trunc.get("remove"):
            if remove_logic == 'punctuation':
                for char in string.punctuation:
                    response = response.replace(char, "")
            elif remove_logic == 'whitespace':
                response = response.strip()
                response = response.replace('\t', ' ')
                response = re.sub(r'\s+', ' ', response)
    
    # Ignore case if specified
    if config_trunc.get("ignore_case", False):
        response = response.lower()

    return response.strip()

def _createDummyLogicConfig(logic):
    """
    Creates a standard dummy configuration.

    Returns:
        dict: The standard dummy configuration.
    """
    return {
        "name": "exact-match",
        "cls": "ExactMatchEvaluator",
        "truncate": logic
    }

def _run_test_skip_truncation(logic):
    """
    Runs tests for skip truncation scenarios.
    """
    dummy_config = _createDummyLogicConfig(logic)
    responses = [
        'The Capital of India is NewDelhi\nBefore that Agra was the capital of India', # Test No Truncation
    ]
    results = [
        'The Capital of India is NewDelhi\nBefore that Agra was the capital of India', # Test No Truncation
    ]
    for test_response, test_result in zip(responses, results):
        assert truncate_response(dummy_config, test_response) == test_result, str('\n'+test_response+'\nTruncated Response = '+truncate_response(dummy_config, test_response)+'\nCorrect Response = '+test_result)
    print('All Test Cases Have Passed!', inspect.stack()[0].function)

def _run_tests_eleutherAI(logic):
    """
    Runs tests for various truncation scenarios.
    """
    dummy_config = _createDummyLogicConfig(logic)
    responses = [
        'Capital of India is New Delhi\nBefore that Agra was the capital of India', # Test \n
        'This is the story of Peter Pan. He was a young boy.', # Test .
        'Biggest Cities in US are New York, Chicago and Los Angeles', # Test ,
        'This is a test case\nThis part is, not important.', # Test \n . ,
        '      This             is a test case         ', # Test Remove Whitespace
        'THiS Is A TeST CAsE', # Test Ignore Case ,
        ':;This ?!:;--{([])}\'\" is a ?test case?!', # Test Ignore Punctuations,
        'The Big Apple is the city of New York', # Remove Regex # "\\b(?: The the An | A |The | a |an )"
    ]
    results = [
        'capital of india is new delhi', # Test \n
        'this is story of peter pan', # Test . and Remove Regex (the)
        'biggest cities in us are new york', # Test ,
        'this is test case', # Test \n . , and Remove Regex (a)
        'this is test case', # Test Remove Whitespace and Remove Regex (a)
        'this is test case', # Test Ignore Case , and Remove Regex (a)
        'this is test case', # Test Ignore Punctuations and Remove Regex (a)
        'big apple is city of new york', # Remove Regex # "\\b(?: The the An | A |The | a |an )"
    ]

    for test_response, test_result in zip(responses, results):
        assert truncate_response(dummy_config, test_response) == test_result, str('\n'+test_response+'\nTruncated Response = '+truncate_response(dummy_config, test_response)+'\nCorrect Response = '+test_result)
    print('All Test Cases Have Passed!', inspect.stack()[0].function)

def _run_test_newline(logic = None):
    """
    Runs tests for skip truncation scenarios.
    """
    dummy_config = _createDummyLogicConfig(logic)
    responses = [
        'The Capital of India is NewDelhi\nBefore that Agra was the capital of India',
    ]
    results = [
        'The Capital of India is NewDelhi'
    ]
    for test_response, test_result in zip(responses, results):
        assert truncate_response(dummy_config, test_response) == test_result, str('\n'+test_response+'\nTruncated Response = '+truncate_response(dummy_config, test_response)+'\nCorrect Response = '+test_result)
    print('All Test Cases Have Passed!', inspect.stack()[0].function)

def _run_test_newlinequestion(logic):
    """
    Runs tests for skip truncation scenarios.
    """
    dummy_config = _createDummyLogicConfig(logic)
    responses = [
        'The Capital of India is NewDelhi\n New Delhi is the Capital of India \nQ: foo bar'
    ]
    results = [
        'The Capital of India is NewDelhi\n New Delhi is the Capital of India',
    ]
    for test_response, test_result in zip(responses, results):
        assert truncate_response(dummy_config, test_response) == test_result, str('\n'+test_response+'\nTruncated Response = '+truncate_response(dummy_config, test_response)+'\nCorrect Response = '+test_result)
    print('All Test Cases Have Passed!', inspect.stack()[0].function)

if __name__ == "__main__":
    _run_test_skip_truncation('skip')
    _run_tests_eleutherAI('eleutherai')
    _run_test_newline('newline')
    _run_test_newline()
    _run_test_newlinequestion('newlinequestion')
