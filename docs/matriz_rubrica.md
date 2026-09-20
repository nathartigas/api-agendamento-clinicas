# Matriz de atendimento da rubrica

**Autora:** Nathalia Artigas  
**Escopo verificado:** 24 critérios da rubrica do Assessment DR2  
**Resultado da revisão:** 24/24 critérios demonstrados por código, teste e/ou evidência reproduzível

Esta matriz funciona como índice para o avaliador. “Atendido” significa que existe implementação
ou justificativa escrita diretamente verificável; não significa que os riscos de produção tenham
sido aceitos. A decisão de produção continua bloqueada no relatório final.

## 1. FastAPI e fundamentos de segurança

| ID | Critério da rubrica | Estado | Evidência objetiva | Como reproduzir/verificar |
|---|---|---|---|---|
| R01 | Ambiente virtual, Uvicorn, resposta de rotas e módulos `routes`, `models`, `database` | Atendido | `README.md`, estrutura `app/`, `docs/evidencias/validacao_http_final.txt` | Criar `.venv`, instalar dependências, executar `uvicorn app.main:app` e consultar `/health`, `/docs` e `/openapi.json`. |
| R02 | `response_model` controla os campos expostos | Atendido | `AppointmentRead`; `response_model` em POST/GET/PATCH; `AvailabilityRead`, `UserRead`, `TokenResponse` | `tests/test_openapi_security.py` e `tests/test_appointments.py`. |
| R03 | Justificativa do risco sem `response_model` | Atendido | `docs/cia_frameworks.md`, seção Confidencialidade | O texto explica vazamento silencioso de auditoria, autoria e metadados ao serializar modelos persistentes. |
| R04 | Jinja2 com herança e autoescape contra XSS | Atendido | `base.html`, `daily_schedule.html`, autoescape em `app/routes/reception.py` | `test_daily_schedule_escapes_stored_xss`; CSS externo compatível com CSP. |
| R05 | Tríade CIA e OWASP/NIST/MITRE ligados a controles | Atendido | `docs/cia_frameworks.md` | Conferir classificação dos ativos e tabela de mapeamento dos frameworks. |
| R06 | DFD, trust boundaries e fluxos sensíveis | Atendido | `docs/dfd.md` | Diagrama Mermaid, F1-F12 e TB-1-TB-4 identificam dados de pacientes. |

## 2. Threat modeling, JWT e OAuth

| ID | Critério da rubrica | Estado | Evidência objetiva | Como reproduzir/verificar |
|---|---|---|---|---|
| R07 | Misuse cases reais da aplicação | Atendido | `docs/misuse_cases.md` | MC-01 a MC-10 cobrem BOLA, mass assignment, XSS, DoS, M2M e banco. |
| R08 | STRIDE e threat model com ativos, superfícies e mitigações | Atendido | `docs/matriz_stride.md`, `docs/threat_model.md` | Sete componentes recebem as seis categorias; TM-01 a TM-10 são rastreáveis. |
| R09 | Fronteiras e vetores nos três eixos de API | Atendido | `docs/arquitetura_seguranca.md` | Seções específicas de design, implementação e infraestrutura. |
| R10 | OAuth2PasswordBearer, bcrypt e ownership | Atendido | `authentication.py`, `passwords.py`, `authorization.py` | `test_professional_cannot_access_another_professionals_appointment` retorna 403. |
| R11 | JWT expirável, MFA e escolha RBAC/ABAC/recurso | Atendido | `jwt.py`, `auth.py`, `docs/autenticacao_autorizacao.md` | `test_admin_login_requires_mfa`; texto justifica RBAC + ownership + atributos. |
| R12 | Fluxo M2M, escopos e claims distintos | Atendido | Client Credentials, `token_type=service`, `client_id`, `availability:read` | `tests/test_m2m.py` e teste de negação do token de serviço no CRUD humano. |

## 3. OWASP e controles defensivos

| ID | Critério da rubrica | Estado | Evidência objetiva | Como reproduzir/verificar |
|---|---|---|---|---|
| R13 | Três ou mais categorias OWASP identificadas por leitura de código | Atendido | `docs/owasp_vulnerabilidades.md` | API1, API2, API3, API4, API8 e A03 estão correlacionadas a fluxos reais. |
| R14 | BOLA corrigida com ownership central | Atendido | `authorize_appointment`, `authorize_create`, filtro de listagem | Testes de GET cruzado, listagem filtrada, PATCH negado e ordem autorização -> mutação. |
| R15 | Whitelist/regex e `extra='forbid'` | Atendido | `SAFE_NOTES_PATTERN`, forms de autenticação e schemas fechados | Testes de XSS, SQL payload, campo extra e auditoria OAS-06. |
| R16 | Stored XSS corrigido com autoescape | Atendido | autoescape explícito, template sem `safe`, CSP | Teste persiste `<script>` diretamente e confirma saída codificada. |
| R17 | CORS, HSTS, X-Frame, nosniff e rate limiting diferenciado | Atendido | `SecurityHeadersMiddleware`, `RateLimitMiddleware`, `CORSMiddleware` | `tests/test_http_security.py` e `tests/test_authentication.py`. |
| R18 | SQLModel, queries parametrizadas e `BaseSettings`/`.env` | Atendido | `app/database/`, `app/services/appointments.py`, `app/config.py`, `.env.example` | Nenhum `.env`, banco ou segredo real é rastreado pelo Git. |

## 4. DevSecOps, ZAP, testes e capstone

| ID | Critério da rubrica | Estado | Evidência objetiva | Como reproduzir/verificar |
|---|---|---|---|---|
| R19 | Fase do SDLC para SAST, DAST, SCA e IAST | Atendido | `docs/devsecops_pipeline.md` | Tabela explica momento, implementação e justificativa das quatro técnicas. |
| R20 | Priorização CVSS e impacto de negócio | Atendido | `docs/cvss_priorizacao.md` | Scores/vetores, efeito em dados de saúde e decisão de gate por vulnerabilidade. |
| R21 | Security gate justificado e impedindo merge | Atendido | workflow, `security_gate.py`, ruleset ativo e PR #3 | Branch `main` exige PR atualizado e check obrigatório `Security gate`; cinco checks verdes. |
| R22 | Estratégia rastreável ao threat model e pytest expandido | Atendido | `docs/estrategia_testes_seguranca.md` | TM-01, 02, 03, 04, 05, 08, 09, 10 e revogação/claims possuem testes. |
| R23 | ZAP passivo, interpretação, OWASP, correção, residual e deploy | Atendido | ZAP antes/depois e `docs/relatorio_final_rastreabilidade.md` | Inicial: 2 médios, 5 baixos; final: nenhum alto/médio/baixo; produção bloqueada pelos residuais. |
| R24 | Pytest com mocking, entradas/autorização e auditoria OpenAPI | Atendido | `tests/test_mocked_security.py`, `tests/test_openapi_security.py`, `scripts/audit_openapi.py` | 34 testes, 94,64% de cobertura e OpenAPI 6/6. |

## Evidência operacional final

- Pull Request: https://github.com/nathartigas/api-agendamento-clinicas/pull/3
- Pipeline com cinco checks aprovados: https://github.com/nathartigas/api-agendamento-clinicas/actions/runs/35517662287
- Regras da `main`: PR obrigatório, branch atualizada, bloqueio de exclusão/force push e check
  obrigatório `Security gate`.
- ZAP inicial: `docs/evidencias/zap_before_hardening/`.
- ZAP final: `docs/evidencias/zap/`.
- Relatório técnico: `docs/relatorio_tecnico_final.pdf`.
- Roteiro de demonstração: `docs/roteiro_video.md`.

## Itens externos ao código

O único item que depende da autora é gravar e publicar o vídeo de até cinco minutos como não
listado e substituir o conteúdo de `VIDEO_LINK.txt` pela URL. O merge do PR também permanece sem
ser executado para preservar a revisão e o gate até o fechamento da entrega.

