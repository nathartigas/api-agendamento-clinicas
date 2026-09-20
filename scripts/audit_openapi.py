"""Auditoria reproduzível do contrato OpenAPI da aplicação."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.main import app

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
SENSITIVE_FIELDS = {
    "client_secret_hash",
    "created_by",
    "hashed_password",
    "internal_audit_note",
    "mfa_code_hash",
}


def _result(check_id: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"id": check_id, "status": "pass" if passed else "fail", "evidence": evidence}


def audit_openapi(schema: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    components = schema.get("components", {})
    schemes = components.get("securitySchemes", {})
    oauth = schemes.get("OAuth2PasswordBearer", {})
    password_flow = oauth.get("flows", {}).get("password", {})
    scopes = password_flow.get("scopes", {})
    expected_scopes = {
        "admin:read",
        "appointments:read",
        "appointments:write",
        "availability:read",
    }
    checks.append(
        _result(
            "OAS-01",
            password_flow.get("tokenUrl") == "/api/v1/auth/token",
            "OAuth2 Password aponta para o emissor humano esperado.",
        )
    )
    checks.append(
        _result(
            "OAS-02",
            expected_scopes.issubset(scopes),
            "Escopos humanos, administrativos e M2M estão declarados.",
        )
    )

    protected_operations = []
    missing_security_responses = []
    missing_rate_limit_response = []
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue
            operation_name = f"{method.upper()} {path}"
            responses = operation.get("responses", {})
            if "429" not in responses:
                missing_rate_limit_response.append(operation_name)
            if operation.get("security"):
                protected_operations.append(operation_name)
                if not {"401", "403"}.issubset(responses):
                    missing_security_responses.append(operation_name)
    checks.append(
        _result(
            "OAS-03",
            bool(protected_operations) and not missing_security_responses,
            f"{len(protected_operations)} operações protegidas documentam 401 e 403.",
        )
    )
    checks.append(
        _result(
            "OAS-04",
            not missing_rate_limit_response,
            "Todas as operações públicas documentadas incluem resposta 429.",
        )
    )

    schemas = components.get("schemas", {})
    schema_text = json.dumps(schemas, sort_keys=True)
    leaked_fields = sorted(field for field in SENSITIVE_FIELDS if field in schema_text)
    checks.append(
        _result(
            "OAS-05",
            not leaked_fields,
            f"Campos internos expostos: {leaked_fields or 'nenhum'}.",
        )
    )
    input_schemas = [schemas.get("AppointmentCreate", {}), schemas.get("AppointmentUpdate", {})]
    checks.append(
        _result(
            "OAS-06",
            all(item.get("additionalProperties") is False for item in input_schemas),
            "Schemas de criação e atualização rejeitam propriedades extras.",
        )
    )
    failures = [check for check in checks if check["status"] == "fail"]
    return {
        "title": "Auditoria OpenAPI — API de Agendamento",
        "status": "pass" if not failures else "fail",
        "summary": {
            "checks": len(checks),
            "passed": len(checks) - len(failures),
            "failed": len(failures),
        },
        "checks": checks,
        "observations": [
            "O endpoint /health é intencionalmente excluído do contrato público.",
            "HTTP Basic aparece somente no emissor Client Credentials.",
            "O contrato não substitui testes de ownership, pois OpenAPI não expressa BOLA.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = audit_openapi(app.openapi())
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
