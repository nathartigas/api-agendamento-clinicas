# Exercício 3 — CIA e frameworks de referência

## Classificação dos ativos

| Ativo | Classificação | Confidencialidade | Integridade | Disponibilidade |
|---|---|---:|---:|---:|
| Identificação do paciente | Pessoal/LGPD | Alta | Alta | Média |
| Agenda e vínculo paciente–profissional | Dado de saúde inferível | Muito alta | Muito alta | Alta |
| Observação da consulta | Dado de saúde | Muito alta | Muito alta | Média |
| Credenciais e tokens | Segredo de autenticação | Muito alta | Muito alta | Alta |
| Registro profissional | Pessoal/profissional | Média | Alta | Média |
| Trilha de auditoria | Interno restrito | Alta | Muito alta | Média |
| Disponibilidade de horários | Operacional | Baixa quando agregada | Alta | Alta |

O simples vínculo entre uma pessoa e uma clínica ou especialidade pode revelar informação de
saúde. Por isso, `patient_id`, horário, profissional e observação são tratados como conjunto
sensível, ainda que cada campo isolado pareça pouco revelador.

## Confidencialidade

### Controles implementados

- `AppointmentRead` enumera os únicos campos públicos; `internal_audit_note`, `created_by` e
  timestamps internos permanecem fora do contrato (`app/schemas/appointment.py:40`).
- Todas as rotas JSON declaram `response_model` (`app/routes/appointments.py:32`,
  `app/routes/appointments.py:38`, `app/routes/appointments.py:49` e
  `app/routes/appointments.py:56`).
- O Jinja2 possui autoescape explícito (`app/routes/reception.py:24`) e o teste comprova a
  codificação de `<script>` persistido (`tests/test_templates.py:9`).
- O hash do documento, e não o documento em claro, é representado no modelo do paciente
  (`app/models/patient.py:12`).
- A configuração do banco é externa ao código por `BaseSettings` (`app/config.py:6`).

### Lacunas desta versão

- A aplicação revoga efetivamente o acesso ao confrontar cada JWT com `is_active`, papel, vínculo
  e escopos atuais; ainda não existe denylist por `jti` para revogar um token isolado sem desativar
  o principal.
- O MFA administrativo é uma simulação acadêmica, não um fator de posse real.
- SQLite local não oferece, sozinho, criptografia em repouso ou separação de privilégios.
- Logs, retenção, anonimização e atendimento a direitos do titular ainda não foram definidos.

Um `response_model` ausente poderia serializar acidentalmente os campos internos adicionados ao
modelo de banco. Isso exporia metadados de auditoria, identificadores operacionais e informações
úteis para correlação de pessoas. O contrato de saída separado reduz esse risco e evita que uma
mudança no modelo persistente altere silenciosamente a API pública.

## Integridade

### Controles implementados

- UUID tipado para IDs e enumeração fechada para status (`app/models/appointment.py:8`).
- Referências de paciente e profissional são verificadas antes da criação
  (`app/services/appointments.py:11`).
- Schemas rejeitam propriedades não declaradas com `extra="forbid"`
  (`app/schemas/appointment.py:15` e `app/schemas/appointment.py:30`).
- Datas exigem timezone (`app/schemas/appointment.py:17`).
- Acesso ao banco usa `session.get()` e `select()`, sem concatenação de SQL
  (`app/services/appointments.py:36` e `app/services/appointments.py:43`).
- O teste de mass assignment tenta enviar um campo interno e espera `422`
  (`tests/test_appointments.py:83`).

### Lacunas desta versão

- Não há controle de concorrência otimista, trilha de autoria confiável ou log imutável.
- A aplicação ainda não detecta choque de horários.

## Disponibilidade

### Controles implementados

- Listagem limitada a no máximo 100 registros (`app/routes/appointments.py:43`).
- `pool_pre_ping=True` detecta conexões de banco inválidas (`app/database/engine.py:9`).
- `/health` permite verificação básica de processo (`app/main.py:24`).
- Operações de banco usam sessões de vida curta por dependência (`app/database/session.py:8`).

### Lacunas desta versão

- Há rate limiting local e diferenciado, mas múltiplas réplicas exigem armazenamento distribuído;
  timeouts de infraestrutura, retry controlado e circuit breaker ainda dependem do deploy.
- `/health` não verifica a dependência de banco.
- O banco SQLite é um ponto único de falha e não é adequado à carga de produção.
- Backup, restauração e objetivos RPO/RTO ainda não foram especificados.

## Mapeamento de frameworks

| Referência | Risco/prática | Controle concreto atual | Situação futura |
|---|---|---|---|
| OWASP API1:2023 BOLA | Autorização por objeto | JWT + ownership centralizado + teste negativo | Ampliar matriz de objetos e papéis |
| OWASP API3:2023 BOPLA | Exposição/alteração indevida de propriedades | Schemas separados, `response_model`, `extra="forbid"` | Revisão automatizada do OpenAPI |
| OWASP API4:2023 | Consumo irrestrito | Paginação com limite 100 | Rate limiting por rota e cliente |
| OWASP API8:2023 | Configuração insegura | `debug=false`, configuração externa | CORS allowlist, headers e TLS no proxy |
| NIST SSDF PO.1/PO.2 | Requisitos e papéis de segurança | `SECURITY.md`, classificação CIA e invariantes | Revisão periódica e responsáveis formais |
| NIST SSDF PW.1 | Design seguro | Modularização, schemas separados e threat model | Atualizar modelo a cada mudança relevante |
| NIST SSDF PW.4 | Reutilizar componentes bem mantidos | FastAPI, Pydantic e SQLModel declarados | `pip-audit` e política de atualização |
| NIST SSDF PW.5/PW.7 | Práticas seguras e revisão do código | Validação, output encoding e pytest | SAST, revisão e security gate |
| NIST SSDF RV.1/RV.2 | Detectar e responder a vulnerabilidades | Testes iniciais e evidências | ZAP, triagem, SLA e rastreabilidade |
| MITRE ATT&CK T1190 | Explorar aplicação pública | Validação e SQL parametrizado reduzem parte da superfície | WAF/proxy, patching, DAST e segmentação |
| MITRE ATT&CK T1110 | Força bruta | Bcrypt e MFA administrativo simulado | Rate limiting e alertas |
| MITRE ATT&CK T1078 | Uso de conta válida | Expiração JWT, scopes e MFA administrativo | Revogação operacional e detecção |
| MITRE ATT&CK T1565 | Manipulação de dados | Tipos, enum e integridade referencial lógica | Autorização, auditoria e controle de concorrência |

MITRE ATT&CK descreve comportamento adversário, não uma checklist de controles. O mapeamento é
usado para relacionar técnicas plausíveis às medidas preventivas e detectivas do projeto.

## Referências oficiais

- [OWASP API Security Top 10 — 2023](https://api-security.owasp.org/editions/2023/en/0x00-header/)
- [NIST SP 800-218 — SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
- [MITRE ATT&CK T1190](https://attack.mitre.org/techniques/T1190/)
- [MITRE ATT&CK T1110](https://attack.mitre.org/techniques/T1110/)
