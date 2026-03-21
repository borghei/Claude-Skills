#!/usr/bin/env python3
"""ICP Fit Scorer - Score prospects against Ideal Customer Profile criteria.

Evaluates prospects on firmographic, technographic, and behavioral signals
to produce an A/B/C/D fit score.

Usage:
    python icp_fit_scorer.py prospects.json --icp icp_config.json
    python icp_fit_scorer.py prospects.json --json
    python icp_fit_scorer.py --demo
"""

import argparse
import json
import sys


DEFAULT_ICP = {
    "firmographics": {
        "employees": {"min": 50, "max": 5000, "weight": 20},
        "revenue": {"min": 5000000, "max": 500000000, "weight": 15},
        "industry": {"values": ["saas", "technology", "fintech", "services"], "weight": 20},
        "geography": {"values": ["us", "uk", "dach", "canada"], "weight": 10},
    },
    "technographics": {
        "tech_stack": {"values": ["salesforce", "hubspot", "slack", "jira"], "weight": 10},
        "maturity": {"values": ["growth", "scale"], "weight": 5},
    },
    "behavioral": {
        "funding_stage": {"values": ["series_a", "series_b", "series_c", "growth"], "weight": 10},
        "pain_level": {"min": 3, "max": 5, "weight": 10},
    },
}

GRADE_THRESHOLDS = {
    "A": 80,
    "B": 60,
    "C": 40,
    "D": 0,
}


def score_prospect(prospect, icp_config=None):
    """Score a single prospect against ICP criteria."""
    if icp_config is None:
        icp_config = DEFAULT_ICP

    total_score = 0
    total_weight = 0
    criteria_results = []

    for category, criteria in icp_config.items():
        for criterion, config in criteria.items():
            weight = config.get("weight", 10)
            total_weight += weight
            prospect_value = prospect.get(criterion)

            if prospect_value is None:
                criteria_results.append({
                    "criterion": criterion,
                    "category": category,
                    "status": "missing",
                    "score": 0,
                    "weight": weight,
                })
                continue

            score = 0
            status = "no_match"

            if "min" in config and "max" in config:
                # Range check
                val = float(prospect_value) if not isinstance(prospect_value, (int, float)) else prospect_value
                if config["min"] <= val <= config["max"]:
                    # Score based on position in range (center = best)
                    mid = (config["min"] + config["max"]) / 2
                    range_size = config["max"] - config["min"]
                    distance = abs(val - mid) / (range_size / 2)
                    score = max(0, (1 - distance * 0.3)) * weight
                    status = "match"
                elif val < config["min"]:
                    # Below range: partial credit
                    ratio = val / config["min"]
                    score = max(0, ratio * 0.5) * weight
                    status = "partial_below"
                else:
                    # Above range: partial credit
                    ratio = config["max"] / val
                    score = max(0, ratio * 0.5) * weight
                    status = "partial_above"

            elif "values" in config:
                # List match
                if isinstance(prospect_value, list):
                    matches = len(set(v.lower() for v in prospect_value) & set(v.lower() for v in config["values"]))
                    total_possible = len(config["values"])
                    score = (matches / max(total_possible, 1)) * weight
                    status = "match" if matches > 0 else "no_match"
                else:
                    val_lower = str(prospect_value).lower()
                    if val_lower in [v.lower() for v in config["values"]]:
                        score = weight
                        status = "match"

            total_score += score
            criteria_results.append({
                "criterion": criterion,
                "category": category,
                "value": prospect_value,
                "score": round(score, 1),
                "max_score": weight,
                "status": status,
            })

    # Calculate percentage and grade
    percentage = (total_score / max(total_weight, 1)) * 100
    grade = "D"
    for g, threshold in sorted(GRADE_THRESHOLDS.items()):
        if percentage >= threshold:
            grade = g

    return {
        "prospect": prospect.get("name", prospect.get("company", "Unknown")),
        "score": round(total_score, 1),
        "max_score": total_weight,
        "percentage": round(percentage, 1),
        "grade": grade,
        "criteria": criteria_results,
        "matched": len([c for c in criteria_results if c["status"] == "match"]),
        "missing": len([c for c in criteria_results if c["status"] == "missing"]),
    }


def get_demo_data():
    return {
        "prospects": [
            {"name": "TechStart Inc", "employees": 120, "revenue": 15000000, "industry": "saas", "geography": "us", "tech_stack": ["salesforce", "slack"], "funding_stage": "series_a", "pain_level": 4},
            {"name": "BigCorp Ltd", "employees": 8000, "revenue": 800000000, "industry": "manufacturing", "geography": "uk", "tech_stack": ["sap"], "funding_stage": "public", "pain_level": 2},
            {"name": "GrowthCo", "employees": 250, "revenue": 30000000, "industry": "fintech", "geography": "us", "tech_stack": ["hubspot", "jira", "slack"], "funding_stage": "series_b", "pain_level": 5},
            {"name": "SmallBiz", "employees": 15, "revenue": 500000, "industry": "retail", "geography": "canada", "tech_stack": [], "funding_stage": "seed", "pain_level": 3},
        ],
    }


def format_report(results):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("ICP FIT SCORING REPORT")
    lines.append("=" * 65)

    # Summary table
    lines.append(f"{'Prospect':<25} {'Score':>8} {'Grade':>6} {'Matched':>8}")
    lines.append("-" * 50)

    for r in sorted(results, key=lambda x: x["percentage"], reverse=True):
        lines.append(f"{r['prospect']:<25} {r['percentage']:>7.0f}% {r['grade']:>6} {r['matched']:>5}/{r['matched'] + r['missing']}")

    lines.append("")

    # Detailed per prospect
    for r in sorted(results, key=lambda x: x["percentage"], reverse=True):
        lines.append(f"--- {r['prospect']} (Grade: {r['grade']}, {r['percentage']:.0f}%) ---")
        for c in r["criteria"]:
            status_icon = {"match": "+", "partial_below": "~", "partial_above": "~", "no_match": "-", "missing": "?"}
            icon = status_icon.get(c["status"], "?")
            val = c.get("value", "N/A")
            lines.append(f"  [{icon}] {c['criterion']:<20} {str(val):<20} ({c['score']:.0f}/{c['max_score']})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score prospects against ICP criteria")
    parser.add_argument("input", nargs="?", help="JSON file with prospect data")
    parser.add_argument("--icp", help="Custom ICP config JSON file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    icp_config = DEFAULT_ICP
    if args.icp:
        with open(args.icp, "r") as f:
            icp_config = json.load(f)

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    prospects = data.get("prospects", data) if isinstance(data, dict) else data
    results = [score_prospect(p, icp_config) for p in prospects]

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()
