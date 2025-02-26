# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
import logging

from ..models.rule import Rule, RuleCreate, RulePriority, RuleComponent, ComponentCreate, ComponentAction
from ..models.auth import Permission
from ..dependencies import get_current_user, get_db
from ..helpers.validation import Validator
from ..services.permissions import PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rules",
    tags=["Rules"]
    )

MAX_PRIORITY = 1000

# GET /rules
# gets all rules that user can see (has perms to see)
@router.get("", response_model=List[Rule])
async def get_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    # Get all zones where user has permission higher than READONLY
    all_zones = await db.zones.find({"authz.alias": current_user["preferred_username"]}, {"_id": 0, "fqdn": 1}).to_list(None)
    confirmed_zones = []
    for zone in all_zones:
        can_read:bool = await permission_service.has_at_least_permissions_on_zone(zone["fqdn"], current_user["preferred_username"], Permission.READONLY)
        
        if can_read:
            confirmed_zones.append(zone["fqdn"])

    rules = await db.rules.find({"zone": {"$in": confirmed_zones}}).skip(skip).limit(limit).to_list(None)
    if not rules:
        raise HTTPException(status_code=404, detail="Rules not found")

    return [Rule(**rule) for rule in rules]

# GET /rules/{zone}
# gets all rules for a given zone
@router.get("/{zone}", response_model=List[Rule])
async def get_rules_by_zone(
    zone: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    can_read:bool = await permission_service.has_at_least_permissions_on_zone(zone, current_user["preferred_username"], Permission.READONLY)
    if not can_read:
        logger.warning(f"User {current_user['preferred_username']} attempted to access zone {zone} rules")
        raise HTTPException(status_code=403, detail="Unauthorized")

    rules = await db.rules.find({"zone": zone}).to_list(None)
    if not rules:
        raise HTTPException(status_code=404, detail="Rule not found")

    return [Rule(**rule) for rule in rules]

# GET /rules/{zone}/{rule_id}
# gets a specific rule by ID, and the zone it belongs to
@router.get("/{zone}/{rule_id}", response_model=Rule)
async def get_rule(
    zone: str,
    rule_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    user_id:str = current_user["preferred_username"]
    can_read:bool = await permission_service.has_at_least_permissions_on_zone(zone, user_id, Permission.READONLY)
    if not can_read:
        logger.warning(f"User {user_id} attempted to access zone {zone} rule {rule_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    rule = await db.rules.find_one({"ruleid": UUID(rule_id)})
    if not rule:
        logger.debug(f"Rule {rule_id} not found")
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return Rule(**rule)


# POST /rules
# creates a new rule
@router.post("", response_model=Rule)
async def create_rule(
    rule: RuleCreate,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    user_id = current_user["preferred_username"]
    can_rw:bool = await permission_service.has_at_least_permissions_on_zone(rule.zone, user_id, Permission.READWRITE)
    if not can_rw:
        logger.warning(f"User {current_user['preferred_username']} attempted to create rule for zone {rule.zone}")
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validate priority 
    if rule.priority <= 0 or rule.priority > MAX_PRIORITY:
        raise HTTPException(status_code=400, detail="Invalid priority")

    priority_result = await db.rules.find({"zone": rule.zone}, {"_id": 0, "priority": 1}).to_list(None)
    if priority_result:
        priority_only_list = []
        for priority in priority_result:
            priority_only_list.append(priority["priority"])
        
        if rule.priority in priority_only_list:   
            # BEGIN Priority check and set
            priority_only_list.sort()
            available_priorities = [ele for ele in range(1, MAX_PRIORITY + 1) if ele not in priority_only_list]
            # END Priority check and set
            if len(available_priorities) > 0:
                rule.priority = available_priorities[0]
            else:
                raise HTTPException(status_code=400, detail=f"Unable to find an unused priority")

    new_rule = rule.dict()
    new_rule["ruleid"] = uuid4()
    new_rule["rulecomponents"] = []
    result = await db.rules.insert_one(new_rule)
    if not result.inserted_id:
        raise HTTPException(status_code=400, detail=f"Failed to create rule")
    
    logger.info(f"User {user_id} created zone {rule.zone} rule {new_rule['ruleid']}")
    return Rule(**new_rule)


# PUT /rules/{zone}/{rule_id}
# updates a rule's priority
@router.put("/{zone}/{rule_id}")
async def update_rule_priority(
    zone: str,
    rule_id: str,
    priority: RulePriority,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    user_id:str = current_user["preferred_username"]

    can_read_write:bool = await permission_service.has_at_least_permissions_on_zone(zone, user_id, Permission.READWRITE)
    if can_read_write == False:
        logger.warning(f"User {current_user['preferred_username']} attempted to update zone {zone} rule {rule_id}")
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validate priority 
    if priority.priority <= 0 or priority.priority > MAX_PRIORITY:
        raise HTTPException(status_code=400, detail="Invalid priority")

    update_result = await db.rules.update_one({"zone": zone, "ruleid": UUID(rule_id)}, {"$set": {"priority": priority.priority}})
    if update_result.modified_count != 1:
        logger.error(f"Failed to update rule {zone}/{rule_id} priority: modified_count: {update_result.modified_count}")
        raise HTTPException(status_code=400, detail="Rule update failed")
    
    logger.info(f"User {current_user['preferred_username']} updated rule {zone}/{rule_id} priority to {priority.priority}")
    return {"status": "success"}


# DELETE /rules/{zone}/{rule_id}
# deletes a rule (and thus its components)
@router.delete("/{zone}/{rule_id}")
async def delete_rule(
    zone: str,
    rule_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    can_rw:bool = await permission_service.has_at_least_permissions_on_zone(zone, current_user["preferred_username"], Permission.READWRITE)
    if not can_rw:
        logger.warning(f"User {current_user['preferred_username']} attempted to delete rule {zone}/{rule_id}")
        raise HTTPException(status_code=403, detail="Unauthorized to delete rule")
    
    result = await db.rules.delete_one({"zone": zone, "ruleid": UUID(rule_id)})
    if result.deleted_count != 1:
        logger.exception(f"Failed to delete rule {zone}/{rule_id}: deleted_count: {result.deleted_count}")
        raise HTTPException(status_code=400, detail="Failed to delete rule")
    
    logger.info(f"User {current_user['preferred_username']} deleted rule {zone}/{rule_id}")
    return {"status": "success"}


# POST /rules/{zone}/{rule_id}/components
# adds a component to a rule
@router.post("/{zone}/{rule_id}/components", response_model=RuleComponent)
async def add_rule_component(
    zone: str,
    rule_id: str,
    component: ComponentCreate,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    if not await permission_service.has_at_least_permissions_on_zone(zone, current_user["preferred_username"], Permission.READWRITE):
        logger.warning(f"User {current_user['preferred_username']} attempted to add components for zone {zone} rule {rule_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Validate action name
    if not Validator.validate_action_name(component.actionname, component.ispredicate):
        raise HTTPException(status_code=400, detail="Invalid action name")

    new_component = component.dict()
    new_component["componentid"] = uuid4()

    update_result = await db.rules.update_one({"zone": zone, "ruleid": UUID(rule_id)}, {"$push": {"rulecomponents": new_component}})
    if update_result.modified_count != 1:
        raise HTTPException(status_code=400, detail="Failed to add rule component")
    
    logger.info(f"User {current_user['preferred_username']} added zone {zone} rule {rule_id} component {new_component['componentid']}")
    return RuleComponent(**new_component)


# PUT /rules/{zone}/{rule_id}/components/{component_id}
# updates a rule's component's action value
@router.put("/{zone}/{rule_id}/components/{component_id}")
async def edit_rule_component(
    zone: str,
    rule_id: str,
    component_id: str,
    action_value: ComponentAction,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    """Edit rule component's action value"""
    can_write:bool =  await permission_service.has_at_least_permissions_on_zone(zone, current_user["preferred_username"], Permission.READWRITE)
    if not can_write:
        logger.warning(f"User {current_user['preferred_username']} attempted to modify zone {zone} rule {rule_id} component {component_id}")
        raise HTTPException(status_code=403, detail="Forbidden")

    update_result = await db.rules.update_one(
        {"zone": zone, "ruleid": UUID(rule_id), "rulecomponents.componentid": UUID(component_id)}, 
        {"$set": {"rulecomponents.$.actionvalue": action_value.actionvalue}}
    )

    if update_result.matched_count != 1:
        raise HTTPException(status_code=400, detail='Failed to update component')

    logger.info(
        f"User {current_user['preferred_username']} updated zone {zone} rule {rule_id} component {component_id} action value to {action_value.actionvalue}"
    )
    return {"status": "success"}


# DELETE /rules/{zone}/{rule_id}/components/{component_id}
# deletes a component from a rule
@router.delete('/{zone}/{rule_id}/components/{component_id}')
async def delete_rule_component(
    zone: str,
    rule_id: str,
    component_id: str,
    db: AsyncIOMotorClient = Depends(get_db),
    current_user: str = Depends(get_current_user),
    permission_service: PermissionService = Depends()
):
    if not await permission_service.has_at_least_permissions_on_zone(zone, current_user["preferred_username"], Permission.READWRITE):
        logger.warning(f"User {current_user['preferred_username']} attempted to delete zone {zone} rule {rule_id} component {component_id}")
        raise HTTPException(status_code=403, detail="Forbidden")

    delete_result = await db.rules.update_one(
        {"zone": zone, "ruleid": UUID(rule_id)}, 
        {"$pull": {"rulecomponents": {"componentid": UUID(component_id)}}})
    
    if delete_result.modified_count != 1:
        raise HTTPException(status_code=400, detail='Failed to delete component')
    
    logger.info(f"User {current_user['preferred_username']} deleted zone {zone} rule {rule_id} component {component_id}")
    return {"status": "success"}
        