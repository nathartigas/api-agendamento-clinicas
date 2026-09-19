# Evidências — Etapa 3

## Exercícios cobertos

- Exercício 6: OAuth2PasswordBearer, bcrypt, JWT, expiração, MFA, RBAC e ownership.
- Exercício 7: Client Credentials, escopos e claims distintos para M2M.

## Controles implementados

| Controle | Implementação | Teste principal |
|---|---|---|
| Hash bcrypt | `app/security/passwords.py` | Login válido/inválido |
| JWT e expiração | `app/security/jwt.py` | Emissão e uso nos endpoints |
| OAuth2PasswordBearer | `app/security/authentication.py` | CRUD autenticado |
| MFA administrativo | `app/routes/auth.py` | `test_admin_login_requires_mfa` |
| Papel administrativo | `app/routes/admin.py` | `test_non_admin_cannot_access_admin_route` |
| Ownership | `app/security/authorization.py` | Acesso cruzado retorna `403` |
| Client Credentials | `app/routes/auth.py` | Token do laboratório |
| Escopo M2M | `app/routes/availability.py` | Separação entre token humano e serviço |

## Resultado da validação

```text
Ruff: All checks passed!
Pytest: 12 passed
Cobertura: 93%

Validação adicional: o script de seed foi executado contra um banco descartável e a geração do
OpenAPI confirmou sete paths e os schemes `OAuth2PasswordBearer` e `HTTPBasic`.
```

Os avisos emitidos são de depreciação interna da integração `TestClient` da versão instalada e
não representam falha dos testes da aplicação.
