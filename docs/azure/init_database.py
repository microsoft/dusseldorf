# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging
import os
import sys
import getopt
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_collections(db):
    logger.info("Creating database")
    await db.create_collection("domains")
    await db.create_collection("zones")
    await db.create_collection("requests")
    await db.create_collection("rules")
    # await db.create_collection("templates")
    logger.debug("Created database")

async def delete_collections(db):
    logger.info("Deleting database")
    await db.domains.drop()
    await db.zones.drop()
    await db.requests.drop()
    await db.rules.drop()
    #await db.templates.drop()
    logger.debug("Deleted database")


async def create_indexes(db):
    logger.info("Creating indexes")
    await db.domains.create_index("domain", unique=True)
    await db.zones.create_index("fqdn", unique=True)
    await db.zones.create_index([("fqdn", 1), ("alias", 1)])
    await db.requests.create_index([("_id", 1), ("time", 1)])
    await db.requests.create_index([("zone", 1), ("time", 1)])
    await db.rules.create_index([("zone", 1), ("priority", 1), ("networkprotocol", 1)], unique=True)
    await db.rules.create_index("name")
    #await db.templates.create_index("name", unique=True)
    #await db.templates.create_index("tags", sparse=True)
    #await db.template_components.create_index("template_name")
    logger.debug("Created indexes")

async def init_database(mongodb_url: str, db_name: str = "dusseldorf", domain: str = None, delete_first: bool = False, ips = []):
    """Initialize MongoDB database with collections and indexes"""

    print(f"Initializing database {db_name}")
    
    try:
        client = AsyncIOMotorClient(mongodb_url)
        db = client[db_name]

        if delete_first:
            await delete_collections(db)

        # Create collections (equivalent to tables)
        await create_collections(db)
        #await db.create_collection("templates")

        logger.debug("Created collections, creating indexes now")

        # Create indexes
        await create_indexes(db)

        logger.debug("Created indexes")

        # Determine initial domain
        logger.info(f"Adding domain {domain} ")

        ip_addresses = []
        for ip in ips:
            # validate IP address
            if ip.count(".") != 3:
                logger.error(f"Invalid IP address: {ip}")
                raise ValueError(f"Invalid IP address: {ip}")
            ip_addresses.append(ip)


        first_domain = {
            "domain": domain,
            "owner": "dusseldorf", # This is the default owner for all zones
            "users": [], # This is the default list of for all zones
            "public_ips": ip_addresses, # This is the default list of for all zones
        }

        # Insert initial data
        await db.domains.insert_one(first_domain)

        logger.debug(f"Inserted initial domain: {domain}")

        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        client.close()


def main():
    """Main entry point for database initialization"""

    # handle arguments:
    # --domain <domain> - specify the domain to use for public zones
    # --delete : delete the database before initializing

    usage:str = "Usage: init_database.py [-vh] --domain <domain> [--delete] --ips <ip1,ip2,...>"
    helpmsg:str = ("--domain <domain> : (required) specify the FQDN to use\n" + 
                  "--ips <ip1,ip2,...> : specify the public IP addresses for the domain\n" +
                  "--delete : optionally deletes the collections before initializing\n" + 
                  "-v, --verbose : enable debug logging\n" + 
                  "-h : show this help message")

    domain = None
    db_name = "dusseldorf"
    delete_dbs = False
    ips = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "vh", ["domain=", "delete", "verbose", "ips="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            print(helpmsg)
            sys.exit(0)
        elif opt == "--domain":
            domain = arg
        elif opt == "--delete":
            delete_dbs = True
        elif opt in ("--verbose", "-v"):
            logger.setLevel(logging.DEBUG)
        elif opt == "--ips":
            ips = arg.split(",")

    # ensure we have a domain
    if not domain:
        print(usage)
        sys.exit(2)

    if "DSSLDRF_CONNSTR" not in os.environ:
        logger.error("DSSLDRF_CONNSTR environment variable not set")

    mongodb_url = os.getenv("DSSLDRF_CONNSTR")

    asyncio.run(init_database(
        mongodb_url=mongodb_url, 
        db_name=db_name, 
        domain=domain, 
        delete_first = delete_dbs, 
        ips=ips)
    )

if __name__ == "__main__":
    main() 
