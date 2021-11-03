"""
Testing neural net command prediction
"""
#pylint: disable=C0413

import sys
import json
sys.path.append('../')
from init_bp import listener

def test_neural_code_():
    """
    Test neural net using training dataset
    :return:
    """
    with open('../data/intents.json', 'r', encoding="utf-8") as file:
        test_dict =json.load(file)
    for intent in test_dict['intents']:
        for pattern in intent['patterns'][:2]:
            res = listener(pattern)
            assert (res['to_call'], pattern) == (intent['tag'], pattern)


def test_neural_code_invalid_input():
    """
    Test neural net using 'invalid' requests
    :return:
    """
    patterns = ['123', 'sdfdsf', '', ' ', '*****', '&&&!!!\\\n', 'привет']
    for pattern in patterns:
        res = listener(pattern)
        assert (res['to_call'], pattern) == ("help", pattern)
