from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel import Session, select

from app.database.session import get_session
from app.models import OAuthClient, User
from app.schemas.auth import Principal
from app.security.authorization import ROLE_SCOPES
from app.security.jwt import decode_access_token
from app.security.passwords import verify_secret

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "appointments:read": "Consultar consultas autorizadas",
        "appointments:write": "Criar e gerenciar consultas autorizadas",
        "admin:read": "Consultar recursos administrativos",
        "availability:read": "Consultar somente horários disponíveis",
    },
)

SessionDependency = Annotated[Session, Depends(get_session)]


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None or not user.is_active or not verify_secret(password, user.hashed_password):
        return None
    return user


def authenticate_client(session: Session, client_id: str, client_secret: str) -> OAuthClient | None:
    client = session.exec(select(OAuthClient).where(OAuthClient.client_id == client_id)).first()
    if (
        client is None
        or not client.is_active
        or not verify_secret(client_secret, client.client_secret_hash)
    ):
        return None
    return client


def get_current_principal(
    security_scopes: SecurityScopes,
    request: Request,
    session: SessionDependency,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Principal:
    payload = request.state.jwt_payload or decode_access_token(token)
    token_scopes = frozenset(payload.get("scope", "").split())
    missing_scopes = set(security_scopes.scopes) - token_scopes
    if missing_scopes:
        required = " ".join(security_scopes.scopes)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Escopo insuficiente",
            headers={"WWW-Authenticate": f'Bearer scope="{required}"'},
        )
    token_type = payload["token_type"]
    if token_type == "user":
        try:
            user_id = UUID(str(payload["sub"]))
        except ValueError as exc:
            raise _invalid_token() from exc
        user = session.get(User, user_id)
        if user is None or not user.is_active:
            raise _invalid_token()
        current_scopes = ROLE_SCOPES[user.role]
        expected_professional = str(user.professional_id) if user.professional_id else None
        if (
            payload.get("role") != user.role.value
            or payload.get("professional_id") != expected_professional
            or not token_scopes.issubset(current_scopes)
        ):
            raise _invalid_token()
        return Principal(
            subject=str(user.id),
            token_type="user",
            role=user.role.value,
            professional_id=expected_professional,
            scopes=token_scopes,
            mfa=bool(payload.get("mfa", False)),
        )
    if token_type == "service":
        client_id = str(payload.get("client_id", ""))
        client = session.exec(select(OAuthClient).where(OAuthClient.client_id == client_id)).first()
        if client is None or not client.is_active or payload["sub"] != client.client_id:
            raise _invalid_token()
        if not token_scopes.issubset(set(client.allowed_scopes.split())):
            raise _invalid_token()
        return Principal(
            subject=client.client_id,
            token_type="service",
            client_id=client.client_id,
            scopes=token_scopes,
        )
    raise _invalid_token()


def _invalid_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    principal: Annotated[Principal, Security(get_current_principal)],
) -> Principal:
    if principal.token_type != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de usuário exigido",
        )
    return principal


def get_current_service(
    principal: Annotated[Principal, Security(get_current_principal)],
) -> Principal:
    if principal.token_type != "service":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de serviço exigido",
        )
    return principal
