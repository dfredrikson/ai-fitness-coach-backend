"""
AI Fitness Coach - Configuration Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "AI Fitness Coach"
    secret_key: str = "change-this-secret-key-in-production"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./ai_coach.db"
    
    # JWT
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"
    
    # Strava
    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_redirect_uri: str = "http://localhost:8000/api/v1/strava/callback"
    strava_auth_url: str = "https://www.strava.com/oauth/authorize"
    strava_token_url: str = "https://www.strava.com/oauth/token"
    strava_api_url: str = "https://www.strava.com/api/v3"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    # Frontend
    frontend_url: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
