# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# aka.ms/dusseldorf

from networkrequest import NetworkRequest

class Rule:
    """
    This class describes a rule that should be evaluated for a given request.
    Each rule has one Predicate object and one Result object.
    Set the request before evaluating (the RuleOrchestrator does this automagically for you).
    You shouldn't need to call methods on this class, but you can call Evaluate if you'd like.

    Constructor: Rule(predicates, results)
        name        type
        -----------------------------
        predicates  list[Predicate]
        results     list[Result]

    >>> p = new myPredicate()
    >>> r = new myResult()
    >>> rule = new myRule([p], [r])
    >>> rule.Evaluate()
    <<< ArgumentException: rule._request is None.
    >>> rule.SetRequest(myRequest)
    >>> rule.Evaluate()
    <<< SomeResult ... 
    """
    def __init__(self, predicates, results, rule_identifier = None):
        self._predicates = predicates
        self._results = results
        self._request:NetworkRequest = None
        self._rule_identifier = rule_identifier
    
    def __bool__(self):
        return all([p.IsTrue() for p in self._predicates])

    def SetRequest(self, request:NetworkRequest):
        self._request = request
        for p in self._predicates:
            p.SetRequest(request)
        return self

    def SetRuleForComponents(self):
        for p in self._predicates:
            p.SetRule(self)
        for r in self._results:
            r.SetRule(self)

    def Evaluate(self, request = None):
        self.SetRuleForComponents()
        if request is not None:
            self.SetRequest(request)
        if self._request == None:
            raise ValueError('No request to run rules on.')
        return self._results if self else []