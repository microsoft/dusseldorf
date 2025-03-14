# Dusseldorf DNS Listener
This repository holds the DNS listener component for duSSeldoRF's dataplane.  This component is a versatile DNS server with a built-in rule engine.

One of the ways how Dusseldorf detects out-of-band vulnerabilties (such as SSRF, XXE, etc), is by listening for DNS `A` requests when something, somewhere tries to  resolve a hostname which is handled by this component.  

## Installation
This component is build for to run in a containerized environment.  For normal DNS functionality this component needs to be accessible on port 53/UDP.  For better security, we recommend to run this component on a higher port, so it doesn't have to run as root.

## Running locally
To get started quickly, and to start a listener on port 10053 (port 53 requires you to have root permissions):
```shell
$ python -m virtualenv .venv
$ source .venv/bin/activate
(.venv)$ LSTNER_DNS_PORT=10053 python3 src/run.py
```
This `setenv` script will set up your local environment, and install all correct dependencies.  This will setup a [_virtual environment_](https://docs.python.org/3/library/venv.html) in Python 3 to maintain your dependencies locally. 

