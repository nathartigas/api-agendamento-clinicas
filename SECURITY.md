# Política de segurança do projeto

## Escopo

Esta política se aplica a toda a API de agendamento, à página interna da recepção, à camada de
persistência, aos testes e aos componentes de autenticação e integração M2M. Pacientes,
profissionais, consultas e observações de consulta são dados protegidos; dados de saúde recebem
o nível mais restritivo.

## Invariantes obrigatórias

1. Uma identidade só pode ler ou alterar recursos autorizados por papel, escopo e ownership.
2. O laboratório recebe somente disponibilidade agregada, nunca dados clínicos ou identidade do
   paciente.
3. Senhas, chaves, tokens e credenciais de banco nunca são armazenados em texto claro no
   repositório, nos logs ou nas respostas.
4. Campos internos de auditoria não atravessam contratos públicos de resposta.
5. Toda entrada externa é validada por schema fechado e toda saída HTML é codificada.
6. Consultas ao banco usam a API parametrizada do SQLModel/SQLAlchemy.
7. Operações sensíveis devem produzir trilha de auditoria sem registrar dados clínicos ou tokens.
8. Controles de segurança devem ser centralizados e testados; rotas não devem duplicar regras de
   autenticação ou autorização.
9. Falhas de segurança não podem resultar em comportamento permissivo.
10. O deploy é bloqueado por vulnerabilidade alta/crítica ou por exposição não autorizada de dado
    de saúde, independentemente da classificação técnica isolada.

## Critério de finding reportável

É reportável qualquer caminho plausível que conceda a um ator uma capacidade nova de ler,
modificar, excluir ou indisponibilizar dados além de sua autorização. Falhas BOLA, bypass de
autenticação, exposição de segredos, injeção, stored XSS e ausência de limites em rotas sensíveis
são especialmente relevantes.

## Estado da versão atual

A versão atual possui validação Pydantic, contratos de saída, consultas SQLModel, autoescape
Jinja2, autenticação JWT, bcrypt, MFA administrativo simulado, RBAC, ownership, escopos M2M,
rate limiting, revogação por estado atual, CORS restrito e headers de segurança. A auditoria
estática da etapa 4 identificou três findings pré-correção, todos tratados e cobertos por testes.

Ainda faltam auditoria append-only, infraestrutura TLS comprovada, limitador distribuído,
monitoramento, backup, rotação de segredos e controles automatizados de implantação. Portanto,
esta versão continua somente para desenvolvimento local e não está autorizada para produção.
