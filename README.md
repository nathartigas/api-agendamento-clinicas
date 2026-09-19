# API de Agendamento de Consultas — Nathalia Artigas

Assessment DR2: API FastAPI modular para pacientes, profissionais de saúde e consultas.

## Etapa 1

Esta versão implementa a fundação dos Exercícios 1, 2 e 11:

- aplicação organizada em `routes`, `models`, `schemas`, `services` e `database`;
- CRUD REST de consultas via `APIRouter`;
- SQLModel com sessão injetada por dependência;
- configuração por `BaseSettings` e `.env.example` sem credenciais reais;
- schemas Pydantic de entrada e saída com `extra="forbid"`;
- `response_model` sem campos internos de auditoria;
- página HTML com herança Jinja2 e autoescape explícito;
- testes pytest para caminho feliz, mass assignment e stored XSS.

> Esta seção registra a fundação da etapa 1. Autenticação e ownership foram incorporados na etapa
> 3; os controles HTTP e a auditoria OWASP foram incorporados na etapa 4.

## Ambiente isolado

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

## Executar

```bash
uvicorn app.main:app --reload
```

Documentação OpenAPI: `http://127.0.0.1:8000/docs`.

## Testar

```bash
pytest -q
```

## Rotas desta etapa

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/health` | Verificação de saúde |
| POST | `/api/v1/appointments` | Criar consulta |
| GET | `/api/v1/appointments` | Listar consultas |
| GET | `/api/v1/appointments/{id}` | Consultar por ID |
| PATCH | `/api/v1/appointments/{id}` | Atualizar consulta |
| DELETE | `/api/v1/appointments/{id}` | Excluir consulta |
| GET | `/reception/schedule/today` | Agenda HTML do dia |

Pacientes e profissionais usados por uma consulta devem existir previamente. A criação desses
recursos e a autenticação serão incorporadas nas próximas etapas do Assessment.

## Etapa 2 — documentação de segurança

Os exercícios 3, 4 e 5 estão documentados em:

- `docs/cia_frameworks.md`;
- `docs/dfd.md`;
- `docs/misuse_cases.md`;
- `docs/matriz_stride.md`;
- `docs/arquitetura_seguranca.md`;
- `docs/threat_model.md`;
- `SECURITY.md`.

Os documentos diferenciam controles implementados, controles planejados e questões abertas. A
etapa 3 atualizou o threat model após implementar autenticação e autorização por recurso; a versão
continua local até que hardening, pipeline e auditoria final sejam concluídos.

## Etapa 3 — autenticação e integração M2M

Os Exercícios 6 e 7 adicionam:

- OAuth2PasswordBearer e JWT com expiração, issuer e audience;
- senhas e códigos MFA armazenados com bcrypt;
- RBAC combinado com ownership;
- MFA simulado obrigatório para administradores;
- OAuth 2.0 Client Credentials para o laboratório;
- escopo `availability:read` e tokens de serviço separados de tokens humanos.

Depois de copiar `.env.example` para `.env`, substitua todos os placeholders por valores locais.
Para criar usuários e o cliente de demonstração:

```bash
python -m scripts.seed_demo
```

Exemplo de token humano:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=professional.demo&password=SENHA_LOCAL&grant_type=password'
```

Exemplo de Client Credentials:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/client-token \
  -u 'laboratory-demo:SEGREDO_LOCAL' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&scope=availability:read'
```

As decisões e limitações estão em `docs/autenticacao_autorizacao.md`.

## Etapa 4 — auditoria OWASP e hardening

Os Exercícios 8, 9 e 10 adicionam:

- análise e demonstrações de BOLA, autenticação, consumo de recursos, configuração insegura,
  mass assignment, stored XSS e SQL injection;
- rate limiting central com políticas próprias para login humano e Client Credentials;
- revogação imediata de tokens quando usuário ou cliente é desativado;
- allowlist CORS e headers HSTS, CSP, anti-frame, `nosniff` e referrer;
- validação de notas em POST e PATCH, mantendo autoescape como defesa em profundidade;
- testes de regressão para cada correção.

Consulte `docs/owasp_vulnerabilidades.md`, `docs/hardening_http.md` e
`docs/evidencias/etapa_4.md`. A evidência da varredura antes das correções permanece em
`docs/evidencias/security_scan_before/`.

## Etapa 5 — pipeline DevSecOps

O Exercício 12 adiciona um workflow GitHub Actions com testes e cobertura, SAST Bandit, análise de
dependências Trivy, DAST passivo OWASP ZAP e um security gate agregador. A política bloqueia
alta/crítica, achados médios de SAST com confiança suficiente e qualquer risco de negócio que
permita acesso indevido a dados de saúde.

A justificativa das fases está em `docs/devsecops_pipeline.md`, a priorização em
`docs/cvss_priorizacao.md`, a rastreabilidade dos testes em
`docs/estrategia_testes_seguranca.md` e as evidências em `docs/evidencias/etapa_5.md`.
