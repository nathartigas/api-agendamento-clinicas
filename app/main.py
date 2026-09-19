from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.engine import create_db_and_tables
from app.routes import admin, appointments, auth, availability, health, reception
from app.security.middleware import (
    JWTContextMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API REST para agendamento seguro de consultas médicas.",
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(
    RateLimitMiddleware,
    window_seconds=settings.rate_limit_window_seconds,
    default_limit=settings.rate_limit_default_requests,
    login_limit=settings.rate_limit_login_requests,
    client_token_limit=settings.rate_limit_client_token_requests,
)
app.add_middleware(JWTContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(availability.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(reception.router)
