#!/usr/bin/env python3
"""
Access Control Auditor

Comprehensive access control audit covering:
- Identity Provider (IdP) configuration
- Single Sign-On (SSO) / SCIM provisioning
- Multi-Factor Authentication (MFA) enforcement
- Hardware security key (FIDO2/YubiKey) deployment
- Privileged Access Management (PAM)
- Role-Based Access Control (RBAC)
- Service account governance
- SSH key management
- API key management
- Zero Trust architecture

Maps findings to SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA,
NIST CSF, FedRAMP, and CCPA.

Usage:
    python access_control_auditor.py --config access_controls.json --output report.json
    python access_control_auditor.py --config access_controls.json --format markdown
    python access_control_auditor.py --generate-template --output template.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Control Definitions
# ---------------------------------------------------------------------------

SEVERITY_WEIGHTS = {
    "Critical": 10,
    "High": 5,
    "Medium": 2,
    "Low": 1,
    "Info": 0,
}

FRAMEWORK_LABELS = {
    "soc2": "SOC 2 Type II",
    "iso27001": "ISO 27001:2022",
    "hipaa": "HIPAA",
    "gdpr": "GDPR",
    "pci_dss": "PCI-DSS v4.0",
    "nis2": "NIS2 Directive",
    "dora": "DORA",
    "nist_csf": "NIST CSF 2.0",
    "fedramp": "FedRAMP",
    "ccpa": "CCPA/CPRA",
}

# (check_id, title, severity, frameworks[], config_key, expected_value, category, remediation)
CONTROLS = [
    # --- Identity Provider ---
    ("AC-IDP-001", "Centralized IdP deployed", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "fedramp"],
     "idp.deployed", True, "Identity Provider",
     "Deploy a centralized Identity Provider (Okta, Azure AD/Entra ID, Google Workspace). All authentication should flow through the IdP."),

    ("AC-IDP-002", "All applications integrated with IdP via SSO", "High",
     ["soc2", "iso27001"],
     "idp.all_apps_integrated", True, "Identity Provider",
     "Integrate all business applications with the IdP via SAML 2.0 or OIDC. Create an application inventory and track SSO coverage."),

    ("AC-IDP-003", "IdP admin MFA with hardware key", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "idp.admin_hardware_mfa", True, "Identity Provider",
     "Require FIDO2/WebAuthn hardware security keys for all IdP administrator accounts. Disable TOTP/SMS fallback for admins."),

    ("AC-IDP-004", "IdP audit logs exported to SIEM", "Medium",
     ["soc2", "iso27001"],
     "idp.audit_logs_to_siem", True, "Identity Provider",
     "Export IdP audit logs to SIEM for monitoring. Configure alerts for: admin role changes, MFA resets, suspicious sign-ins."),

    # --- SSO ---
    ("AC-SSO-001", "SSO via SAML 2.0 or OIDC", "High",
     ["soc2", "iso27001", "nist_csf"],
     "sso.protocol_saml_oidc", True, "Single Sign-On",
     "Implement SSO using SAML 2.0 or OIDC. Password-based SSO (form-fill) is not acceptable."),

    ("AC-SSO-002", "SSO session timeout max 8 hours", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "sso.session_timeout_8h", True, "Single Sign-On",
     "Configure SSO session timeout to maximum 8 hours. For sensitive applications, use shorter timeouts (1-4 hours)."),

    ("AC-SSO-003", "SSO enforced (local auth disabled)", "High",
     ["soc2", "iso27001"],
     "sso.local_auth_disabled", True, "Single Sign-On",
     "Disable local authentication where possible. Force all authentication through SSO to ensure consistent policy enforcement."),

    ("AC-SSO-004", "SCIM provisioning enabled", "High",
     ["soc2", "iso27001", "nist_csf"],
     "sso.scim_enabled", True, "Single Sign-On",
     "Enable SCIM provisioning for automated user creation/deactivation. This ensures timely deprovisioning when employees leave."),

    ("AC-SSO-005", "Deprovisioning revokes SSO sessions", "High",
     ["soc2", "iso27001"],
     "sso.deprovision_revokes_sessions", True, "Single Sign-On",
     "Configure IdP to immediately revoke all active sessions when a user is deprovisioned. Test this process regularly."),

    # --- MFA ---
    ("AC-MFA-001", "MFA enforced for ALL accounts (no exceptions)", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "gdpr", "nis2", "dora", "fedramp"],
     "mfa.enforced_all_accounts", True, "Multi-Factor Authentication",
     "Enforce MFA for 100% of user accounts with zero exceptions. This is the single most impactful security control. Use Conditional Access policies to enforce."),

    ("AC-MFA-002", "Phishing-resistant MFA for privileged accounts", "Critical",
     ["soc2", "iso27001", "nist_csf", "fedramp"],
     "mfa.phishing_resistant_privileged", True, "Multi-Factor Authentication",
     "Require FIDO2/WebAuthn (hardware security keys) for all privileged/admin accounts. TOTP and push notifications are phishable."),

    ("AC-MFA-003", "SMS-based MFA prohibited", "High",
     ["soc2", "nist_csf"],
     "mfa.sms_prohibited", True, "Multi-Factor Authentication",
     "Disable SMS-based MFA. SMS is vulnerable to SIM swap attacks, SS7 interception, and social engineering. Use TOTP, FIDO2, or push instead."),

    ("AC-MFA-004", "TOTP accepted as minimum MFA", "Medium",
     ["soc2"],
     "mfa.totp_accepted", True, "Multi-Factor Authentication",
     "Allow TOTP (Google Authenticator, Authy) as minimum acceptable MFA factor for non-privileged users."),

    ("AC-MFA-005", "Hardware security keys for all admins", "High",
     ["soc2", "iso27001", "nist_csf"],
     "mfa.hardware_keys_all_admins", True, "Multi-Factor Authentication",
     "Issue FIDO2 hardware security keys (YubiKey 5 Series or Bio Series) to all admin users. Require 2 keys per admin (primary + backup)."),

    ("AC-MFA-006", "MFA recovery process documented", "Medium",
     ["soc2", "iso27001"],
     "mfa.recovery_process_documented", True, "Multi-Factor Authentication",
     "Document MFA recovery process. Must include identity verification steps. Recovery should NOT bypass MFA — it should re-enroll."),

    ("AC-MFA-007", "MFA enrollment at 100% coverage", "Medium",
     ["soc2"],
     "mfa.enrollment_100_percent", True, "Multi-Factor Authentication",
     "Track and report MFA enrollment. Target 100% coverage. Follow up with any unenrolled users within 48 hours."),

    # --- Hardware Security Keys ---
    ("AC-HSK-001", "YubiKey/FIDO2 keys issued to all admins", "High",
     ["soc2", "iso27001", "nist_csf"],
     "hardware_keys.issued_to_admins", True, "Hardware Security Keys",
     "Issue FIDO2-compatible hardware security keys to all admin users. YubiKey 5 Series supports FIDO2, PIV, TOTP, OpenPGP."),

    ("AC-HSK-002", "Each user has primary + backup key", "High",
     ["soc2", "iso27001"],
     "hardware_keys.backup_keys_issued", True, "Hardware Security Keys",
     "Issue 2 hardware keys per user (primary for daily use, backup stored securely). This prevents lockout if primary key is lost."),

    ("AC-HSK-003", "PIN configured on hardware keys (FIDO2 UV)", "Medium",
     ["soc2", "iso27001"],
     "hardware_keys.pin_configured", True, "Hardware Security Keys",
     "Configure FIDO2 PIN (User Verification) on all hardware keys. This provides a second factor even if the key is stolen."),

    ("AC-HSK-004", "Hardware key inventory maintained", "Medium",
     ["soc2", "iso27001"],
     "hardware_keys.inventory_maintained", True, "Hardware Security Keys",
     "Maintain inventory of all issued hardware keys: serial number, assigned user, issuance date, status (active/lost/revoked)."),

    ("AC-HSK-005", "Lost key process documented", "Medium",
     ["soc2", "iso27001"],
     "hardware_keys.lost_key_process", True, "Hardware Security Keys",
     "Document lost key process: 1) Immediate revocation in IdP, 2) Identity reverification, 3) New key issuance, 4) Backup key verification."),

    ("AC-HSK-006", "Hardware keys required for high-value targets", "High",
     ["soc2", "iso27001", "pci_dss"],
     "hardware_keys.required_high_value", True, "Hardware Security Keys",
     "Require hardware keys (not TOTP/push) for: IdP admins, cloud admins, production access, financial systems, customer data access."),

    # --- PAM ---
    ("AC-PAM-001", "JIT access for privileged roles", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "pam.jit_access_enabled", True, "Privileged Access Management",
     "Implement just-in-time access for all privileged roles. No standing admin access. Use Azure PIM, AWS IAM Identity Center, or Okta Privileged Access."),

    ("AC-PAM-002", "Privileged access requires approval", "High",
     ["soc2", "iso27001"],
     "pam.approval_required", True, "Privileged Access Management",
     "Require manager or security team approval for privileged access requests. Automated approval only for pre-authorized break-glass scenarios."),

    ("AC-PAM-003", "Privileged sessions time-limited (max 4h)", "Medium",
     ["soc2", "iso27001"],
     "pam.session_time_limited", True, "Privileged Access Management",
     "Limit privileged access sessions to maximum 4 hours. Require re-approval for extensions."),

    ("AC-PAM-004", "Privileged sessions recorded", "High",
     ["soc2", "iso27001", "pci_dss"],
     "pam.session_recording", True, "Privileged Access Management",
     "Record all privileged sessions (screen recording or command logging). Store recordings for minimum 1 year."),

    ("AC-PAM-005", "Break-glass procedure documented and tested", "Medium",
     ["soc2", "iso27001", "nist_csf"],
     "pam.break_glass_documented", True, "Privileged Access Management",
     "Document break-glass (emergency access) procedure. Test quarterly. Ensure break-glass accounts trigger immediate alerts."),

    ("AC-PAM-006", "Privileged account inventory reviewed quarterly", "High",
     ["soc2", "iso27001", "pci_dss"],
     "pam.inventory_quarterly_review", True, "Privileged Access Management",
     "Maintain inventory of all privileged accounts. Review quarterly with business justification for each. Remove unnecessary access."),

    ("AC-PAM-007", "No permanent admin accounts", "High",
     ["soc2", "iso27001", "nist_csf"],
     "pam.no_permanent_admins", True, "Privileged Access Management",
     "Eliminate standing privileged access. All admin access should be JIT with time-limited sessions. Exception: break-glass accounts (monitored)."),

    # --- RBAC ---
    ("AC-RBAC-001", "RBAC model documented", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"],
     "rbac.model_documented", True, "Role-Based Access Control",
     "Document RBAC model: role definitions, permission sets, and role-to-group mappings. Review and update annually."),

    ("AC-RBAC-002", "Access recertification quarterly", "High",
     ["soc2", "iso27001", "pci_dss"],
     "rbac.quarterly_recertification", True, "Role-Based Access Control",
     "Conduct quarterly access recertification. Managers review and certify their team's access. Remove access that cannot be justified."),

    ("AC-RBAC-003", "Separation of duties enforced", "High",
     ["soc2", "iso27001", "pci_dss"],
     "rbac.separation_of_duties", True, "Role-Based Access Control",
     "Enforce separation of duties: no user should have conflicting roles (e.g., both 'deploy code' and 'approve deployment')."),

    ("AC-RBAC-004", "Default deny (minimum permissions)", "High",
     ["soc2", "iso27001"],
     "rbac.default_deny", True, "Role-Based Access Control",
     "Users start with zero permissions. Access granted only as needed for role. No inherited admin or broad access by default."),

    ("AC-RBAC-005", "Role changes logged and auditable", "Medium",
     ["soc2", "iso27001"],
     "rbac.changes_logged", True, "Role-Based Access Control",
     "Log all role assignment/removal events. Include who changed it, when, and business justification."),

    # --- Service Accounts ---
    ("AC-SVC-001", "No shared service account credentials", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "service_accounts.no_shared_credentials", True, "Service Account Governance",
     "Each service account must have unique credentials. Never share passwords or API keys between services or environments."),

    ("AC-SVC-002", "Service account permissions least privilege", "High",
     ["soc2", "iso27001"],
     "service_accounts.least_privilege", True, "Service Account Governance",
     "Review and minimize service account permissions. Each service account should only access what its service requires."),

    ("AC-SVC-003", "Service account credentials rotate every 90 days", "High",
     ["soc2", "iso27001", "pci_dss"],
     "service_accounts.rotation_90_days", True, "Service Account Governance",
     "Rotate service account credentials every 90 days maximum. Use dynamic credentials (Vault, AWS STS) where possible."),

    ("AC-SVC-004", "Service account inventory with owner", "High",
     ["soc2", "iso27001"],
     "service_accounts.inventory_with_owner", True, "Service Account Governance",
     "Maintain inventory of all service accounts: name, purpose, owner, permissions, last rotation date, review status."),

    ("AC-SVC-005", "Unused service accounts disabled", "Medium",
     ["soc2", "iso27001"],
     "service_accounts.unused_disabled", True, "Service Account Governance",
     "Identify and disable unused service accounts. Check last authentication date — disable if >90 days inactive."),

    # --- API Key Management ---
    ("AC-API-001", "API keys scoped to minimum permissions", "High",
     ["soc2", "iso27001"],
     "api_keys.scoped_minimum", True, "API Key Management",
     "Scope each API key to minimum required permissions. Avoid admin-level or wildcard API keys."),

    ("AC-API-002", "API keys have expiration dates", "Medium",
     ["soc2", "iso27001"],
     "api_keys.have_expiration", True, "API Key Management",
     "Set expiration dates on API keys (maximum 1 year). Prefer short-lived tokens (OAuth2, JWT) over long-lived API keys."),

    ("AC-API-003", "API key usage monitored", "Medium",
     ["soc2", "iso27001"],
     "api_keys.usage_monitored", True, "API Key Management",
     "Monitor API key usage patterns. Alert on anomalous access: unusual volumes, off-hours access, new source IPs."),

    ("AC-API-004", "API key inventory maintained", "Medium",
     ["soc2", "iso27001"],
     "api_keys.inventory_maintained", True, "API Key Management",
     "Maintain inventory of all API keys: service, owner, scope, creation date, expiry date, last used."),

    # --- SSH Key Management ---
    ("AC-SSH-001", "SSH keys ED25519 or RSA >= 4096 bit", "High",
     ["soc2", "iso27001"],
     "ssh.strong_key_algorithms", True, "SSH Key Management",
     "Require ED25519 SSH keys (preferred) or RSA >= 4096 bit. Reject DSA and RSA < 2048 bit. Configure sshd_config: PubkeyAcceptedAlgorithms."),

    ("AC-SSH-002", "Certificate-based SSH for infrastructure", "Medium",
     ["soc2", "iso27001"],
     "ssh.certificate_based", True, "SSH Key Management",
     "Use SSH certificates instead of raw public keys for infrastructure access. Certificates support automatic expiration and central revocation."),

    ("AC-SSH-003", "SSH key passphrase required", "Medium",
     ["soc2", "iso27001"],
     "ssh.passphrase_required", True, "SSH Key Management",
     "Require passphrases on all SSH private keys. Use ssh-agent for convenience. Check with: ssh-keygen -y -P '' -f keyfile (should fail)."),

    ("AC-SSH-004", "SSH key inventory maintained", "Medium",
     ["soc2", "iso27001"],
     "ssh.key_inventory", True, "SSH Key Management",
     "Maintain inventory of authorized SSH keys: key fingerprint, owner, servers authorized on, last used, expiration."),

    ("AC-SSH-005", "SSH keys rotate annually", "Medium",
     ["soc2", "pci_dss"],
     "ssh.annual_rotation", True, "SSH Key Management",
     "Rotate SSH keys annually at minimum. Use SSH certificates with short validity (24h-30d) for automatic rotation."),

    ("AC-SSH-006", "Root SSH login disabled", "High",
     ["soc2", "iso27001", "pci_dss"],
     "ssh.root_login_disabled", True, "SSH Key Management",
     "Disable root SSH login: PermitRootLogin no in sshd_config. Use named accounts + sudo for privilege escalation."),

    ("AC-SSH-007", "SSH password authentication disabled", "High",
     ["soc2", "iso27001"],
     "ssh.password_auth_disabled", True, "SSH Key Management",
     "Disable SSH password authentication: PasswordAuthentication no in sshd_config. Use key-based or certificate-based auth only."),

    # --- Zero Trust ---
    ("AC-ZT-001", "Identity-based access (verify user+device+context)", "High",
     ["soc2", "iso27001", "nist_csf"],
     "zero_trust.identity_based_access", True, "Zero Trust Architecture",
     "Implement identity-based access: verify user identity, device identity/posture, and request context before granting access."),

    ("AC-ZT-002", "Device posture checked before access", "High",
     ["soc2", "iso27001"],
     "zero_trust.device_posture_check", True, "Zero Trust Architecture",
     "Check device posture before granting access: MDM enrollment, disk encryption, OS version, EDR status, patch level."),

    ("AC-ZT-003", "No implicit trust for internal network", "High",
     ["soc2", "iso27001", "nist_csf"],
     "zero_trust.no_network_trust", True, "Zero Trust Architecture",
     "Eliminate implicit trust based on network location. Internal network should not grant access without identity verification."),

    ("AC-ZT-004", "Continuous verification for sensitive ops", "Medium",
     ["soc2", "nist_csf"],
     "zero_trust.continuous_verification", True, "Zero Trust Architecture",
     "Require re-authentication for sensitive operations: financial transactions, admin actions, data exports, configuration changes."),

    ("AC-ZT-005", "Microsegmentation between services", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "zero_trust.microsegmentation", True, "Zero Trust Architecture",
     "Implement microsegmentation: each service can only communicate with explicitly authorized services. Use network policies or service mesh."),
]


def get_nested_value(data, dotted_key):
    """Retrieve value from nested dict using dot notation."""
    keys = dotted_key.split(".")
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current


def run_access_audit(config):
    """Run the access control audit against provided configuration."""
    findings = []
    category_stats = defaultdict(lambda: {
        "passed": 0, "failed": 0, "na": 0,
        "weighted_passed": 0, "weighted_total": 0
    })

    for check_id, title, severity, frameworks, config_key, expected, category, remediation in CONTROLS:
        value = get_nested_value(config, config_key)
        weight = SEVERITY_WEIGHTS.get(severity, 0)

        if value is None:
            result = "not_applicable"
            category_stats[category]["na"] += 1
        elif isinstance(expected, bool):
            result = "pass" if bool(value) == expected else "fail"
        elif isinstance(expected, (int, float)):
            try:
                result = "pass" if float(value) >= float(expected) else "fail"
            except (ValueError, TypeError):
                result = "fail"
        else:
            result = "pass" if value == expected else "fail"

        finding = {
            "check_id": check_id,
            "title": title,
            "severity": severity,
            "frameworks": frameworks,
            "category": category,
            "result": result,
        }

        if result == "pass":
            category_stats[category]["passed"] += 1
            category_stats[category]["weighted_passed"] += weight
            category_stats[category]["weighted_total"] += weight
        elif result == "fail":
            category_stats[category]["failed"] += 1
            category_stats[category]["weighted_total"] += weight
            finding["remediation"] = remediation
        # N/A doesn't affect score

        findings.append(finding)

    # MFA coverage analysis
    mfa_config = config.get("mfa", {})
    total_users = mfa_config.get("total_users", 0)
    mfa_enrolled = mfa_config.get("enrolled_users", 0)
    hardware_key_users = mfa_config.get("hardware_key_users", 0)
    admin_count = mfa_config.get("admin_count", 0)
    admin_with_hardware_keys = mfa_config.get("admins_with_hardware_keys", 0)

    mfa_analysis = {
        "total_users": total_users,
        "mfa_enrolled": mfa_enrolled,
        "mfa_coverage": round((mfa_enrolled / total_users * 100), 1) if total_users > 0 else 0,
        "hardware_key_users": hardware_key_users,
        "hardware_key_coverage": round((hardware_key_users / total_users * 100), 1) if total_users > 0 else 0,
        "admin_count": admin_count,
        "admins_with_hardware_keys": admin_with_hardware_keys,
        "admin_hardware_key_coverage": round((admin_with_hardware_keys / admin_count * 100), 1) if admin_count > 0 else 0,
        "gaps": [],
    }

    if total_users > 0 and mfa_enrolled < total_users:
        mfa_analysis["gaps"].append(
            f"{total_users - mfa_enrolled} users without MFA. Immediately enforce MFA for these accounts."
        )
    if admin_count > 0 and admin_with_hardware_keys < admin_count:
        mfa_analysis["gaps"].append(
            f"{admin_count - admin_with_hardware_keys} admin accounts without hardware security keys. Issue YubiKeys immediately."
        )

    # Service account analysis
    sa_config = config.get("service_accounts", {})
    sa_list = sa_config.get("accounts", [])
    sa_analysis = {
        "total_service_accounts": len(sa_list),
        "without_owner": 0,
        "shared_credentials": 0,
        "overdue_rotation": 0,
        "excessive_permissions": 0,
        "issues": [],
    }

    for sa in sa_list:
        if not sa.get("owner"):
            sa_analysis["without_owner"] += 1
            sa_analysis["issues"].append(f"Service account '{sa.get('name', 'unknown')}' has no assigned owner.")
        if sa.get("shared_credentials"):
            sa_analysis["shared_credentials"] += 1
            sa_analysis["issues"].append(f"Service account '{sa.get('name', 'unknown')}' uses shared credentials.")
        if sa.get("rotation_overdue"):
            sa_analysis["overdue_rotation"] += 1
            sa_analysis["issues"].append(f"Service account '{sa.get('name', 'unknown')}' has overdue credential rotation.")
        if sa.get("excessive_permissions"):
            sa_analysis["excessive_permissions"] += 1
            sa_analysis["issues"].append(f"Service account '{sa.get('name', 'unknown')}' has excessive permissions.")

    # Calculate category scores
    category_scores = {}
    for category, stats in category_stats.items():
        total = stats["weighted_total"]
        if total > 0:
            score = round((stats["weighted_passed"] / total) * 100, 1)
        else:
            score = 100.0
        category_scores[category] = {
            "score": score,
            "passed": stats["passed"],
            "failed": stats["failed"],
            "not_applicable": stats["na"],
        }

    # Overall score
    total_wp = sum(s["weighted_passed"] for s in category_stats.values())
    total_wt = sum(s["weighted_total"] for s in category_stats.values())
    overall_score = round((total_wp / total_wt) * 100, 1) if total_wt > 0 else 0.0

    if overall_score >= 90:
        rating = "Excellent"
    elif overall_score >= 80:
        rating = "Good"
    elif overall_score >= 70:
        rating = "Fair"
    elif overall_score >= 60:
        rating = "Poor"
    else:
        rating = "Critical"

    # Severity summary
    severity_counts = defaultdict(int)
    for f in findings:
        if f["result"] == "fail":
            severity_counts[f["severity"]] += 1

    # Framework scores
    framework_coverage = defaultdict(lambda: {"passed": 0, "failed": 0, "total": 0})
    for f in findings:
        if f["result"] in ("pass", "fail"):
            for fw in f["frameworks"]:
                framework_coverage[fw]["total"] += 1
                if f["result"] == "pass":
                    framework_coverage[fw]["passed"] += 1
                else:
                    framework_coverage[fw]["failed"] += 1

    framework_scores = {}
    for fw, stats in framework_coverage.items():
        if stats["total"] > 0:
            framework_scores[fw] = {
                "label": FRAMEWORK_LABELS.get(fw, fw),
                "score": round((stats["passed"] / stats["total"]) * 100, 1),
                "passed": stats["passed"],
                "failed": stats["failed"],
                "total": stats["total"],
            }

    return {
        "audit_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "access-control-auditor",
            "version": "1.0.0",
            "total_controls_evaluated": sum(1 for f in findings if f["result"] != "not_applicable"),
            "total_controls_skipped": sum(1 for f in findings if f["result"] == "not_applicable"),
        },
        "overall_score": overall_score,
        "overall_rating": rating,
        "severity_summary": {
            "critical_failures": severity_counts.get("Critical", 0),
            "high_failures": severity_counts.get("High", 0),
            "medium_failures": severity_counts.get("Medium", 0),
            "low_failures": severity_counts.get("Low", 0),
        },
        "category_scores": category_scores,
        "framework_scores": framework_scores,
        "mfa_analysis": mfa_analysis,
        "service_account_analysis": sa_analysis,
        "findings": findings,
    }


def format_markdown(report):
    """Format access control audit report as Markdown."""
    lines = []
    lines.append("# Access Control Audit Report")
    lines.append("")
    lines.append(f"**Date:** {report['audit_metadata']['timestamp']}")
    lines.append(f"**Controls Evaluated:** {report['audit_metadata']['total_controls_evaluated']}")
    lines.append(f"**Controls Skipped (N/A):** {report['audit_metadata']['total_controls_skipped']}")
    lines.append("")

    # Overall Score
    lines.append("## Overall Score")
    lines.append("")
    lines.append(f"**Score: {report['overall_score']}/100 — {report['overall_rating']}**")
    lines.append("")
    ss = report["severity_summary"]
    lines.append(f"| Severity | Failures |")
    lines.append(f"|----------|----------|")
    lines.append(f"| Critical | {ss['critical_failures']} |")
    lines.append(f"| High | {ss['high_failures']} |")
    lines.append(f"| Medium | {ss['medium_failures']} |")
    lines.append(f"| Low | {ss['low_failures']} |")
    lines.append("")

    # Category Scores
    lines.append("## Category Scores")
    lines.append("")
    lines.append("| Category | Score | Passed | Failed | N/A |")
    lines.append("|----------|-------|--------|--------|-----|")
    for cat, data in sorted(report["category_scores"].items(), key=lambda x: x[1]["score"]):
        lines.append(f"| {cat} | {data['score']}/100 | {data['passed']} | {data['failed']} | {data['not_applicable']} |")
    lines.append("")

    # MFA Analysis
    mfa = report["mfa_analysis"]
    if mfa["total_users"] > 0:
        lines.append("## MFA Coverage Analysis")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Users | {mfa['total_users']} |")
        lines.append(f"| MFA Enrolled | {mfa['mfa_enrolled']} ({mfa['mfa_coverage']}%) |")
        lines.append(f"| Hardware Key Users | {mfa['hardware_key_users']} ({mfa['hardware_key_coverage']}%) |")
        lines.append(f"| Admin Count | {mfa['admin_count']} |")
        lines.append(f"| Admins with HW Keys | {mfa['admins_with_hardware_keys']} ({mfa['admin_hardware_key_coverage']}%) |")
        lines.append("")
        if mfa["gaps"]:
            lines.append("**Gaps:**")
            for gap in mfa["gaps"]:
                lines.append(f"- {gap}")
            lines.append("")

    # Service Account Analysis
    sa = report["service_account_analysis"]
    if sa["total_service_accounts"] > 0:
        lines.append("## Service Account Analysis")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Service Accounts | {sa['total_service_accounts']} |")
        lines.append(f"| Without Owner | {sa['without_owner']} |")
        lines.append(f"| Shared Credentials | {sa['shared_credentials']} |")
        lines.append(f"| Overdue Rotation | {sa['overdue_rotation']} |")
        lines.append(f"| Excessive Permissions | {sa['excessive_permissions']} |")
        lines.append("")
        if sa["issues"]:
            lines.append("**Issues:**")
            for issue in sa["issues"][:20]:
                lines.append(f"- {issue}")
            lines.append("")

    # Framework Scores
    if report["framework_scores"]:
        lines.append("## Framework Compliance Scores")
        lines.append("")
        lines.append("| Framework | Score | Passed | Failed | Total |")
        lines.append("|-----------|-------|--------|--------|-------|")
        for fw, data in sorted(report["framework_scores"].items(), key=lambda x: x[1]["score"]):
            lines.append(f"| {data['label']} | {data['score']}% | {data['passed']} | {data['failed']} | {data['total']} |")
        lines.append("")

    # Critical and High Findings
    critical_high = [f for f in report["findings"] if f["result"] == "fail" and f["severity"] in ("Critical", "High")]
    if critical_high:
        lines.append("## Critical and High Findings")
        lines.append("")
        for f in sorted(critical_high, key=lambda x: (0 if x["severity"] == "Critical" else 1, x["check_id"])):
            lines.append(f"### [{f['severity']}] {f['check_id']}: {f['title']}")
            lines.append("")
            lines.append(f"**Category:** {f['category']}")
            lines.append(f"**Frameworks:** {', '.join(FRAMEWORK_LABELS.get(fw, fw) for fw in f['frameworks'])}")
            if "remediation" in f:
                lines.append(f"**Remediation:** {f['remediation']}")
            lines.append("")

    # Medium and Low
    med_low = [f for f in report["findings"] if f["result"] == "fail" and f["severity"] in ("Medium", "Low")]
    if med_low:
        lines.append("## Medium and Low Findings")
        lines.append("")
        lines.append("| Check ID | Title | Category | Severity |")
        lines.append("|----------|-------|----------|----------|")
        for f in sorted(med_low, key=lambda x: x["check_id"]):
            lines.append(f"| {f['check_id']} | {f['title']} | {f['category']} | {f['severity']} |")
        lines.append("")

    return "\n".join(lines)


def generate_template():
    """Generate template access control configuration."""
    template = {
        "_description": "Access Control Audit Configuration Template",
        "_instructions": "Fill in each value based on your current access control state. Set boolean values to true/false.",
        "idp": {
            "deployed": False,
            "provider": "okta|azure_ad|google_workspace|other",
            "all_apps_integrated": False,
            "admin_hardware_mfa": False,
            "audit_logs_to_siem": False
        },
        "sso": {
            "protocol_saml_oidc": False,
            "session_timeout_8h": False,
            "local_auth_disabled": False,
            "scim_enabled": False,
            "deprovision_revokes_sessions": False
        },
        "mfa": {
            "enforced_all_accounts": False,
            "phishing_resistant_privileged": False,
            "sms_prohibited": False,
            "totp_accepted": True,
            "hardware_keys_all_admins": False,
            "recovery_process_documented": False,
            "enrollment_100_percent": False,
            "total_users": 0,
            "enrolled_users": 0,
            "hardware_key_users": 0,
            "admin_count": 0,
            "admins_with_hardware_keys": 0
        },
        "hardware_keys": {
            "issued_to_admins": False,
            "backup_keys_issued": False,
            "pin_configured": False,
            "inventory_maintained": False,
            "lost_key_process": False,
            "required_high_value": False
        },
        "pam": {
            "jit_access_enabled": False,
            "approval_required": False,
            "session_time_limited": False,
            "session_recording": False,
            "break_glass_documented": False,
            "inventory_quarterly_review": False,
            "no_permanent_admins": False
        },
        "rbac": {
            "model_documented": False,
            "quarterly_recertification": False,
            "separation_of_duties": False,
            "default_deny": False,
            "changes_logged": False
        },
        "service_accounts": {
            "no_shared_credentials": False,
            "least_privilege": False,
            "rotation_90_days": False,
            "inventory_with_owner": False,
            "unused_disabled": False,
            "accounts": [
                {
                    "name": "example-sa",
                    "owner": "team-name",
                    "shared_credentials": False,
                    "rotation_overdue": False,
                    "excessive_permissions": False
                }
            ]
        },
        "api_keys": {
            "scoped_minimum": False,
            "have_expiration": False,
            "usage_monitored": False,
            "inventory_maintained": False
        },
        "ssh": {
            "strong_key_algorithms": False,
            "certificate_based": False,
            "passphrase_required": False,
            "key_inventory": False,
            "annual_rotation": False,
            "root_login_disabled": False,
            "password_auth_disabled": False
        },
        "zero_trust": {
            "identity_based_access": False,
            "device_posture_check": False,
            "no_network_trust": False,
            "continuous_verification": False,
            "microsegmentation": False
        }
    }
    return template


def main():
    parser = argparse.ArgumentParser(
        description="Access Control Auditor — comprehensive audit of identity, authentication, authorization, and access governance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate config template
  python access_control_auditor.py --generate-template --output template.json

  # Run audit
  python access_control_auditor.py --config access_controls.json --output report.json

  # Markdown report
  python access_control_auditor.py --config access_controls.json --format markdown --output report.md
        """,
    )

    parser.add_argument("--config", type=str, help="Path to access control configuration JSON")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--generate-template", action="store_true",
                        help="Generate template configuration JSON")

    args = parser.parse_args()

    if args.generate_template:
        template = generate_template()
        output = json.dumps(template, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Template written to {args.output}", file=sys.stderr)
        else:
            print(output)
        return

    if not args.config:
        parser.error("--config is required (or use --generate-template)")

    try:
        with open(args.config, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    report = run_access_audit(config)

    if args.format == "markdown":
        output = format_markdown(report)
    else:
        output = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)
        print(f"Score: {report['overall_score']}/100 ({report['overall_rating']})", file=sys.stderr)
        ss = report["severity_summary"]
        print(f"Failures: {ss['critical_failures']} Critical, {ss['high_failures']} High, "
              f"{ss['medium_failures']} Medium, {ss['low_failures']} Low", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
