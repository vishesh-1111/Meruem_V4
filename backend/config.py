from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    JWT_SECRET:str
    GOOGLE_OAUTH_CLIENT_ID:str
    GOOGLE_OAUTH_CLIENT_SECRET:str
    GOOGLE_OAUTH_REDIRECT_URI:str

    # DB_HOS = SettingsConfigDict(env_file=".env")
    model_config= SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")



@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't reload .env every request"""
    return Settings()


