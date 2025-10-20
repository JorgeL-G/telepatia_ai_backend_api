from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration using pydantic-settings."""
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    
    # Application Configuration
    app_name: str = "Telepatía AI Backend API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
settings = Settings()
