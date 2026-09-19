# Priorização CVSS e impacto de negócio

Os scores abaixo registram as falhas históricas e as hipóteses relevantes do threat model. CVSS
mede gravidade técnica; a decisão de merge também considera que dados de agenda médica são dados
pessoais sensíveis e que indisponibilidade afeta atendimento.

| Vulnerabilidade | Categoria | CVSS | Impacto de negócio | Gate | Estado |
|---|---|---:|---|---|---|
| SQL injection em entrada pública | A03:2021 | 9,8 crítico | Leitura/alteração da base clínica e indisponibilidade | Bloqueia | Prevenida por queries parametrizadas; teste de payload. |
| BOLA entre profissionais | API1:2023 | 8,1 alto | Exposição ou alteração de consulta de terceiro | Bloqueia | Corrigida por ownership central; teste 403 e filtro de listagem. |
| Tentativas ilimitadas e exaustão bcrypt | API2/API4:2023 | 8,1 alto | Tomada de conta ou interrupção de agendamento | Bloqueia | Corrigida por rate limiting. |
| Mass assignment de campo interno | API3:2023 | 6,5 médio | Fraude de auditoria e perda de integridade | Bloqueia pelo impacto | Corrigida por `extra="forbid"`. |
| Token de principal desativado | API2:2023 | 6,5 médio | Persistência de acesso após resposta a incidente | Bloqueia pelo impacto | Corrigida por confronto com estado atual. |
| Stored XSS na agenda | A03:2021 | 6,1 médio | Ação no navegador da recepção e possível sequestro de sessão | Bloqueia pelo impacto | Whitelist, autoescape e CSP. |
| Headers HTTP ausentes | API8:2023 | 3,7 baixo | Facilita clickjacking/MIME confusion como parte de cadeia | Avisa | Corrigida por middleware. |

Os valores de 8,1, 6,5 e 3,7 dos três findings auditados reproduzem o relatório estático preservado
em `docs/evidencias/security_scan_before/report.md`. Os demais são priorizações defensivas para o
pipeline; devem ser recalculados se a superfície ou o ambiente de produção mudar.

## Critério de aceite

Uma exceção ao gate exige risco documentado, responsável, prazo e controle compensatório. Não há
exceção aceitável para bypass de autenticação/autorização, segredo exposto, SQL injection ou acesso
indevido a dados de saúde. Um risco residual de infraestrutura também bloqueia o deploy quando não
houver TLS, gestão de segredos ou isolamento de banco comprovados.
