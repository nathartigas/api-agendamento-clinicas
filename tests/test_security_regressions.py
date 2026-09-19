from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Appointment, Patient, Professional, User
from app.security.jwt import create_access_token


def test_professional_list_is_filtered_by_ownership(
    client: TestClient,
    session: Session,
    sample_people: tuple[Patient, Professional],
    professional_user: User,
    auth_headers: dict[str, str],
) -> None:
    patient, own_professional = sample_people
    other_professional = Professional(
        full_name="Dra. Outra Pessoa",
        council_registration="CRM-RJ-54321",
    )
    session.add(other_professional)
    session.commit()
    session.refresh(other_professional)
    session.add_all(
        [
            Appointment(
                patient_id=patient.id,
                professional_id=own_professional.id,
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            ),
            Appointment(
                patient_id=patient.id,
                professional_id=other_professional.id,
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=2),
            ),
        ]
    )
    session.commit()

    response = client.get("/api/v1/appointments", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["professional_id"] == str(professional_user.professional_id)


def test_signed_token_with_stale_role_claim_is_rejected(
    client: TestClient,
    professional_user: User,
) -> None:
    token, _ = create_access_token(
        subject=str(professional_user.id),
        token_type="user",
        scopes={"appointments:read"},
        extra_claims={
            "role": "admin",
            "professional_id": str(professional_user.professional_id),
            "mfa": True,
        },
    )

    response = client.get(
        "/api/v1/appointments",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_pagination_above_resource_budget_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/appointments?limit=101", headers=auth_headers)

    assert response.status_code == 422


def test_naive_datetime_is_rejected(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    response = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "professional_id": str(professional.id),
            "scheduled_at": "2026-09-22T10:00:00",
            "public_notes": "Sem fuso",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
