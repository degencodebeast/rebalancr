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
    DATABASE_URL: str = "sqlite:///./data/rebalancr.db"
    #DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

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
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    PRIVY_APP_ID: str = os.getenv("PRIVY_APP_ID", "")
    PRIVY_APP_SECRET: Optional[str] = os.getenv("PRIVY_APP_SECRET")
    PRIVY_WALLET_ID: Optional[str] = os.getenv("PRIVY_WALLET_ID")
    PRIVY_API_KEY: str = os.getenv("PRIVY_API_KEY", "")  # API key for server wallets
    PRIVY_WEBHOOK_SECRET: str = os.getenv("PRIVY_WEBHOOK_SECRET", "")  # For webhook verification

    CDP_API_KEY_NAME: Optional[str] = os.getenv("CDP_API_KEY_NAME")
    CDP_API_KEY_PRIVATE_KEY: Optional[str] = os.getenv("CDP_API_KEY_PRIVATE_KEY")
    
    # Privy configuration
    PRIVY_PUBLIC_KEY: str = os.getenv("PRIVY_PUBLIC_KEY", "")  # For token verification
    
    # # Add this field to your existing Settings class
    # PRIVY_WALLET_ID: Optional[str] = None

    DATA_DIR: str = os.getenv("DATA_DIR", "./data")

    NETWORK_ID: str = os.getenv("NETWORK_ID", "base-sepolia")
    
    # Privy Server Wallets
    sqlite_db_path: str = "sqlite:///./data/conversations.db"
    wallet_data_dir: str = "./data/wallets"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Alternative solution: ignore extra fields

# Initialize settings once
settings = Settings()

def get_settings():
    return Settings()
