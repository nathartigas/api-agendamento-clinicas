# Auditoria de segurança da especificação OpenAPI

## Escopo

A auditoria é reproduzível por `python -m scripts.audit_openapi` e verifica o contrato gerado pela
própria aplicação, não um arquivo mantido manualmente. A evidência JSON está em
`docs/evidencias/openapi_audit.json`.

## Gaps encontrados e correção

| ID | Gap antes da auditoria | Risco | Correção |
|---|---|---|---|
| GAP-OAS-01 | Operações protegidas não declaravam respostas 401 e 403. | Consumidores poderiam tratar falhas de autenticação/autorização de forma incorreta. | `app/openapi.py` adiciona as respostas a toda operação com requisito de segurança. |
| GAP-OAS-02 | O 429 do middleware não aparecia no contrato. | Clientes poderiam repetir chamadas em vez de respeitar `Retry-After`. | O gerador central adiciona 429 a todas as operações documentadas. |

## Controles aprovados

- O fluxo OAuth2 Password aponta para `/api/v1/auth/token`.
- Os quatro escopos esperados aparecem no security scheme.
- Nove operações protegidas declaram segurança, 401 e 403.
- Schemas `AppointmentCreate` e `AppointmentUpdate` têm `additionalProperties: false`.
- Nenhum schema público contém hashes de senha/segredo, nota de auditoria ou autor interno.
- HTTP Basic aparece somente no emissor M2M, enquanto recursos usam Bearer com escopos.

## Limitações

OpenAPI não expressa ownership por objeto e não prova ausência de BOLA; essa propriedade continua
coberta por pytest. `/health` permanece fora do contrato público para reduzir ruído operacional.
A auditoria também não substitui DAST: headers e comportamento real são validados pelo ZAP e pelos
testes HTTP.
