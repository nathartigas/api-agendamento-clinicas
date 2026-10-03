# Exercícios 6 e 7 — Autenticação, autorização e integração externa

## Modelo adotado

A aplicação combina três mecanismos porque nenhum deles, isoladamente, representa a regra de
negócio:

1. **RBAC** concede operações gerais aos papéis `receptionist`, `professional` e `admin`.
2. **Autorização por recurso** exige que o `professional_id` do token corresponda ao da consulta.
3. **Escopos e atributos do token** separam leitura, escrita, administração e acesso M2M.

RBAC puro diria apenas que alguém é profissional; não impediria esse profissional de trocar o
UUID e alcançar a consulta de outro. O ownership fecha essa lacuna. O administrador acessa as
rotas administrativas somente com `mfa=true`, mas não recebe permissão de escrita clínica.

## Matriz de autorização

| Operação | Recepcionista | Profissional | Administrador | Laboratório |
|---|---:|---:|---:|---:|
| Ler agenda operacional | Sim | Somente própria | Sim + MFA | Não |
| Criar consulta | Não | Somente própria | Não | Não |
| Alterar/excluir consulta | Não | Somente própria | Não | Não |
| Listar usuários | Não | Não | Sim + MFA | Não |
| Consultar disponibilidade | Não | Não | Não | Sim, escopo dedicado |

## Sessão JWT humana

`POST /api/v1/auth/token` implementa o password flow solicitado pelo exercício. A senha é
comparada com hash bcrypt de custo 12; o hash nunca integra a resposta. O token possui:

- `sub`: UUID do usuário;
- `token_type=user`;
- `role`;
- `professional_id`, quando aplicável;
- `scope`;
- `mfa`;
- `iat`, `exp`, `iss`, `aud` e `jti`.

A chave de assinatura não possui default no código e deve entrar por `JWT_SECRET_KEY`. A
decodificação fixa o algoritmo permitido, valida issuer/audience e exige os claims essenciais.
A sessão expira em 30 minutos por padrão.

## MFA simulado

Contas administrativas têm um código de seis dígitos cujo valor também é armazenado como hash
bcrypt. Sem código válido, nenhum JWT administrativo é emitido. É uma simulação acadêmica: em
produção, deve ser substituída por TOTP/WebAuthn, proteção contra replay e recuperação segura.

## Fluxo M2M

Foi escolhido **OAuth 2.0 Client Credentials**, porque o laboratório atua em nome do próprio
sistema e não de uma pessoa. O endpoint `POST /api/v1/auth/client-token` recebe o cliente via HTTP
Basic e exige `grant_type=client_credentials`.

O token contém:

- `token_type=service`;
- `client_id` e `sub` do parceiro;
- `scope=availability:read`;
- audience da API e expiração.

`GET /api/v1/availability` aceita somente token de serviço com esse escopo. A resposta contém
apenas `date`, `professional_id` e slots vagos; não inclui paciente, consulta, observação ou
diagnóstico. Tokens humanos são rejeitados nesse endpoint, assim como tokens M2M são rejeitados
nas rotas humanas.

## Limitações conhecidas

- O password flow é requisito explícito do exercício; para uma aplicação pública moderna seria
  preferível Authorization Code com PKCE e um provedor de identidade.
- Usuários e clientes desativados perdem acesso na requisição seguinte porque as claims são
  confrontadas com o estado atual. Ainda não existe denylist por `jti` para revogar apenas uma
  sessão sem desativar o principal.
- O MFA é simulado e não deve ser considerado fator de posse real.
- Rotação de segredo do laboratório e chave de assinatura depende da infraestrutura futura.
