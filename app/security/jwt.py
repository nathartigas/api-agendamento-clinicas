from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from app.config import get_settings


def _secret_key() -> str:
    secret = get_settings().jwt_secret_key
    if secret is None or len(secret.get_secret_value()) < 32:
        raise RuntimeError("JWT_SECRET_KEY deve possuir pelo menos 32 caracteres")
    return secret.get_secret_value()


def create_access_token(
    *,
    subject: str,
    token_type: str,
    scopes: set[str],
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, int]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_in = settings.access_token_expire_minutes * 60
    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": token_type,
        "scope": " ".join(sorted(scopes)),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "jti": str(uuid4()),
    }
    payload.update(extra_claims or {})
    token = jwt.encode(payload, _secret_key(), algorithm=settings.jwt_algorithm)
    return token, expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            _secret_key(),
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={"require": ["sub", "token_type", "scope", "iat", "exp", "iss", "aud", "jti"]},
        )
    except (jwt.PyJWTError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
