# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# duSSeldoRF v3
# aka.ms/dusseldorf

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from msal import ConfidentialClientApplication
from typing import Optional, Dict
from datetime import datetime
import jwt
import logging
import httpx
import json
from jwt.algorithms import RSAAlgorithm

from config import Settings

logger = logging.getLogger(__name__)

class AzureADService:
    def __init__(self):
        self.settings = Settings()
        self.credential = ManagedIdentityCredential(client_id=self.settings.AZURE_CLIENT_ID)
        self._app = None
        self._token_cache = {}
        self._signing_keys = None
        self._keys_last_updated = None

    @property
    def app(self) -> ConfidentialClientApplication:
        """Get or create MSAL application"""
        if not self._app:
            self._app = ConfidentialClientApplication(
                client_id=self.settings.AZURE_CLIENT_ID,
                client_credential=self.settings.AZURE_CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{self.settings.AZURE_TENANT_ID}"
            )
        return self._app

    async def _get_signing_keys(self) -> dict:
        """Get Azure AD signing keys with caching"""
        # Check if keys need refresh (every 24 hours)
        now = datetime.utcnow()
        if (self._signing_keys is None or 
            self._keys_last_updated is None or 
            (now - self._keys_last_updated).total_seconds() > 86400):
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://login.microsoftonline.com/{self.settings.AZURE_TENANT_ID}/discovery/v2.0/keys"
                    )
                    response.raise_for_status()
                    keys_data = response.json()

                    # Convert JWK to PEM format
                    self._signing_keys = {}
                    for key in keys_data.get("keys", []):
                        kid = key.get("kid")
                        if kid:
                            public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                            self._signing_keys[kid] = public_key
                            
                    self._keys_last_updated = now
                    
            except Exception as e:
                logger.error(f"Failed to get signing keys: {str(e)}")
                raise
                
        return self._signing_keys

    async def validate_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return claims"""
        try:
            # First decode without verification to get the key ID
            unverified_headers = jwt.get_unverified_header(token)
            alg = unverified_headers.get("alg")
            kid = unverified_headers.get("kid")
            if not kid:
                raise ValueError("No key ID in token header")
              
            # Get the signing keys
            signing_keys = await self._get_signing_keys()
            if kid not in signing_keys:
                raise ValueError("Unknown key ID")

            # Accept both raw client ID and api:// format for audience  
            valid_audiences = [
                self.settings.AZURE_CLIENT_ID,
                f"api://{self.settings.AZURE_CLIENT_ID}"
            ]
            
            # Decode and validate token
            claims = jwt.decode(
                token,
                key=signing_keys[kid],
                algorithms=[alg],
                audience=valid_audiences
            )
            
            # Verify tenant ID
            tid = claims.get("tid")
            if not tid or tid != self.settings.AZURE_TENANT_ID:
                raise ValueError("Invalid tenant ID")
                
            # Verify object ID exists
            oid = claims.get("oid")
            if not oid:
                raise ValueError("No object ID in token")

            # Accept both v1.0 (sts.windows.net) and v2.0 (login.microsoftonline.com) issuers
            iss = claims.get("iss")
            valid_issuers = [
                f"https://login.microsoftonline.com/{self.settings.AZURE_TENANT_ID}/v2.0",
                f"https://sts.windows.net/{self.settings.AZURE_TENANT_ID}/"
            ]
            if iss not in valid_issuers:
                raise ValueError("Invalid issuer")
                
            # Return normalized user info (only what's needed)
            # Handle both v1.0 (upn) and v2.0 (preferred_username) token formats  
            preferred_username = claims.get("preferred_username") or claims.get("upn")
            return {
                "id": oid,  # Object ID (unique user identifier)
                "tid": tid,  # Tenant ID
                "preferred_username": preferred_username,  # User Principal Name
                "name": claims.get("name"),
                "email": claims.get("email") or preferred_username,
                "roles": claims.get("roles", [])
            }
            
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None

    async def get_graph_token(self) -> str:
        """Get access token for Microsoft Graph"""
        try:
            result = await self.app.acquire_token_silent(
                ["https://graph.microsoft.com/.default"],
                account=None
            )
            
            if not result:
                result = await self.app.acquire_token_for_client(
                    ["https://graph.microsoft.com/.default"]
                )
                
            return result["access_token"]
            
        except Exception as e:
            logger.error(f"Failed to get Graph token: {str(e)}")
            raise 
