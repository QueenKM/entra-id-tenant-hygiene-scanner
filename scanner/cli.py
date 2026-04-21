from __future__ import annotations

import argparse
import json
from pathlib import Path

from .reporting import render_html, render_json, render_markdown
from .rules import evaluate_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan Entra ID tenant export data for hygiene gaps.")
    parser.add_argument("snapshot_path", help="Path to exported tenant snapshot JSON")
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--output", help="Optional output file path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_path)
    snapshot = json.loads(snapshot_path.read_text())
    findings = evaluate_snapshot(snapshot)

    if args.format == "json":
        rendered = render_json(findings)
    elif args.format == "html":
        rendered = render_html(findings, tenant_name=snapshot.get("tenant_name", "Tenant"))
    else:
        rendered = render_markdown(findings)

    if args.output:
        Path(args.output).write_text(rendered)
    else:
        print(rendered)


if __name__ == "__main__":
    main()
