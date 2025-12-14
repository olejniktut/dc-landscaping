import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dc-landscaping-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # App
    APP_NAME: str = "DC Landscaping"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()