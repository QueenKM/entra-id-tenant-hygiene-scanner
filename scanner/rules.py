from __future__ import annotations

from typing import Any

from .models import Finding

PRIVILEGED_ROLES = {
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Exchange Administrator",
}


def evaluate_snapshot(snapshot: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_privileged_users_without_mfa(snapshot))
    findings.extend(_stale_privileged_accounts(snapshot))
    findings.extend(_guest_admins(snapshot))
    findings.extend(_expiring_app_credentials(snapshot))
    findings.extend(_weak_mfa_coverage(snapshot))
    findings.extend(_legacy_auth_not_blocked(snapshot))
    return findings


def _privileged_users_without_mfa(snapshot: dict[str, Any]) -> list[Finding]:
    findings = []
    for user in snapshot.get("users", []):
        if PRIVILEGED_ROLES.intersection(user.get("roles", [])) and not user.get("mfa_registered", False):
            findings.append(
                Finding(
                    id=f"user-mfa-{user['id']}",
                    severity="high",
                    category="Identity Protection",
                    title=f"Privileged account without MFA: {user['display_name']}",
                    evidence=f"Roles: {', '.join(user.get('roles', []))}",
                    recommendation="Require MFA registration and validate break-glass exceptions explicitly.",
                )
            )
    return findings


def _stale_privileged_accounts(snapshot: dict[str, Any]) -> list[Finding]:
    findings = []
    for user in snapshot.get("users", []):
        if PRIVILEGED_ROLES.intersection(user.get("roles", [])) and user.get("last_sign_in_days_ago", 0) > 45:
            findings.append(
                Finding(
                    id=f"user-stale-{user['id']}",
                    severity="medium",
                    category="Account Hygiene",
                    title=f"Stale privileged account: {user['display_name']}",
                    evidence=f"Last sign-in was {user['last_sign_in_days_ago']} days ago.",
                    recommendation="Review whether the role is still needed and disable or reduce standing privilege.",
                )
            )
    return findings


def _guest_admins(snapshot: dict[str, Any]) -> list[Finding]:
    findings = []
    for user in snapshot.get("users", []):
        if user.get("user_type") == "Guest" and PRIVILEGED_ROLES.intersection(user.get("roles", [])):
            findings.append(
                Finding(
                    id=f"guest-admin-{user['id']}",
                    severity="high",
                    category="External Access",
                    title=f"Guest account holds privileged role: {user['display_name']}",
                    evidence=f"Guest user assigned: {', '.join(user.get('roles', []))}",
                    recommendation="Replace guest standing privilege with just-in-time or internal admin accounts.",
                )
            )
    return findings


def _expiring_app_credentials(snapshot: dict[str, Any]) -> list[Finding]:
    findings = []
    for app in snapshot.get("service_principals", []):
        if app.get("credential_days_to_expiry", 999) <= 30 and app.get("high_privilege_permissions", False):
            findings.append(
                Finding(
                    id=f"sp-expiry-{app['id']}",
                    severity="medium",
                    category="Application Security",
                    title=f"High-privilege app credential expiring soon: {app['display_name']}",
                    evidence=f"Credential expiry in {app['credential_days_to_expiry']} days.",
                    recommendation="Rotate credentials now and prefer managed identity or certificate-backed auth.",
                )
            )
    return findings


def _weak_mfa_coverage(snapshot: dict[str, Any]) -> list[Finding]:
    enabled_policy_names = {
        policy["name"].lower()
        for policy in snapshot.get("conditional_access_policies", [])
        if policy.get("state") == "enabled"
    }
    if snapshot.get("security_defaults_enabled"):
        return []
    if any("mfa" in name for name in enabled_policy_names):
        return []

    return [
        Finding(
            id="policy-mfa-coverage",
            severity="high",
            category="Policy Coverage",
            title="No strong MFA enforcement policy detected",
            evidence="Security defaults are disabled and no enabled Conditional Access policy includes MFA enforcement.",
            recommendation="Enable security defaults or publish explicit Conditional Access MFA coverage for admins and core users.",
        )
    ]


def _legacy_auth_not_blocked(snapshot: dict[str, Any]) -> list[Finding]:
    enabled_policy_names = {
        policy["name"].lower()
        for policy in snapshot.get("conditional_access_policies", [])
        if policy.get("state") == "enabled"
    }
    if any("legacy" in name and ("block" in name or "disable" in name) for name in enabled_policy_names):
        return []

    return [
        Finding(
            id="policy-legacy-auth",
            severity="medium",
            category="Authentication",
            title="Legacy authentication is not clearly blocked",
            evidence="No enabled Conditional Access policy name indicates a legacy authentication block control.",
            recommendation="Add a verified control that blocks legacy authentication and validate exceptions.",
        )
    ]
