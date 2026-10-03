from fastapi.testclient import TestClient


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"].startswith("max-age=31536000")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cross-Origin-Embedder-Policy"] == "require-corp"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert response.headers["Permissions-Policy"].startswith("camera=()")
    assert response.headers["Cache-Control"] == "no-store, max-age=0"


def test_swagger_assets_are_versioned_and_have_sri(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui-dist@5.17.14" in response.text
    assert response.text.count('integrity="sha384-') == 2
    assert 'crossorigin="anonymous"' in response.text
    assert "<script>" not in response.text


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
