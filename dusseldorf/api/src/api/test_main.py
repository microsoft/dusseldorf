# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

import base64
import json
import os
import pytest
import time
import random
import string
from fastapi.testclient import TestClient

# set logging to debug
import logging
logging.basicConfig(level=logging.DEBUG)

# This will run a series of tests against the API.  To run all tests, make sure:
# Set a token such as: 
#   export DSSLDRF_AUTH_TOKEN=`az account get-access-token --resource=dc1b6b75-8167-4baf-9e75-d3d1f755de1b | jq -r .accessToken`
#
# to set the domain, set DSSLDRF_DOMAIN to the domain you want to test against.  Example:
#   export DSSLDRF_DOMAIN="contoso.com"

# "globals"
time_to_sleep:int = 1


def filter_preffered_username_from_jwt(token):
    token = token.split(".")[1]
    token += "=" * ((4 - len(token) % 4) % 4)
    return json.loads(base64.b64decode(token).decode('utf-8'))["preferred_username"]

def auth_hdr() -> dict:
    return {
        'Authorization': f'Bearer {os.environ["DSSLDRF_AUTH_TOKEN"]}'
    }

def make_random_string(length: int) -> str:
    # return an alphanumeric string without digits of length
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def get_domain_name():
    return os.environ.get("DSSLDRF_DOMAIN", None)

def have_token():
    # note, this tdoes **not** promise that the token is valid and not expired, and yours. :)
    return "DSSLDRF_AUTH_TOKEN" in os.environ

skip_if_not_authenticated = pytest.mark.skipif(not have_token(), reason="No DSSLDRF_AUTH_TOKEN set")
skip_if_no_domain_set = pytest.mark.skipif(not get_domain_name(), reason="No DSSLDRF_DOMAIN set")

# general API client
from .main import app
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    resp = response.json() 
    assert resp["name"] == "Dusseldorf API"

def test_unauth_ping():
    response = client.get("/ping")
    assert response.status_code == 403

@skip_if_not_authenticated
def test_auth_ping_success():
    response = client.get("/ping", headers=auth_hdr())
    assert response.status_code == 200
    resp = response.json()

@skip_if_not_authenticated
def test_auth_ping_fields():
    response = client.get("/ping", headers=auth_hdr())
    resp = response.json()
    # "pong" is a timestamp of "now" on the server, that's at least 5 days ago
    assert int(resp["pong"]) > time.time() - (5 * 24 * 60 * 60)  # 5 days 
    # check if the user is the same as the one in the token
    assert resp["user"] == filter_preffered_username_from_jwt(os.environ["DSSLDRF_AUTH_TOKEN"])

# ------------------------------
# tests for domains
# mihendri: disabled for now, since we disabled the domains controller
# "disabled the domains controller" is more disruptive on a LAN :D

# @skip_if_not_authenticated
# def test_get_domains():
#     response = client.get("/domains", headers=auth_hdr())
#     assert response.status_code == 200

# @skip_if_not_authenticated
# def test_has_more_than_zero_domains():
#     response = client.get("/domains", headers=auth_hdr())
#     resp = response.json()
#     assert len(resp) > 0

# @skip_if_not_authenticated
# @skip_if_no_domain_set
# def test_matches_domain():
#     response = client.get("/domains", headers=auth_hdr())
#     resp = response.json()
#     assert get_domain_name() in resp

# ------------------------------
# tests for zones 

@skip_if_not_authenticated
def test_get_zones():
    response = client.get(f"/zones", headers=auth_hdr())
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) >= 0 # there should be at least 0 zones


@skip_if_not_authenticated
@skip_if_no_domain_set
def test_make_and_delete_zone():

    # first, get number of zones
    response = client.get(f"/zones", headers=auth_hdr())
    resp = response.json()
    num_zones = len(resp)
    
    # make a random, new zone
    zone_name = make_random_string(10)
    req_obj = {
        "zone": zone_name,
        "domain": get_domain_name()
    }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) == 1 # only 1 was added
    new_fqdn = resp[0]["fqdn"]

    # sleep for a bit to allow the zone to be created
    time.sleep(time_to_sleep)

    # count again
    response = client.get(f"/zones", headers=auth_hdr())
    resp = response.json()
    assert len(resp) == num_zones + 1


    response = client.get(f"/zones/{new_fqdn}", headers=auth_hdr())
    assert response.status_code == 200
    resp = response.json()
    assert resp["fqdn"] == new_fqdn

    # clean up
    response = client.delete(f"/zones/{new_fqdn}", headers=auth_hdr())
    assert response.status_code == 200

    time.sleep(time_to_sleep)

    # detect decrease in zones again
    response = client.get(f"/zones", headers=auth_hdr())
    resp = response.json()
    assert len(resp) == num_zones


@skip_if_not_authenticated
def test_make_5_random_zones_in_any_domain_and_delete():
    time_to_sleep:int = 1
    # make 5 ramdom zones
    req_obj = { "num": 5 }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) == 5

    time.sleep(time_to_sleep)

    # delete all the zones
    for zone in resp:
        fqdn = zone["fqdn"]
        time.sleep(time_to_sleep)
        response = client.delete(f"/zones/{fqdn}", headers=auth_hdr())
        assert response.status_code == 200

@skip_if_not_authenticated
@skip_if_no_domain_set
def test_make_5_random_zones_in_domain_and_delete():
    time_to_sleep:int = 1
    # make a zone
    req_obj = {
        "domain": get_domain_name(),
        "num": 5
    }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) == 5

    # delete all 
    for zone in resp:
        time.sleep(time_to_sleep)
        fqdn = zone["fqdn"]
        response = client.delete(f"/zones/{fqdn}", headers=auth_hdr())
        assert response.status_code == 200



@skip_if_not_authenticated
def test_make_one_random_zone_and_delete():
    time_to_sleep:int = 1
    req_obj = {}
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) == 1

    # delete it again
    fqdn:str = resp[0]["fqdn"]
    time.sleep(time_to_sleep)
    response = client.delete(f"/zones/{fqdn}", headers=auth_hdr())
    assert response.status_code == 200



@skip_if_not_authenticated
def test_make_one_particular_zone_and_delete():
    time_to_sleep:int = 1
    # make a zone
    req_obj = {
        "zone": "unique" + make_random_string(13)
    }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    resp = response.json()
    assert len(resp) == 1
    time.sleep(time_to_sleep)
    fqdn:str = resp[0]["fqdn"]

    response = client.delete(f"/zones/{fqdn}", headers=auth_hdr())
    assert response.status_code == 200

@skip_if_not_authenticated
def test_make_illegal_domain():
    req_obj = {
        "zone": "www",
        "domain": "microsoft.com"
    }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 403


# ------------------------------
# tests for authz

@skip_if_not_authenticated
@skip_if_no_domain_set
def test_make_zone_add_users_and_then_delete_all():

    zone_name = make_random_string(10)
    req_obj = {
        "zone": zone_name,
        "domain": get_domain_name()
    }
    response = client.post(f"/zones", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200
    full_zone_fqdn = response.json()[0]["fqdn"]

    time.sleep(time_to_sleep)

    # get users 
    response = client.get(f"/authz/{full_zone_fqdn}", headers=auth_hdr())
    assert response.status_code == 200

    # add a user
    random_user:str = "nonexisting@domain.net"
    req_obj = {
        "alias": random_user,
        "permission": "readonly"
    }

    response = client.post(f"/authz/{full_zone_fqdn}", headers=auth_hdr(), json=req_obj)
    assert response.status_code == 200

    # test if at least user is there, me and random_user
    response = client.get(f"/authz/{full_zone_fqdn}", headers=auth_hdr())
    assert response.status_code == 200
    resp = response.json()
    # there should be at least 2 users
    assert len(resp) >= 2
    
    # find both users:
    reduce_me_to_zero:int = 2
    for user in resp:
        if user["alias"] == random_user:
            reduce_me_to_zero -= 1
        if user["alias"] == filter_preffered_username_from_jwt(os.environ["DSSLDRF_AUTH_TOKEN"]):
            reduce_me_to_zero -= 1

    assert reduce_me_to_zero == 0


    # remove this user again
    response = client.delete(f"/authz/{full_zone_fqdn}/{random_user}", headers=auth_hdr())
    assert response.status_code == 200

    # delete the zone
    response = client.delete(f"/zones/{full_zone_fqdn}", headers=auth_hdr())
    assert response.status_code == 200

