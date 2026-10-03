from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.models import Appointment, Patient, Professional


def valid_payload(patient: Patient, professional: Professional) -> dict[str, str]:
    return {
        "patient_id": str(patient.id),
        "professional_id": str(professional.id),
        "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "public_notes": "Consulta válida",
    }


def test_invalid_extra_field_never_reaches_service(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    payload = valid_payload(patient, professional)
    payload["created_by"] = "attacker"

    with patch("app.routes.appointments.create_appointment") as create_mock:
        response = client.post("/api/v1/appointments", json=payload, headers=auth_headers)

    assert response.status_code == 422
    create_mock.assert_not_called()


def test_update_authorizes_before_calling_service(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    appointment = Appointment(
        patient_id=patient.id,
        professional_id=professional.id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    call_order: list[str] = []

    with (
        patch(
            "app.routes.appointments.get_appointment_or_404",
            return_value=appointment,
        ),
        patch(
            "app.routes.appointments.authorize_appointment",
            side_effect=lambda *args, **kwargs: call_order.append("authorize"),
        ) as authorize_mock,
        patch(
            "app.routes.appointments.update_appointment",
            side_effect=lambda *args, **kwargs: (call_order.append("update"), appointment)[1],
        ) as update_mock,
    ):
        response = client.patch(
            f"/api/v1/appointments/{appointment.id}",
            json={"status": "confirmed"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert call_order == ["authorize", "update"]
    authorize_mock.assert_called_once()
    update_mock.assert_called_once()


def test_denied_authorization_prevents_update_service(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    appointment = Appointment(
        patient_id=patient.id,
        professional_id=professional.id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
    )

    with (
        patch(
            "app.routes.appointments.get_appointment_or_404",
            return_value=appointment,
        ),
        patch(
            "app.routes.appointments.authorize_appointment",
            side_effect=HTTPException(status_code=403, detail="Acesso negado"),
        ),
        patch("app.routes.appointments.update_appointment") as update_mock,
    ):
        response = client.patch(
            f"/api/v1/appointments/{appointment.id}",
            json={"status": "confirmed"},
            headers=auth_headers,
        )

    assert response.status_code == 403
    update_mock.assert_not_called()
