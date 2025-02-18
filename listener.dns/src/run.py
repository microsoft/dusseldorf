# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v2
# aka.ms/dusseldorf

# DNS Listener for duSSeldoRF
# ---------------------------
# This is the main listener for DNS requests. It uses the dnslib
# library to listen for them and uses the zentralbibliothek to
# respond with a corresponding rule, if any.

import time
import logging
import os 
import sys

from zentralbibliothek.config import Config
from zentralbibliothek.utils import Utils
from zentralbibliothek.dbclient3 import DatabaseClient
from zentralbibliothek.logging import Logger

from dnsresolver import DusseldorfResolver
from dnslib.server import DNSServer, DNSLogger

def main():
    Utils.banner()
    Logger.setup_logger()

    logger = logging.getLogger("listener.dns")

    db = DatabaseClient.get_instance()
    if db.test_connectivity() == False:
        logger.critical("db connection failed")
        return -1

    logger.info("db connected")

    # default: listen on port 53, UDP, on all interfaces
    port:int = int(os.getenv("LSTNER_DNS_PORT", 53))
    udp_env:str = os.getenv("LSTNER_DNS_UDP", "True")
    udp:bool = udp_env.lower() in ("true", "1", "on", "y", "yes")
    iface:str = str(os.getenv("LSTNER_DNS_INTERFACE", ""))

    # if port is below 1024, we need to be root
    if port < 1024 and os.geteuid() != 0:
        logger.error(f"Listening on port {port} requires root privileges")
        return -1

    dnsserver = DNSServer(
        resolver = DusseldorfResolver(),
        port=port,
        address=iface,
        logger = DNSLogger('-send,-recv,-request,-reply,-truncated,-data'),
        tcp = not udp
    )

    try:
        msg:str = f"Trying to listen on {port}/{'tcp' if not udp else 'udp'}"
        logger.info(msg)
        dnsserver.start_thread()

        while 1:
            time.sleep(10)
            sys.stderr.flush()
            sys.stdout.flush()
          
    except Exception as ex:
        logging.exception(ex)
        dnsserver.stop()
        return -1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
