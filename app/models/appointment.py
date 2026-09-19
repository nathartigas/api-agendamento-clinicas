from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    patient_id: UUID = Field(foreign_key="patients.id", index=True)
    professional_id: UUID = Field(foreign_key="professionals.id", index=True)
    scheduled_at: datetime = Field(index=True)
    status: AppointmentStatus = Field(default=AppointmentStatus.scheduled, index=True)
    public_notes: str | None = Field(default=None, max_length=500)

    # Campos internos não aparecem em nenhum response model público.
    internal_audit_note: str | None = Field(default=None, max_length=500)
    created_by: str = Field(default="system", max_length=120)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

