import json
from pathlib import Path

from scripts.security_gate import evaluate_bandit, evaluate_zap


def write_report(path: Path, report: dict) -> Path:
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_bandit_gate_blocks_medium_high_confidence(tmp_path: Path) -> None:
    report = write_report(
        tmp_path / "bandit.json",
        {
            "results": [
                {
                    "issue_severity": "MEDIUM",
                    "issue_confidence": "HIGH",
                    "issue_text": "uso inseguro",
                },
                {
                    "issue_severity": "LOW",
                    "issue_confidence": "HIGH",
                    "issue_text": "informativo",
                },
            ]
        },
    )

    findings = evaluate_bandit(report)

    assert [finding.title for finding in findings] == ["uso inseguro"]


def test_zap_gate_blocks_only_high_risk(tmp_path: Path) -> None:
    report = write_report(
        tmp_path / "zap.json",
        {
            "site": [
                {
                    "alerts": [
                        {"riskcode": "3", "riskdesc": "High (High)", "name": "SQL Injection"},
                        {"riskcode": "2", "riskdesc": "Medium", "name": "Header ausente"},
                    ]
                }
            ]
        },
    )

    findings = evaluate_zap(report)

    assert [finding.title for finding in findings] == ["SQL Injection"]
