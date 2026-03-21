#!/usr/bin/env python3
"""Parse and score RFP requirements for response prioritization.

Reads RFP requirements from CSV or JSON, categorizes each by coverage status,
calculates overall response strength, and identifies gaps requiring attention.
Produces a prioritized response plan with effort estimates.

Usage:
    python rfp_analyzer.py --data rfp_requirements.csv
    python rfp_analyzer.py --data rfp.json --json
    python rfp_analyzer.py --data rfp.csv --deadline 2026-04-15
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


RESPONSE_CATEGORIES = {
    "full": {"score": 100, "effort_hours": 0.5, "label": "Full", "color": "green"},
    "partial": {"score": 60, "effort_hours": 2.0, "label": "Partial", "color": "yellow"},
    "roadmap": {"score": 30, "effort_hours": 1.5, "label": "Roadmap", "color": "orange"},
    "partner": {"score": 50, "effort_hours": 1.5, "label": "Partner", "color": "blue"},
    "na": {"score": 100, "effort_hours": 0.25, "label": "N/A", "color": "gray"},
    "gap": {"score": 0, "effort_hours": 3.0, "label": "Gap", "color": "red"},
}

SECTION_WEIGHTS = {
    "security": 1.5,
    "compliance": 1.5,
    "technical": 1.3,
    "integration": 1.3,
    "performance": 1.2,
    "functionality": 1.2,
    "support": 1.0,
    "pricing": 1.0,
    "general": 0.8,
    "company": 0.7,
}

PRIORITY_MAP = {
    "mandatory": 3,
    "required": 3,
    "must": 3,
    "important": 2,
    "desired": 1,
    "optional": 1,
    "nice": 1,
}


def load_data(filepath):
    """Load RFP requirements from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def normalize_category(value):
    """Normalize response category."""
    if not value:
        return "gap"
    val = str(value).lower().strip().replace(" ", "_")
    for key in RESPONSE_CATEGORIES:
        if key in val:
            return key
    if val in ("yes", "true", "1", "supported", "met"):
        return "full"
    if val in ("no", "false", "0", "unsupported", "not_met"):
        return "gap"
    return "gap"


def get_priority_score(value):
    """Get numeric priority from string."""
    if not value:
        return 2
    val = str(value).lower().strip()
    for key, score in PRIORITY_MAP.items():
        if key in val:
            return score
    return 2


def get_section_weight(section):
    """Get section importance weight."""
    if not section:
        return 1.0
    s = section.lower().strip()
    for key, weight in SECTION_WEIGHTS.items():
        if key in s:
            return weight
    return 1.0


def analyze_rfp(requirements, deadline=None):
    """Analyze RFP requirements and produce scoring report."""
    scored_reqs = []
    section_stats = defaultdict(lambda: {"count": 0, "score_sum": 0, "gaps": 0})
    category_counts = defaultdict(int)
    total_effort = 0
    total_weighted_score = 0
    total_weight = 0

    for req in requirements:
        req_id = req.get("id", req.get("req_id", req.get("number", f"R{len(scored_reqs)+1}")))
        requirement = req.get("requirement", req.get("description", req.get("question", "Unknown")))
        section = req.get("section", req.get("category", req.get("area", "General")))
        response_raw = req.get("response", req.get("coverage", req.get("status", "")))
        priority_raw = req.get("priority", req.get("importance", "important"))
        detail = req.get("detail", req.get("response_text", req.get("notes", "")))
        owner = req.get("owner", req.get("sme", req.get("assigned_to", "Unassigned")))

        category = normalize_category(response_raw)
        cat_data = RESPONSE_CATEGORIES[category]
        priority = get_priority_score(priority_raw)
        section_weight = get_section_weight(section)

        weighted_score = cat_data["score"] * priority * section_weight
        max_score = 100 * priority * section_weight
        total_weighted_score += weighted_score
        total_weight += max_score

        effort = cat_data["effort_hours"]
        if priority >= 3:
            effort *= 1.5  # More effort on mandatory items
        total_effort += effort

        category_counts[category] += 1
        section_stats[section]["count"] += 1
        section_stats[section]["score_sum"] += cat_data["score"]
        if category in ("gap", "partial"):
            section_stats[section]["gaps"] += 1

        scored_reqs.append({
            "id": req_id,
            "requirement": requirement,
            "section": section,
            "priority": priority_raw,
            "priority_score": priority,
            "response_category": cat_data["label"],
            "response_key": category,
            "score": cat_data["score"],
            "effort_hours": round(effort, 1),
            "detail": detail,
            "owner": owner,
            "needs_attention": category in ("gap", "partial") and priority >= 2,
        })

    overall_score = round((total_weighted_score / total_weight) * 100, 1) if total_weight > 0 else 0

    # Competitive position assessment
    if overall_score >= 85:
        position = "Strong Contender"
        recommendation = "Proceed with confidence. Focus on executive summary and differentiation."
    elif overall_score >= 70:
        position = "Competitive"
        recommendation = "Address gaps before submission. Emphasize strengths in executive summary."
    elif overall_score >= 55:
        position = "Viable with Risks"
        recommendation = "Significant gaps to address. Consider go/no-go review with leadership."
    else:
        position = "Weak Position"
        recommendation = "Major gaps present. Recommend no-bid unless strategic reasons justify investment."

    # Section analysis
    section_results = {}
    for section, stats in section_stats.items():
        avg = stats["score_sum"] / stats["count"] if stats["count"] > 0 else 0
        section_results[section] = {
            "requirements": stats["count"],
            "average_score": round(avg, 1),
            "gaps": stats["gaps"],
            "weight": get_section_weight(section),
        }

    # Attention items (gaps and partials on high-priority requirements)
    attention_items = [r for r in scored_reqs if r["needs_attention"]]
    attention_items.sort(key=lambda x: (x["priority_score"], -x["score"]), reverse=True)

    # Effort planning
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            days_remaining = (deadline_date - datetime.now()).days
        except ValueError:
            days_remaining = None
    else:
        days_remaining = None

    return {
        "overall_score": overall_score,
        "competitive_position": position,
        "recommendation": recommendation,
        "total_requirements": len(scored_reqs),
        "response_distribution": {
            RESPONSE_CATEGORIES[k]["label"]: v for k, v in category_counts.items() if v > 0
        },
        "section_analysis": dict(sorted(section_results.items(), key=lambda x: x[1]["average_score"])),
        "total_effort_hours": round(total_effort, 1),
        "days_remaining": days_remaining,
        "hours_per_day_needed": round(total_effort / max(days_remaining, 1), 1) if days_remaining and days_remaining > 0 else None,
        "attention_items": attention_items[:15],
        "scored_requirements": scored_reqs,
    }


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("RFP ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    lines.append(f"\n  Overall RFP Score:       {results['overall_score']}%")
    lines.append(f"  Competitive Position:    {results['competitive_position']}")
    lines.append(f"  Recommendation:          {results['recommendation']}")
    lines.append(f"  Total Requirements:      {results['total_requirements']}")
    lines.append(f"  Estimated Effort:        {results['total_effort_hours']} hours")
    if results["days_remaining"] is not None:
        lines.append(f"  Days Until Deadline:     {results['days_remaining']}")
        if results["hours_per_day_needed"]:
            lines.append(f"  Hours/Day Needed:        {results['hours_per_day_needed']}")

    lines.append(f"\n  Response Distribution:")
    for label, count in results["response_distribution"].items():
        pct = round(count / results["total_requirements"] * 100, 1)
        bar_len = int(pct / 5)
        bar = "#" * bar_len
        lines.append(f"    {label:<15} {count:>4} ({pct:>5.1f}%) {bar}")

    lines.append(f"\n{'SECTION ANALYSIS':^70}")
    lines.append("-" * 70)
    lines.append(f"  {'Section':<25} {'Reqs':>5} {'Avg Score':>10} {'Gaps':>5} {'Weight':>7}")
    lines.append("  " + "-" * 54)
    for section, data in results["section_analysis"].items():
        flag = " !!" if data["gaps"] > 0 and data["weight"] >= 1.3 else ""
        lines.append(
            f"  {section:<25} {data['requirements']:>5} "
            f"{data['average_score']:>9.1f} {data['gaps']:>5} {data['weight']:>6.1f}x{flag}"
        )

    if results["attention_items"]:
        lines.append(f"\n{'ITEMS REQUIRING ATTENTION':^70}")
        lines.append("-" * 70)
        for item in results["attention_items"]:
            lines.append(f"  [{item['id']}] {item['requirement'][:50]}")
            lines.append(
                f"         Section: {item['section']} | Priority: {item['priority']} | "
                f"Status: {item['response_category']} | Effort: {item['effort_hours']}h | "
                f"Owner: {item['owner']}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse and score RFP requirements for response prioritization."
    )
    parser.add_argument("--data", required=True, help="Path to RFP requirements CSV or JSON file")
    parser.add_argument("--deadline", default=None, help="Submission deadline (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    requirements = load_data(args.data)
    if not requirements:
        print("Error: No requirements found in input file.", file=sys.stderr)
        sys.exit(1)

    results = analyze_rfp(requirements, args.deadline)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    sys.exit(0 if results["overall_score"] >= 55 else 1)


if __name__ == "__main__":
    main()
