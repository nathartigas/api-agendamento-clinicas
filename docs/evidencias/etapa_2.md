# Evidências — Etapa 2

## Exercícios cobertos

- Exercício 3: análise CIA, frameworks e DFD.
- Exercício 4: misuse cases, STRIDE e threat model consolidado.
- Exercício 5: partições, fronteiras e três eixos de segurança de APIs.

## Artefatos

| Evidência | Arquivo | Critério demonstrado |
|---|---|---|
| CIA e frameworks | `docs/cia_frameworks.md` | Confidencialidade, integridade, disponibilidade, OWASP, NIST e MITRE |
| DFD | `docs/dfd.md` | Entidades, processos, stores, fluxos sensíveis e trust boundaries |
| Misuse cases | `docs/misuse_cases.md` | Atores, abuso, impacto, controle e mitigação |
| STRIDE | `docs/matriz_stride.md` | Seis categorias em sete componentes e priorização |
| Arquitetura | `docs/arquitetura_seguranca.md` | Partições e vetores de design, implementação e infraestrutura |
| Threat model | `docs/threat_model.md` | Ativos, superfícies, capacidades, invariantes, cenários e severidade |
| Política | `SECURITY.md` | Escopo, invariantes, critérios e estado seguro de deploy |

## Rastreabilidade ao código

As afirmações sobre controles existentes possuem referências `arquivo:linha`. Controles ainda não
implementados estão marcados como “planejado”, “lacuna” ou “questão aberta”. Nenhuma hipótese foi
promovida a finding sem a fase posterior de validação.

## Decisão de liberação nesta etapa

**Não autorizada para produção.** As hipóteses TM-01 e TM-02 representam ausência atual de
autenticação e ownership. Elas são aceitáveis somente porque a etapa 1 foi explicitamente
classificada como execução local. A autorização de deploy será reavaliada no capstone.

