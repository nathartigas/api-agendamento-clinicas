# Exercício 4 — Matriz STRIDE

Legenda de situação: **I** implementado, **P** planejado, **L** lacuna conhecida.

| Componente | S — Spoofing | T — Tampering | R — Repudiation | I — Information disclosure | D — Denial of service | E — Elevation of privilege |
|---|---|---|---|---|---|---|
| API FastAPI | I: OAuth2/JWT | I: schema fechado, assinatura e ownership | L: sem auditoria imutável | I: response model e rotas protegidas | I: paginação e rate limit | I: RBAC + ownership |
| Serviço de autenticação | I: bcrypt, JWT e MFA simulado | I: assinatura JWT e algoritmo fixo | P: eventos de login | I: erros uniformes e tokens fora de respostas indevidas | I: limites fortes distintos; P: distribuição | I: papéis, scopes e claims validados |
| Serviço de consultas | I: recebe principal validado | I: enum, UUID e referências; P: conflito de agenda | L: sem trilha imutável | I: ownership antes do acesso | I: quota local por ator; P: distribuição | I: RBAC + recurso |
| Banco SQLModel | P: conta de serviço | I: API parametrizada; P: least privilege | L: sem auditoria de banco | L: SQLite legível no host | L: ponto único de falha | P: credencial restrita, sem papel admin |
| Página da recepção | I: JWT obrigatório | I: somente leitura | L: sem auditoria de visualização | I: autoescape, CSP e agenda autenticada | I: no-store e limite local | I: papel e filtro do profissional |
| Laboratório M2M | I: Client Credentials | I: claims assinadas e audience | P: `client_id` nos eventos | I: somente disponibilidade agregada | I: quota M2M local; P: distribuição | I: escopo `availability:read` e negação nas outras rotas |
| Pipeline CI | I: permissões mínimas do runner | I: actions/imagem fixadas e branch protection | I: logs e artefatos de CI | I: push protection e ausência de segredos em PR | I: jobs efêmeros | I: PR sem token amplo e gate obrigatório |

## Priorização

| ID | STRIDE | Ameaça | Ativo | Probabilidade atual | Impacto | Prioridade | Mitigação principal |
|---|---|---|---|---|---|---|---|
| TM-01 | I/E | BOLA em consulta | Dado de saúde | Alta se exposta | Muito alto | Crítica antes de produção | Ownership centralizado |
| TM-02 | S/E | Uso anônimo das rotas | Todo o domínio | Alta se exposta | Muito alto | Crítica antes de produção | OAuth2/JWT e deny-by-default |
| TM-03 | I | Agenda HTML aberta | Identidade e agenda | Alta se exposta | Alto | Alta | Sessão e RBAC |
| TM-04 | S/E | Credencial M2M com poderes humanos | Dados clínicos | Média após integração | Muito alto | Alta | Audience, tipo e escopo dedicados |
| TM-05 | D | Abuso de login/CRUD | Disponibilidade | Média | Alto | Alta | Rate limiting e observabilidade |
| TM-06 | T/R | Alteração sem autoria confiável | Agenda/auditoria | Alta se exposta | Alto | Alta | Identidade, trilha e integridade |
| TM-07 | I/T | Compromisso do banco | Base completa | Baixa remotamente; alta com host | Muito alto | Alta | Segmentação, criptografia e least privilege |
| TM-08 | T/I | Stored XSS | Sessão da recepção | Baixa com controle atual | Alto | Média | Autoescape + CSP + regressão |
| TM-09 | T | Mass assignment | Auditoria/estado | Baixa com controle atual | Alto | Média | Schema fechado em todas as entradas |
| TM-10 | D/T | Choque ou data inconsistente | Agenda | Média | Médio/alto | Média | UTC, regra de conflito e transação |

## Cobertura dos componentes exigidos

A matriz aplica as seis categorias STRIDE a mais de três componentes: API, autenticação, serviço
de consultas, banco, HTML da recepção, integração M2M e pipeline. Ela distingue controles
existentes de mitigações ainda não implementadas, evitando atribuir segurança futura à versão
atual.
