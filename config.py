from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Security
    HONEYPOT_API_KEY: str = "agentic-honeypot-secret-key"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./honeypot.db"
    
    # App Metadata
    APP_NAME: str = "Agentic HoneyPot API"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
