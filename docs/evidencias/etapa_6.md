# Evidências da etapa 6

Responsável: Nathalia Artigas

## Exercício 13 - capstone

- Pull Request: https://github.com/nathartigas/api-agendamento-clinicas/pull/3
- Pipeline inicial: https://github.com/nathartigas/api-agendamento-clinicas/actions/runs/35468605011
- Pipeline após hardening: https://github.com/nathartigas/api-agendamento-clinicas/actions/runs/35517319082
- Relatório final: `docs/relatorio_final_rastreabilidade.md`
- Matriz das 24 rubricas: `docs/matriz_rubrica.md`
- Validação HTTP com Uvicorn: `docs/evidencias/validacao_http_final.txt`
- Auditoria OpenAPI local: `docs/evidencias/openapi_audit.json`
- Auditoria OpenAPI do pipeline: `docs/evidencias/openapi_audit_pipeline.json`
- ZAP inicial: `docs/evidencias/zap_before_hardening/`
- ZAP após correção: `docs/evidencias/zap/`
- Testes com mocking: `tests/test_mocked_security.py`
- Testes do contrato: `tests/test_openapi_security.py`

## Resultado final

- Ruff: aprovado;
- pytest: 34 testes aprovados;
- cobertura: 94,64%;
- OpenAPI: 6/6 controles aprovados;
- Bandit: aprovado pelo gate;
- Trivy: aprovado pelo gate;
- ZAP antes: 2 médios, 5 baixos e 2 informativos;
- ZAP depois: 0 altos, 0 médios, 0 baixos e 2 informativos;
- Security gate: aprovado.

## Correções guiadas pelo ZAP

A página Swagger passou a usar dependências com versão exata e SRI SHA-384, sem script inline. O
middleware passou a emitir CSP completa, COEP, COOP, CORP, Permissions Policy e prevenção de cache.
Os testes verificam a presença dos headers e as propriedades da página de documentação.

## Decisão

Entrega aprovada para demonstração local e avaliação acadêmica. Produção permanece bloqueada pelos
riscos de infraestrutura e operação enumerados no relatório final.
