import os
from collections.abc import Generator
from typing import Any

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key-with-at-least-32-characters")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database.session import get_session
from app.main import app
from app.models import OAuthClient, Patient, Professional, User, UserRole
from app.security.middleware import rate_limiter
from app.security.passwords import hash_secret

USER_PASSWORD = "StrongTestPassword123!"
ADMIN_MFA_CODE = "123456"
CLIENT_SECRET = "LaboratorySecret123!"


@pytest.fixture(autouse=True)
def reset_rate_limits() -> Generator[None, None, None]:
    rate_limiter.clear()
    yield
    rate_limiter.clear()


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as test_session:
        yield test_session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def sample_people(session: Session) -> tuple[Patient, Professional]:
    patient = Patient(full_name="Maria da Silva", document_hash="sha256-patient-test")
    professional = Professional(
        full_name="Dra. Ana Souza",
        council_registration="CRM-RJ-12345",
    )
    session.add(patient)
    session.add(professional)
    session.commit()
    session.refresh(patient)
    session.refresh(professional)
    return patient, professional


@pytest.fixture
def professional_user(
    session: Session,
    sample_people: tuple[Patient, Professional],
) -> User:
    _, professional = sample_people
    user = User(
        username="doctor.one",
        hashed_password=hash_secret(USER_PASSWORD),
        role=UserRole.professional,
        professional_id=professional.id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def receptionist_user(session: Session) -> User:
    user = User(
        username="reception.one",
        hashed_password=hash_secret(USER_PASSWORD),
        role=UserRole.receptionist,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_user(session: Session) -> User:
    user = User(
        username="admin.one",
        hashed_password=hash_secret(USER_PASSWORD),
        role=UserRole.admin,
        mfa_enabled=True,
        mfa_code_hash=hash_secret(ADMIN_MFA_CODE),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def oauth_client(session: Session) -> OAuthClient:
    client = OAuthClient(
        client_id="laboratory-partner",
        client_secret_hash=hash_secret(CLIENT_SECRET),
        allowed_scopes="availability:read",
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login_headers(
    client: TestClient,
    username: str,
    *,
    mfa_code: str | None = None,
) -> dict[str, str]:
    data: dict[str, Any] = {
        "username": username,
        "password": USER_PASSWORD,
        "grant_type": "password",
    }
    if mfa_code:
        data["mfa_code"] = mfa_code
    response = client.post("/api/v1/auth/token", data=data)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client: TestClient, professional_user: User) -> dict[str, str]:
    return login_headers(client, professional_user.username)


@pytest.fixture
def receptionist_headers(client: TestClient, receptionist_user: User) -> dict[str, str]:
    return login_headers(client, receptionist_user.username)


@pytest.fixture
def admin_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    return login_headers(client, admin_user.username, mfa_code=ADMIN_MFA_CODE)


@pytest.fixture
def service_headers(client: TestClient, oauth_client: OAuthClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/client-token",
        data={
            "grant_type": "client_credentials",
            "scope": "availability:read",
        },
        auth=(oauth_client.client_id, CLIENT_SECRET),
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
