# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import random
import string
import pytest
from zentralbibliothek.dbclient3 import DatabaseClient
from zentralbibliothek.utils import Utils

# only run DB tests if we have a connection string
# from https://docs.pytest.org/en/6.2.x/skipping.html
def have_connstr():
    return "DSSLDRF_CONNSTR" in os.environ

only_run_if_db_connected = pytest.mark.skipif(not have_connstr(), reason="No database connection string found in environment variables")

@pytest.fixture
def db():
    db = DatabaseClient.get_instance()
    return db


@only_run_if_db_connected
def test_db3_as_instance(db):
    assert db is not None


@only_run_if_db_connected
def test_db3_is_singleton(db):
    db3 = DatabaseClient.get_instance()
    assert db is db3

@only_run_if_db_connected
def test_db3_domain_exist(db):
    non_existing_domain = db.domain_exists("test") 
    assert non_existing_domain == False

@only_run_if_db_connected
def test_db3_zone_exist(db):
    non_existing_zone = db.zone_exists("nonexistingzone") 
    assert non_existing_zone == False

@only_run_if_db_connected
def test_db3_5_non_zone_exist(db):
    for i in range(3):
        non_existing_zone = db.zone_exists("non_existing_zone" + str(i)) 
        assert non_existing_zone == False

@only_run_if_db_connected
def test_db3_empty_zone_doesnt_exist(db):
    non_existing_zone = db.zone_exists("") 
    assert non_existing_zone == False

@only_run_if_db_connected
def test_db3_get_rules_for_nonexisting(db):
    rules = db.get_rules("non_existing_zone_good_pasta") 
    assert len(rules) == 0

@only_run_if_db_connected
def test_db3_get_aggregated_rule_predicates_for_zone(db):
    rules = db.get_aggregated_rule_predicates_for_zone("http", "non_existing_zone_weeheewoohoo") 
    assert len(rules) == 0

@only_run_if_db_connected
def test_db3_find_zone_for_request(db):
    zone = db.find_zone_for_request("this.www.does.not.exist.com")
    assert zone is None

# @only_run_if_db_connected
# def test_db3_get_aggregated_rule_results_noguid(db):
#     with pytest.raises(ValueError):
#         _ = db.get_aggregated_rule_results("not_a_guid") # raises an exception

# @only_run_if_db_connected
# def test_db3_get_aggregated_rule_results_noguid22(db):
#     import uuid
#     guid = str(uuid.uuid4())
#     zone = db.get_aggregated_rule_results(guid) 
#     assert zone == (guid, [], [])

@only_run_if_db_connected
def test_db3_get_domain_from_zone(db):
    domain = db.get_domain_from_zone("this_zone_does_not_exist_weeheewoohoo") 
    assert domain == ""

# these are being deprecated
# @only_run_if_db_connected
# def test_db3_create_zone(db):
#     zone = db.create_zone(zone_prefix="foo", parent_zone="bar")
#     assert len(zone) == 0 # empty string
    
# @only_run_if_db_connected
# def test_db3_create_zone_noprefix(db):
#     zone = db.create_zone(zone_prefix="", parent_zone="bar")
#     assert len(zone) == 0 # empty string

# @only_run_if_db_connected
# def test_db3_create_zone_noparent(db):
#     with pytest.raises(ValueError):
#         # this should raise an exception
#         zone = db.create_zone(zone_prefix="", parent_zone="")

@only_run_if_db_connected
def test_create_and_delete_domain(db):

    random_domain:str = ''.join(random.choices(string.ascii_lowercase, k=18)) + ".net"
    found = db.domain_exists(random_domain)
    assert found == False

    db.create_domain(domain=random_domain)
    # this may be cached
    # found = db.domain_exists(random_domain)
    # assert found == True

    db.delete_domain(random_domain)
    found = db.domain_exists(random_domain)
    assert found == False


@only_run_if_db_connected
def test_create_and_delete_domain(db):
    random_domain:str = ''.join(random.choices(string.ascii_lowercase, k=19)) + ".net"
    db.create_domain(domain=random_domain)
    found = db.domain_exists(random_domain)
    assert found == True
    db.delete_domain(random_domain)


@only_run_if_db_connected
def test_get_domain_data(db):
    doms = db.get_domains()
    assert len(doms) > 0

    for dom in doms:
        ips = db.get_public_ips(dom)
        print(dom, ips)
        assert len(ips) > 0

@only_run_if_db_connected
def test_get_default_domains(db):
    doms = db.get_domains()
    assert len(doms) > 0

@only_run_if_db_connected
def test_validate_zone(db):
    primary_domain = db.get_domains()[0]

    zone = f"test1337.{primary_domain}"
    assert Utils.fqdn_is_valid(fqdn=zone, domain=primary_domain) == True

@only_run_if_db_connected
def test_validate_invalid_zone(db):
    primary_domain = db.get_domains()[0]
    zone = f"test1337{primary_domain}"
    assert Utils.fqdn_is_valid(fqdn=zone, domain=primary_domain) == False

@only_run_if_db_connected
def test_delete_domain(db):
    ret  = db.delete_domain("nonexisting")
    assert ret.acknowledged == True
    assert ret.deleted_count == 0
