# Evidências — Etapa 1

## Requisitos atendidos

1. Ambiente isolado: comandos de criação da `.venv` documentados no `README.md`.
2. Modularização: módulos `routes`, `models`, `schemas`, `services` e `database`.
3. Recurso RESTful: CRUD de consultas em `app/routes/appointments.py`.
4. Persistência: SQLModel e sessões por injeção de dependência.
5. Configuração: `BaseSettings` e `.env.example`, sem segredos reais.
6. Saída segura: `AppointmentRead` é o contrato explícito de resposta.
7. Entrada fechada: schemas usam `extra="forbid"`.
8. HTML seguro: herança de `base.html` e autoescape explícito.
9. Testes: caminho feliz, bloqueio de campo interno e stored XSS.

## Evidências reproduzíveis

Execute:

```bash
pytest -q
```

Depois inicie a aplicação:

```bash
uvicorn app.main:app
```

Verifique:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/reception/schedule/today
```

## Resultado da validação em 19/09/2026

```text
Ruff: All checks passed!
Pytest: 4 passed
Cobertura inicial: 96%
GET /health: HTTP 200 {"status":"ok"}
GET /openapi.json: HTTP 200
GET /reception/schedule/today: HTTP 200
```

O teste de ciclo completo cria, lista, altera, exclui e confirma o `404` subsequente de uma
consulta. O ambiente virtual usado na validação foi criado em `.venv`, que está ignorado pelo
controle de versão e será excluído do ZIP final.
