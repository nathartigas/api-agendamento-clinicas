from typing import Literal

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    scope: str

    model_config = ConfigDict(extra="forbid")


class Principal(BaseModel):
    subject: str
    token_type: Literal["user", "service"]
    role: str | None = None
    professional_id: str | None = None
    client_id: str | None = None
    scopes: frozenset[str] = frozenset()
    mfa: bool = False

    model_config = ConfigDict(frozen=True, extra="forbid")
