# Estratégia de testes rastreável ao threat model

| Ameaça | Propriedade testada | Evidência pytest |
|---|---|---|
| TM-01 BOLA | Profissional recebe 403 por objeto alheio e a listagem contém apenas objetos próprios | `tests/test_authorization.py`, `tests/test_security_regressions.py` |
| TM-02 CRUD anônimo | OAuth2 rejeita ausência ou token inválido | `tests/test_http_security.py` |
| TM-03 agenda nominal | Página exige papel humano e filtra profissional | `tests/test_templates.py`, regras em `app/routes/reception.py` |
| TM-04 confusão M2M/humano | Token de serviço não entra em CRUD e token humano não entra em disponibilidade | `tests/test_authorization.py`, `tests/test_m2m.py` |
| TM-05 brute force/DoS | Login e Client Credentials retornam 429; paginação acima de 100 retorna 422 | `tests/test_authentication.py`, `tests/test_security_regressions.py` |
| TM-08 stored XSS | POST/PATCH rejeitam markup e dado legado é escapado | `tests/test_appointments.py`, `tests/test_templates.py` |
| TM-09 mass assignment | Campo interno não declarado retorna 422 | `tests/test_appointments.py` |
| TM-10 datas inconsistentes | Data sem timezone retorna 422 | `tests/test_security_regressions.py` |
| Revogação/claims obsoletas | Usuário/cliente inativo e papel divergente recebem 401 | `tests/test_authentication.py`, `tests/test_security_regressions.py` |
| Hardening HTTP | Headers presentes e origem CORS não autorizada não recebe permissão | `tests/test_http_security.py` |
| Security gate | Relatórios sintéticos confirmam limiares Bandit e ZAP | `tests/test_security_gate.py` |
| Ordem de autorização | Mock confirma que autorização ocorre antes da mutação e que negação impede o serviço | `tests/test_mocked_security.py` |
| Contrato OpenAPI | Token URL, escopos, 401/403/429, campos internos e schemas fechados | `tests/test_openapi_security.py`, `scripts/audit_openapi.py` |

Os testes de autorização são deliberadamente baseados em capacidade do atacante, não apenas em
linhas de código: trocar UUID, apresentar tipo de token incorreto, reaproveitar token após mudança
de estado e ampliar o volume da resposta. Assim, uma refatoração pode manter a propriedade de
segurança sem acoplar a suíte à implementação interna.

Resultado final: 34 testes aprovados, 94,64% de cobertura e auditoria OpenAPI com 6/6 controles.
