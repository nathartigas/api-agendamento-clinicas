import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.appointment import AppointmentStatus

SAFE_NOTES_PATTERN = re.compile(r"^[\w\s.,;:!?()/'-]*$", flags=re.UNICODE)


def validate_safe_notes(value: str | None) -> str | None:
    if value is not None and not SAFE_NOTES_PATTERN.fullmatch(value):
        raise ValueError("public_notes contém caracteres não permitidos")
    return value


class AppointmentCreate(BaseModel):
    patient_id: UUID
    professional_id: UUID
    scheduled_at: datetime
    public_notes: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_at deve conter fuso horário")
        return value

    @field_validator("public_notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return validate_safe_notes(value)


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None
    status: AppointmentStatus | None = None
    public_notes: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("scheduled_at deve conter fuso horário")
        return value

    @field_validator("public_notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return validate_safe_notes(value)


class AppointmentRead(BaseModel):
    """Lista fechada de campos que podem sair pela API."""

    id: UUID
    patient_id: UUID
    professional_id: UUID
    scheduled_at: datetime
    status: AppointmentStatus
    public_notes: str | None

    model_config = ConfigDict(from_attributes=True)
