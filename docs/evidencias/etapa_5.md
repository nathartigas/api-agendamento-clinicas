# Evidências da etapa 5

Responsável: Nathalia Artigas

## Exercício 12 — pipeline DevSecOps

- Workflow: `.github/workflows/security.yml`.
- Política e fases do SDLC: `docs/devsecops_pipeline.md`.
- CVSS e impacto de negócio: `docs/cvss_priorizacao.md`.
- Rastreabilidade threat model → pytest: `docs/estrategia_testes_seguranca.md`.
- Gate determinístico: `scripts/security_gate.py`.
- Relatório SAST local: `docs/evidencias/bandit_etapa_5.json`.

O pipeline contém testes/cobertura, SAST com Bandit, análise de dependências com Trivy, DAST
passivo com OWASP ZAP e um job final que falha quando qualquer controle obrigatório falha.

## Comandos locais

```bash
ruff check .
pytest --cov=app --cov-fail-under=90 -q
bandit --recursive app scripts --format json --output bandit-report.json --exit-zero
python scripts/security_gate.py --bandit bandit-report.json
```

O teste local valida código, política do gate e os novos cenários de ownership de listagem, claim
de papel obsoleta, paginação abusiva e data sem timezone. Trivy e ZAP são executados no runner
Linux do GitHub, onde Docker está disponível. A execução passiva final e os artefatos foram
consolidados no capstone em `docs/evidencias/zap/`.

Resultado local: **28 testes aprovados**, **94,45% de cobertura**, Ruff sem erros e security gate
aprovado. O Bandit 1.9.4 analisou 1.090 linhas e produziu oito alertas baixos, todos falsos
positivos sobre os literais de domínio `"user"` e `"service"` usados como tipos de token; nenhum
achado médio ou alto foi encontrado.
