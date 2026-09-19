# Exercício 5 — Arquitetura de segurança e vetores de ataque

## Partições do sistema

| Partição | Responsabilidade | Dados manipulados | Autoridade esperada |
|---|---|---|---|
| Clientes humanos | UI JSON e navegador da recepção | Credenciais, agenda e consultas autorizadas | Papel e recursos do próprio contexto |
| Cliente M2M | Consultar disponibilidade | Horários agregados | Apenas `availability:read` |
| Borda | TLS, limites e headers | Metadados HTTP | Encaminhar, limitar e registrar sem conteúdo clínico |
| API/routers | Contrato HTTP | JSON e parâmetros | Invocar dependências e serviços autorizados |
| Autenticação/autorização | Emitir/validar identidade e decisão | Senhas com hash, JWT, claims e MFA | Negar por padrão |
| Serviços de domínio | Regras de consulta | IDs, horários, status e observações | Operar somente após autorização |
| Templates | Renderização interna | Agenda diária mínima | Output encoding, sem lógica de autorização |
| Persistência | Estado transacional | Dados pessoais, profissionais e consultas | Conta restrita da aplicação |
| Auditoria | Evidência de ações | Identidade, ação, recurso, resultado e instante | Append-only; leitura restrita |
| CI/CD | Construção e verificação | Código, dependências e artefatos | Sem acesso a dados de produção em PR |

## Fluxo de decisão pretendido

```text
requisição
  → controles de borda
  → parsing e validação Pydantic
  → autenticação do token
  → autorização por papel/escopo
  → autorização por recurso/ownership
  → serviço de domínio
  → query SQLModel parametrizada
  → response model ou template com encoding
  → auditoria sem conteúdo clínico
```

Uma decisão negativa em qualquer etapa encerra o fluxo. O serviço de domínio não deve confiar em
IDs fornecidos pelo cliente como prova de ownership.

## Eixo 1 — Segurança de design

| Vetor | Consequência | Decisão arquitetural |
|---|---|---|
| BOLA/IDOR | Consulta de outro paciente/profissional | Ownership central e filtros por principal |
| Privilégio excessivo do laboratório | Exposição clínica em caso de token roubado | Endpoint, audience, tipo de token e escopo dedicados |
| RBAC amplo demais | Profissional acessa toda a rede | RBAC + autorização por recurso e atributos |
| Excesso de dados | Correlação de paciente e condição | Schemas mínimos por consumidor |
| Repúdio | Impossibilidade de atribuir alterações | Auditoria estruturada e protegida |
| Falha de disponibilidade | Paralisação de atendimento | SLO, rate limit, backup e restauração testada |

## Eixo 2 — Segurança de implementação

| Vetor | Controle atual | Ação seguinte |
|---|---|---|
| SQL injection | `select()`/`session.get()` sem concatenação | Testes de payload e análise estática |
| Mass assignment | `extra="forbid"` | Aplicar a todos os novos schemas |
| Stored XSS | Autoescape Jinja2 + teste | CSP e proibição de `safe` em dado externo |
| Algoritmo JWT inseguro | Algoritmo permitido fixo; `exp`, `iss` e `aud` validados | Planejar rotação e revogação |
| Senha em texto claro | Bcrypt com custo 12; hash nunca retornado | Aplicar política e migração de custo |
| Condição de corrida | Não controlada | Constraint/transação para choque de horário |
| Erro verboso | `debug=false` por padrão | Handler uniforme e correlation ID |

## Eixo 3 — Segurança de infraestrutura

| Vetor | Estado atual | Controle de produção necessário |
|---|---|---|
| Tráfego em claro | Fora do escopo local | TLS/HSTS no proxy e rede privada internamente |
| CORS wildcard | CORS não configurado | Allowlist explícita por ambiente |
| Clickjacking/MIME sniffing | Headers ausentes | `X-Frame-Options` e `X-Content-Type-Options` |
| Força bruta/DoS | Limite apenas de paginação | Rate limiting distribuído e limite especial no login |
| Banco exposto | SQLite local | Banco sem porta pública e security group restrito |
| Segredos no deploy | `.env.example` sem segredo | Secret manager e rotação |
| Dependência vulnerável | Sem automação | `pip-audit`, lock e security gate |
| Falta de telemetria | Sem stack definida | métricas, logs minimizados e alertas |

## Fronteiras e responsabilidades

- O proxy é responsável por TLS e controles volumétricos, não por ownership.
- A camada de autenticação prova identidade, mas não autoriza automaticamente objetos.
- A autorização combina papel, tipo de cliente, escopo e relacionamento com o recurso.
- O serviço aplica regras de negócio, mas recebe um principal já validado e também efetua filtros
  defensivos na query.
- O banco reforça integridade e least privilege, sem substituir autorização na aplicação.
- O template codifica a saída, sem aceitar conteúdo marcado como seguro pelo cliente.

## Premissas de implantação

1. Apenas o proxy recebe tráfego externo; banco e porta interna da API não são públicos.
2. TLS termina em componente administrado e o salto interno ocorre em rede restrita.
3. Chaves JWT e credenciais de banco vêm de secret manager, nunca do repositório.
4. Relógios dos componentes são sincronizados para expiração de tokens e auditoria.
5. Backups são criptografados, têm acesso restrito e restauração testada.

Essas premissas ainda não são comprovadas por manifestos de infraestrutura; serão tratadas como
requisitos de deploy, não como controles existentes.
