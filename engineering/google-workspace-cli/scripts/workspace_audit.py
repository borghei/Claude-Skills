#!/usr/bin/env python3
"""
Google Workspace Audit - Audit GWS configurations for security best practices.

Analyzes exported Workspace configuration JSON for security gaps including
2FA enforcement, password policies, sharing settings, and admin roles.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Finding:
    """An audit finding."""
    severity: str  # critical, high, medium, low
    category: str
    setting: str
    current_value: str
    expected_value: str
    message: str
    recommendation: str


# Default security policy expectations
SECURITY_POLICIES = {
    "2fa_enforcement": {
        "path": "security.2fa_enforcement",
        "expected": True,
        "severity": "critical",
        "category": "authentication",
        "message": "2-Step Verification is not enforced for all users.",
        "recommendation": "Enable 2-Step Verification enforcement in Admin Console > Security > Authentication.",
    },
    "password_min_length": {
        "path": "security.password_policy.min_length",
        "expected_min": 12,
        "severity": "critical",
        "category": "authentication",
        "message": "Password minimum length is below recommended threshold.",
        "recommendation": "Set minimum password length to 12+ characters in Admin Console > Security > Password management.",
    },
    "password_require_numbers": {
        "path": "security.password_policy.require_numbers",
        "expected": True,
        "severity": "high",
        "category": "authentication",
        "message": "Password policy does not require numbers.",
        "recommendation": "Enable number requirement in password policy.",
    },
    "password_require_symbols": {
        "path": "security.password_policy.require_symbols",
        "expected": True,
        "severity": "medium",
        "category": "authentication",
        "message": "Password policy does not require symbols.",
        "recommendation": "Enable symbol requirement in password policy.",
    },
    "external_sharing": {
        "path": "drive.external_sharing",
        "expected": "restricted",
        "severity": "high",
        "category": "data_protection",
        "message": "External file sharing is not restricted.",
        "recommendation": "Set Drive external sharing to 'restricted' or 'off' for sensitive OUs.",
    },
    "link_sharing_default": {
        "path": "drive.link_sharing_default",
        "expected": "restricted",
        "severity": "high",
        "category": "data_protection",
        "message": "Default link sharing allows broad access.",
        "recommendation": "Set default link sharing to 'Restricted' (only people with access).",
    },
    "third_party_apps": {
        "path": "security.third_party_app_access",
        "expected": "restricted",
        "severity": "high",
        "category": "app_security",
        "message": "Third-party app access is not restricted.",
        "recommendation": "Limit third-party app access. Review and whitelist approved apps only.",
    },
    "mobile_management": {
        "path": "devices.mobile_management",
        "expected": "advanced",
        "severity": "medium",
        "category": "device_security",
        "message": "Mobile device management is not set to advanced.",
        "recommendation": "Enable advanced mobile management for device encryption and remote wipe.",
    },
    "admin_recovery": {
        "path": "security.admin_recovery_options",
        "expected": True,
        "severity": "medium",
        "category": "authentication",
        "message": "Admin account recovery options may be misconfigured.",
        "recommendation": "Ensure super admin accounts have recovery phone and email configured.",
    },
    "session_duration": {
        "path": "security.session_duration_hours",
        "expected_max": 12,
        "severity": "medium",
        "category": "authentication",
        "message": "Session duration is longer than recommended.",
        "recommendation": "Set session duration to 12 hours or less for web sessions.",
    },
    "email_whitelist_only": {
        "path": "gmail.restrict_delivery",
        "expected": False,
        "severity": "low",
        "category": "email",
        "message": "Email delivery restrictions check.",
        "recommendation": "Review email delivery settings for appropriate restriction level.",
    },
}


def get_nested_value(data: Dict, path: str, default=None) -> Any:
    """Get a nested dictionary value by dot-separated path."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


class WorkspaceAuditor:
    """Audits Google Workspace configuration against security best practices."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.findings: List[Finding] = []

    def audit(self) -> List[Finding]:
        """Run full security audit."""
        self._audit_security_policies()
        self._audit_admin_roles()
        self._audit_api_access()
        self._audit_email_security()
        return self.findings

    def _audit_security_policies(self):
        """Audit against defined security policies."""
        for policy_name, policy in SECURITY_POLICIES.items():
            path = policy["path"]
            current = get_nested_value(self.config, path)

            if current is None:
                self.findings.append(Finding(
                    severity=policy["severity"],
                    category=policy["category"],
                    setting=path,
                    current_value="not configured",
                    expected_value=str(policy.get("expected", policy.get("expected_min", policy.get("expected_max", "")))),
                    message=policy["message"],
                    recommendation=policy["recommendation"],
                ))
                continue

            # Boolean check
            if "expected" in policy and isinstance(policy["expected"], bool):
                if current != policy["expected"]:
                    self.findings.append(Finding(
                        severity=policy["severity"],
                        category=policy["category"],
                        setting=path,
                        current_value=str(current),
                        expected_value=str(policy["expected"]),
                        message=policy["message"],
                        recommendation=policy["recommendation"],
                    ))

            # Minimum check
            elif "expected_min" in policy:
                try:
                    if int(current) < policy["expected_min"]:
                        self.findings.append(Finding(
                            severity=policy["severity"],
                            category=policy["category"],
                            setting=path,
                            current_value=str(current),
                            expected_value=f">= {policy['expected_min']}",
                            message=policy["message"],
                            recommendation=policy["recommendation"],
                        ))
                except (ValueError, TypeError):
                    pass

            # Maximum check
            elif "expected_max" in policy:
                try:
                    if int(current) > policy["expected_max"]:
                        self.findings.append(Finding(
                            severity=policy["severity"],
                            category=policy["category"],
                            setting=path,
                            current_value=str(current),
                            expected_value=f"<= {policy['expected_max']}",
                            message=policy["message"],
                            recommendation=policy["recommendation"],
                        ))
                except (ValueError, TypeError):
                    pass

            # String check
            elif "expected" in policy and isinstance(policy["expected"], str):
                if str(current).lower() != policy["expected"].lower():
                    self.findings.append(Finding(
                        severity=policy["severity"],
                        category=policy["category"],
                        setting=path,
                        current_value=str(current),
                        expected_value=policy["expected"],
                        message=policy["message"],
                        recommendation=policy["recommendation"],
                    ))

    def _audit_admin_roles(self):
        """Audit admin role assignments."""
        admins = get_nested_value(self.config, "admin.super_admins", [])
        if isinstance(admins, list):
            if len(admins) > 5:
                self.findings.append(Finding(
                    severity="high",
                    category="access_control",
                    setting="admin.super_admins",
                    current_value=f"{len(admins)} super admins",
                    expected_value="<= 5 super admins",
                    message=f"Too many super admin accounts ({len(admins)}). Excessive privileges increase risk.",
                    recommendation="Reduce super admin count. Use delegated admin roles for specific tasks.",
                ))

            if len(admins) < 2:
                self.findings.append(Finding(
                    severity="medium",
                    category="access_control",
                    setting="admin.super_admins",
                    current_value=f"{len(admins)} super admin(s)",
                    expected_value=">= 2 super admins",
                    message="Too few super admins. Single point of failure for admin access.",
                    recommendation="Designate at least 2 super admin accounts for redundancy.",
                ))

    def _audit_api_access(self):
        """Audit API and OAuth app access."""
        api_clients = get_nested_value(self.config, "security.api_clients", [])
        if isinstance(api_clients, list):
            for client in api_clients:
                if isinstance(client, dict):
                    scopes = client.get("scopes", [])
                    name = client.get("name", "unknown")
                    if isinstance(scopes, list) and len(scopes) > 10:
                        self.findings.append(Finding(
                            severity="medium",
                            category="app_security",
                            setting=f"security.api_clients.{name}",
                            current_value=f"{len(scopes)} scopes",
                            expected_value="minimal scopes",
                            message=f"API client '{name}' has {len(scopes)} scopes. Excessive scope grants increase risk.",
                            recommendation=f"Review scopes for '{name}' and remove unnecessary permissions.",
                        ))

    def _audit_email_security(self):
        """Audit email-related security settings."""
        spoofing = get_nested_value(self.config, "gmail.spoofing_protection")
        if spoofing is not None and not spoofing:
            self.findings.append(Finding(
                severity="high",
                category="email",
                setting="gmail.spoofing_protection",
                current_value="disabled",
                expected_value="enabled",
                message="Email spoofing protection is not enabled.",
                recommendation="Enable spoofing protection in Gmail > Safety > Spoofing and authentication.",
            ))

        dmarc = get_nested_value(self.config, "dns.dmarc_policy")
        if dmarc and str(dmarc).lower() == "none":
            self.findings.append(Finding(
                severity="high",
                category="email",
                setting="dns.dmarc_policy",
                current_value="none",
                expected_value="quarantine or reject",
                message="DMARC policy is set to 'none', providing no email protection.",
                recommendation="Set DMARC policy to 'quarantine' or 'reject' after monitoring period.",
            ))


def generate_sample_config() -> Dict[str, Any]:
    """Generate a sample configuration for testing."""
    return {
        "security": {
            "2fa_enforcement": False,
            "password_policy": {
                "min_length": 8,
                "require_numbers": True,
                "require_symbols": False,
            },
            "third_party_app_access": "unrestricted",
            "session_duration_hours": 24,
            "admin_recovery_options": True,
            "api_clients": [],
        },
        "drive": {
            "external_sharing": "allowed",
            "link_sharing_default": "anyone_with_link",
        },
        "devices": {
            "mobile_management": "basic",
        },
        "admin": {
            "super_admins": ["admin@example.com"],
        },
        "gmail": {
            "spoofing_protection": True,
            "restrict_delivery": False,
        },
        "dns": {
            "dmarc_policy": "none",
        },
    }


def format_text(findings: List[Finding]) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("GOOGLE WORKSPACE SECURITY AUDIT REPORT")
    lines.append("=" * 60)

    by_severity = {}
    for f in findings:
        by_severity.setdefault(f.severity, []).append(f)

    lines.append(f"\nTotal findings: {len(findings)}")
    for sev in ["critical", "high", "medium", "low"]:
        count = len(by_severity.get(sev, []))
        if count:
            lines.append(f"  {sev.upper()}: {count}")

    lines.append("-" * 60)

    for sev in ["critical", "high", "medium", "low"]:
        group = by_severity.get(sev, [])
        if not group:
            continue
        lines.append(f"\n[{sev.upper()}]")
        for f in group:
            lines.append(f"  [{f.category}] {f.setting}")
            lines.append(f"    Issue: {f.message}")
            lines.append(f"    Current: {f.current_value} | Expected: {f.expected_value}")
            lines.append(f"    Fix: {f.recommendation}")
            lines.append("")

    if not findings:
        lines.append("\nNo security issues found. Configuration follows best practices.")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(findings: List[Finding]) -> str:
    """Format as JSON."""
    return json.dumps({
        "findings": [asdict(f) for f in findings],
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.severity == "critical"),
            "high": sum(1 for f in findings if f.severity == "high"),
            "medium": sum(1 for f in findings if f.severity == "medium"),
            "low": sum(1 for f in findings if f.severity == "low"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Audit Google Workspace configuration for security best practices."
    )
    parser.add_argument("--config", "-c", help="Path to GWS configuration JSON export")
    parser.add_argument("--sample", action="store_true", help="Run audit against sample config for demo")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--generate-sample", action="store_true",
                       help="Output sample config JSON for testing")
    args = parser.parse_args()

    if args.generate_sample:
        print(json.dumps(generate_sample_config(), indent=2))
        return

    if args.sample:
        config = generate_sample_config()
    elif args.config:
        path = Path(args.config)
        if not path.exists():
            print(f"Error: File not found: {args.config}", file=sys.stderr)
            sys.exit(2)
        try:
            config = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        parser.error("Provide --config or --sample")
        return

    auditor = WorkspaceAuditor(config)
    findings = auditor.audit()

    if args.format == "json":
        print(format_json(findings))
    else:
        print(format_text(findings))

    if any(f.severity == "critical" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
