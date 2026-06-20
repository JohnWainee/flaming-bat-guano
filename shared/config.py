from __future__ import annotations

from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_embedding_dimensions: int = 1536

    # ServiceNow
    snow_instance_url: str = ""
    snow_client_id: Optional[str] = None
    snow_client_secret: Optional[str] = None
    snow_username: Optional[str] = None
    snow_password: Optional[str] = None
    snow_auth_method: Literal["oauth", "basic"] = "basic"
    snow_api_timeout_seconds: int = 30
    snow_max_records_per_page: int = 1000

    # Redis
    redis_url: str = "redis://redis:6379"
    conversation_ttl_seconds: int = 3600

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: Optional[str] = None

    # Email
    email_host: str = ""
    email_port: int = 993
    email_username: str = ""
    email_password: str = ""
    email_use_ssl: bool = True
    email_type: Literal["imap", "ews"] = "imap"
    email_poll_interval_seconds: int = 300
    email_inbox_folder: str = "INBOX"
    email_processed_folder: str = "Processed"

    # Bot Framework (Azure Bot Service)
    microsoft_app_id: str = ""
    microsoft_app_password: str = ""

    # Orchestrator
    orchestrator_url: str = "http://orchestrator:8000"

    # Ingestion
    ingestion_batch_size: int = 50
    ingestion_rate_limit_delay_seconds: float = 0.5


settings = Settings()
