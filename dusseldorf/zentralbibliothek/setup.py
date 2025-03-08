# setup.py
import os
from setuptools import setup

# get build number from ADO environment variable
dev_version = os.environ.get("Build.BuildNumber")

setup(
  version=f"{dev_version}" if dev_version else f"0.0.0-dev"
)

