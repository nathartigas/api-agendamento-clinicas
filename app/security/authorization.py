from collections.abc import Callable
from uuid import UUID

from fastapi import HTTPException, status

from app.models import Appointment, UserRole
from app.schemas.auth import Principal

ROLE_SCOPES: dict[UserRole, set[str]] = {
    UserRole.receptionist: {"appointments:read"},
    UserRole.professional: {"appointments:read", "appointments:write"},
    UserRole.admin: {"appointments:read", "admin:read"},
}


def professional_id_for(principal: Principal) -> UUID | None:
    if principal.role != UserRole.professional.value:
        return None
    if principal.professional_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta profissional sem vínculo profissional",
        )
    return UUID(principal.professional_id)


def require_roles(*allowed_roles: UserRole) -> Callable[[Principal], Principal]:
    def authorize(principal: Principal) -> Principal:
        if principal.role not in {role.value for role in allowed_roles}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Papel insuficiente")
        if principal.role == UserRole.admin.value and not principal.mfa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA administrativo exigido",
            )
        return principal

    return authorize


def authorize_create(principal: Principal, professional_id: str) -> None:
    require_roles(UserRole.professional)(principal)
    is_other_professional = (
        principal.role == UserRole.professional.value
        and principal.professional_id != professional_id
    )
    if is_other_professional:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profissional só pode criar consultas próprias",
        )


def authorize_appointment(principal: Principal, appointment: Appointment, *, write: bool) -> None:
    if principal.role == UserRole.admin.value:
        require_roles(UserRole.admin)(principal)
        if write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrador não gerencia consultas clínicas",
            )
        return
    if principal.role == UserRole.receptionist.value and not write:
        return
    if (
        principal.role == UserRole.professional.value
        and principal.professional_id == str(appointment.professional_id)
    ):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso ao recurso negado")
