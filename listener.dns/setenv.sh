# this sets up the development envrionment for Dusseldorf

PIPCMD="python3 -m pip"


# download and install the library
install_zentral()
{
    echo "Downloading zentralbibliothek from Azure Devops"
    pushd .
    cd /tmp
    export ZENTRAL_RANDOM_DIR="zentral-$(date +%s | sha256sum | base64 | head -c 12)"
    mkdir $ZENTRAL_RANDOM_DIR
    # check if dir was made
    if [ ! -d "$ZENTRAL_RANDOM_DIR" ]; then
    echo "Directory was not made, check permissions"
    exit 1
    fi

    # latest is in `main`, not release.
    # BRANCHNAME="main"
    BRANCHNAME="main"

    # download the library into our new directory
    cd $ZENTRAL_RANDOM_DIR
    git clone -b $BRANCHNAME --single-branch https://securityassurance@dev.azure.com/securityassurance/Dusseldorf/_git/zentralbibliothek z
    cd z
    # cd ~/code/zentralbibliothek/
    # and build the library
    $PIPCMD install -r requirements.txt
    $PIPCMD install --editable .
    popd
}


# check if we are in a real environment, or in a venv already.
if [[ "$VIRTUAL_ENV" == "" ]]
then
    python3 -m venv .venv
    source .venv/bin/activate
fi


# See if we have the zentralbibliothek library installed
ZVERSION=`python3 -m pip show zentralbibliothek | grep Version | awk '{print $2}'`
# if [[ $ZVERSION != "0.0.9" ]]; then
#     echo "Zentralbibliothek not installed/outdated, installing now"
#     install_zentral
# fi
install_zentral


python3 -m pip install --upgrade artifacts-keyring
python3 -m pip install -r src/requirements.txt

# az login
# export CONNSTR=`az keyvault secret show --vault-name dssldrf-canary --name dataplane-connstr | jq -r ".value"`
# export DSSLDRF_CONNSTR=`az keyvault secret show --vault-name dssldrf-test --name dataplane-connstr | jq -r ".value"`

