import asyncio
import logging
import os
import sys
import getopt
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_collections(db):
    logger.info("Creating database collections")
    await db.create_collection("domains")
    await db.create_collection("zones")
    await db.create_collection("requests")
    await db.create_collection("rules")

async def create_indexes(db):
    logger.info("Creating indexes")
    await db.domains.create_index("domain", unique=True)
    await db.zones.create_index("fqdn", unique=True)
    await db.zones.create_index([("fqdn", 1), ("alias", 1)])
    await db.requests.create_index([("zone", 1), ("time", 1)])
    await db.requests.create_index("time")  # Required for CosmosDB order-by
    await db.rules.create_index([("zone", 1), ("priority", 1), ("networkprotocol", 1)], unique=True)
    await db.rules.create_index("name")

async def init_database(mongodb_url: str, db_name: str, domain: str, ips: list):
    if not domain:
        logger.error("Missing required argument: --domain")
        sys.exit(1)
    if not ips or ips == ['']:
        logger.error("Missing required argument: --ips")
        sys.exit(1)

    logger.info(f"Initializing database {db_name}")
    try:
        client = AsyncIOMotorClient(mongodb_url, username=os.getenv("MONGO_USERNAME"), password=os.getenv("MONGO_PASSWORD"))
        db = client[db_name]
        await create_collections(db)
        await create_indexes(db)
        first_domain = {"domain": domain, "public_ips": ips}
        await db.domains.insert_one(first_domain)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    mongodb_url = os.getenv("DSSLDRF_CONNSTR")
    db_name = "dusseldorf"
    domain = None
    ips = []
    
    opts, _ = getopt.getopt(sys.argv[1:], "", ["domain=", "ips="])
    for opt, arg in opts:
        if opt == "--domain":
            domain = arg
        elif opt == "--ips":
            ips = arg.split(",")
    
    asyncio.run(init_database(mongodb_url, db_name, domain, ips))