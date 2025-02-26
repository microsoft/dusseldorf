from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # MongoDB
    DSSLDRF_CONNSTR: str
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    
    # Azure
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
#    AZURE_CLIENT_SECRET: str
#    KEY_VAULT_URL: str
    
    # JWT
#    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    def get_mongodb_options(self) -> Dict[str, Any]:
        """Get MongoDB client options"""
        return {
            "minPoolSize": self.MONGODB_MIN_POOL_SIZE,
            "maxPoolSize": self.MONGODB_MAX_POOL_SIZE,
            "retryWrites": True,
            "retryReads": True
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 