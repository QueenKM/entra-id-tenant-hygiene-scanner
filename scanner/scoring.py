from __future__ import annotations

from collections import Counter

from .models import Finding


SEVERITY_PENALTY = {
    "high": 14,
    "medium": 7,
    "low": 3,
}


def calculate_health_score(findings: list[Finding]) -> int:
    score = 100
    for finding in findings:
        score -= SEVERITY_PENALTY.get(finding.severity.lower(), 5)
    return max(score, 0)


def summarize_findings(findings: list[Finding]) -> dict[str, object]:
    by_severity = Counter(finding.severity.lower() for finding in findings)
    by_category = Counter(finding.category for finding in findings)
    score = calculate_health_score(findings)
    if score >= 85:
        posture = "strong"
    elif score >= 65:
        posture = "watch"
    else:
        posture = "urgent"

    return {
        "score": score,
        "posture": posture,
        "by_severity": dict(by_severity),
        "by_category": dict(by_category),
        "total_findings": len(findings),
    }
