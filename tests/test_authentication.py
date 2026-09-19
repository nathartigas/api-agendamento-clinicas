from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import OAuthClient, User
from tests.conftest import ADMIN_MFA_CODE, USER_PASSWORD


def test_admin_login_requires_mfa(client: TestClient, admin_user: User) -> None:
    without_mfa = client.post(
        "/api/v1/auth/token",
        data={
            "username": admin_user.username,
            "password": USER_PASSWORD,
            "grant_type": "password",
        },
    )
    assert without_mfa.status_code == 401

    with_mfa = client.post(
        "/api/v1/auth/token",
        data={
            "username": admin_user.username,
            "password": USER_PASSWORD,
            "grant_type": "password",
            "mfa_code": ADMIN_MFA_CODE,
        },
    )
    assert with_mfa.status_code == 200
    assert with_mfa.json()["token_type"] == "bearer"
    assert "admin:read" in with_mfa.json()["scope"]


def test_invalid_password_is_rejected(client: TestClient, professional_user: User) -> None:
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": professional_user.username,
            "password": "IncorrectPassword!",
            "grant_type": "password",
        },
    )
    assert response.status_code == 401


def test_login_rate_limit_returns_429(client: TestClient, professional_user: User) -> None:
    request_data = {
        "username": professional_user.username,
        "password": "IncorrectPassword!",
        "grant_type": "password",
    }
    for _ in range(5):
        assert client.post("/api/v1/auth/token", data=request_data).status_code == 401

    blocked = client.post("/api/v1/auth/token", data=request_data)

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


def test_client_token_rate_limit_returns_429(client: TestClient) -> None:
    request_data = {
        "grant_type": "client_credentials",
        "scope": "availability:read",
    }
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/client-token",
            data=request_data,
            auth=("unknown-client", "IncorrectSecret123!"),
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/v1/auth/client-token",
        data=request_data,
        auth=("unknown-client", "IncorrectSecret123!"),
    )

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


def test_username_sql_injection_payload_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "' OR 1=1 --",
            "password": "IncorrectPassword!",
            "grant_type": "password",
        },
    )
    assert response.status_code == 422


def test_disabled_user_token_is_rejected_immediately(
    client: TestClient,
    session: Session,
    professional_user: User,
    auth_headers: dict[str, str],
) -> None:
    professional_user.is_active = False
    session.add(professional_user)
    session.commit()

    response = client.get("/api/v1/appointments", headers=auth_headers)

    assert response.status_code == 401


def test_disabled_service_token_is_rejected_immediately(
    client: TestClient,
    session: Session,
    oauth_client: OAuthClient,
    service_headers: dict[str, str],
) -> None:
    oauth_client.is_active = False
    session.add(oauth_client)
    session.commit()

    response = client.get(
        "/api/v1/availability",
        params={"professional_id": "00000000-0000-0000-0000-000000000000", "date": "2026-09-19"},
        headers=service_headers,
    )

    assert response.status_code == 401
