# Roteiro completo do vídeo — Assessment DR2

**Autora:** Nathalia Artigas

**Duração obrigatória:** até 5 minutos

**Formato:** gravação de tela com a autora narrando

**Publicação:** YouTube como **não listado**

**Objetivo:** comprovar autoria, explicar as decisões de segurança e demonstrar a aplicação funcionando

Este documento tem duas partes: o roteiro cronometrado, com as falas exatas e o que mostrar; e a
explicação completa dos conceitos, para que a apresentação não pareça apenas uma leitura.

## 1. Preparação antes de gravar

### 1.1 Segurança da gravação

Não abra nem mostre o arquivo `.env`. Não exiba senhas, JWTs, cookies, notificações pessoais,
e-mail, histórico do navegador ou qualquer dado real. Os dados do projeto são fictícios e o vídeo
deve preservar isso. Ative “Não Perturbe” e feche programas pessoais.

### 1.2 Preparação local

No terminal, entre na pasta do projeto e ative o ambiente virtual:

```bash
cd /Users/nathaliaartigas/Documents/Codex/2026-09-19/files-pasted-by-the-user-voc/outputs/nathalia_artigas_DR2_AT
source .venv/bin/activate
```

Se ainda não existir um `.env` local, copie o modelo e troque os placeholders por valores locais.
Faça isso **antes** de gravar e nunca mostre o conteúdo:

```bash
cp .env.example .env
```

Inicie a aplicação:

```bash
uvicorn app.main:app --reload
```

Confirme previamente:

- `http://127.0.0.1:8000/health` responde `{"status":"ok"}`;
- `http://127.0.0.1:8000/docs` abre a documentação Swagger;
- a internet está estável para abrir o GitHub;
- o pipeline final está verde.

### 1.3 Deixe estas telas abertas, nesta ordem

1. editor na raiz do projeto, com a árvore `app/` expandida;
2. navegador em `http://127.0.0.1:8000/docs`;
3. terminal na raiz do projeto;
4. `docs/threat_model.md` no editor;
5. `.github/workflows/security.yml` no editor;
6. execução final do pipeline:
   `https://github.com/nathartigas/api-agendamento-clinicas/actions/runs/35518542972`;
7. `docs/relatorio_tecnico_final.pdf` aberto na última página.

Use zoom entre 110% e 125%. Faça uma gravação de teste e procure terminar entre **4min30s e
4min50s**. O texto principal tem aproximadamente 650 palavras. Fale com calma, mas não pare para
explicar cada linha do código.

## 2. Roteiro cronometrado — falas exatas e telas

### 0:00–0:25 — apresentação e contexto

**Tela:** editor mostrando a raiz e o título do `README.md`.

**Ação:** comece com a árvore do projeto recolhida; depois expanda `app`.

**Fala:**

> Olá, meu nome é Nathalia Artigas. Neste Assessment eu desenvolvi uma API REST segura para uma
> rede de clínicas realizar o agendamento de consultas médicas. Como a aplicação trata dados de
> saúde, eu considerei confidencialidade, integridade e disponibilidade desde a arquitetura, e não
> somente no final do desenvolvimento.

### 0:25–0:55 — arquitetura modular e aplicação funcionando

**Tela:** árvore de `app/`, destacando `routes`, `models`, `schemas`, `services`, `database` e
`security`. Depois troque rapidamente para `/health` no navegador.

**Ação:** aponte as pastas e atualize a página `/health`.

**Fala:**

> A aplicação foi construída em FastAPI e separada em rotas, modelos, schemas, serviços, banco de
> dados e segurança. Essa divisão evita concentrar regras em um único arquivo e permite testar cada
> responsabilidade. Aqui o servidor Uvicorn está em execução, e o endpoint de saúde confirma que a
> API está disponível.

**Resultado visível esperado:** `{"status":"ok"}`.

### 0:55–1:30 — entrada, saída, persistência e XSS

**Tela:** `app/schemas/appointment.py`, deixando visíveis `AppointmentCreate`,
`AppointmentUpdate`, `AppointmentRead`, `extra="forbid"` e `SAFE_NOTES_PATTERN`.

**Ação:** role uma única vez para mostrar o schema de saída.

**Fala:**

> Nos schemas Pydantic, a entrada usa whitelist, regex, limites e `extra forbid`, portanto campos
> não declarados são rejeitados. O `AppointmentRead` é o response model e contém somente os campos
> autorizados. Sem esse contrato, campos internos do modelo persistido poderiam vazar na resposta.
> A persistência usa SQLModel, sessão por injeção de dependência e consultas parametrizadas. Na
> agenda HTML, Jinja2 usa herança e autoescape, transformando uma tentativa de script em texto e
> impedindo stored XSS.

### 1:30–2:10 — autenticação, autorização e integração M2M

**Tela:** primeiro `app/security/authentication.py`; depois `app/security/authorization.py`.

**Ação:** em `authentication.py`, aponte `OAuth2PasswordBearer` e os escopos. Em
`authorization.py`, aponte `authorize_appointment`.

**Fala:**

> Para usuários humanos, implementei OAuth2 Password, senhas com hash bcrypt e JWT com expiração,
> issuer e audience. Administradores precisam de um MFA simulado. A autorização combina RBAC com
> ownership: o papel define a capacidade geral, mas um profissional só acessa as consultas ligadas
> ao próprio identificador. Isso corrige BOLA, porque trocar o ID na URL não concede acesso. Para o
> laboratório, escolhi Client Credentials, próprio para máquina a máquina. O token recebe o tipo
> `service` e somente o escopo `availability read`, sem acesso ao CRUD clínico.

### 2:10–2:40 — ameaça, OWASP e hardening

**Tela:** `docs/threat_model.md`; use a busca do editor por `TM-01` e depois por `TM-08`.

**Ação:** deixe a tabela de ameaças visível.

**Fala:**

> O threat model foi construído com DFD, trust boundaries, misuse cases e STRIDE. Eu rastreei
> ameaças como BOLA, brute force, confusão entre token humano e de serviço, mass assignment e XSS.
> As mitigações incluem ownership central, validação fechada, revogação pelo estado atual, CORS com
> allowlist, CSP, HSTS, proteção contra frames, `nosniff` e rate limiting mais restritivo no login.

### 2:40–3:10 — demonstração rápida de proteção da rota

**Tela:** Swagger em `http://127.0.0.1:8000/docs`.

**Ação:** expanda `GET /api/v1/appointments`, clique em **Try it out**, depois **Execute**, sem
autorizar. Mostre a resposta `401` e os códigos `401`, `403` e `429` documentados.

**Fala:**

> A documentação OpenAPI apresenta as rotas e os controles esperados. Nesta demonstração, uma
> tentativa anônima de listar consultas retorna 401. As respostas 403 e 429 também fazem parte do
> contrato: 403 representa autenticação válida sem autorização suficiente, e 429 representa o
> bloqueio por excesso de requisições.

**Resultado visível esperado:** status `401`, normalmente com `{"detail":"Not authenticated"}`.

### 3:10–3:50 — testes, pipeline e critério do security gate

**Tela:** execução final do GitHub Actions, com os cinco jobs verdes. Em seguida, mostre
`.github/workflows/security.yml`.

**Ação:** aponte os jobs Tests, Bandit, Trivy, ZAP e Security gate.

**Fala:**

> A suíte final tem 34 testes e 94,64 por cento de cobertura. Há testes funcionais, regressões de
> segurança e testes com mocking, que provam que uma entrada inválida não chega ao serviço e que
> uma autorização negada impede a mutação. No pipeline, testes e auditoria OpenAPI, SAST com
> Bandit, análise de dependências com Trivy e DAST passivo com ZAP executam antes do gate. Eu defini
> que vulnerabilidades altas ou críticas bloqueiam, assim como achados médios confiáveis de SAST e
> qualquer falha que permita acesso indevido a dados de saúde. O impacto de negócio pode elevar o
> bloqueio mesmo quando o score técnico isolado não seria alto. O check `Security gate` é obrigatório
> na branch principal, então uma falha impede o merge.

### 3:50–4:25 — capstone, OpenAPI e OWASP ZAP

**Tela:** `docs/evidencias/etapa_6.md` ou a seção 6/7 do relatório PDF, com o antes e depois do ZAP.

**Ação:** destaque os números da auditoria OpenAPI e do ZAP.

**Fala:**

> No capstone, a auditoria automatizada do OpenAPI aprovou seis de seis controles, incluindo
> escopos, respostas de segurança e ausência de campos internos. O primeiro scan passivo do ZAP
> encontrou dois alertas médios e cinco baixos na interface Swagger. Eu corrigi CSP, integridade
> SRI, versões externas, políticas cross-origin, permissões e cache. A segunda execução ficou com
> zero alertas altos, médios ou baixos; restaram somente duas observações informativas.

### 4:25–4:55 — risco residual e decisão de deploy

**Tela:** última página de `docs/relatorio_tecnico_final.pdf`, seção “Riscos residuais e decisão de
deploy”.

**Ação:** aponte a tabela e depois a decisão abaixo dela.

**Fala:**

> Mesmo com o pipeline aprovado, eu liberaria esta versão somente para avaliação acadêmica e
> ambiente local controlado. Eu bloquearia produção até comprovar TLS na borda, banco gerenciado e
> criptografado, cofre e rotação de segredos, rate limiting distribuído, MFA real, auditoria
> imutável e backup restaurável. Essa decisão é conservadora porque dados de saúde aumentam o
> impacto de qualquer falha residual.

### 4:55–5:00 — encerramento

**Tela:** capa do relatório ou raiz do projeto.

**Fala:**

> Este foi o resultado final do meu Assessment. Obrigada.

Pare a gravação imediatamente para não ultrapassar cinco minutos.

## 3. Plano B se alguma demonstração falhar

- Se o Swagger não abrir, mostre `/health` e `docs/evidencias/validacao_http_final.txt`.
- Se `Try it out` não responder, abra o terminal e execute:

```bash
curl -i http://127.0.0.1:8000/api/v1/appointments
```

- Se o GitHub estiver lento, deixe previamente aberta a página com os cinco jobs verdes.
- Se os testes demorarem, não os execute durante o vídeo. Mostre o pipeline e o resultado registrado
  no relatório. O pipeline é uma evidência mais forte porque executou em ambiente limpo.
- Se errar uma palavra, continue. Regrave somente se a frase mudar o significado técnico.

## 4. Explicação completa para entender o que está apresentando

### 4.1 Por que FastAPI e por que separar módulos?

FastAPI define endpoints HTTP e gera automaticamente um contrato OpenAPI. O `APIRouter` permite
separar conjuntos de rotas. Neste projeto:

- `routes` recebe e responde requisições HTTP;
- `schemas` valida entrada e controla saída;
- `services` executa regras de negócio e persistência;
- `models` representa tabelas e entidades;
- `database` cria o engine e fornece sessões;
- `security` concentra autenticação, autorização, tokens e middlewares.

Essa separação reduz duplicação e evita que uma correção de segurança seja aplicada em uma rota e
esquecida em outra.

### 4.2 `response_model`: por que ele protege dados?

Um objeto do banco pode possuir campos internos que não devem sair pela API, como autor da
alteração, identificadores internos ou informações de auditoria. O `response_model` manda o
FastAPI serializar a resposta segundo uma lista fechada de campos. Mesmo que o serviço retorne um
objeto mais completo, somente os campos de `AppointmentRead` chegam ao cliente.

### 4.3 `extra="forbid"`, whitelist e regex

`extra="forbid"` rejeita atributos que não fazem parte do schema. Isso reduz mass assignment: um
cliente não consegue enviar silenciosamente algo como `is_admin`, `created_by` ou outro campo
interno. A whitelist e a expressão regular de `public_notes` aceitam somente caracteres previstos,
enquanto os limites impedem entradas excessivas. A validação de timezone evita horários ambíguos.

### 4.4 Jinja2, autoescape e stored XSS

Stored XSS ocorre quando um conteúdo malicioso é armazenado e, mais tarde, renderizado como HTML
executável para outro usuário. O autoescape converte caracteres especiais: `<script>` é exibido
como texto em vez de ser interpretado pelo navegador. O template herda de `base.html`, não usa o
filtro `safe`, e a CSP funciona como defesa adicional.

### 4.5 CIA, DFD e trust boundary

- **Confidencialidade:** apenas pessoas e serviços autorizados veem dados de pacientes.
- **Integridade:** alterações precisam de identidade, permissão e validação.
- **Disponibilidade:** rate limiting e monitoramento reduzem abuso e indisponibilidade.

O DFD mostra de onde os dados vêm, para onde vão e onde são armazenados. Uma trust boundary é um
limite onde muda o nível de confiança, por exemplo entre a internet e a API ou entre a API e o
banco. Esses limites são pontos importantes para autenticação, validação e criptografia.

### 4.6 STRIDE e misuse cases

STRIDE ajuda a procurar seis tipos de ameaça:

- **Spoofing:** fingir ser outra identidade;
- **Tampering:** adulterar dados;
- **Repudiation:** negar uma ação sem existir prova confiável;
- **Information Disclosure:** expor informação;
- **Denial of Service:** esgotar recursos;
- **Elevation of Privilege:** obter permissão indevida.

Misuse cases descrevem como alguém tentaria abusar do sistema. O projeto transforma esses abusos
em ameaças `TM-01` a `TM-10`, liga cada ameaça a um controle e, quando possível, a um teste.

### 4.7 OAuth2, bcrypt, JWT e MFA

OAuth2PasswordBearer indica como um usuário humano obtém e envia um bearer token. A senha não é
armazenada em texto: bcrypt gera um hash lento e com salt, dificultando ataques caso o banco seja
copiado. O JWT carrega identidade e claims assinadas, tem expiração, issuer e audience. O MFA do
Assessment é simulado para demonstrar a segunda verificação; não é suficiente para produção porque
não implementa enrollment, recuperação e um autenticador real como TOTP ou WebAuthn.

### 4.8 RBAC, ownership e por que usar os dois

RBAC autoriza com base no papel: recepcionista, profissional ou administrador. Só isso não impede
um profissional de consultar o recurso de outro profissional. Ownership adiciona autorização por
recurso: compara o `professional_id` autenticado com o `professional_id` da consulta. Por isso a
solução combina RBAC com autorização por recurso e alguns atributos do token.

### 4.9 BOLA

BOLA, Broken Object Level Authorization, acontece quando a API recebe um ID de objeto e não
confirma se o solicitante pode acessar aquele objeto. A correção central consulta a consulta,
verifica ownership antes de ler ou alterar e também filtra a listagem. Assim, trocar um UUID na URL
gera 403 em vez de expor dados de outra pessoa.

### 4.10 Client Credentials e separação M2M

O laboratório não é uma pessoa e não deve usar login e senha de usuário. Client Credentials foi
feito para um software autenticar outro software. O token de serviço recebe `token_type=service`,
o identificador do cliente e somente `availability:read`. As dependências das rotas também exigem
o tipo correto, evitando que um token de laboratório acesse rotas humanas.

### 4.11 CORS, headers e rate limiting

- CORS com allowlist autoriza somente origens conhecidas no navegador;
- HSTS orienta o navegador a preferir HTTPS, quando usado atrás de uma borda TLS;
- `X-Frame-Options` reduz clickjacking;
- `X-Content-Type-Options: nosniff` impede inferência insegura de conteúdo;
- CSP restringe as fontes que podem executar scripts e carregar recursos;
- rate limiting aplica limites menores aos emissores de token, que são alvos de brute force.

O rate limiter atual fica em memória e protege uma instância. Em produção, várias réplicas exigem
um contador distribuído, por exemplo em gateway ou Redis.

### 4.12 SQLModel, queries parametrizadas e segredos

SQLModel integra modelos Python e persistência SQL. Expressões como `select(...).where(...)` fazem
o driver enviar os valores como parâmetros separados do comando, reduzindo SQL injection. A
configuração vem de `BaseSettings`. O Git contém somente `.env.example`; o `.env` verdadeiro fica
ignorado e nunca entra no ZIP.

### 4.13 SAST, SCA, DAST e IAST no SDLC

- **SAST/Bandit:** analisa código sem executar a aplicação; entra cedo, em cada pull request.
- **SCA/Trivy:** verifica dependências e componentes conhecidos; roda na CI e antes do deploy.
- **DAST/ZAP:** testa a aplicação em execução; roda depois que o serviço sobe no pipeline.
- **IAST:** instrumentaria a aplicação durante testes para combinar execução e contexto interno.
  Foi classificado para integração/homologação, mas não foi implementado neste escopo acadêmico.

### 4.14 CVSS, impacto de negócio e gate

CVSS estima severidade técnica com fatores como vetor de ataque, complexidade, privilégios e
impacto. Ele não conhece sozinho o contexto da clínica. Por isso, o projeto também considera o
impacto de negócio: acesso indevido a dados de saúde pode bloquear o pipeline mesmo que alguma
ferramenta atribua severidade menor. O gate agrega quatro resultados e falha quando qualquer
controle obrigatório falha.

### 4.15 Testes com mocking

Mocking substitui temporariamente uma dependência por uma implementação controlada. Ele permite
provar propriedades específicas: se a validação rejeitar a entrada, o serviço não deve ser chamado;
se a autorização negar o acesso, a função de atualização também não deve ser chamada. Isso é mais
forte do que verificar somente um status HTTP.

### 4.16 Auditoria OpenAPI

O script lê o contrato gerado pela própria aplicação e verifica seis propriedades: emissor OAuth2,
escopos, respostas 401/403, resposta 429, ausência de campos internos e rejeição de propriedades
extras. O resultado 6/6 mostra que o contrato público corresponde às decisões de segurança. BOLA
continua validada por testes, pois OpenAPI não expressa ownership de objetos.

### 4.17 OWASP ZAP passivo e o antes/depois

O ZAP passivo observa respostas sem executar ataques destrutivos. O scan inicial encontrou dois
alertas médios e cinco baixos na Swagger UI. As correções incluíram CSP completa, SRI, versões
fixadas, políticas cross-origin, Permissions Policy e bloqueio de cache. No scan final não havia
alertas altos, médios ou baixos. “Modern Web Application” e “Non-Storable Content” são
informativos; o segundo inclusive confirma que o cache foi restringido.

### 4.18 Por que o pipeline verde não autoriza produção?

O pipeline prova propriedades do código e do ambiente de CI, mas não prova toda a infraestrutura
real. Ainda faltam evidências de TLS na borda, criptografia do banco, segredo em cofre, rotação,
MFA real, rate limiting compartilhado, logs imutáveis, isolamento por clínica e restauração de
backup. Como o impacto envolve dados de saúde, esses riscos residuais bloqueiam produção, embora a
entrega acadêmica esteja aprovada.

## 5. Respostas curtas para perguntas prováveis

**Por que não usar somente RBAC?**

Porque dois profissionais possuem o mesmo papel, mas não devem acessar as consultas um do outro.
Ownership resolve a autorização no nível do objeto.

**Qual a diferença entre 401 e 403?**

401 significa identidade ausente ou inválida. 403 significa identidade válida, mas sem papel,
escopo ou ownership suficiente.

**Por que Client Credentials?**

Porque o laboratório é um cliente de software, não um usuário humano, e precisa de escopo mínimo.

**O JWT criptografa os dados?**

Não. Neste projeto ele é assinado para impedir adulteração. Por isso não se colocam dados clínicos
sensíveis dentro do token e TLS continua obrigatório.

**Por que o ZAP não substitui os testes de BOLA?**

Porque BOLA depende da relação de negócio entre usuário e objeto. Um scanner genérico não conhece
essa relação com a mesma precisão dos testes de autorização.

**Por que usar score CVSS e impacto de negócio?**

O CVSS padroniza a gravidade técnica; o impacto de negócio considera LGPD e dados de saúde.

**O que o `extra="forbid"` evita?**

Evita que propriedades não previstas sejam aceitas e eventualmente atribuídas a campos internos.

**Por que produção está bloqueada se não há finding alto?**

Porque ausência de finding no código não comprova controles operacionais da infraestrutura.

## 6. Checklist final de gravação e entrega

- [ ] A gravação tem no máximo 5 minutos.
- [ ] Seu nome é falado no início.
- [ ] A árvore modular e o `/health` aparecem.
- [ ] `response_model`, validação, autenticação, ownership e M2M são explicados.
- [ ] O threat model ou sua rastreabilidade aparece.
- [ ] A decisão do security gate é explicada com suas próprias palavras.
- [ ] Os cinco jobs verdes aparecem.
- [ ] O antes/depois do ZAP aparece.
- [ ] Os riscos residuais e o bloqueio de produção são explicados.
- [ ] Nenhum `.env`, segredo, senha ou token aparece.
- [ ] O vídeo foi assistido após o upload para conferir áudio e legibilidade.
- [ ] A visibilidade no YouTube está como **não listado**, não privado.
- [ ] A URL foi registrada em `VIDEO_LINK.txt`.
- [ ] O ZIP final se chama `nathalia_artigas_DR2_AT.zip`.

## 7. Publicação no YouTube

1. Faça upload do vídeo.
2. Use um título como `Assessment DR2 — API segura de agendamento — Nathalia Artigas`.
3. Na visibilidade, selecione **Não listado**.
4. Aguarde o processamento e assista ao vídeo publicado.
5. Copie a URL e registre-a em `VIDEO_LINK.txt`.
6. Só depois gere o ZIP definitivo.
