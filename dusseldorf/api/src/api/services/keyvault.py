# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from typing import Optional
import logging

from ..config import Settings

logger = logging.getLogger(__name__)

class KeyVaultService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.credential = ManagedIdentityCredential(client_id=self.settings.AZURE_CLIENT_ID)
        self.client = SecretClient(
            vault_url=settings.KEY_VAULT_URL,
            credential=self.credential
        )
        self._cache = {}

    async def get_secret(self, name: str) -> Optional[str]:
        """Get a secret from Key Vault with caching"""
        try:
            # Check cache first
            if name in self._cache:
                return self._cache[name]
                
            # Get from Key Vault
            secret = self.client.get_secret(name)
            
            # Cache the value
            self._cache[name] = secret.value
            
            return secret.value
            
        except Exception as e:
            logger.error(f"Failed to get secret {name}: {str(e)}")
            return None

    async def set_secret(self, name: str, value: str) -> bool:
        """Set a secret in Key Vault"""
        try:
            self.client.set_secret(name, value)
            
            # Update cache
            self._cache[name] = value
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set secret {name}: {str(e)}")
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete a secret from Key Vault"""
        try:
            self.client.begin_delete_secret(name)
            
            # Remove from cache
            self._cache.pop(name, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret {name}: {str(e)}")
            return False

    def clear_cache(self):
        """Clear the secret cache"""
        self._cache.clear() 
