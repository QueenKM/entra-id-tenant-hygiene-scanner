import json
import unittest
from pathlib import Path

from scanner.reporting import render_html
from scanner.rules import evaluate_snapshot
from scanner.scoring import calculate_health_score


class RulesTests(unittest.TestCase):
    def test_sample_snapshot_produces_findings(self) -> None:
        snapshot = json.loads(
            Path(__file__).resolve().parent.parent.joinpath("sample_data", "tenant_snapshot.json").read_text()
        )
        findings = evaluate_snapshot(snapshot)
        self.assertGreaterEqual(len(findings), 4)
        self.assertTrue(any("without MFA" in finding.title for finding in findings))
        self.assertTrue(any("Legacy authentication" in finding.title for finding in findings))
        self.assertLess(calculate_health_score(findings), 100)

    def test_html_report_contains_health_score(self) -> None:
        snapshot = json.loads(
            Path(__file__).resolve().parent.parent.joinpath("sample_data", "tenant_snapshot.json").read_text()
        )
        findings = evaluate_snapshot(snapshot)
        report = render_html(findings, tenant_name=snapshot["tenant_name"])
        self.assertIn("identity posture review", report)
        self.assertIn("Total findings", report)


if __name__ == "__main__":
    unittest.main()
