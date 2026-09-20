from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Appointment, Patient, Professional


def test_daily_schedule_escapes_stored_xss(
    client: TestClient,
    session: Session,
    sample_people: tuple[Patient, Professional],
    auth_headers: dict[str, str],
) -> None:
    patient, professional = sample_people
    session.add(
        Appointment(
            patient_id=patient.id,
            professional_id=professional.id,
            scheduled_at=datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
            public_notes='<script>alert("xss")</script>',
        )
    )
    session.commit()

    response = client.get("/reception/schedule/today", headers=auth_headers)

    assert response.status_code == 200
    assert '<script>alert("xss")</script>' not in response.text
    assert "&lt;script&gt;" in response.text
    assert '<link rel="stylesheet" href="/static/reception.css">' in response.text
    assert "<style>" not in response.text
