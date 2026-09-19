from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, Security, status
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate
from app.schemas.auth import Principal
from app.security.authentication import get_current_user
from app.security.authorization import authorize_appointment, authorize_create, professional_id_for
from app.services.appointments import (
    create_appointment,
    delete_appointment,
    get_appointment_or_404,
    list_appointments,
    update_appointment,
)

router = APIRouter(prefix="/appointments", tags=["consultas"])
SessionDependency = Annotated[Session, Depends(get_session)]
ReadPrincipal = Annotated[
    Principal,
    Security(get_current_user, scopes=["appointments:read"]),
]
WritePrincipal = Annotated[
    Principal,
    Security(get_current_user, scopes=["appointments:write"]),
]


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create(payload: AppointmentCreate, session: SessionDependency, principal: WritePrincipal):
    authorize_create(principal, str(payload.professional_id))
    return create_appointment(session, payload)


@router.get("", response_model=list[AppointmentRead])
def list_all(
    session: SessionDependency,
    principal: ReadPrincipal,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    professional_id = professional_id_for(principal)
    return list_appointments(session, offset, limit, professional_id)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_one(appointment_id: UUID, session: SessionDependency, principal: ReadPrincipal):
    appointment = get_appointment_or_404(session, appointment_id)
    authorize_appointment(principal, appointment, write=False)
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update(
    appointment_id: UUID,
    payload: AppointmentUpdate,
    session: SessionDependency,
    principal: WritePrincipal,
):
    appointment = get_appointment_or_404(session, appointment_id)
    authorize_appointment(principal, appointment, write=True)
    return update_appointment(session, appointment_id, payload)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    appointment_id: UUID,
    session: SessionDependency,
    principal: WritePrincipal,
) -> Response:
    appointment = get_appointment_or_404(session, appointment_id)
    authorize_appointment(principal, appointment, write=True)
    delete_appointment(session, appointment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
