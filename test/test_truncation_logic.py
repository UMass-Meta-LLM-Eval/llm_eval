from llm_eval.helpers.misc import truncate_response
import inspect

def _create_dummy_logic_config(logic):
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
    dummy_config = _create_dummy_logic_config(logic)
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
    dummy_config = _create_dummy_logic_config(logic)
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
    dummy_config = _create_dummy_logic_config(logic)
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
    dummy_config = _create_dummy_logic_config(logic)
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
