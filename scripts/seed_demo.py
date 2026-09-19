import os

from dotenv import load_dotenv
from sqlmodel import Session, select

from app.database.engine import create_db_and_tables, engine
from app.models import OAuthClient, Patient, Professional, User, UserRole
from app.security.passwords import hash_secret


def required_secret(name: str, minimum: int) -> str:
    value = os.getenv(name)
    if value is None or value.startswith("replace-") or len(value) < minimum:
        raise RuntimeError(f"Defina {name} no .env com pelo menos {minimum} caracteres")
    return value


def add_if_missing(session: Session, model, key_field, key_value, instance) -> None:
    existing = session.exec(select(model).where(key_field == key_value)).first()
    if existing is None:
        session.add(instance)


def main() -> None:
    load_dotenv()
    admin_password = required_secret("SEED_ADMIN_PASSWORD", 12)
    professional_password = required_secret("SEED_PROFESSIONAL_PASSWORD", 12)
    reception_password = required_secret("SEED_RECEPTION_PASSWORD", 12)
    client_secret = required_secret("SEED_LAB_CLIENT_SECRET", 16)
    mfa_code = required_secret("SEED_ADMIN_MFA_CODE", 6)
    if not (len(mfa_code) == 6 and mfa_code.isdigit()):
        raise RuntimeError("SEED_ADMIN_MFA_CODE deve conter exatamente seis dígitos")

    create_db_and_tables()
    with Session(engine) as session:
        professional = session.exec(
            select(Professional).where(Professional.council_registration == "CRM-RJ-DEMO-01")
        ).first()
        if professional is None:
            professional = Professional(
                full_name="Dra. Ana Souza",
                council_registration="CRM-RJ-DEMO-01",
            )
            session.add(professional)
            session.flush()

        add_if_missing(
            session,
            Patient,
            Patient.document_hash,
            "demo-document-hash-not-a-real-document",
            Patient(
                full_name="Paciente Demonstração",
                document_hash="demo-document-hash-not-a-real-document",
            ),
        )
        add_if_missing(
            session,
            User,
            User.username,
            "admin.demo",
            User(
                username="admin.demo",
                hashed_password=hash_secret(admin_password),
                role=UserRole.admin,
                mfa_enabled=True,
                mfa_code_hash=hash_secret(mfa_code),
            ),
        )
        add_if_missing(
            session,
            User,
            User.username,
            "professional.demo",
            User(
                username="professional.demo",
                hashed_password=hash_secret(professional_password),
                role=UserRole.professional,
                professional_id=professional.id,
            ),
        )
        add_if_missing(
            session,
            User,
            User.username,
            "reception.demo",
            User(
                username="reception.demo",
                hashed_password=hash_secret(reception_password),
                role=UserRole.receptionist,
            ),
        )
        add_if_missing(
            session,
            OAuthClient,
            OAuthClient.client_id,
            "laboratory-demo",
            OAuthClient(
                client_id="laboratory-demo",
                client_secret_hash=hash_secret(client_secret),
                allowed_scopes="availability:read",
            ),
        )
        session.commit()

    print("Dados de demonstração criados sem exibir credenciais.")


if __name__ == "__main__":
    main()
