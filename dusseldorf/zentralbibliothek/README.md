# Zentralbibliothek: The Central Library of Dusseldorf

This library contains the common functionality shared across the network listeners in 
Dusseldorf.  If you want to develop a custom one, or wish to build these listeners from source, 
this library will make that easier.

Zentralbibliothek, or sometimes referred to as _zentral_, is implemented in Python3, and 
provides the following functionality to listeners:

 - Database connectivity: the `dbclient3.py` file implements a `DatabaseClient` class which allows flexible storage interactions.
 - The file `ruleengine.py` implements a strong `RuleEngine` which allows filters to be created, as well as custom responses to be sent back.
 - The `Utils` class in `utils.py` exposes some commonly used functions, such as FQDN validation etc.

 


## Running Locally 
We recommend using a virtual environment for your development, this makes managing dependencies
easier.

1. Set up a virtual environment with `python3 -m venv .venv`
2. Activate the virtual environment with `source .venv/bin/activate` (vscode should automatically do this)
3. Install the dependencies with `python -m pip install -r requirements.txt`

## Installing Locally
From the repo root, with the virtual environment activated:
1. `python -m build`
2. `pip install --editable .`

## Running Tests
Our testing happens using __pytest__, which you can run from the CLI easily.  From the in your virtual environment, ensure you have pytest installed:

```shell
(.venv) $ pip install pytest
(.venv) $ pytest
```

## MongoDB Setup
Ensure you have MongoDB installed and running. You can set the connection string in the environment variable `DSSLDRF_CONNSTR`.

For example:
```shell
export DSSLDRF_CONNSTR="mongodb://localhost:27017/yourdbname"
```

