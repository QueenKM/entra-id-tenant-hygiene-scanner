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


SNAPSHOT_FIELDS = {
    "users": {"id": str, "display_name": str, "roles": list, "user_type": str,
              "last_sign_in_days_ago": int, "mfa_registered": bool},
    "service_principals": {"id": str, "display_name": str,
                           "credential_days_to_expiry": int, "high_privilege_permissions": bool},
    "conditional_access_policies": {"name": str, "state": str},
}


def validate_snapshot(snapshot: object) -> None:
    if not isinstance(snapshot, dict):
        raise ValueError("expected a JSON object")
    if type(snapshot.get("security_defaults_enabled")) is not bool:
        raise ValueError("security_defaults_enabled must be a boolean")
    for section, fields in SNAPSHOT_FIELDS.items():
        rows = snapshot.get(section)
        if not isinstance(rows, list):
            raise ValueError(f"{section} must be an array")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"{section}[{index}] must be an object")
            for field, field_type in fields.items():
                if type(row.get(field)) is not field_type:
                    raise ValueError(f"{section}[{index}].{field} must be {field_type.__name__}")
            if section == "users" and any(not isinstance(role, str) for role in row["roles"]):
                raise ValueError(f"{section}[{index}].roles must contain strings")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot_path)
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        validate_snapshot(snapshot)
    except (OSError, ValueError) as exc:
        parser.error(f"Insufficient snapshot data: {exc}")
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
