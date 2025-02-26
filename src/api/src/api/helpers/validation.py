# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class Validator:
    """Helper class to validate all the things"""

    @staticmethod
    def validate_action_name(action_name: str, is_predicate: bool) -> bool:
        allowed_predicates = [
            "dns.type",
            "http.method", 
            "http.tls", 
            "http.path", 
            "http.header",
            "http.headers.keys",
            "http.headers.values",
            "http.headers.regexes",
            "http.body"
        ]
        allowed_results = [
                "dns.data",
                "dns.type",
                "http.code", 
                "http.header", 
                "http.headers", 
                "http.body",
                "http.passthru",
                "var"
        ]
        if is_predicate:
            if action_name in allowed_predicates:
                return True
        else:
            if action_name in allowed_results:
                return True
        
        return False


def validate_payload_content(content: Dict[str, Any], payload_type: str) -> bool:
    """Validate payload content based on type"""
    try:
        if payload_type == "ZONE_IMPORT":
            return validate_zone_import_content(content)
        elif payload_type == "ZONE_EXPORT":
            return validate_zone_export_content(content)
        elif payload_type == "BULK_UPDATE":
            return validate_bulk_update_content(content)
        else:
            return False
    except Exception as e:
        logger.debug(f"Payload validation failed: {str(e)}")
        return False

def validate_zone_import_content(content: Dict[str, Any]) -> bool:
    """Validate zone import payload content"""
    required_fields = ['records', 'format']
    if not all(field in content for field in required_fields):
        return False
        
    if content['format'] not in ['BIND', 'JSON', 'CSV']:
        return False
        
    if not isinstance(content['records'], list):
        return False
        
    return True

def validate_zone_export_content(content: Dict[str, Any]) -> bool:
    """Validate zone export payload content"""
    required_fields = ['format', 'include_metadata']
    if not all(field in content for field in required_fields):
        return False
        
    if content['format'] not in ['BIND', 'JSON', 'CSV']:
        return False
        
    if not isinstance(content['include_metadata'], bool):
        return False
        
    return True

def validate_bulk_update_content(content: Dict[str, Any]) -> bool:
    """Validate bulk update payload content"""
    required_fields = ['updates']
    if not all(field in content for field in required_fields):
        return False
        
    if not isinstance(content['updates'], list):
        return False
        
    # Validate each update
    for update in content['updates']:
        if not validate_update_entry(update):
            return False
            
    return True

def validate_update_entry(update: Dict[str, Any]) -> bool:
    """Validate a single update entry"""
    required_fields = ['action', 'record']
    if not all(field in update for field in required_fields):
        return False
        
    if update['action'] not in ['CREATE', 'UPDATE', 'DELETE']:
        return False
        
    if update['action'] != 'DELETE':
        if not validate_record_data(update['record']):
            return False
            
    return True

def validate_record_data(record: Dict[str, Any]) -> bool:
    """Validate DNS record data"""
    required_fields = ['name', 'type', 'content']
    if not all(field in record for field in required_fields):
        return False
        
    # Additional validation could be added here
    return True 