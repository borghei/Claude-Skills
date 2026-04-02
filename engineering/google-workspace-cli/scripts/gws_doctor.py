#!/usr/bin/env python3
"""
GWS Doctor - Diagnostic tool for common Google Workspace issues.

Checks DNS record format, email configuration, and common integration
patterns. Validates SPF, DKIM, DMARC records and provides fix guidance.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any


@dataclass
class DiagnosticResult:
    """A diagnostic check result."""
    check: str
    status: str  # pass, fail, warn, skip
    category: str
    message: str
    detail: Optional[str]
    fix: Optional[str]


GOOGLE_MX_RECORDS = [
    "ASPMX.L.GOOGLE.COM",
    "ALT1.ASPMX.L.GOOGLE.COM",
    "ALT2.ASPMX.L.GOOGLE.COM",
    "ALT3.ASPMX.L.GOOGLE.COM",
    "ALT4.ASPMX.L.GOOGLE.COM",
]

SPF_PATTERN = re.compile(r'v=spf1\s+.*include:_spf\.google\.com\s+.*(?:~all|-all)')
DMARC_PATTERN = re.compile(r'v=DMARC1;\s*p=(\w+)')
DKIM_PATTERN = re.compile(r'v=DKIM1;\s*k=rsa;\s*p=\S+')


class GWSDiagnostics:
    """Runs diagnostic checks on Google Workspace configuration."""

    def __init__(self, config: Dict[str, Any], checks: List[str]):
        self.config = config
        self.checks = checks
        self.results: List[DiagnosticResult] = []

    def run(self) -> List[DiagnosticResult]:
        """Run selected diagnostics."""
        check_map = {
            "dns": self._check_dns,
            "email": self._check_email,
            "security": self._check_security,
            "integration": self._check_integration,
            "consistency": self._check_consistency,
        }

        for check_name in self.checks:
            if check_name == "all":
                for func in check_map.values():
                    func()
                break
            elif check_name in check_map:
                check_map[check_name]()

        return self.results

    def _check_dns(self):
        """Check DNS record configurations."""
        dns = self.config.get("dns", {})

        # MX Records
        mx_records = dns.get("mx_records", [])
        if not mx_records:
            self.results.append(DiagnosticResult(
                check="MX Records",
                status="fail",
                category="dns",
                message="No MX records configured.",
                detail="MX records are required for email delivery.",
                fix="Add Google Workspace MX records: ASPMX.L.GOOGLE.COM (priority 1), "
                    "ALT1.ASPMX.L.GOOGLE.COM (priority 5), etc.",
            ))
        else:
            google_mx_found = any(
                any(gmx in str(mx).upper() for gmx in GOOGLE_MX_RECORDS)
                for mx in mx_records
            )
            if google_mx_found:
                self.results.append(DiagnosticResult(
                    check="MX Records",
                    status="pass",
                    category="dns",
                    message="Google Workspace MX records found.",
                    detail=f"MX records: {', '.join(str(mx) for mx in mx_records[:3])}",
                    fix=None,
                ))
            else:
                self.results.append(DiagnosticResult(
                    check="MX Records",
                    status="warn",
                    category="dns",
                    message="MX records present but Google Workspace records not detected.",
                    detail=f"Current MX: {', '.join(str(mx) for mx in mx_records[:3])}",
                    fix="Verify MX records point to Google: ASPMX.L.GOOGLE.COM",
                ))

        # SPF Record
        spf = dns.get("spf_record", "")
        if not spf:
            self.results.append(DiagnosticResult(
                check="SPF Record",
                status="fail",
                category="dns",
                message="No SPF record configured.",
                detail="SPF validates email sender identity.",
                fix='Add TXT record: "v=spf1 include:_spf.google.com ~all"',
            ))
        elif SPF_PATTERN.search(spf):
            mechanism = "~all (softfail)" if "~all" in spf else "-all (hardfail)"
            self.results.append(DiagnosticResult(
                check="SPF Record",
                status="pass",
                category="dns",
                message=f"SPF record correctly includes Google and uses {mechanism}.",
                detail=spf,
                fix=None,
            ))
        elif "_spf.google.com" in spf:
            self.results.append(DiagnosticResult(
                check="SPF Record",
                status="warn",
                category="dns",
                message="SPF record includes Google but may have formatting issues.",
                detail=spf,
                fix='Ensure format is: "v=spf1 include:_spf.google.com ~all"',
            ))
        else:
            self.results.append(DiagnosticResult(
                check="SPF Record",
                status="fail",
                category="dns",
                message="SPF record does not include Google Workspace.",
                detail=spf,
                fix='Add "include:_spf.google.com" to your SPF record.',
            ))

        # DKIM
        dkim = dns.get("dkim_record", "")
        if not dkim:
            self.results.append(DiagnosticResult(
                check="DKIM Record",
                status="fail",
                category="dns",
                message="No DKIM record configured.",
                detail="DKIM signs outgoing emails to prevent tampering.",
                fix="Enable DKIM in Admin Console > Apps > Google Workspace > Gmail > Authenticate email. "
                    "Then add the CNAME or TXT record to your DNS.",
            ))
        elif DKIM_PATTERN.search(dkim) or "CNAME" in str(dkim):
            self.results.append(DiagnosticResult(
                check="DKIM Record",
                status="pass",
                category="dns",
                message="DKIM record found.",
                detail=f"DKIM: {str(dkim)[:80]}...",
                fix=None,
            ))

        # DMARC
        dmarc = dns.get("dmarc_record", "")
        if not dmarc:
            self.results.append(DiagnosticResult(
                check="DMARC Record",
                status="fail",
                category="dns",
                message="No DMARC record configured.",
                detail="DMARC enforces SPF and DKIM policies.",
                fix='Add TXT record at _dmarc.yourdomain.com: '
                    '"v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com"',
            ))
        else:
            dmarc_match = DMARC_PATTERN.search(dmarc)
            if dmarc_match:
                policy = dmarc_match.group(1).lower()
                if policy == "none":
                    self.results.append(DiagnosticResult(
                        check="DMARC Record",
                        status="warn",
                        category="dns",
                        message="DMARC policy is 'none' (monitoring only, no enforcement).",
                        detail=dmarc,
                        fix="After monitoring period, change p=none to p=quarantine or p=reject.",
                    ))
                else:
                    self.results.append(DiagnosticResult(
                        check="DMARC Record",
                        status="pass",
                        category="dns",
                        message=f"DMARC record with '{policy}' policy found.",
                        detail=dmarc,
                        fix=None,
                    ))

    def _check_email(self):
        """Check email configuration."""
        email = self.config.get("email", {})

        # Routing
        routing = email.get("routing", "")
        if routing:
            self.results.append(DiagnosticResult(
                check="Email Routing",
                status="pass" if routing == "direct" else "warn",
                category="email",
                message=f"Email routing: {routing}.",
                detail="Direct routing is simplest. Third-party routing adds complexity.",
                fix=None if routing == "direct" else "Review routing configuration for necessity.",
            ))

        # Spam filtering
        spam = email.get("spam_filtering", True)
        if not spam:
            self.results.append(DiagnosticResult(
                check="Spam Filtering",
                status="fail",
                category="email",
                message="Spam filtering appears to be disabled.",
                detail=None,
                fix="Enable spam filtering in Gmail > Spam, phishing, and malware.",
            ))
        else:
            self.results.append(DiagnosticResult(
                check="Spam Filtering",
                status="pass",
                category="email",
                message="Spam filtering is enabled.",
                detail=None,
                fix=None,
            ))

    def _check_security(self):
        """Check security settings."""
        security = self.config.get("security", {})

        # 2FA
        tfa = security.get("2fa_enforcement", False)
        self.results.append(DiagnosticResult(
            check="2FA Enforcement",
            status="pass" if tfa else "fail",
            category="security",
            message=f"2-Step Verification enforcement: {'enabled' if tfa else 'disabled'}.",
            detail=None,
            fix=None if tfa else "Enable 2FA enforcement in Admin Console > Security > Authentication.",
        ))

        # Session control
        session = security.get("session_duration_hours", 24)
        if session and int(session) > 12:
            self.results.append(DiagnosticResult(
                check="Session Duration",
                status="warn",
                category="security",
                message=f"Session duration ({session}h) is longer than recommended (12h).",
                detail=None,
                fix="Reduce session duration to 12 hours or less.",
            ))
        else:
            self.results.append(DiagnosticResult(
                check="Session Duration",
                status="pass",
                category="security",
                message=f"Session duration ({session}h) is within recommended range.",
                detail=None,
                fix=None,
            ))

    def _check_integration(self):
        """Check common integration patterns."""
        integrations = self.config.get("integrations", {})

        # SSO
        sso = integrations.get("sso_enabled", False)
        sso_provider = integrations.get("sso_provider", "")
        if sso:
            self.results.append(DiagnosticResult(
                check="SSO Configuration",
                status="pass",
                category="integration",
                message=f"SSO enabled via {sso_provider or 'configured provider'}.",
                detail=None,
                fix=None,
            ))
        else:
            self.results.append(DiagnosticResult(
                check="SSO Configuration",
                status="warn",
                category="integration",
                message="SSO is not configured.",
                detail="SSO provides centralized authentication control.",
                fix="Consider configuring SSO if using an identity provider (Okta, Azure AD, etc.).",
            ))

        # LDAP/Directory Sync
        dir_sync = integrations.get("directory_sync", False)
        if dir_sync:
            self.results.append(DiagnosticResult(
                check="Directory Sync",
                status="pass",
                category="integration",
                message="Directory synchronization is active.",
                detail=None,
                fix=None,
            ))

    def _check_consistency(self):
        """Check for configuration consistency issues."""
        security = self.config.get("security", {})
        drive = self.config.get("drive", {})

        # Inconsistency: strict auth but open sharing
        tfa = security.get("2fa_enforcement", False)
        sharing = drive.get("external_sharing", "")
        if tfa and sharing in ("allowed", "unrestricted"):
            self.results.append(DiagnosticResult(
                check="Auth-Sharing Consistency",
                status="warn",
                category="consistency",
                message="2FA enforced but external sharing is unrestricted.",
                detail="Strong auth with open sharing may still leak data.",
                fix="Consider restricting external sharing to match the strict auth posture.",
            ))

        # Inconsistency: advanced mobile but no 2FA
        mobile = self.config.get("devices", {}).get("mobile_management", "")
        if mobile == "advanced" and not tfa:
            self.results.append(DiagnosticResult(
                check="Mobile-Auth Consistency",
                status="warn",
                category="consistency",
                message="Advanced mobile management without 2FA enforcement.",
                detail="Mobile management is less effective without mandatory 2FA.",
                fix="Enable 2FA enforcement to complement mobile management.",
            ))


def generate_sample_config() -> Dict[str, Any]:
    """Generate sample configuration for testing."""
    return {
        "dns": {
            "mx_records": ["ASPMX.L.GOOGLE.COM", "ALT1.ASPMX.L.GOOGLE.COM"],
            "spf_record": "v=spf1 include:_spf.google.com ~all",
            "dkim_record": "",
            "dmarc_record": "v=DMARC1; p=none; rua=mailto:dmarc@example.com",
        },
        "email": {
            "routing": "direct",
            "spam_filtering": True,
        },
        "security": {
            "2fa_enforcement": False,
            "session_duration_hours": 24,
        },
        "drive": {
            "external_sharing": "allowed",
        },
        "devices": {
            "mobile_management": "basic",
        },
        "integrations": {
            "sso_enabled": False,
            "directory_sync": False,
        },
    }


def format_text(results: List[DiagnosticResult]) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("GOOGLE WORKSPACE DIAGNOSTIC REPORT")
    lines.append("=" * 60)

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    warned = sum(1 for r in results if r.status == "warn")

    lines.append(f"\nChecks: {len(results)} total")
    lines.append(f"  PASS: {passed}  |  FAIL: {failed}  |  WARN: {warned}")
    lines.append("-" * 60)

    for status_label, status_key in [("FAILURES", "fail"), ("WARNINGS", "warn"), ("PASSED", "pass")]:
        group = [r for r in results if r.status == status_key]
        if not group:
            continue

        icon = {"fail": "FAIL", "warn": "WARN", "pass": "PASS"}[status_key]
        lines.append(f"\n[{status_label}]")
        for r in group:
            lines.append(f"  [{icon}] {r.check} ({r.category})")
            lines.append(f"    {r.message}")
            if r.detail:
                lines.append(f"    Detail: {r.detail}")
            if r.fix:
                lines.append(f"    Fix: {r.fix}")
            lines.append("")

    health = "HEALTHY" if failed == 0 else "NEEDS ATTENTION" if failed <= 2 else "CRITICAL"
    lines.append(f"Overall Health: {health}")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(results: List[DiagnosticResult]) -> str:
    """Format as JSON."""
    return json.dumps({
        "results": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "pass": sum(1 for r in results if r.status == "pass"),
            "fail": sum(1 for r in results if r.status == "fail"),
            "warn": sum(1 for r in results if r.status == "warn"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Diagnostic tool for common Google Workspace configuration issues."
    )
    parser.add_argument("--config", "-c", help="Path to GWS config JSON")
    parser.add_argument("--sample", action="store_true", help="Run against sample config")
    parser.add_argument("--check", default="all",
                       help="Checks to run: all,dns,email,security,integration,consistency")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--generate-sample", action="store_true", help="Output sample config")
    args = parser.parse_args()

    if args.generate_sample:
        print(json.dumps(generate_sample_config(), indent=2))
        return

    if args.sample:
        config = generate_sample_config()
    elif args.config:
        from pathlib import Path
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

    checks = [c.strip() for c in args.check.split(",")]
    diagnostics = GWSDiagnostics(config, checks)
    results = diagnostics.run()

    if args.format == "json":
        print(format_json(results))
    else:
        print(format_text(results))

    if any(r.status == "fail" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
