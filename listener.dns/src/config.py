# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v2
# aka.ms/dusseldorf

# Shared config variables for DNS Listener
# ---------------------------
# 2024-12-18 Are repeated os.getenv() calls slowing
# things down? Let's find out! Throwing variables in
# here and since Python only evaluates module imports
# once, should speed things up(?)

import os

DSSLDRF_DOMAINS = os.getenv("DSSLDRF_DOMAINS", "").split(" ")
DSSLDRF_IPV4 = os.getenv("DSSLDRF_IPV4", "127.0.0.1 127.0.0.2").split(" ")
DSSLDRF_IPV6 = os.getenv("DSSLDRF_IPV6", "").split(" ")