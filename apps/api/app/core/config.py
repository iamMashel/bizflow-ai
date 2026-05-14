from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BizFlow AI API"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        validation_alias=AliasChoices("CORS_ORIGINS", "BIZFLOW_CORS_ORIGINS"),
    )
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
    supabase_service_role_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "SUPABASE_SERVICE_ROLE_KEY",
            "BIZFLOW_SUPABASE_SERVICE_ROLE_KEY",
        ),
    )
    supabase_storage_bucket: str = Field(
        default="documents",
        validation_alias=AliasChoices(
            "SUPABASE_STORAGE_BUCKET",
            "BIZFLOW_SUPABASE_STORAGE_BUCKET",
        ),
    )
    max_upload_bytes: int = Field(
        default=20 * 1024 * 1024,
        validation_alias=AliasChoices("MAX_UPLOAD_BYTES", "BIZFLOW_MAX_UPLOAD_BYTES"),
    )
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "BIZFLOW_GEMINI_API_KEY"),
    )
    default_embedding_provider: str = Field(
        default="gemini",
        validation_alias=AliasChoices(
            "DEFAULT_EMBEDDING_PROVIDER",
            "BIZFLOW_DEFAULT_EMBEDDING_PROVIDER",
        ),
    )
    default_embedding_model: str = Field(
        default="gemini-embedding-001",
        validation_alias=AliasChoices(
            "DEFAULT_EMBEDDING_MODEL",
            "BIZFLOW_DEFAULT_EMBEDDING_MODEL",
        ),
    )
    embedding_dimensions: int = Field(
        default=3072,
        validation_alias=AliasChoices("EMBEDDING_DIMENSIONS", "BIZFLOW_EMBEDDING_DIMENSIONS"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BIZFLOW_",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
