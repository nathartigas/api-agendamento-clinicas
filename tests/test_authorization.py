from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Appointment, Patient, Professional, User, UserRole
from app.security.passwords import hash_secret
from tests.conftest import USER_PASSWORD, login_headers


def test_non_admin_cannot_access_admin_route(
    client: TestClient,
    professional_user: User,
    auth_headers: dict[str, str],
) -> None:
    del professional_user
    response = client.get("/api/v1/admin/users", headers=auth_headers)
    assert response.status_code == 403


def test_professional_cannot_access_another_professionals_appointment(
    client: TestClient,
    session: Session,
    sample_people: tuple[Patient, Professional],
    professional_user: User,
) -> None:
    patient, owner_professional = sample_people
    appointment = Appointment(
        patient_id=patient.id,
        professional_id=owner_professional.id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    other_professional = Professional(
        full_name="Dr. Carlos Lima",
        council_registration="CRM-RJ-99999",
    )
    session.add(appointment)
    session.add(other_professional)
    session.commit()
    session.refresh(appointment)
    session.refresh(other_professional)
    other_user = User(
        username="doctor.other",
        hashed_password=hash_secret(USER_PASSWORD),
        role=UserRole.professional,
        professional_id=other_professional.id,
    )
    session.add(other_user)
    session.commit()
    headers = login_headers(client, other_user.username)

    response = client.get(f"/api/v1/appointments/{appointment.id}", headers=headers)

    assert response.status_code == 403
    del professional_user


def test_service_token_cannot_access_human_appointment_routes(
    client: TestClient,
    service_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/appointments", headers=service_headers)
    assert response.status_code == 403


def test_admin_cannot_create_clinical_appointment(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    admin_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    response = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "professional_id": str(professional.id),
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "public_notes": "Admin não deve criar",
        },
        headers=admin_headers,
    )
    assert response.status_code == 403
