# Etapa 5 — pipeline DevSecOps

## Fluxo e fases do SDLC

| Técnica | Momento | Implementação nesta entrega | Por que aqui |
|---|---|---|---|
| SAST | IDE/pre-commit e todo pull request | Ruff e Bandit; gate para achados médios/altos com confiança média/alta | Feedback rápido sem precisar executar a aplicação. |
| SCA/dependências | Pull request, push em `main` e execução agendada futura | Trivy em filesystem, falhando para vulnerabilidade alta/crítica com correção disponível | Detecta risco introduzido pelo grafo de pacotes antes do merge. |
| Testes de segurança | Pull request | Pytest, cobertura mínima de 90% e casos derivados do threat model | Confirma regras de negócio que scanners não compreendem, especialmente BOLA. |
| DAST | Após subir ambiente efêmero no CI e novamente em staging | OWASP ZAP Baseline passivo contra a aplicação local; alertas altos passam pelo gate | Precisa observar respostas HTTP e configuração efetiva. |
| IAST | Testes de integração em staging, antes da promoção | Decisão arquitetural documentada; agente ainda não adotado | Exige aplicação instrumentada e avaliação de overhead, privacidade e compatibilidade. |

O workflow está em `.github/workflows/security.yml`. Ele usa permissões mínimas (`contents: read`),
não persiste a credencial do checkout e utiliza segredo JWT exclusivo do ambiente efêmero. Nenhuma
credencial de produção é entregue a pull requests.

## Gate de merge

O job final depende de quatro jobs independentes: testes, SAST, dependências e DAST. Ele falha se
qualquer um não terminar com sucesso. A política aplicada é:

- CVSS 7,0 ou maior: bloqueio obrigatório;
- achado médio de SAST com confiança média/alta: bloqueio preventivo;
- CVSS 4,0–6,9 com impacto em autenticação, autorização, segredo, dado de saúde ou integridade da
  agenda: bloqueio após classificação de negócio;
- CVSS abaixo de 4,0: registra dívida e exige prazo, mas não bloqueia isoladamente;
- qualquer evidência de acesso não autorizado a dados de saúde bloqueia mesmo se o score técnico
  for inferior a 7,0.

O script `scripts/security_gate.py` aplica o limiar aos relatórios JSON do Bandit e ZAP. Trivy usa
seu próprio `exit-code: 1` para alta/crítica. Testes unitários verificam o comportamento do parser,
evitando que uma mudança acidental torne o gate permissivo.

## Segurança do próprio pipeline

- O workflow usa somente `pull_request`, não `pull_request_target`, portanto código de forks não
  recebe contexto privilegiado.
- Actions de checkout, Python e Trivy são fixadas em SHAs completos revisados, com a versão legível
  em comentário; o Dependabot propõe atualizações controladas semanalmente.
- Relatórios não devem conter tokens, bodies clínicos ou dados reais.
- A regra de proteção da branch deve exigir o check `Security gate`; essa configuração acontece no
  repositório GitHub e não pode ser imposta apenas pelo YAML.

## Referências de versões verificadas

- GitHub `actions/checkout` v7: https://github.com/actions/checkout
- GitHub `actions/setup-python` v7: https://github.com/actions/setup-python
- Trivy Action v0.36.0: https://github.com/aquasecurity/trivy-action/releases/tag/v0.36.0
- OWASP ZAP Baseline: https://github.com/marketplace/actions/zap-baseline-scan
