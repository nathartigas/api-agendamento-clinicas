from datetime import date, datetime, time, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlmodel import Session, select

from app.database.session import get_session
from app.models import Appointment, AppointmentStatus, Professional
from app.schemas.auth import Principal
from app.schemas.availability import AvailabilityRead
from app.security.authentication import get_current_service

router = APIRouter(prefix="/availability", tags=["disponibilidade M2M"])
SessionDependency = Annotated[Session, Depends(get_session)]
ServicePrincipal = Annotated[
    Principal,
    Security(get_current_service, scopes=["availability:read"]),
]


@router.get("", response_model=AvailabilityRead)
def get_availability(
    session: SessionDependency,
    principal: ServicePrincipal,
    professional_id: Annotated[UUID, Query()],
    target_date: Annotated[date, Query(alias="date")],
) -> AvailabilityRead:
    del principal
    if session.get(Professional, professional_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado",
        )
    start = datetime.combine(target_date, time(hour=8))
    end = datetime.combine(target_date, time(hour=18))
    statement = select(Appointment.scheduled_at).where(
        Appointment.professional_id == professional_id,
        Appointment.scheduled_at >= start,
        Appointment.scheduled_at < end,
        Appointment.status != AppointmentStatus.cancelled,
    )
    occupied = {value.replace(tzinfo=None) for value in session.exec(statement).all()}
    slots: list[datetime] = []
    current = start
    while current < end:
        if current not in occupied:
            slots.append(current)
        current += timedelta(minutes=30)
    return AvailabilityRead(
        date=target_date,
        professional_id=professional_id,
        available_slots=slots,
    )
