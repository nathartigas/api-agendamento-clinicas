from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session

from app.database.session import get_session
from app.models import UserRole
from app.schemas.auth import TokenResponse
from app.security.authentication import authenticate_client, authenticate_user
from app.security.authorization import ROLE_SCOPES
from app.security.jwt import create_access_token
from app.security.passwords import verify_secret

router = APIRouter(prefix="/auth", tags=["autenticação"])
SessionDependency = Annotated[Session, Depends(get_session)]
client_basic = HTTPBasic()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou credencial inválida",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/token", response_model=TokenResponse)
def issue_user_token(
    session: SessionDependency,
    username: Annotated[
        str,
        Form(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9._-]+$"),
    ],
    password: Annotated[str, Form(min_length=8, max_length=72)],
    grant_type: Annotated[str, Form(pattern="^password$")] = "password",
    scope: Annotated[str, Form()] = "",
    mfa_code: Annotated[str | None, Form(pattern="^[0-9]{6}$")] = None,
) -> TokenResponse:
    del grant_type
    user = authenticate_user(session, username, password)
    if user is None:
        raise _unauthorized()
    mfa_verified = False
    if user.role == UserRole.admin:
        if not user.mfa_enabled or not user.mfa_code_hash:
            raise HTTPException(status_code=403, detail="MFA administrativo não configurado")
        if mfa_code is None or not verify_secret(mfa_code, user.mfa_code_hash):
            raise HTTPException(status_code=401, detail="Código MFA inválido")
        mfa_verified = True
    allowed_scopes = ROLE_SCOPES[user.role]
    requested_scopes = set(scope.split()) if scope else allowed_scopes
    if not requested_scopes.issubset(allowed_scopes):
        raise HTTPException(status_code=403, detail="Escopo solicitado não permitido")
    token, expires_in = create_access_token(
        subject=str(user.id),
        token_type="user",
        scopes=requested_scopes,
        extra_claims={
            "role": user.role.value,
            "professional_id": str(user.professional_id) if user.professional_id else None,
            "mfa": mfa_verified,
        },
    )
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        scope=" ".join(sorted(requested_scopes)),
    )


@router.post("/client-token", response_model=TokenResponse)
def issue_client_token(
    session: SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(client_basic)],
    grant_type: Annotated[str, Form(pattern="^client_credentials$")] = "client_credentials",
    scope: Annotated[str, Form()] = "availability:read",
) -> TokenResponse:
    del grant_type
    client = authenticate_client(session, credentials.username, credentials.password)
    if client is None:
        raise _unauthorized()
    allowed_scopes = set(client.allowed_scopes.split())
    requested_scopes = set(scope.split())
    if not requested_scopes or not requested_scopes.issubset(allowed_scopes):
        raise HTTPException(status_code=403, detail="Escopo solicitado não permitido")
    token, expires_in = create_access_token(
        subject=client.client_id,
        token_type="service",
        scopes=requested_scopes,
        extra_claims={"client_id": client.client_id, "mfa": False},
    )
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        scope=" ".join(sorted(requested_scopes)),
    )
