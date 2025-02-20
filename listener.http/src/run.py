# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v2
# aka.ms/dusseldorf

# main file that's called to run this listener

from socketserver import TCPServer
import logging
import os 
import sys
import ssl
from ssl import SSLContext

from zentralbibliothek.utils import Utils
from zentralbibliothek.dbclient3 import DatabaseClient
from httplistener import HttpRequestHandler

logger = logging.getLogger(__name__)

def main():

    Utils.banner()

    logging.basicConfig(level = logging.DEBUG)
    logger.info("Starting Dusseldorf")

    iface:str = os.getenv("LSTNER_HTTP_INTERFACE", "")
    port:int = int(os.getenv("LSTNER_HTTP_PORT", 443))
    tls:bool = bool(int(os.getenv("LSTNER_HTTP_TLS", 1))) # LSTNER_HTTP_TLS=0 for HTTP 
    tls_crt_file:str = os.environ.get("DSSLDRF_TLS_CRT_FILE", None)
    tls_key_file:str = os.environ.get("DSSLDRF_TLS_KEY_FILE", None)

    if "DSSLDRF_CONNSTR" not in os.environ:
        logger.critical("DSSLDRF_CONNSTR not found in environment variables")
        return -1

    # wake up the DB
    _ = DatabaseClient.get_instance()

    try:    
        server = TCPServer((iface, port), HttpRequestHandler)
        if tls is True:
            # if this is an HTTP server, load the cert and keyfile
            if tls_crt_file is None:
                logger.critical("DSSLDRF_TLS_CRT_FILE not found in environment variables")
                return -1
            if tls_key_file is None:
                logger.critical("DSSLDRF_TLS_KEY_FILE not found in environment variables")
                return -1

            # but check if they exist on filesystem
            if not os.path.isfile(tls_crt_file):
                logger.critical("TLS cert file (%s) not found", tls_crt_file)
                return -1
            if not os.path.isfile(tls_key_file):
                logger.critical("TLS key file (%s) not found", tls_key_file)
                return -1

            ctx = SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(tls_crt_file, tls_key_file)
            server.socket = ctx.wrap_socket(
                server.socket, 
                server_side = True,
                do_handshake_on_connect = True,
                suppress_ragged_eofs = True,                
            )
        
        logger.info("Listening on %s", port)
        server.allow_reuse_address = True
        server.server_version = "Dusseldorf"
        server.serve_forever()

    except ssl.SSLError as ex:
        logger.critical(ex)
        raise ex
    except (Exception, KeyboardInterrupt, SystemExit) as ex:            
        logger.exception(ex)
        raise ex

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as ex:
        logging.exception(ex)
    finally:
        sys.exit(1)
