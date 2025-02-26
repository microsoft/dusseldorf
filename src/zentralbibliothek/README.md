# *Zentralbibliothek*: The Central Library of Dusseldorf
This python library contains the common code and functionality that all listeners for Project duSSeldoRF will need.  If you want to build a networklistener for Dusseldorf, this library will make that easier.

## Microsoft Specific
In `.microsoft/` you find 1P specific scripts and config files, no secrets, just config data.


## Contributing

We love contributions, please ensure you create a PR named `users/<alias>/<feature>` where <alias> is your Microsoft alias, and <feature> is a branch name of your new bugfix / feature / ...


After doing
```shell
$ git clone https://dev.azure.com/securityassurance/Dusseldorf/_git/zentralbibliothek/
$ cd zentralbibliothek
$ git checkout -b users/<alias>/<feature> 

# make changes

$ git commit -am "<put a meaningful message describing the changes>"
$ git push

# then you can use the AZ cli to make a PR

$ az repos pr create --auto-complete true --delete-source-branch false --required-reviewers dusseldorks  --target-branch main  --title "<your message>"  --org https://dev.azure.com/securityassurance/  --project Dusseldorf --repository zentralbibliothek 
```

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

