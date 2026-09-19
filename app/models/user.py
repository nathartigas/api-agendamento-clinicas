from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    receptionist = "receptionist"
    professional = "professional"
    admin = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=3, max_length=64, unique=True, index=True)
    hashed_password: str = Field(max_length=128)
    role: UserRole = Field(index=True)
    professional_id: UUID | None = Field(default=None, foreign_key="professionals.id", index=True)
    is_active: bool = Field(default=True)
    mfa_enabled: bool = Field(default=False)
    mfa_code_hash: str | None = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OAuthClient(SQLModel, table=True):
    __tablename__ = "oauth_clients"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    client_id: str = Field(min_length=3, max_length=80, unique=True, index=True)
    client_secret_hash: str = Field(max_length=128)
    allowed_scopes: str = Field(default="availability:read", max_length=300)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
