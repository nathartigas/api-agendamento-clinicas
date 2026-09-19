# Etapa 4 — vulnerabilidades OWASP e correções

## Método e evidência

A revisão combinou análise manual de fluxos, testes negativos e uma varredura estática completa do
repositório. A varredura foi preservada como evidência **antes das correções** em
`docs/evidencias/security_scan_before/`. Ela encontrou três falhas: uma alta, uma média e uma
baixa. Também foram reavaliados BOLA, mass assignment, SQL injection e stored XSS.

| Padrão | Estado antes da correção | Correção e prova |
|---|---|---|
| API1:2023 BOLA | O CRUD inicial buscava a consulta somente pelo UUID, sem principal nem ownership. | As rotas obtêm um principal e chamam `authorize_appointment`; o teste cruzado recebe 403 (`app/security/authorization.py:54`, `tests/test_authorization.py:21`). |
| API2/API4: autenticação e consumo irrestrito | `/auth/token` e `/auth/client-token` aceitavam tentativas ilimitadas, incluindo trabalho bcrypt. Finding alto, CWE-307/CWE-400. | Middleware central usa janelas e orçamentos distintos; a tentativa seguinte retorna 429 e `Retry-After` (`app/security/middleware.py:39`, `tests/test_authentication.py:45`, `tests/test_authentication.py:60`). |
| API2: sessão não revogada | Um JWT continuava válido até expirar mesmo após `is_active=False`. Finding médio, CWE-613/CWE-284. | Cada requisição protegida confronta subject, papel, vínculo, escopos e estado atual no banco (`app/security/authentication.py:46`); testes de usuário e cliente desativados retornam 401. |
| API8: configuração insegura | Não havia headers HSTS, anti-frame ou `nosniff`. Finding baixo, CWE-693/CWE-1021. | Middleware adiciona HSTS, CSP, `DENY`, `nosniff` e `no-referrer`; CORS agora usa allowlist (`app/main.py:38`, `app/security/middleware.py:99`). |
| API3: autorização de propriedades / mass assignment | Um campo interno enviado pelo cliente poderia ser perigoso se o schema o aceitasse. | Schemas de criação e atualização usam `extra="forbid"`, e o contrato de saída é uma allowlist (`app/schemas/appointment.py:18`, `app/schemas/appointment.py:39`, `app/schemas/appointment.py:59`). |
| A03:2021 Injection — stored XSS | Uma nota persistida é dado hostil quando chega ao navegador. | Entrada pública rejeita markup e Jinja2 mantém output encoding. POST e PATCH maliciosos retornam 422; dado legado inserido diretamente é exibido escapado (`app/schemas/appointment.py:9`, `tests/test_templates.py:9`). |
| A03:2021 Injection — SQL | Username e UUID são controlados pelo cliente. | SQLModel gera consultas parametrizadas e username possui allowlist. O payload `' OR 1=1 --` retorna 422 (`app/security/authentication.py:28`, `app/routes/auth.py:28`). |

## Demonstrações antes/depois

### BOLA — acesso a objeto alheio

Padrão histórico do CRUD inicial:

```python
appointment = session.get(Appointment, appointment_id)
return appointment
```

O UUID selecionava diretamente o objeto. Na versão corrigida, GET, PATCH e DELETE carregam o
recurso e executam a mesma autorização central por ownership. Um profissional autenticado que usa
o UUID de outro profissional recebe `403 Forbidden`. A correção não foi aplicada somente ao GET:
PATCH e DELETE compartilham `authorize_appointment`.

### Brute force e exaustão

Antes, qualquer quantidade de tentativas sintaticamente válidas alcançava autenticação. Depois,
o sexto login humano dentro de 60 segundos recebe 429; no Client Credentials, a 11ª tentativa
recebe 429. Os limites são configuráveis por ambiente e respostas bloqueadas informam
`Retry-After`.

### XSS e propriedades indevidas

Exemplo rejeitado em criação e atualização:

```json
{"public_notes":"<img src=x onerror=alert(1)>"}
```

Resposta esperada: `422 Unprocessable Entity`. Um campo não declarado como
`internal_audit_note` também recebe 422. O autoescape continua sendo defesa em profundidade para
conteúdo legado que não passou pelo contrato HTTP.

## Cobertura dos padrões compartilhados

- `/api/v1/auth/client-token` não apareceu como item separado: compartilha a causa do finding de
  rate limiting e recebeu política e teste próprios.
- PATCH e DELETE não aparecem como findings BOLA separados: compartilham a autorização central
  aplicada ao GET por ID.
- `AppointmentUpdate` compartilha a validação de notas de `AppointmentCreate`; ambos são testados.
- As consultas de autenticação e CRUD permanecem parametrizadas; não foi identificada SQL montada
  por concatenação.

## Resultado

Os três findings da varredura pré-correção foram tratados e têm testes de regressão. Isso não
autoriza produção: auditoria append-only, infraestrutura TLS comprovada, limitador distribuído,
monitoramento e gestão de segredos ainda pertencem ao hardening de implantação.
