from app.main import app
from scripts.audit_openapi import audit_openapi


def test_openapi_security_audit_passes() -> None:
    report = audit_openapi(app.openapi())

    assert report["status"] == "pass", report
    assert report["summary"] == {"checks": 6, "passed": 6, "failed": 0}


def test_openapi_does_not_expose_internal_appointment_fields() -> None:
    schemas = app.openapi()["components"]["schemas"]
    appointment_read = schemas["AppointmentRead"]["properties"]

    assert "internal_audit_note" not in appointment_read
    assert "created_by" not in appointment_read
    assert "created_at" not in appointment_read
