#!/usr/bin/env python3
"""Permission Auditor - Audit Atlassian permission schemes for security compliance.

Reads permission configuration data and identifies overly permissive access,
orphaned permissions, and compliance gaps against best practices.

Usage:
    python permission_auditor.py --config permissions.json
    python permission_auditor.py --config permissions.json --json
    python permission_auditor.py --example
"""

import argparse
import json
import sys
from datetime import datetime


PERMISSION_RISKS = {
    "individual_permissions": {"severity": "High", "description": "Individual user permissions (use groups instead)"},
    "admin_overflow": {"severity": "High", "description": "Too many org/project admins (limit to 2-3)"},
    "no_mfa": {"severity": "Critical", "description": "Admin accounts without MFA enforced"},
    "stale_accounts": {"severity": "Medium", "description": "Inactive accounts with active permissions"},
    "public_project": {"severity": "Medium", "description": "Project visible to all authenticated users"},
    "everyone_group": {"severity": "High", "description": "Sensitive permissions granted to 'everyone' group"},
    "no_audit_trail": {"severity": "High", "description": "Admin actions not logged in audit trail"},
}


def load_data(path: str) -> dict:
    """Load permission config from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def audit_permissions(data: dict) -> dict:
    """Audit permissions against security best practices."""
    org = data.get("organization", "Unknown")
    projects = data.get("projects", [])
    users = data.get("users", [])
    global_settings = data.get("global_settings", {})

    findings = []
    total_score = 100

    # Check global settings
    if not global_settings.get("mfa_enforced", False):
        findings.append({
            "id": "GLOBAL-001",
            "severity": "Critical",
            "category": "Authentication",
            "finding": "MFA is not enforced organization-wide",
            "recommendation": "Enable mandatory MFA for all users, especially admins.",
        })
        total_score -= 20

    if not global_settings.get("sso_enabled", False):
        findings.append({
            "id": "GLOBAL-002",
            "severity": "High",
            "category": "Authentication",
            "finding": "SSO is not configured",
            "recommendation": "Configure SAML SSO with your identity provider for centralized access control.",
        })
        total_score -= 10

    if not global_settings.get("audit_logging", False):
        findings.append({
            "id": "GLOBAL-003",
            "severity": "High",
            "category": "Compliance",
            "finding": "Audit logging is not enabled",
            "recommendation": "Enable comprehensive audit logging and export to SIEM for compliance.",
        })
        total_score -= 10

    # Check admin count
    admin_users = [u for u in users if u.get("role") == "admin"]
    if len(admin_users) > 3:
        findings.append({
            "id": "USER-001",
            "severity": "High",
            "category": "Access Control",
            "finding": f"Too many org admins: {len(admin_users)} (recommended: 2-3)",
            "recommendation": "Reduce org admin count. Use project admins for delegation.",
            "details": [u.get("name", "Unknown") for u in admin_users],
        })
        total_score -= 10

    # Check for inactive users with access
    inactive_users = [u for u in users if u.get("status") == "inactive" and u.get("has_access", True)]
    if inactive_users:
        findings.append({
            "id": "USER-002",
            "severity": "Medium",
            "category": "Access Control",
            "finding": f"{len(inactive_users)} inactive user(s) still have product access",
            "recommendation": "Deactivate or remove access for inactive accounts immediately.",
            "details": [u.get("name", "Unknown") for u in inactive_users],
        })
        total_score -= 5 * min(len(inactive_users), 4)

    # Check admin MFA
    admin_no_mfa = [u for u in admin_users if not u.get("mfa_enabled", False)]
    if admin_no_mfa:
        findings.append({
            "id": "USER-003",
            "severity": "Critical",
            "category": "Authentication",
            "finding": f"{len(admin_no_mfa)} admin(s) without MFA enabled",
            "recommendation": "Enforce MFA for all admin accounts immediately.",
            "details": [u.get("name", "Unknown") for u in admin_no_mfa],
        })
        total_score -= 15

    # Check projects
    for proj in projects:
        proj_name = proj.get("name", "Unknown")

        # Individual permissions
        individual_perms = proj.get("individual_permissions", [])
        if individual_perms:
            findings.append({
                "id": f"PROJ-{proj_name}-001",
                "severity": "High",
                "category": "Permission Design",
                "finding": f"Project '{proj_name}' has {len(individual_perms)} individual permission(s) (use groups instead)",
                "recommendation": "Replace individual permissions with group-based access for scalability.",
                "details": individual_perms,
            })
            total_score -= 5

        # Public access
        if proj.get("public_access", False):
            findings.append({
                "id": f"PROJ-{proj_name}-002",
                "severity": "Medium",
                "category": "Access Control",
                "finding": f"Project '{proj_name}' is accessible to all authenticated users",
                "recommendation": "Review if public access is intentional. Restrict to relevant groups if not.",
            })
            total_score -= 3

        # Everyone group with write access
        groups = proj.get("group_permissions", {})
        if "everyone" in [g.lower() for g in groups.keys()]:
            everyone_perms = groups.get("everyone", groups.get("Everyone", []))
            write_perms = [p for p in everyone_perms if p in ("edit", "create", "delete", "admin")]
            if write_perms:
                findings.append({
                    "id": f"PROJ-{proj_name}-003",
                    "severity": "High",
                    "category": "Permission Design",
                    "finding": f"Project '{proj_name}' grants write access ({', '.join(write_perms)}) to 'everyone' group",
                    "recommendation": "Remove write permissions from 'everyone' group. Grant to specific teams only.",
                })
                total_score -= 10

    # Score classification
    total_score = max(0, total_score)
    if total_score >= 90:
        rating = "Compliant"
    elif total_score >= 70:
        rating = "Minor Gaps"
    elif total_score >= 50:
        rating = "Significant Gaps"
    else:
        rating = "Non-Compliant"

    # Severity summary
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        severity_counts[f["severity"]] = severity_counts.get(f["severity"], 0) + 1

    return {
        "organization": org,
        "audit_date": datetime.now().strftime("%Y-%m-%d"),
        "compliance_score": total_score,
        "rating": rating,
        "total_findings": len(findings),
        "severity_distribution": severity_counts,
        "users_audited": len(users),
        "projects_audited": len(projects),
        "findings": findings,
    }


def print_report(result: dict) -> None:
    """Print human-readable audit report."""
    print(f"\nPermission Audit: {result['organization']}")
    print(f"Date: {result['audit_date']}")
    print("=" * 65)
    print(f"Compliance Score: {result['compliance_score']}/100 ({result['rating']})")
    print(f"Users: {result['users_audited']}  |  Projects: {result['projects_audited']}  |  Findings: {result['total_findings']}")

    sd = result["severity_distribution"]
    print(f"Severity: Critical={sd.get('Critical',0)}, High={sd.get('High',0)}, Medium={sd.get('Medium',0)}, Low={sd.get('Low',0)}")

    if result["findings"]:
        print(f"\nFindings:")
        for f in sorted(result["findings"], key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}[x["severity"]]):
            print(f"\n  [{f['severity']}] {f['id']}: {f['finding']}")
            print(f"    Recommendation: {f['recommendation']}")
            if f.get("details"):
                details = f["details"][:5]
                print(f"    Details: {', '.join(str(d) for d in details)}")
    print()


def print_example() -> None:
    """Print example permission config JSON."""
    example = {
        "organization": "Acme Corp",
        "global_settings": {"mfa_enforced": False, "sso_enabled": True, "audit_logging": True},
        "users": [
            {"name": "Alice", "role": "admin", "status": "active", "mfa_enabled": True, "has_access": True},
            {"name": "Bob", "role": "admin", "status": "active", "mfa_enabled": False, "has_access": True},
            {"name": "Carol", "role": "user", "status": "inactive", "mfa_enabled": False, "has_access": True},
            {"name": "Dave", "role": "user", "status": "active", "mfa_enabled": True, "has_access": True},
        ],
        "projects": [
            {
                "name": "PROJ-A",
                "public_access": False,
                "individual_permissions": ["carol@acme.com"],
                "group_permissions": {"engineering": ["view", "edit", "create"], "everyone": ["view"]},
            },
            {
                "name": "PROJ-B",
                "public_access": True,
                "individual_permissions": [],
                "group_permissions": {"Everyone": ["view", "edit"], "admins": ["admin"]},
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Audit Atlassian permission schemes for security compliance."
    )
    parser.add_argument("--config", type=str, help="Path to permissions JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example config and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.config:
        parser.error("--config is required (use --example to see the expected format)")

    data = load_data(args.config)
    result = audit_permissions(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
