# Exercício 4 — Misuse cases

Os casos abaixo são cenários de ameaça, não findings confirmados. O estado de cada controle foi
atualizado após a etapa 3; lacunas restantes serão tratadas nas próximas etapas.

## MC-01 — Trocar o ID e acessar consulta alheia

- **Ator:** usuário autenticado de baixo privilégio ou cliente externo enquanto a API estiver
  desprotegida.
- **Pré-condição:** obter ou adivinhar um UUID de consulta.
- **Ação:** chamar `GET`, `PATCH` ou `DELETE /appointments/{id}` com o ID de outro titular.
- **Resultado indevido:** leitura, alteração ou exclusão de dado de saúde de terceiro.
- **Propriedade violada:** confidencialidade e integridade; OWASP API1 BOLA.
- **Controle implementado na etapa 3:** autenticação obrigatória e autorização central que compara
  o `professional_id` do principal com o recurso (`app/security/authorization.py:54`), com teste
  cruzando dois profissionais. Permanece como cenário de regressão a ser ampliado na etapa 12.

## MC-02 — Mass assignment de campos internos

- **Ator:** consumidor da API.
- **Ação:** incluir `created_by`, `internal_audit_note`, `status` ou campos inesperados no POST.
- **Resultado indevido pretendido:** forjar autoria, auditoria ou estado.
- **Controle atual:** `extra="forbid"` rejeita o corpo (`app/schemas/appointment.py:15`) e há teste
  com expectativa `422` (`tests/test_appointments.py:83`).
- **Risco residual:** novos schemas podem esquecer a política; o OpenAPI e testes precisam cobrir
  todos os corpos de entrada.

## MC-03 — Stored XSS na agenda da recepção

- **Ator:** cliente capaz de persistir `public_notes`.
- **Ação:** gravar `<script>` ou markup malicioso e aguardar a recepção abrir a agenda.
- **Resultado indevido pretendido:** executar código no navegador e sequestrar a futura sessão.
- **Controle atual:** autoescape explícito (`app/routes/reception.py:24`) e teste de regressão
  (`tests/test_templates.py:9`).
- **Risco residual:** uso futuro de `|safe`, inserção em contexto JavaScript/URL ou biblioteca de
  template diferente pode reabrir o caminho.

## MC-04 — Consultar toda a agenda sem autenticação

- **Ator:** pessoa com acesso de rede ao serviço.
- **Ação:** chamar a listagem JSON ou a página interna.
- **Resultado indevido:** enumerar vínculos paciente–profissional e observações.
- **Controle implementado na etapa 3:** OAuth2PasswordBearer, escopo de leitura e filtros pelo
  profissional autenticado. Ainda falta isolamento explícito por clínica.

## MC-05 — Indisponibilidade por abuso de recursos

- **Ator:** cliente anônimo ou bot.
- **Ação:** repetir criação, atualização, login ou renderização da agenda.
- **Resultado indevido:** saturar workers, conexões ou armazenamento.
- **Controle atual:** listagem limitada a 100 itens (`app/routes/appointments.py:43`).
- **Mitigação planejada:** limites globais e por rota, limite mais forte no login, tamanho máximo
  de corpo, timeout e monitoramento.

## MC-06 — Laboratório usa token além do contrato

- **Ator:** parceiro mal configurado ou invasor com credencial M2M comprometida.
- **Ação:** usar o token para chamar rotas de pacientes ou consultas.
- **Resultado indevido:** acesso a dados pessoais e clínicos.
- **Controle implementado na etapa 3:** Client Credentials, audience específica,
  `token_type=service`, escopo `availability:read`, endpoint dedicado e negação explícita nas
  rotas humanas.

## MC-07 — Força bruta contra conta administrativa

- **Ator:** atacante remoto.
- **Ação:** password spraying ou credential stuffing no endpoint de login.
- **Resultado indevido:** assumir conta com acesso amplo.
- **Controle atual:** bcrypt, mensagens uniformes, MFA administrativo simulado e expiração JWT.
- **Lacuna:** rate limiting e eventos de auditoria entram nas próximas etapas.

## MC-08 — Roubo ou adulteração do banco local

- **Ator:** usuário ou processo com acesso ao host.
- **Ação:** copiar ou alterar `data/appointments.db`.
- **Resultado indevido:** vazamento ou corrupção completa.
- **Estado atual:** SQLite local e URL default em `app/config.py:11` são destinados apenas ao
  desenvolvimento.
- **Mitigação planejada:** banco de produção separado, credencial externa, TLS, criptografia em
  repouso, least privilege, backup testado e restrição de rede.

## MC-09 — Vazamento por serialização acidental

- **Ator:** consumidor da API beneficiado por uma alteração futura do backend.
- **Ação:** explorar endpoint que devolva diretamente o modelo persistente sem contrato.
- **Resultado indevido:** obter auditoria ou novos campos internos.
- **Controle atual:** response models em todas as rotas CRUD (`app/routes/appointments.py:32`).
- **Mitigação adicional:** teste automático do OpenAPI e teste negativo de campos proibidos.

## MC-10 — Manipular data/hora para corromper a agenda

- **Ator:** cliente da API.
- **Ação:** enviar data sem timezone, formato inválido ou horário conflitante.
- **Resultado indevido:** agendamento no dia errado ou dupla marcação.
- **Controle atual:** timezone obrigatório (`app/schemas/appointment.py:17`).
- **Lacuna:** ainda não há prevenção de conflito, janela operacional ou normalização UTC.
