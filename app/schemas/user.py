from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class UserRead(BaseModel):
    id: UUID
    username: str
    role: UserRole
    professional_id: UUID | None
    is_active: bool
    mfa_enabled: bool

    model_config = ConfigDict(from_attributes=True, extra="forbid")
