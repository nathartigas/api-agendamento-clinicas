from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Security
from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from sqlmodel import Session, select

from app.database.session import get_session
from app.models import Appointment, Patient, Professional, UserRole
from app.schemas.auth import Principal
from app.security.authentication import get_current_user
from app.security.authorization import professional_id_for, require_roles

router = APIRouter(prefix="/reception", tags=["recepção"])
SessionDependency = Annotated[Session, Depends(get_session)]
ReceptionPrincipal = Annotated[
    Principal,
    Security(get_current_user, scopes=["appointments:read"]),
]

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
templates.env.autoescape = select_autoescape(enabled_extensions=("html", "xml"), default=True)


@router.get("/schedule/today")
def daily_schedule(request: Request, session: SessionDependency, principal: ReceptionPrincipal):
    require_roles(UserRole.receptionist, UserRole.professional, UserRole.admin)(principal)
    today = date.today()
    start = datetime.combine(today, time.min)
    end = start + timedelta(days=1)
    statement = (
        select(Appointment, Patient, Professional)
        .join(Patient, Patient.id == Appointment.patient_id)
        .join(Professional, Professional.id == Appointment.professional_id)
        .where(Appointment.scheduled_at >= start, Appointment.scheduled_at < end)
    )
    if principal.role == UserRole.professional.value:
        statement = statement.where(Appointment.professional_id == professional_id_for(principal))
    statement = statement.order_by(Appointment.scheduled_at)
    schedule = [
        {
            "scheduled_at": appointment.scheduled_at,
            "patient_name": patient.full_name,
            "professional_name": professional.full_name,
            "status": appointment.status.value,
            "public_notes": appointment.public_notes,
        }
        for appointment, patient, professional in session.exec(statement).all()
    ]
    return templates.TemplateResponse(
        request=request,
        name="daily_schedule.html",
        context={"schedule": schedule, "today": today},
    )
