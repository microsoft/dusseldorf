from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime
import logging

from ..models.request import RequestStatus
from ..models.rule import Rule

logger = logging.getLogger(__name__)

class RequestProcessor:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def process_request(self, request_id: str):
        """Process a pending DNS change request"""
        try:
            # Get request details
            request = await self.db.dns_requests.find_one({"_id": request_id})
            if not request:
                logger.error(f"Request {request_id} not found")
                return
                
            # Update status to processing
            await self.db.dns_requests.update_one(
                {"_id": request_id},
                {"$set": {"status": RequestStatus.PROCESSING}}
            )
            
            # Process changes
            success = await self._apply_changes(request)
            
            # Update final status
            status = RequestStatus.COMPLETED if success else RequestStatus.FAILED
            await self.db.dns_requests.update_one(
                {"_id": request_id},
                {
                    "$set": {
                        "status": status,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process request {request_id}: {str(e)}")
            await self.db.dns_requests.update_one(
                {"_id": request_id},
                {
                    "$set": {
                        "status": RequestStatus.FAILED,
                        "error_message": str(e)
                    }
                }
            )

    async def _apply_changes(self, request: dict) -> bool:
        """Apply DNS changes from request"""
        try:
            changes = request["changes"]
            zone_id = request["zone_id"]
            
            # Process each change
            for change in changes:
                if change["action"] == "CREATE":
                    await self._create_rule(zone_id, change["rule"])
                elif change["action"] == "UPDATE":
                    await self._update_rule(zone_id, change["rule"])
                elif change["action"] == "DELETE":
                    await self._delete_rule(zone_id, change["rule_id"])
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply changes: {str(e)}")
            return False

    async def _create_rule(self, zone_id: str, rule_data: dict):
        """Create a new DNS rule"""
        rule_data["zone_id"] = zone_id
        await self.db.rules.insert_one(rule_data)

    async def _update_rule(self, zone_id: str, rule_data: dict):
        """Update an existing DNS rule"""
        rule_id = rule_data.pop("id")
        await self.db.rules.update_one(
            {"_id": rule_id, "zone_id": zone_id},
            {"$set": rule_data}
        )

    async def _delete_rule(self, zone_id: str, rule_id: str):
        """Delete a DNS rule"""
        await self.db.rules.delete_one(
            {"_id": rule_id, "zone_id": zone_id}
        ) 