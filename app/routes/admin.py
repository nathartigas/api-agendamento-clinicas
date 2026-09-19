from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlmodel import Session, select

from app.database.session import get_session
from app.models import User, UserRole
from app.schemas.auth import Principal
from app.schemas.user import UserRead
from app.security.authentication import get_current_user
from app.security.authorization import require_roles

router = APIRouter(prefix="/admin", tags=["administração"])
SessionDependency = Annotated[Session, Depends(get_session)]
AdminPrincipal = Annotated[Principal, Security(get_current_user, scopes=["admin:read"])]


@router.get("/users", response_model=list[UserRead])
def list_users(session: SessionDependency, principal: AdminPrincipal):
    require_roles(UserRole.admin)(principal)
    return list(session.exec(select(User).order_by(User.username)).all())
