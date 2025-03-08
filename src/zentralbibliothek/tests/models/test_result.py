# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest
from zentralbibliothek.models.result import Result

def test_result_successful():
    '''
    This test makes sure that we can write a child class outside of zentralbibliothek
    that can be parented to the abstract result class in zentralbibliothek.
    '''
    class TestResult(Result):
        def __init__(self):
            super().__init__()

        def execute(self, result_data, parameter):
            return {"new":"stuff"}

    test_result = TestResult()
    assert test_result.execute("result_data", "parameter") == {"new":"stuff"}

def test_result_missingmethods():
    '''
    This test does not implement the abstract methods in the child class, and so should fail.
    '''
    class TestResult(Result):
        def __init__(self):
            super().__init__()

    with pytest.raises(TypeError):
        test_result = TestResult()