from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

from app.config import get_settings


def build_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


settings = get_settings()
if settings.database_url.startswith("sqlite:///./"):
    Path("data").mkdir(parents=True, exist_ok=True)

engine = build_engine(settings.database_url)


def create_db_and_tables(db_engine: Engine = engine) -> None:
    # Importa os modelos antes de criar o metadata.
    from app.models import Appointment, OAuthClient, Patient, Professional, User  # noqa: F401

    SQLModel.metadata.create_all(db_engine)
