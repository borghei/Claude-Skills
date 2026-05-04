#!/usr/bin/env python3
"""
Lead Qualifier — score and tier a list of leads against an ICP definition.

Usage:
    python lead_qualifier.py icp.json leads.csv
    python lead_qualifier.py icp.json leads.csv --json
"""

import argparse
import csv
import json
import sys
from pathlib import Path


def normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def value_matches(rule_value, lead_value):
    """Check whether a lead's field value matches an ICP rule value.

    Rules can be a single value or a list. Comparison is case-insensitive
    substring match: "saas" rule matches lead "B2B SaaS Platform".
    """
    if rule_value is None:
        return False
    lead_str = normalize(lead_value)
    if not lead_str:
        return False
    if isinstance(rule_value, list):
        candidates = rule_value
    else:
        candidates = [rule_value]
    for cand in candidates:
        if normalize(cand) and normalize(cand) in lead_str:
            return True
    return False


def size_matches(rule, lead_size):
    """Match a numeric size band like {"min": 50, "max": 1000}."""
    try:
        n = int(str(lead_size).replace(",", "").strip())
    except (ValueError, TypeError):
        return False
    lo = rule.get("min")
    hi = rule.get("max")
    if lo is not None and n < lo:
        return False
    if hi is not None and n > hi:
        return False
    return True


def score_lead(icp, lead):
    must_rules = icp.get("must_have", [])
    nice_rules = icp.get("nice_to_have", [])
    disq_rules = icp.get("disqualifiers", [])

    # Disqualifiers first — any hit knocks the lead out
    for rule in disq_rules:
        field = rule.get("field")
        if field and value_matches(rule.get("value"), lead.get(field, "")):
            return {
                "score": 0,
                "tier": "disqualified",
                "reason": f"Disqualified on {field}: {lead.get(field, '')}",
                "matched_signals": [],
                "missing_signals": [],
            }

    matched = []
    missing = []
    earned = 0.0
    total_possible = 0.0

    for rule in must_rules:
        weight = float(rule.get("weight", 10))
        total_possible += weight
        field = rule.get("field")
        if field == "size" and size_matches(rule, lead.get("size", "")):
            earned += weight
            matched.append(f"size in [{rule.get('min')},{rule.get('max')}]")
        elif value_matches(rule.get("value"), lead.get(field, "")):
            earned += weight
            matched.append(f"{field}: {lead.get(field, '')}")
        else:
            missing.append(f"must-have {field}")

    for rule in nice_rules:
        weight = float(rule.get("weight", 5)) * 0.5  # nice-to-have at half weight
        total_possible += weight
        field = rule.get("field")
        if value_matches(rule.get("value"), lead.get(field, "")):
            earned += weight
            matched.append(f"{field}: {lead.get(field, '')}")

    score = round((earned / total_possible) * 100, 1) if total_possible else 0

    if score >= 75:
        tier = "A"
    elif score >= 50:
        tier = "B"
    elif score > 0:
        tier = "C"
    else:
        tier = "disqualified"

    return {
        "score": score,
        "tier": tier,
        "reason": f"Matched {len(matched)} signals" if matched else "No signal matches",
        "matched_signals": matched,
        "missing_signals": missing,
    }


def render_human(scored):
    if not scored:
        return "No leads to score."
    counts = {"A": 0, "B": 0, "C": 0, "disqualified": 0}
    for row in scored:
        counts[row["tier"]] = counts.get(row["tier"], 0) + 1
    lines = []
    lines.append(f"Scored {len(scored)} leads — A: {counts['A']}, B: {counts['B']}, C: {counts['C']}, disqualified: {counts['disqualified']}")
    lines.append("")
    lines.append(f"{'Tier':<14}{'Score':<8}{'Company':<32}Reason")
    lines.append("-" * 90)
    for row in sorted(scored, key=lambda r: -r["score"]):
        lines.append(
            f"{row['tier']:<14}{row['score']:<8}{(row['company'] or '')[:30]:<32}{row['reason']}"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score leads against an ICP definition.")
    parser.add_argument("icp", help="Path to icp.json")
    parser.add_argument("leads", help="Path to leads.csv")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    try:
        icp = json.loads(Path(args.icp).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"Error reading ICP: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in ICP file: {exc}", file=sys.stderr)
        return 1

    try:
        with Path(args.leads).open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    except FileNotFoundError as exc:
        print(f"Error reading leads: {exc}", file=sys.stderr)
        return 1

    scored = []
    for lead in leads:
        result = score_lead(icp, lead)
        result["company"] = lead.get("company", "")
        scored.append(result)

    if args.json:
        print(json.dumps(scored, indent=2))
    else:
        print(render_human(scored))
    return 0


if __name__ == "__main__":
    sys.exit(main())
