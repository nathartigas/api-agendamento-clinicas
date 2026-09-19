from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AvailabilityRead(BaseModel):
    date: date
    professional_id: UUID
    available_slots: list[datetime]

    model_config = ConfigDict(extra="forbid")
