from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field("User Service", description="Human-friendly service name", alias="APP_NAME")
    mongodb_uri: str = Field(..., description="MongoDB connection URI", alias="MONGODB_URI")
    mongodb_db: str = Field("users_db", description="Database name", alias="MONGODB_DB")
    mongodb_collection: str = Field("users", description="Collection to store users", alias="MONGODB_COLLECTION")


@lru_cache
def get_settings() -> Settings:
    return Settings()
