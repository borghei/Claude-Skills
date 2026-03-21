#!/usr/bin/env python3
"""
Contract Comparison Analyzer

Compare two contract versions and identify differences in key clauses,
payment terms, and risk areas. Useful for reviewing redlines and
tracking changes between negotiation rounds.

Usage:
    python contract_comparison_analyzer.py contract_v1.json contract_v2.json
    python contract_comparison_analyzer.py contract_v1.json contract_v2.json --json
"""

import argparse
import json
import sys


KEY_CLAUSES = [
    "parties", "scope_of_work", "deliverables", "acceptance_criteria",
    "payment_terms", "payment_schedule", "ip_assignment", "pre_existing_ip",
    "confidentiality", "confidentiality_term", "liability_cap",
    "termination_for_cause", "termination_for_convenience", "notice_period",
    "governing_law", "dispute_resolution", "force_majeure",
    "change_order", "warranties", "indemnification", "non_compete",
    "non_solicitation", "dpa", "insurance",
]

RISK_INDICATORS = {
    "liability_cap": {"field": "liability_cap", "risk": "Liability cap changed -- review exposure"},
    "indemnification": {"field": "indemnification", "risk": "Indemnification terms changed -- may shift risk"},
    "termination_for_convenience": {"field": "termination_for_convenience", "risk": "Termination convenience changed -- check notice and financial terms"},
    "ip_assignment": {"field": "ip_assignment", "risk": "IP assignment changed -- verify ownership is clear"},
    "non_compete": {"field": "non_compete", "risk": "Non-compete added or modified -- check scope and duration"},
    "governing_law": {"field": "governing_law", "risk": "Governing law changed -- may affect enforceability"},
}


def compare_contracts(v1: dict, v2: dict) -> dict:
    """Compare two contract versions."""
    v1_clauses = v1.get("clauses", {})
    v2_clauses = v2.get("clauses", {})
    v1_meta = v1.get("metadata", {})
    v2_meta = v2.get("metadata", {})

    changes = []
    additions = []
    removals = []
    unchanged = []

    all_keys = set(list(v1_clauses.keys()) + list(v2_clauses.keys()))

    for key in sorted(all_keys):
        v1_val = v1_clauses.get(key)
        v2_val = v2_clauses.get(key)

        if v1_val is None and v2_val is not None:
            additions.append({
                "clause": key,
                "new_value": _summarize(v2_val),
                "is_key_clause": key in KEY_CLAUSES,
            })
        elif v1_val is not None and v2_val is None:
            removals.append({
                "clause": key,
                "old_value": _summarize(v1_val),
                "is_key_clause": key in KEY_CLAUSES,
            })
        elif v1_val != v2_val:
            changes.append({
                "clause": key,
                "old_value": _summarize(v1_val),
                "new_value": _summarize(v2_val),
                "is_key_clause": key in KEY_CLAUSES,
            })
        else:
            unchanged.append(key)

    # Risk assessment
    risk_flags = []
    for change in changes:
        if change["clause"] in RISK_INDICATORS:
            ri = RISK_INDICATORS[change["clause"]]
            risk_flags.append({
                "clause": change["clause"],
                "risk": ri["risk"],
                "old_value": change["old_value"],
                "new_value": change["new_value"],
                "severity": "HIGH",
            })

    for removal in removals:
        if removal["is_key_clause"]:
            risk_flags.append({
                "clause": removal["clause"],
                "risk": f"Key clause '{removal['clause']}' was removed -- this may create exposure",
                "old_value": removal["old_value"],
                "new_value": "(removed)",
                "severity": "HIGH",
            })

    for addition in additions:
        if addition["clause"] in ["non_compete", "non_solicitation", "indemnification"]:
            risk_flags.append({
                "clause": addition["clause"],
                "risk": f"New clause '{addition['clause']}' was added -- review carefully",
                "old_value": "(not present)",
                "new_value": addition["new_value"],
                "severity": "MEDIUM",
            })

    return {
        "version_1": v1_meta.get("version", "v1"),
        "version_2": v2_meta.get("version", "v2"),
        "summary": {
            "total_clauses_compared": len(all_keys),
            "changes": len(changes),
            "additions": len(additions),
            "removals": len(removals),
            "unchanged": len(unchanged),
            "risk_flags": len(risk_flags),
        },
        "changes": changes,
        "additions": additions,
        "removals": removals,
        "risk_flags": risk_flags,
        "recommendations": _generate_recommendations(changes, additions, removals, risk_flags),
    }


def _summarize(value) -> str:
    """Summarize a clause value for display."""
    if isinstance(value, str):
        return value[:100] + "..." if len(value) > 100 else value
    elif isinstance(value, dict):
        return json.dumps(value)[:100]
    elif isinstance(value, list):
        return f"[{len(value)} items]"
    return str(value)


def _generate_recommendations(changes: list, additions: list,
                              removals: list, risks: list) -> list:
    """Generate recommendations."""
    recs = []
    if risks:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"{len(risks)} risk flag(s) detected. Review each flagged clause before signing.",
        })
    if removals:
        key_removals = [r for r in removals if r["is_key_clause"]]
        if key_removals:
            recs.append({
                "priority": "HIGH",
                "recommendation": f"{len(key_removals)} key clause(s) removed: {', '.join(r['clause'] for r in key_removals)}. Ensure this is intentional.",
            })
    if not changes and not additions and not removals:
        recs.append({
            "priority": "INFO",
            "recommendation": "No differences found between versions.",
        })
    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"CONTRACT COMPARISON: {result['version_1']} vs {result['version_2']}")
    lines.append("=" * 60)

    s = result["summary"]
    lines.append(f"\nClauses Compared: {s['total_clauses_compared']}")
    lines.append(f"Changes: {s['changes']}, Additions: {s['additions']}, Removals: {s['removals']}, Unchanged: {s['unchanged']}")
    lines.append(f"Risk Flags: {s['risk_flags']}")

    if result["changes"]:
        lines.append(f"\n--- Changes ---")
        for c in result["changes"]:
            key_marker = " [KEY]" if c["is_key_clause"] else ""
            lines.append(f"  {c['clause']}{key_marker}:")
            lines.append(f"    OLD: {c['old_value']}")
            lines.append(f"    NEW: {c['new_value']}")

    if result["additions"]:
        lines.append(f"\n--- Additions ---")
        for a in result["additions"]:
            key_marker = " [KEY]" if a["is_key_clause"] else ""
            lines.append(f"  + {a['clause']}{key_marker}: {a['new_value']}")

    if result["removals"]:
        lines.append(f"\n--- Removals ---")
        for r in result["removals"]:
            key_marker = " [KEY]" if r["is_key_clause"] else ""
            lines.append(f"  - {r['clause']}{key_marker}: {r['old_value']}")

    if result["risk_flags"]:
        lines.append(f"\n--- Risk Flags ---")
        for rf in result["risk_flags"]:
            lines.append(f"  [{rf['severity']}] {rf['clause']}: {rf['risk']}")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two contract versions and identify differences and risk areas."
    )
    parser.add_argument("file_v1", help="JSON file with first contract version")
    parser.add_argument("file_v2", help="JSON file with second contract version")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        with open(args.file_v1, "r") as f:
            v1 = json.load(f)
        with open(args.file_v2, "r") as f:
            v2 = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = compare_contracts(v1, v2)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
