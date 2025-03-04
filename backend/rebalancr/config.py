from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings and configuration
    
    Loads from environment variables or uses defaults
    """
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-replace-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    ALLORA_API_KEY: str = os.getenv("ALLORA_API_KEY")
    AGENT_ID: str = os.getenv("AGENT_ID")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # Agent Configuration
    DEFAULT_REBALANCE_THRESHOLD: float = 5.0
    MAX_GAS_LIMIT_OPTIONS: dict = {
        "low": 1.0,
        "moderate": 1.5, 
        "high": 2.0
    }
    
    # External APIs
    PRIVY_APP_ID: Optional[str] = os.getenv("PRIVY_APP_ID")
    PRIVY_APP_SECRET: Optional[str] = os.getenv("PRIVY_APP_SECRET")
    PRIVY_WALLET_ID: Optional[str] = os.getenv("PRIVY_WALLET_ID")

    CDP_API_KEY_NAME: Optional[str] = os.getenv("CDP_API_KEY_NAME")
    CDP_API_KEY_PRIVATE_KEY: Optional[str] = os.getenv("CDP_API_KEY_PRIVATE_KEY")
    
    # # Add this field to your existing Settings class
    # PRIVY_WALLET_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Alternative solution: ignore extra fields

# Initialize settings once
settings = Settings()

def get_settings():
    return Settings()
