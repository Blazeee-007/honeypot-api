from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # API Security
    HONEYPOT_API_KEY: str = "agentic-honeypot-secret-key"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database Configuration
    # Automatically use /tmp for SQLite on Vercel to avoid Read-Only errors
    DATABASE_URL: str = "sqlite:////tmp/honeypot.db" if os.environ.get("VERCEL") else "sqlite:///./honeypot.db"
    
    # App Metadata
    APP_NAME: str = "Agentic HoneyPot API"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
