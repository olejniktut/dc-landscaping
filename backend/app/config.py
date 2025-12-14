import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://dcland:dcland123@localhost:3306/dclandscaping"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dc-landscaping-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # App
    APP_NAME: str = "DC Landscaping"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    class Config:
        env_file = ".env"


settings = Settings()
