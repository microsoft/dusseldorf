# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

'''
This test class makes sure we can import the modules in zentralbibliothek.
'''
def test_importing_modules():
    import zentralbibliothek
    from zentralbibliothek.ruleengine import RuleEngine
    from zentralbibliothek.dbclient3 import DatabaseClient
    from zentralbibliothek.utils import Utils
    # from zentralbibliothek.logging import Logger

