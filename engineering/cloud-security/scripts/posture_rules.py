#!/usr/bin/env python3
"""Posture rule data and account-level checks used by posture_auditor.py.

Holds the severity scale, the sensitive-port / data-store / open-CIDR
vocabularies, the provider-specific remediation catalog, and the account,
subscription, or project guardrail checks. The resource-level checks, scoring,
and CLI live in posture_auditor.py.

Usage:
    python3 posture_rules.py --list-rules
"""

import argparse
import json
import sys
from typing import Any, Dict, List

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_WEIGHT = {"critical": 25, "high": 10, "medium": 4, "low": 1}

SENSITIVE_PORTS = {
    "22": "SSH", "3389": "RDP", "3306": "MySQL", "5432": "PostgreSQL",
    "1433": "MSSQL", "27017": "MongoDB", "6379": "Redis", "9200": "Elasticsearch",
    "2375": "Docker API", "5984": "CouchDB", "11211": "Memcached",
}
DATA_STORES = {"storage_bucket", "database", "data_warehouse", "queue",
               "secret_store", "key_vault", "backup_vault", "file_share"}
OPEN_CIDRS = {"0.0.0.0/0", "::/0", "*", "any", "internet"}

REMEDIATION = {
    "public_store": {
        "aws": "Enable S3 Block Public Access at the account level, then remove the public bucket policy / ACL.",
        "azure": "Set 'Allow Blob public access' to Disabled on the storage account and switch consumers to SAS or private endpoints.",
        "gcp": "Remove allUsers / allAuthenticatedUsers from the bucket IAM policy and enforce Public Access Prevention at the org level.",
    },
    "open_ingress": {
        "aws": "Replace the 0.0.0.0/0 security-group rule with a prefix list or SG reference; use SSM Session Manager instead of open SSH.",
        "azure": "Replace the Any-source NSG rule with a service tag or ASG; use Azure Bastion for administrative access.",
        "gcp": "Scope the VPC firewall rule to a source range or tag; use IAP TCP forwarding for administrative access.",
    },
    "no_encryption_at_rest": {
        "aws": "Enable default encryption with a customer-managed KMS key; re-encrypt existing objects via a copy or snapshot restore.",
        "azure": "Enable encryption with a customer-managed key in Key Vault; Microsoft-managed keys are the fallback, not the target.",
        "gcp": "Attach a Cloud KMS CMEK to the resource; rewrite existing objects to apply it.",
    },
    "no_encryption_in_transit": {
        "aws": "Add an aws:SecureTransport deny policy and require TLS 1.2+ on load balancers and RDS.",
        "azure": "Enable 'Secure transfer required' on the storage account and set the minimum TLS version to 1.2.",
        "gcp": "Enforce HTTPS-only on load balancers and require SSL on Cloud SQL instances.",
    },
    "no_audit_log": {
        "aws": "Enable a multi-region organization CloudTrail with log-file validation, delivering to a locked, separate log-archive account.",
        "azure": "Route the Activity Log and resource diagnostic settings to a Log Analytics workspace in a separate subscription.",
        "gcp": "Enable Data Access audit logs at the organization level and sink them to a dedicated logging project.",
    },
}


def fix_for(key: str, provider: str) -> str:
    """Return provider-specific remediation text for a finding key."""
    return REMEDIATION.get(key, {}).get(provider, REMEDIATION.get(key, {}).get("aws", ""))


def finding(fid: str, severity: str, resource: str, title: str,
            evidence: str, remediation: str, control: str) -> Dict[str, Any]:
    """Build one normalized finding record."""
    return {"id": fid, "severity": severity, "resource": resource, "title": title,
            "evidence": evidence, "remediation": remediation, "control": control}


def check_account(settings: Dict[str, Any], provider: str) -> List[Dict[str, Any]]:
    """Run account / subscription / project level guardrail checks."""
    out: List[Dict[str, Any]] = []
    scope = {"aws": "account", "azure": "subscription", "gcp": "project"}.get(provider, "account")
    if not settings.get("audit_log_enabled", False):
        out.append(finding(
            "CS-100", "critical", scope, "Control-plane audit logging is disabled",
            "audit_log_enabled=false", fix_for("no_audit_log", provider),
            "CIS 3.1 / detection"))
    if not settings.get("root_mfa", False):
        out.append(finding(
            "CS-101", "critical", scope, "Root / global-admin account lacks MFA",
            "root_mfa=false",
            "Enforce hardware MFA on the root or global-admin identity, seal the "
            "credentials, and alert on any use.", "CIS 1.5 / identity"))
    if not settings.get("threat_detection_enabled", False):
        out.append(finding(
            "CS-102", "high", scope, "Managed threat detection is off",
            "threat_detection_enabled=false",
            "Enable GuardDuty / Defender for Cloud / Security Command Center "
            "across all regions and route findings to the SOC queue.",
            "Detection coverage"))
    if not settings.get("config_recorder_enabled", False):
        out.append(finding(
            "CS-103", "medium", scope, "Configuration recording is off",
            "config_recorder_enabled=false",
            "Enable AWS Config / Azure Policy compliance state / GCP Asset "
            "Inventory so drift is detectable and posture is provable in an audit.",
            "Governance"))
    if not settings.get("org_guardrails_enabled", False):
        out.append(finding(
            "CS-104", "high", scope, "No organization-level preventive guardrails",
            "org_guardrails_enabled=false",
            "Apply SCPs / Azure Policy deny assignments / GCP org policies to "
            "prevent public exposure and audit-log tampering, rather than "
            "detecting them after the fact.", "Landing zone"))
    if not settings.get("log_archive_isolated", False):
        out.append(finding(
            "CS-105", "high", scope, "Log archive is not isolated from workloads",
            "log_archive_isolated=false",
            "Move log storage to a dedicated account/subscription with no "
            "workload admin access, so an account compromise cannot erase evidence.",
            "Landing zone"))
    return out


def rule_catalog() -> Dict[str, Any]:
    """Return every tunable rule input, for review before an audit is trusted."""
    return {
        "severity_weight": SEVERITY_WEIGHT,
        "sensitive_ports": SENSITIVE_PORTS,
        "data_store_types": sorted(DATA_STORES),
        "internet_sources": sorted(OPEN_CIDRS),
        "remediation": REMEDIATION,
    }


def output(catalog: Dict[str, Any], fmt: str) -> None:
    """Print the rule catalog as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(catalog, indent=2))
        return
    print("Severity weights (deducted from the 100-point posture score)")
    for severity, weight in catalog["severity_weight"].items():
        print(f"  {severity:<10} -{weight}")
    print("\nPorts treated as sensitive when open to the internet")
    for port, name in catalog["sensitive_ports"].items():
        print(f"  {port:<7} {name}")
    print(f"\nResource types audited as data stores: "
          f"{', '.join(catalog['data_store_types'])}")
    print(f"Sources treated as the public internet: "
          f"{', '.join(catalog['internet_sources'])}")
    print("\nRemediation catalog")
    for key, per_provider in catalog["remediation"].items():
        print(f"  {key}")
        for provider, text in per_provider.items():
            print(f"    {provider:<6} {text}")


def main() -> None:
    """Parse arguments and print the rule catalog."""
    parser = argparse.ArgumentParser(
        description="Posture rule data for posture_auditor.py; run --list-rules "
                    "to inspect the severity weights, port and data-store "
                    "vocabularies, and the remediation catalog.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print every tunable rule input.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if not args.list_rules:
        parser.print_help()
        sys.exit(0)
    output(rule_catalog(), args.format)


if __name__ == "__main__":
    main()
