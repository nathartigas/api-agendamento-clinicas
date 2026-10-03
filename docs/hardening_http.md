# Hardening HTTP

## Controles implementados

O `SecurityHeadersMiddleware` acrescenta a toda resposta:

- `Strict-Transport-Security: max-age=31536000; includeSubDomains`;
- CSP com `default-src`, fontes explícitas de script/estilo/imagem, `object-src 'none'`,
  `base-uri`, `form-action` e `frame-ancestors`;
- `X-Frame-Options: DENY`;
- `X-Content-Type-Options: nosniff`;
- `Referrer-Policy: no-referrer`;
- COEP `require-corp`, COOP/CORP `same-origin` e Permissions Policy restritiva;
- `Cache-Control: no-store` e `Pragma: no-cache`.

A Swagger UI usa dependências fixadas em versão exata, SRI SHA-384, `crossorigin="anonymous"` e
script de inicialização local. A agenda da recepção usa CSS local, sem estilo inline incompatível
com a CSP.

O CORS não usa wildcard. Origens, métodos e headers permitidos são declarados explicitamente em
`app/main.py`, e as origens vêm de `CORS_ALLOWED_ORIGINS`.

O limitador central usa janela móvel de 60 segundos, com os valores locais abaixo:

| Política | Limite |
|---|---:|
| Login humano | 5 |
| Client Credentials | 10 |
| Demais rotas | 120 |

Quando o orçamento termina, a API responde 429 com `Retry-After`. Requisições OPTIONS passam ao
middleware CORS sem consumir o orçamento. Tokens Bearer também são decodificados em middleware;
as dependências de autenticação confrontam as claims com o usuário ou cliente ativo no banco.

## Configuração

Os parâmetros estão tipados em `app/config.py` e exemplificados em `.env.example`. Em produção,
origens CORS devem conter somente frontends HTTPS conhecidos, nunca `*` quando credenciais forem
permitidas.

## Limites operacionais

O limitador desta entrega fica na memória do processo. Ele é adequado à demonstração e aos
testes, mas cada réplica teria um contador independente. Produção deve mover o estado para Redis,
API gateway ou WAF, considerar o IP real apenas de proxies confiáveis e adicionar métricas e
alertas.

HSTS só protege tráfego servido por HTTPS. O deploy deve terminar TLS corretamente e validar o
header na borda. CSP deve ser revisada se scripts, imagens ou estilos externos forem adicionados.
