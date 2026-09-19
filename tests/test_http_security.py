from fastapi.testclient import TestClient


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"].startswith("max-age=31536000")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Content-Security-Policy"] == (
        "default-src 'self'; frame-ancestors 'none'"
    )


def test_cors_allows_only_configured_origin(client: TestClient) -> None:
    allowed = client.options(
        "/api/v1/appointments",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    denied = client.options(
        "/api/v1/appointments",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_invalid_bearer_token_is_rejected_by_central_middleware(client: TestClient) -> None:
    response = client.get(
        "/api/v1/appointments",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
