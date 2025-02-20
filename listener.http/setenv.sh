# this sets up the development environment for Dusseldorf

# check if we are in a real environment, or in a venv already.
if [[ "$VIRTUAL_ENV" == "" ]]
then
    python -m venv .venv
    source .venv/bin/activate
fi

# Install the zentralbibliothek library from the local repository
python -m pip install -r ../../zentralbibliothek/requirements.txt
python -m pip install --editable ../../zentralbibliothek

python -m pip install --upgrade artifacts-keyring
python -m pip install -r src/requirements.txt

make_cert()
{
    mkdir cert
    # make cert
    openssl req -x509 \
        -newkey rsa:4096 \
        -keyout cert/key.pem \
        -out cert/cert.pem -sha256 -days 10 \
        -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
}
