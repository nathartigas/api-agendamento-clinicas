# Roteiro do vídeo de apresentação - até 5 minutos

## Preparação

1. Copie `.env.example` para `.env` e use somente valores locais de demonstração.
2. Abra o repositório, um terminal e o Pull Request #3.
3. Inicie a API com `uvicorn app.main:app --reload`.
4. Deixe abertas as páginas `/docs`, do pipeline e do relatório final.
5. Não mostre `.env`, senhas, tokens, cookies, dados reais ou notificações pessoais.

## 0:00-0:35 - contexto e arquitetura

“Meu nome é Nathalia Artigas. Este Assessment implementa uma API FastAPI segura para agendamento
de consultas médicas. Separei routes, schemas, services, models, database e security. A aplicação
atende clientes JSON, uma agenda HTML da recepção e um laboratório via integração máquina a
máquina.”

Mostre rapidamente a árvore de diretórios.

## 0:35-1:25 - proteção de dados e persistência

Mostre `AppointmentCreate`, `AppointmentUpdate` e `AppointmentRead`.

“Os schemas de entrada rejeitam campos extras e validam formato e tamanho. O response model expõe
somente os campos permitidos. A persistência usa SQLModel e queries parametrizadas; a conexão é
configurada por BaseSettings e nenhum `.env` real é versionado. A agenda HTML usa herança Jinja2 e
autoescape, evitando stored XSS.”

## 1:25-2:15 - autenticação e autorização

Mostre os módulos `authentication.py`, `authorization.py` e uma rota de consulta.

“Usuários humanos usam OAuth2 Password, bcrypt e JWT expirável. Administradores exigem MFA
simulado. A autorização combina RBAC com ownership, porque o papel profissional não autoriza o
acesso à consulta de outro profissional. O laboratório usa Client Credentials, `token_type`
service e apenas o escopo `availability:read`.”

Na Swagger UI, destaque os cadeados e respostas 401, 403 e 429.

## 2:15-3:05 - threat model e correções OWASP

Mostre `docs/threat_model.md` e `docs/owasp_vulnerabilidades.md`.

“O threat model usa STRIDE e registra ameaças como BOLA, confusão entre token humano e M2M, brute
force, XSS e mass assignment. As correções incluem ownership central, rate limiting diferenciado,
revogação pelo estado atual, `extra=forbid`, autoescape, CORS explícito e headers de segurança.”

## 3:05-3:50 - testes e security gate

Execute ou mostre o resultado de:

```bash
pytest --cov=app --cov-fail-under=90 -q
```

“A suíte possui 34 testes e 94,64% de cobertura. Os testes com mocking provam que entrada inválida
não chega ao serviço e que uma autorização negada impede a mutação. No GitHub Actions, testes,
Bandit, Trivy e ZAP rodam em jobs independentes. O gate bloqueia alta ou crítica e também eleva
riscos de autenticação, autorização e dados de saúde pelo impacto de negócio.”

Mostre o run `35517319082` com os cinco jobs verdes.

## 3:50-4:35 - capstone, OpenAPI e ZAP

Mostre a auditoria OpenAPI e as duas pastas do ZAP.

“A auditoria OpenAPI aprovou seis de seis controles. O primeiro ZAP encontrou dois médios e cinco
baixos na Swagger UI. Corrigi CSP, SRI, versão das dependências, políticas cross-origin, permissões e
cache. O segundo scan ficou com zero alertas altos, médios ou baixos e duas observações apenas
informativas.”

## 4:35-5:00 - risco residual e encerramento

“A solução está aprovada para demonstração acadêmica, mas eu bloquearia produção enquanto não
houver TLS comprovado, banco gerenciado e criptografado, cofre de segredos, rate limiting
distribuído, MFA real, auditoria imutável e backup testado. Essa decisão é mais conservadora porque
a aplicação trata dados de saúde.”

Finalize mostrando o relatório e o nome do ZIP `nathalia_artigas_DR2_AT.zip`.

## Publicação

Publique no YouTube como **não listado**. Depois, registre a URL em `VIDEO_LINK.txt` na raiz antes
de gerar o ZIP definitivo.

