#!/usr/bin/env python3
"""Review cloud IAM principals for least-privilege violations.

Reads an exported IAM principal inventory (AWS, Azure, or GCP) and reports
wildcard grants, privilege-escalation paths, over-broad trust policies, stale
credentials, and missing MFA — with an effective-privilege tier and risk score
per principal.

Usage:
    python3 iam_least_privilege.py --input iam_export.json
    python3 iam_least_privilege.py --input iam_export.json --format json \
        --stale-days 60 --fail-on critical
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iam_rules import (  # noqa: E402
    SEVERITY_RANK, SEVERITY_WEIGHT, WRITE_VERBS, finding, granted_actions,
    matched_escalations, privilege_tier)


def load_export(path: Path) -> Dict[str, Any]:
    """Load and validate the IAM export JSON, exiting with guidance on failure."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: IAM export not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}): {exc.msg}",
              file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict) or "principals" not in data:
        print("ERROR: export must be a JSON object with a 'principals' array. "
              "See assets/sample_iam_export.json for the expected shape.",
              file=sys.stderr)
        sys.exit(1)
    return data


def check_principal(principal: Dict[str, Any], stale_days: int) -> List[Dict[str, Any]]:
    """Run every least-privilege check against a single principal."""
    out: List[Dict[str, Any]] = []
    name = principal.get("name", "<unnamed>")
    ptype = str(principal.get("type", "role")).lower()
    actions = granted_actions(principal)
    action_set = [a for a, _, _ in actions]

    for action, resources, conditions in actions:
        star_resource = any(r == "*" for r in resources)
        if action in {"*", "*:*"} and star_resource:
            out.append(finding(
                "IAM-001", "critical", name,
                "Unrestricted admin grant (action:* on resource:*)",
                f"policy grants {action} on {resources}",
                "Replace with the specific actions the workload has actually used "
                "over the last 90 days; derive them from access-analyzer or audit "
                "log data, not from guesswork."))
        elif action.endswith(":*") and star_resource:
            out.append(finding(
                "IAM-002", "high", name,
                f"Service-wide wildcard on all resources ({action})",
                f"policy grants {action} on {resources}",
                "Scope to the specific ARNs / resource IDs the principal needs, "
                "and split read from write into separate statements."))
        elif any(v in action for v in WRITE_VERBS) and star_resource and not conditions:
            out.append(finding(
                "IAM-003", "medium", name,
                f"Unconditioned write action on all resources ({action})",
                f"{action} on * with no conditions",
                "Add a resource scope, or at minimum a condition on tag, region, "
                "or source network."))

    for path, matched in matched_escalations(action_set):
        out.append(finding(
            "IAM-010", "critical", name,
            f"Privilege-escalation path: {path['name']}",
            f"granted via {' + '.join(matched)}",
            f"{path['why']} Remove one leg of the path, or constrain it with a "
            "permission boundary and a resource condition."))

    trust = principal.get("trust", {}) or {}
    trusted = [str(p) for p in trust.get("principals", []) or []]
    if any(p in {"*", "any"} for p in trusted):
        severity = "critical" if not trust.get("external_id") else "high"
        out.append(finding(
            "IAM-020", severity, name,
            "Role is assumable by any principal",
            f"trust.principals={trusted}, external_id={bool(trust.get('external_id'))}",
            "Enumerate the exact accounts or federated identities allowed to "
            "assume this role; a wildcard trust with no external ID is an open "
            "door into the account."))
    for entry in trusted:
        if entry.startswith("account:") and entry not in trust.get("approved", []):
            out.append(finding(
                "IAM-021", "high", name,
                "Cross-account trust to an unapproved account",
                f"trusts {entry}",
                "Verify the account belongs to your organization; if it is a "
                "vendor, require an external ID and record the relationship in "
                "the third-party register."))

    last_used = principal.get("last_used_days")
    if isinstance(last_used, int) and last_used > stale_days:
        severity = "high" if last_used > stale_days * 2 else "medium"
        out.append(finding(
            "IAM-030", severity, name,
            f"Credential unused for {last_used} days",
            f"last_used_days={last_used} (threshold {stale_days})",
            "Disable the principal, wait one cycle for breakage reports, then "
            "delete it. Unused privileged identities are the cheapest thing an "
            "attacker can find."))

    key_age = principal.get("access_key_age_days")
    if isinstance(key_age, int) and key_age > 90:
        out.append(finding(
            "IAM-031", "high", name,
            f"Long-lived static access key ({key_age} days old)",
            f"access_key_age_days={key_age}",
            "Replace static keys with short-lived federated credentials "
            "(OIDC / workload identity). If a static key is unavoidable, rotate "
            "on a 90-day maximum and alert on use from new networks."))

    if ptype in {"user", "human"} and not principal.get("mfa", False):
        out.append(finding(
            "IAM-040", "high", name,
            "Human principal without MFA",
            "mfa=false",
            "Enforce phishing-resistant MFA and block console access without it; "
            "federate to the corporate IdP rather than managing users in-cloud."))

    tier = privilege_tier(actions)
    if tier in {"admin", "admin-scoped", "write-broad"} and not principal.get("permission_boundary"):
        out.append(finding(
            "IAM-041", "medium", name,
            f"High-privilege principal ({tier}) has no permission boundary",
            "permission_boundary missing",
            "Attach a permission boundary capping the maximum privilege this "
            "principal can ever reach, so a policy mistake cannot become account "
            "takeover."))
    return out


def audit(export: Dict[str, Any], stale_days: int) -> Dict[str, Any]:
    """Audit every principal and summarize risk."""
    provider = str(export.get("provider", "aws")).lower()
    findings: List[Dict[str, Any]] = []
    summary: List[Dict[str, Any]] = []
    for principal in export.get("principals", []):
        found = check_principal(principal, stale_days)
        findings.extend(found)
        summary.append({
            "principal": principal.get("name", "<unnamed>"),
            "type": principal.get("type", "role"),
            "tier": privilege_tier(granted_actions(principal)),
            "findings": len(found),
            "risk_score": min(100, sum(SEVERITY_WEIGHT[f["severity"]] for f in found)),
        })
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["principal"]))
    summary.sort(key=lambda s: -s["risk_score"])
    counts = {sev: sum(1 for f in findings if f["severity"] == sev)
              for sev in SEVERITY_RANK}
    return {
        "provider": provider,
        "account_id": export.get("account_id", "unknown"),
        "principals_reviewed": len(export.get("principals", [])),
        "counts": counts,
        "principals": summary,
        "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str, min_severity: str) -> None:
    """Print the IAM review as JSON or human-readable text."""
    threshold = SEVERITY_RANK[min_severity]
    shown = [f for f in report["findings"] if SEVERITY_RANK[f["severity"]] <= threshold]
    if fmt == "json":
        print(json.dumps({**report, "findings": shown}, indent=2))
        return
    print(f"IAM least-privilege review — {report['provider'].upper()} "
          f"account {report['account_id']}")
    counts = report["counts"]
    print(f"Principals reviewed: {report['principals_reviewed']}   "
          f"{counts['critical']} critical, {counts['high']} high, "
          f"{counts['medium']} medium, {counts['low']} low")
    print("=" * 72)
    print("Principal risk ranking")
    for row in report["principals"]:
        print(f"  {row['risk_score']:>3}  {row['principal']:<28} "
              f"{row['type']:<8} tier={row['tier']:<13} {row['findings']} findings")
    print("-" * 72)
    for item in shown:
        print(f"[{item['severity'].upper():<8}] {item['id']}  {item['principal']}")
        print(f"           {item['title']}")
        print(f"           evidence: {item['evidence']}")
        print(f"           fix: {item['remediation']}")
    if not shown:
        print(f"No findings at or above severity '{min_severity}'.")


def main() -> None:
    """Parse arguments, run the IAM review, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Review cloud IAM principals for least-privilege violations.")
    parser.add_argument("--input", required=True,
                        help="Path to the IAM principal export JSON.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--min-severity", choices=list(SEVERITY_RANK), default="low",
                        help="Lowest severity to display (default: low).")
    parser.add_argument("--stale-days", type=int, default=90,
                        help="Days of non-use before a credential is stale "
                             "(default: 90).")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default=None,
                        help="Exit 2 if any finding at or above this severity exists.")
    args = parser.parse_args()

    if args.stale_days < 1:
        print("ERROR: --stale-days must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    report = audit(load_export(Path(args.input)), args.stale_days)
    output(report, args.format, args.min_severity)

    if args.fail_on:
        limit = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[f["severity"]] <= limit for f in report["findings"]):
            sys.exit(2)


if __name__ == "__main__":
    main()
