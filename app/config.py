from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração carregada do ambiente; valores locais não contêm segredos."""

    app_name: str = "API de Agendamento de Consultas"
    app_env: str = "development"
    database_url: str = "sqlite:///./data/appointments.db"
    debug: bool = False
    jwt_secret_key: SecretStr | None = None
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "clinic-scheduling-api"
    jwt_audience: str = "clinic-api"
    access_token_expire_minutes: int = 30
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    rate_limit_window_seconds: int = 60
    rate_limit_default_requests: int = 120
    rate_limit_login_requests: int = 5
    rate_limit_client_token_requests: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
