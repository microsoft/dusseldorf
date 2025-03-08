# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install --editable .

python3 -m build

