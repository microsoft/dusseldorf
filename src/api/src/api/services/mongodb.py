from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime
import logging

from ..config import Settings

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB"""
        logger.info("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(
            self.settings.MONGODB_URL,
            **self.settings.get_mongodb_options()
        )
        self.db = self.client[self.settings.MONGODB_DB_NAME]
        await self.ping()
        logger.info("Connected to MongoDB")

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def ping(self):
        """Test MongoDB connection"""
        try:
            await self.db.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {str(e)}")
            raise

    async def create_indexes(self):
        """Create required indexes"""
        try:
            # Domains indexes
            await self.db.domains.create_index("name", unique=True)
            
            # Zones indexes
            await self.db.zones.create_index([
                ("domain_id", 1),
                ("name", 1)
            ], unique=True)
            await self.db.zones.create_index("is_public")
            
            # Rules indexes
            await self.db.rules.create_index([
                ("zone_id", 1),
                ("name", 1),
                ("rule_type", 1)
            ], unique=True)
            
            # Permissions indexes
            await self.db.authz_permissions.create_index([
                ("zone_id", 1),
                ("user", 1)
            ], unique=True)
            
            # Requests indexes
            await self.db.dns_requests.create_index("status")
            await self.db.dns_requests.create_index("created_at")
            
            # Payloads indexes
            await self.db.payloads.create_index("status")
            await self.db.payloads.create_index("created_at")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {str(e)}")
            raise 