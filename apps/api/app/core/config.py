from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BizFlow AI API"
    app_version: str = "0.1.0"
    debug: bool = False
    supabase_url: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_URL", "BIZFLOW_SUPABASE_URL"),
    )
    supabase_anon_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_ANON_KEY", "BIZFLOW_SUPABASE_ANON_KEY"),
    )
    supabase_jwt_secret: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_JWT_SECRET", "BIZFLOW_SUPABASE_JWT_SECRET"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BIZFLOW_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
