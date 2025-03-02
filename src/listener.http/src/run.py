# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from socketserver import TCPServer
import logging
import os 
import sys
import ssl
from ssl import SSLContext

from zentralbibliothek.utils import Utils
from zentralbibliothek.dbclient3 import DatabaseClient
from httplistener import HttpRequestHandler
from azure.monitor.opentelemetry import configure_azure_monitor

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(
        logger_name="listener.http",  # Set the namespace for the logger in which you would like to collect telemetry for if you are collecting logging telemetry. This is imperative so you do not collect logging telemetry from the SDK itself.
    )

logger = logging.getLogger("listener.http")

def main():

    Utils.banner()

    logging.basicConfig(level = logging.DEBUG)
    tls:bool = bool(int(os.getenv("LSTNER_HTTP_TLS", 1))) # LSTNER_HTTP_TLS=0 for HTTP
    LISTENER_NAME = "listener.http"
    if tls:
        LISTENER_NAME = "listener.https"

    logger.info(f"Starting Dusseldorf {LISTENER_NAME}")

    iface:str = os.getenv("LSTNER_HTTP_INTERFACE", "")
    port:int = int(os.getenv("LSTNER_HTTP_PORT", 443))
    #tls:bool = bool(int(os.getenv("LSTNER_HTTP_TLS", 1))) # LSTNER_HTTP_TLS=0 for HTTP 
    tls_crt_file:str = os.environ.get("DSSLDRF_TLS_CRT_FILE", None)
    tls_key_file:str = os.environ.get("DSSLDRF_TLS_KEY_FILE", None)

    if "DSSLDRF_CONNSTR" not in os.environ:
        logger.critical(f"{LISTENER_NAME} DSSLDRF_CONNSTR not found in environment variables")
        return -1

    # wake up the DB
    _ = DatabaseClient.get_instance()

    try:    
        server = TCPServer((iface, port), HttpRequestHandler)
        if tls is True:
            # if this is an HTTP server, load the cert and keyfile
            if tls_crt_file is None:
                logger.critical(f"{LISTENER_NAME} DSSLDRF_TLS_CRT_FILE not found in environment variables")
                return -1
            if tls_key_file is None:
                logger.critical(f"{LISTENER_NAME} DSSLDRF_TLS_KEY_FILE not found in environment variables")
                return -1

            # but check if they exist on filesystem
            if not os.path.isfile(tls_crt_file):
                logger.critical(f"{LISTENER_NAME} TLS cert file {tls_crt_file} not found")
                return -1
            if not os.path.isfile(tls_key_file):
                logger.critical(f"{LISTENER_NAME} TLS key file {tls_key_file} not found")
                return -1

            ctx = SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.maximum_version = ssl.TLSVersion.TLSv1_3
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.load_cert_chain(tls_crt_file, tls_key_file)
            ctx.options |= (
                ssl.OP_NO_SSLv2
                | ssl.OP_NO_SSLv3
                | ssl.OP_NO_TLSv1
                | ssl.OP_NO_TLSv1_1
                | ssl.OP_CIPHER_SERVER_PREFERENCE
                | ssl.OP_SINGLE_DH_USE
                | ssl.OP_SINGLE_ECDH_USE
            )  # Disable weak ciphers
            ctx.options |= ssl.OP_NO_COMPRESSION  # Disable compression (CRIME attack prevention)
            ctx.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384')
            server.socket = ctx.wrap_socket(
                server.socket, 
                server_side = True,
                do_handshake_on_connect = True,
                suppress_ragged_eofs = True,                
            )
        
        logger.info(f"{LISTENER_NAME} Listening on {port}")
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
