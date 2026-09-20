from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

ERROR_SCHEMA = {
    "type": "object",
    "required": ["detail"],
    "properties": {"detail": {"type": "string"}},
    "additionalProperties": False,
}


def _error_response(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/SecurityError"},
            }
        },
    }


def build_secure_openapi(app: FastAPI) -> dict[str, Any]:
    """Documenta respostas produzidas por controles centrais de segurança."""

    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("schemas", {})["SecurityError"] = ERROR_SCHEMA
    for path_item in schema.get("paths", {}).values():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            responses = operation.setdefault("responses", {})
            responses.setdefault("429", _error_response("Limite de requisições excedido"))
            if operation.get("security"):
                responses.setdefault("401", _error_response("Credenciais inválidas"))
                responses.setdefault("403", _error_response("Acesso não autorizado"))
    app.openapi_schema = schema
    return schema
