from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/ca_support"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Email
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    
    # Slack
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# グローバル設定インスタンス
settings = Settings() 