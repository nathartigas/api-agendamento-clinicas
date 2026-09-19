from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Professional(SQLModel, table=True):
    __tablename__ = "professionals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    full_name: str = Field(min_length=3, max_length=120, index=True)
    council_registration: str = Field(max_length=30, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

