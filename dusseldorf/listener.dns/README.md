# Dusseldorf DNS Listener
This repo holds the DNS listener component for duSSeldoRF's dataplane.  This component is a versatile DNS server that listens on given network interfaces, usually on port 53.  

## TLDR
To get started quickly, and to start a listener on port 10053 (port 53 requires you to have root permissions):
```shell
$ bash setenv.sh
(venv)$ LSTNER_DNS_PORT=10053 python3 src/run.py
```
This `setenv` script will set up your local environment, and install all correct dependencies.  This will setup a [_virtual environment_](https://docs.python.org/3/library/venv.html) in Python 3 to maintain your dependencies locally. 

> Ensure that you join the  [__crg-dusseldorf-2zv5-srcro-lvyf__](https://coreidentity.microsoft.com/manage/Entitlement/entitlement/dusseldorf-2zv5) group (with the `src-ro` role) to gain access to required dependencies. 

In case you run in any issues, or wish to do any development on Dusseldorf, please check the sections below 


## Setting up the dev environment
Dusseldorf listeners use the __zentralbibliothek__ package, this is the central library for backend Dusseldorf actions.  This library is sort of an SDK and its code lives [here](https://dev.azure.com/securityassurance/Dusseldorf/_git/zentralbibliothek).  

The `setenv.sh` script tries to autoamte this downloads this library and attemps to install it locally.


