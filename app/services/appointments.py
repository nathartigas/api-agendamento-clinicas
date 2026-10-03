from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlmodel import Session, select

from app.models import Appointment, AppointmentStatus, Patient, Professional
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def _require_related_records(session: Session, patient_id: UUID, professional_id: UUID) -> None:
    if session.get(Patient, patient_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    if session.get(Professional, professional_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado",
        )


def _ensure_slot_available(
    session: Session,
    *,
    patient_id: UUID,
    professional_id: UUID,
    scheduled_at: datetime,
    exclude_appointment_id: UUID | None = None,
) -> None:
    statement = select(Appointment).where(
        Appointment.scheduled_at == scheduled_at,
        Appointment.status != AppointmentStatus.cancelled,
        or_(
            Appointment.professional_id == professional_id,
            Appointment.patient_id == patient_id,
        ),
    )
    if exclude_appointment_id is not None:
        statement = statement.where(Appointment.id != exclude_appointment_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horário indisponível para o profissional ou paciente",
        )


def create_appointment(session: Session, payload: AppointmentCreate) -> Appointment:
    _require_related_records(session, payload.patient_id, payload.professional_id)
    _ensure_slot_available(
        session,
        patient_id=payload.patient_id,
        professional_id=payload.professional_id,
        scheduled_at=payload.scheduled_at,
    )
    appointment = Appointment.model_validate(payload)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def list_appointments(
    session: Session,
    offset: int,
    limit: int,
    professional_id: UUID | None = None,
) -> list[Appointment]:
    statement = select(Appointment)
    if professional_id is not None:
        statement = statement.where(Appointment.professional_id == professional_id)
    statement = statement.order_by(Appointment.scheduled_at).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def get_appointment_or_404(session: Session, appointment_id: UUID) -> Appointment:
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta não encontrada")
    return appointment


def update_appointment(
    session: Session,
    appointment_id: UUID,
    payload: AppointmentUpdate,
) -> Appointment:
    appointment = get_appointment_or_404(session, appointment_id)
    target_status = payload.status or appointment.status
    if target_status != AppointmentStatus.cancelled:
        _ensure_slot_available(
            session,
            patient_id=appointment.patient_id,
            professional_id=appointment.professional_id,
            scheduled_at=payload.scheduled_at or appointment.scheduled_at,
            exclude_appointment_id=appointment.id,
        )
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(appointment, field_name, value)
    appointment.updated_at = datetime.now(timezone.utc)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def delete_appointment(session: Session, appointment_id: UUID) -> None:
    appointment = get_appointment_or_404(session, appointment_id)
    session.delete(appointment)
    session.commit()
