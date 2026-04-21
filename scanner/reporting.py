from __future__ import annotations

import json

from .models import Finding
from .scoring import summarize_findings


def render_markdown(findings: list[Finding]) -> str:
    summary = summarize_findings(findings)
    lines = [
        "# Entra ID Hygiene Findings",
        "",
        f"Tenant health score: **{summary['score']} / 100**",
        f"Posture: **{str(summary['posture']).upper()}**",
        f"Total findings: {len(findings)}",
        "",
    ]
    for finding in findings:
        lines.extend(
            [
                f"## [{finding.severity.upper()}] {finding.title}",
                "",
                f"- Category: {finding.category}",
                f"- Evidence: {finding.evidence}",
                f"- Recommendation: {finding.recommendation}",
                "",
            ]
        )
    return "\n".join(lines)


def render_json(findings: list[Finding]) -> str:
    return json.dumps(
        {
            "summary": summarize_findings(findings),
            "findings": [finding.to_dict() for finding in findings],
        },
        indent=2,
    )


def render_html(findings: list[Finding], tenant_name: str = "Tenant") -> str:
    summary = summarize_findings(findings)
    severity_cards = "".join(
        f"""
        <article class="metric-card">
          <span class="metric-label">{severity.title()}</span>
          <strong>{count}</strong>
        </article>
        """
        for severity, count in sorted(summary["by_severity"].items())
    )

    finding_cards = "".join(
        f"""
        <article class="finding-card {finding.severity.lower()}">
          <p class="finding-kicker">{finding.category}</p>
          <h3>{finding.title}</h3>
          <p><strong>Evidence:</strong> {finding.evidence}</p>
          <p><strong>Recommendation:</strong> {finding.recommendation}</p>
        </article>
        """
        for finding in findings
    )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Entra ID Hygiene Report</title>
    <style>
      :root {{
        --bg: #f4f8fb;
        --panel: rgba(255, 255, 255, 0.92);
        --text: #173249;
        --muted: #5a7588;
        --teal: #0b7d74;
        --blue: #156cbe;
        --amber: #d97a10;
        --border: rgba(23, 50, 73, 0.12);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "SF Pro Display", "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(11, 125, 116, 0.16), transparent 30%),
          radial-gradient(circle at top right, rgba(21, 108, 190, 0.16), transparent 28%),
          linear-gradient(180deg, #f8fcff 0%, #eef5f9 100%);
        color: var(--text);
      }}
      main {{
        max-width: 1160px;
        margin: 0 auto;
        padding: 48px 24px 64px;
      }}
      .hero {{
        display: grid;
        gap: 18px;
        margin-bottom: 28px;
      }}
      .hero h1 {{
        margin: 0;
        font-size: clamp(2.4rem, 5vw, 4rem);
        line-height: 1.02;
      }}
      .hero p {{
        margin: 0;
        color: var(--muted);
        max-width: 760px;
      }}
      .summary-grid {{
        display: grid;
        grid-template-columns: 1.4fr 1fr;
        gap: 20px;
        margin-bottom: 24px;
      }}
      .panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 20px 44px rgba(23, 50, 73, 0.08);
        backdrop-filter: blur(14px);
      }}
      .score {{
        display: flex;
        align-items: center;
        gap: 18px;
      }}
      .score-badge {{
        min-width: 128px;
        min-height: 128px;
        border-radius: 28px;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #0b7d74, #156cbe);
        color: white;
      }}
      .score-badge strong {{
        font-size: 2.6rem;
      }}
      .score-text span,
      .metric-label,
      .finding-kicker {{
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.8rem;
        color: var(--muted);
      }}
      .metrics {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
      }}
      .metric-card {{
        border-radius: 18px;
        padding: 16px;
        background: #f6fafc;
        border: 1px solid var(--border);
      }}
      .metric-card strong {{
        font-size: 1.6rem;
      }}
      .findings {{
        display: grid;
        gap: 16px;
      }}
      .finding-card {{
        border-radius: 22px;
        padding: 22px;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--border);
      }}
      .finding-card.high {{
        border-left: 8px solid #d97a10;
      }}
      .finding-card.medium {{
        border-left: 8px solid #156cbe;
      }}
      .finding-card.low {{
        border-left: 8px solid #0b7d74;
      }}
      .finding-card h3 {{
        margin: 8px 0 12px;
      }}
      @media (max-width: 860px) {{
        .summary-grid {{
          grid-template-columns: 1fr;
        }}
        .metrics {{
          grid-template-columns: 1fr 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p>Entra ID Tenant Hygiene Scanner</p>
        <h1>{tenant_name} identity posture review</h1>
        <p>
          A recruiter-friendly security report that converts exported tenant state into
          prioritized findings, posture scoring, and remediation guidance.
        </p>
      </section>

      <section class="summary-grid">
        <article class="panel score">
          <div class="score-badge">
            <div>
              <strong>{summary['score']}</strong>
              <span>/100</span>
            </div>
          </div>
          <div class="score-text">
            <span>Posture</span>
            <h2>{str(summary['posture']).title()}</h2>
            <p>Total findings: {summary['total_findings']}</p>
          </div>
        </article>

        <article class="panel metrics">
          {severity_cards}
        </article>
      </section>

      <section class="findings">
        {finding_cards}
      </section>
    </main>
  </body>
</html>
"""
