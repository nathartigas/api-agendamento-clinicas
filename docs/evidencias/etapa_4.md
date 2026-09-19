# Evidências da etapa 4

Responsável: Nathalia Artigas

## Exercício 8 — identificação e correção de vulnerabilidades

- Matriz e demonstrações: `docs/owasp_vulnerabilidades.md`.
- BOLA histórico corrigido por RBAC + ownership e coberto por teste cruzado.
- Stored XSS bloqueado na entrada e escapado na saída HTML.
- Mass assignment bloqueado por schemas fechados.
- SQL injection mitigado por consultas parametrizadas e allowlist do username.
- Os endpoints que compartilham o mesmo padrão receberam correção central, não apenas o exemplo.

## Exercício 9 — auditoria OWASP

A varredura estática de repositório foi executada em modo sequencial porque esta execução não
tinha autorização para delegação a subagentes. Identificador:
`aeac8413-9e21-431d-8191-2e11f2fe75c2`.

Resultado pré-correção: três findings de alta confiança — alta (tentativas ilimitadas), média
(revogação tardia) e baixa (headers ausentes). Artefatos canônicos preservados:

- `docs/evidencias/security_scan_before/report.md`;
- `docs/evidencias/security_scan_before/findings.json`;
- `docs/evidencias/security_scan_before/coverage.json`;
- `docs/evidencias/security_scan_before/scan-manifest.json`.

A varredura consumiu 3.097.028 tokens medidos: 3.086.469 de entrada, dos quais 3.036.288 em cache,
10.559 de saída e 4.025 de raciocínio.

## Exercício 10 — hardening

- Rate limiting diferenciado para login, Client Credentials e tráfego comum.
- Revogação efetiva por consulta ao estado atual do principal.
- Middleware central de validação inicial do JWT.
- Headers HSTS, CSP, anti-frame, `nosniff` e política de referrer.
- CORS com allowlist explícita.
- Orientações e limites operacionais em `docs/hardening_http.md`.

## Verificação reproduzível

```bash
ruff check .
pytest --cov=app --cov-report=term-missing -q
```

Os testes verificam 403 para BOLA, 422 para XSS e mass assignment, 429 nos dois emissores de
token, 401 após desativação de usuário/cliente, presença dos headers e negação de origem CORS não
autorizada. Resultado final: **22 testes aprovados**, lint sem erros e **94% de cobertura** da
aplicação. Há dois avisos de depreciação em dependências de teste, sem falhas funcionais.
