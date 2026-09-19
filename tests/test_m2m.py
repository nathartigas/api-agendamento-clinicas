from datetime import date

from fastapi.testclient import TestClient

from app.models import Patient, Professional


def test_laboratory_can_only_read_availability(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    service_headers: dict[str, str],
) -> None:
    _, professional = sample_people
    response = client.get(
        "/api/v1/availability",
        params={"professional_id": str(professional.id), "date": date.today().isoformat()},
        headers=service_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["professional_id"] == str(professional.id)
    assert len(payload["available_slots"]) == 20
    assert "patient_id" not in payload


def test_human_token_cannot_use_m2m_endpoint(
    client: TestClient,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    _, professional = sample_people
    response = client.get(
        "/api/v1/availability",
        params={"professional_id": str(professional.id), "date": date.today().isoformat()},
        headers=auth_headers,
    )
    assert response.status_code == 403
