"""Security gate determinístico para relatórios Bandit e OWASP ZAP."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BlockingFinding:
    source: str
    severity: str
    title: str


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as report_file:
        report = json.load(report_file)
    if not isinstance(report, dict):
        raise ValueError(f"Relatório inválido: {path}")
    return report


def evaluate_bandit(path: Path) -> list[BlockingFinding]:
    """Bloqueia achados Bandit médios ou altos com confiança média/alta."""

    report = _read_json(path)
    blocking: list[BlockingFinding] = []
    ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    for issue in report.get("results", []):
        severity = str(issue.get("issue_severity", "LOW")).upper()
        confidence = str(issue.get("issue_confidence", "LOW")).upper()
        if ranks.get(severity, 0) >= 2 and ranks.get(confidence, 0) >= 2:
            blocking.append(
                BlockingFinding(
                    source="Bandit",
                    severity=severity,
                    title=str(issue.get("issue_text", issue.get("test_id", "finding"))),
                )
            )
    return blocking


def evaluate_zap(path: Path) -> list[BlockingFinding]:
    """Bloqueia alertas ZAP de risco alto (riskcode 3) ou superior."""

    report = _read_json(path)
    blocking: list[BlockingFinding] = []
    for site in report.get("site", []):
        for alert in site.get("alerts", []):
            try:
                risk_code = int(alert.get("riskcode", 0))
            except (TypeError, ValueError):
                risk_code = 0
            if risk_code >= 3:
                blocking.append(
                    BlockingFinding(
                        source="OWASP ZAP",
                        severity=str(alert.get("riskdesc", "High")).split()[0].upper(),
                        title=str(alert.get("name", alert.get("alert", "finding"))),
                    )
                )
    return blocking


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bloqueia findings acima da política definida")
    parser.add_argument("--bandit", type=Path)
    parser.add_argument("--zap", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings: list[BlockingFinding] = []
    if args.bandit:
        findings.extend(evaluate_bandit(args.bandit))
    if args.zap:
        findings.extend(evaluate_zap(args.zap))
    if findings:
        print("Security gate bloqueado:")
        for finding in findings:
            print(f"- [{finding.severity}] {finding.source}: {finding.title}")
        return 1
    print("Security gate aprovado: nenhum finding bloqueante.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
