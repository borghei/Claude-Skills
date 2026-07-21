#!/usr/bin/env python3
"""Audit an exported cloud-resource inventory for posture weaknesses.

Reads a normalized inventory JSON (AWS, Azure, or GCP) and reports public
exposure, unencrypted data stores, missing audit logging, absent backups, and
account-level guardrail gaps — each scored by severity with provider-specific
remediation.

Usage:
    python3 posture_auditor.py --input inventory.json
    python3 posture_auditor.py --input inventory.json --format json \
        --min-severity high --fail-on critical
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from posture_rules import (  # noqa: E402
    DATA_STORES, OPEN_CIDRS, SENSITIVE_PORTS, SEVERITY_RANK, SEVERITY_WEIGHT,
    check_account, finding, fix_for)


def load_inventory(path: Path) -> Dict[str, Any]:
    """Load and validate the inventory JSON, exiting with guidance on failure."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: inventory not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}): {exc.msg}",
              file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict) or "resources" not in data:
        print("ERROR: inventory must be a JSON object with a 'resources' array. "
              "See assets/sample_inventory.json for the expected shape.",
              file=sys.stderr)
        sys.exit(1)
    return data


def check_resource(res: Dict[str, Any], provider: str) -> List[Dict[str, Any]]:
    """Run every posture check against a single inventory resource."""
    out: List[Dict[str, Any]] = []
    name = res.get("name") or res.get("id", "<unnamed>")
    rtype = res.get("type", "unknown")
    tags = res.get("tags", {}) or {}
    classification = str(tags.get("data_classification", "unknown")).lower()
    sensitive = classification in {"confidential", "restricted", "pii", "phi", "pci"}
    enc = res.get("encryption", {}) or {}
    logging_cfg = res.get("logging", {}) or {}
    network = res.get("network", {}) or {}

    if res.get("public") and rtype in DATA_STORES:
        out.append(finding(
            "CS-001", "critical", name,
            f"{rtype} is publicly readable",
            f"public=true, classification={classification}",
            fix_for("public_store", provider), "CIS 2.1 / data exposure"))
    elif res.get("public") and rtype not in {"load_balancer", "cdn", "dns_zone"}:
        out.append(finding(
            "CS-002", "high", name,
            f"{rtype} is exposed to the public internet",
            "public=true on a non-edge resource",
            "Move behind a load balancer or private endpoint; only edge resources "
            "should carry a public address.", "Network exposure"))

    for rule in network.get("ingress", []) or []:
        source = str(rule.get("source", "")).lower()
        ports = str(rule.get("ports", ""))
        if source not in OPEN_CIDRS:
            continue
        hits = [SENSITIVE_PORTS[p] for p in SENSITIVE_PORTS if p in ports.split(",")]
        if ports in {"all", "-1", "0-65535", "*"}:
            hits = ["all ports"]
        if hits:
            out.append(finding(
                "CS-010", "critical", name,
                f"{', '.join(hits)} open to the internet",
                f"ingress {ports} from {rule.get('source')}",
                fix_for("open_ingress", provider), "CIS 5.2 / network exposure"))
        elif ports not in {"80", "443"}:
            out.append(finding(
                "CS-011", "medium", name,
                "Non-standard port open to the internet",
                f"ingress {ports} from {rule.get('source')}",
                fix_for("open_ingress", provider), "Network exposure"))

    if rtype in DATA_STORES:
        if not enc.get("at_rest", False):
            out.append(finding(
                "CS-020", "critical" if sensitive else "high", name,
                "Data store is not encrypted at rest",
                f"encryption.at_rest=false, classification={classification}",
                fix_for("no_encryption_at_rest", provider), "CIS 2.1.1 / encryption"))
        elif sensitive and not enc.get("customer_managed_key", False):
            out.append(finding(
                "CS-021", "medium", name,
                "Sensitive data store uses provider-managed keys only",
                f"classification={classification}, customer_managed_key=false",
                "Attach a customer-managed key so key access is auditable and "
                "revocable independently of the platform.", "Key management"))
        if not enc.get("in_transit_enforced", False):
            out.append(finding(
                "CS-022", "high" if sensitive else "medium", name,
                "TLS is not enforced for connections",
                "encryption.in_transit_enforced=false",
                fix_for("no_encryption_in_transit", provider), "Encryption in transit"))
        if not logging_cfg.get("access_logs", False):
            out.append(finding(
                "CS-030", "medium", name,
                "Data-plane access logging is disabled",
                "logging.access_logs=false",
                "Enable data-plane access logs and ship them to the central log "
                "archive; without them, exfiltration is undetectable after the fact.",
                "Detection coverage"))
        backup = res.get("backup", {}) or {}
        if rtype in {"database", "data_warehouse", "file_share"} and not backup.get("enabled", False):
            out.append(finding(
                "CS-040", "high", name,
                "No backups configured for a primary data store",
                "backup.enabled=false",
                "Enable automated backups with a retention window matching the "
                "recovery objective, and store copies in a separate account.",
                "Resilience"))

    if not tags.get("owner"):
        out.append(finding(
            "CS-050", "low", name, "Resource has no owner tag",
            f"tags={sorted(tags)}",
            "Require owner, env, and data_classification tags at provisioning "
            "time; untagged resources have no one to page and no known blast radius.",
            "Governance"))
    if rtype in DATA_STORES and classification == "unknown":
        out.append(finding(
            "CS-051", "low", name, "Data store has no data_classification tag",
            "tags.data_classification missing",
            "Classify every data store; encryption, logging, and retention "
            "requirements all derive from the classification.", "Governance"))
    return out


def audit(inventory: Dict[str, Any]) -> Dict[str, Any]:
    """Audit the full inventory and compute the posture score."""
    provider = str(inventory.get("provider", "aws")).lower()
    findings: List[Dict[str, Any]] = []
    for res in inventory.get("resources", []):
        findings.extend(check_resource(res, provider))
    findings.extend(check_account(inventory.get("account_settings", {}) or {}, provider))
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"]))

    counts = {sev: sum(1 for f in findings if f["severity"] == sev)
              for sev in SEVERITY_RANK}
    penalty = sum(SEVERITY_WEIGHT[f["severity"]] for f in findings)
    score = max(0, 100 - penalty)
    if counts["critical"] or score < 40:
        grade = "critical — do not treat this environment as production-ready"
    elif score < 70:
        grade = "weak — material exposure remains"
    elif score < 90:
        grade = "fair — close the highs before the next audit"
    else:
        grade = "strong"
    return {
        "provider": provider,
        "account_id": inventory.get("account_id", "unknown"),
        "resources_audited": len(inventory.get("resources", [])),
        "posture_score": score,
        "grade": grade,
        "counts": counts,
        "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str, min_severity: str) -> None:
    """Print the audit report as JSON or human-readable text."""
    threshold = SEVERITY_RANK[min_severity]
    shown = [f for f in report["findings"] if SEVERITY_RANK[f["severity"]] <= threshold]
    if fmt == "json":
        print(json.dumps({**report, "findings": shown}, indent=2))
        return
    print(f"Cloud posture audit — {report['provider'].upper()} "
          f"account {report['account_id']}")
    print(f"Resources audited: {report['resources_audited']}   "
          f"Posture score: {report['posture_score']}/100 ({report['grade']})")
    counts = report["counts"]
    print(f"Findings: {counts['critical']} critical, {counts['high']} high, "
          f"{counts['medium']} medium, {counts['low']} low")
    print("=" * 72)
    for item in shown:
        print(f"[{item['severity'].upper():<8}] {item['id']}  {item['resource']}")
        print(f"           {item['title']}")
        print(f"           evidence: {item['evidence']}")
        print(f"           fix: {item['remediation']}")
        print(f"           control: {item['control']}")
    if not shown:
        print(f"No findings at or above severity '{min_severity}'.")


def main() -> None:
    """Parse arguments, run the audit, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Audit an exported cloud-resource inventory for posture weaknesses.")
    parser.add_argument("--input", required=True,
                        help="Path to the normalized inventory JSON export.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--min-severity", choices=list(SEVERITY_RANK),
                        default="low",
                        help="Lowest severity to display (default: low).")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default=None,
                        help="Exit 2 if any finding at or above this severity exists.")
    args = parser.parse_args()

    report = audit(load_inventory(Path(args.input)))
    output(report, args.format, args.min_severity)

    if args.fail_on:
        limit = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[f["severity"]] <= limit for f in report["findings"]):
            sys.exit(2)


if __name__ == "__main__":
    main()
