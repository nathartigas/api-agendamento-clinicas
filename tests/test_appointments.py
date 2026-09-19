from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.models import Patient, Professional


def appointment_payload(patient: Patient, professional: Professional) -> dict[str, str]:
    return {
        "patient_id": str(patient.id),
        "professional_id": str(professional.id),
        "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "public_notes": "Retorno clínico",
    }


def test_create_and_read_appointment_success(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    response = client.post(
        "/api/v1/appointments",
        json=appointment_payload(patient, professional),
        headers=auth_headers,
    )

    assert response.status_code == 201
    created = response.json()
    assert created["patient_id"] == str(patient.id)
    assert created["status"] == "scheduled"
    assert "internal_audit_note" not in created
    assert "created_by" not in created
    assert "created_at" not in created

    read_response = client.get(f"/api/v1/appointments/{created['id']}", headers=auth_headers)
    assert read_response.status_code == 200
    assert read_response.json() == created


def test_complete_appointment_crud(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    create_response = client.post(
        "/api/v1/appointments",
        json=appointment_payload(patient, professional),
        headers=auth_headers,
    )
    appointment_id = create_response.json()["id"]

    list_response = client.get(
        "/api/v1/appointments?offset=0&limit=10",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [appointment_id]

    update_response = client.patch(
        f"/api/v1/appointments/{appointment_id}",
        json={"status": "confirmed", "public_notes": "Consulta confirmada"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "confirmed"

    delete_response = client.delete(
        f"/api/v1/appointments/{appointment_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers=auth_headers,
    )
    assert missing_response.status_code == 404


def test_rejects_undeclared_input_field(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    payload = appointment_payload(patient, professional)
    payload["internal_audit_note"] = "tentativa de mass assignment"

    response = client.post("/api/v1/appointments", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_rejects_script_markup_in_notes(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    payload = appointment_payload(patient, professional)
    payload["public_notes"] = "<script>alert('xss')</script>"

    response = client.post("/api/v1/appointments", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_update_rejects_script_markup_in_notes(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    created = client.post(
        "/api/v1/appointments",
        json=appointment_payload(patient, professional),
        headers=auth_headers,
    )

    response = client.patch(
        f"/api/v1/appointments/{created.json()['id']}",
        json={"public_notes": "<img src=x onerror=alert(1)>"},
        headers=auth_headers,
    )

    assert response.status_code == 422
