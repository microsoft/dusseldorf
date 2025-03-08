# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest
from zentralbibliothek.models.predicate import Predicate

def test_predicate_successful():
    '''
    This test makes sure that we can write a child class outside of zentralbibliothek
    that can be parented to the abstract predicate class in zentralbibliothek.
    '''
    class TestPredicate(Predicate):
        def __init__(self):
            super().__init__()

        def satisfied_by(self, request, parameter):
            return True

    test_predicate = TestPredicate()
    assert test_predicate.satisfied_by("request", "parameter")

def test_predicate_missingmethods():
    '''
    This test does not implement the abstract methods in the child class, and so should fail.
    '''
    class TestPredicate(Predicate):
        def __init__(self):
            super().__init__()

    with pytest.raises(TypeError):
        test_predicate = TestPredicate()