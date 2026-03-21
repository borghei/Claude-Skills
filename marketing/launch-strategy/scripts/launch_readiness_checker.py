#!/usr/bin/env python3
"""Launch Readiness Checker - Assess launch preparedness across all dimensions.

Evaluates launch assets, channel preparation, team readiness, and tracking
setup to generate a go/no-go readiness score.

Usage:
    python launch_readiness_checker.py checklist.json
    python launch_readiness_checker.py checklist.json --json
    python launch_readiness_checker.py --tier 1 --interactive
"""

import argparse
import json
import sys


TIER_1_CHECKLIST = {
    "positioning": {
        "weight": 3,
        "items": [
            "One-sentence value prop defined",
            "Primary audience segment identified",
            "Key differentiator documented",
            "Competitive positioning clear",
        ],
    },
    "assets": {
        "weight": 3,
        "items": [
            "Landing page live or ready to flip",
            "Blog post drafted and reviewed",
            "Product screenshots or demo video ready",
            "Email announcement drafted",
            "Social media posts created per platform",
            "Press release or media pitch prepared",
            "Internal FAQ created",
            "Customer FAQ created",
        ],
    },
    "channels": {
        "weight": 2,
        "items": [
            "Email sequences loaded and tested",
            "Social posts scheduled",
            "Product Hunt listing prepared",
            "Community posts drafted (HN, Reddit)",
            "Paid amplification budget allocated",
            "Partner co-marketing confirmed",
        ],
    },
    "team": {
        "weight": 2,
        "items": [
            "Team briefed on launch plan",
            "Support team briefed on new feature",
            "Talking points distributed",
            "Launch day schedule shared",
            "Escalation contacts identified",
        ],
    },
    "tracking": {
        "weight": 2,
        "items": [
            "Analytics tracking configured",
            "UTM parameters created",
            "Conversion events defined",
            "Launch metrics dashboard ready",
        ],
    },
    "operations": {
        "weight": 1,
        "items": [
            "Rollback plan documented",
            "War room channel created",
            "Post-launch follow-up plan ready",
        ],
    },
}

TIER_2_CHECKLIST = {
    "positioning": {
        "weight": 3,
        "items": [
            "Value prop defined",
            "Target audience identified",
        ],
    },
    "assets": {
        "weight": 3,
        "items": [
            "Landing page or feature page ready",
            "Blog post drafted",
            "Email announcement drafted",
            "Social media posts created",
        ],
    },
    "channels": {
        "weight": 2,
        "items": [
            "Email loaded and tested",
            "Social posts scheduled",
            "In-app notification configured",
        ],
    },
    "team": {
        "weight": 1,
        "items": [
            "Team briefed",
            "Support team aware",
        ],
    },
    "tracking": {
        "weight": 2,
        "items": [
            "Analytics tracking configured",
            "UTM parameters created",
        ],
    },
}


def assess_readiness(checklist_data, tier=1):
    """Assess launch readiness from checklist responses."""
    template = TIER_1_CHECKLIST if tier == 1 else TIER_2_CHECKLIST
    category_results = {}
    total_weighted_score = 0
    total_weight = 0

    for category, config in template.items():
        items = config["items"]
        weight = config["weight"]
        responses = checklist_data.get(category, {})

        completed = 0
        incomplete = []
        for item in items:
            status = responses.get(item, False)
            if status:
                completed += 1
            else:
                incomplete.append(item)

        completion_rate = completed / max(len(items), 1)
        weighted_score = completion_rate * weight

        category_results[category] = {
            "total_items": len(items),
            "completed": completed,
            "completion_rate": round(completion_rate * 100, 1),
            "weight": weight,
            "weighted_score": round(weighted_score, 2),
            "incomplete_items": incomplete,
            "status": "ready" if completion_rate >= 0.8 else ("at_risk" if completion_rate >= 0.5 else "not_ready"),
        }

        total_weighted_score += weighted_score
        total_weight += weight

    overall_score = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0

    # Go/No-Go decision
    blocking = []
    for cat, result in category_results.items():
        if result["status"] == "not_ready" and template[cat]["weight"] >= 2:
            blocking.append(cat)

    if overall_score >= 80 and not blocking:
        decision = "GO"
        rationale = "All critical categories meet minimum readiness. Proceed with launch."
    elif overall_score >= 60 and not blocking:
        decision = "CONDITIONAL GO"
        rationale = "Core readiness met. Complete remaining items in parallel with launch."
    else:
        decision = "NO-GO"
        rationale = f"Critical gaps in: {', '.join(blocking)}. Resolve before launching."

    # Risk assessment
    risks = []
    for cat, result in category_results.items():
        if result["incomplete_items"]:
            severity = "high" if template[cat]["weight"] >= 3 else ("medium" if template[cat]["weight"] >= 2 else "low")
            for item in result["incomplete_items"]:
                risks.append({
                    "category": cat,
                    "item": item,
                    "severity": severity,
                })

    risks.sort(key=lambda r: {"high": 0, "medium": 1, "low": 2}[r["severity"]])

    return {
        "tier": tier,
        "overall_score": round(overall_score, 1),
        "decision": decision,
        "rationale": rationale,
        "categories": category_results,
        "blocking_categories": blocking,
        "risks": risks,
        "total_items": sum(r["total_items"] for r in category_results.values()),
        "total_completed": sum(r["completed"] for r in category_results.values()),
    }


def run_interactive(tier=1):
    """Run interactive readiness check."""
    template = TIER_1_CHECKLIST if tier == 1 else TIER_2_CHECKLIST
    print(f"=== LAUNCH READINESS CHECK (Tier {tier}) ===")
    print("Answer y/n for each item:\n")

    checklist_data = {}
    for category, config in template.items():
        print(f"\n--- {category.upper()} ---")
        checklist_data[category] = {}
        for item in config["items"]:
            try:
                answer = input(f"  {item}? (y/n): ").strip().lower()
                checklist_data[category][item] = answer in ("y", "yes", "1", "true")
            except EOFError:
                checklist_data[category][item] = False

    return checklist_data


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"LAUNCH READINESS REPORT (Tier {analysis['tier']})")
    lines.append("=" * 65)
    lines.append(f"Overall Score:    {analysis['overall_score']:.0f}%")
    lines.append(f"Decision:         {analysis['decision']}")
    lines.append(f"Rationale:        {analysis['rationale']}")
    lines.append(f"Items:            {analysis['total_completed']}/{analysis['total_items']} complete")
    lines.append("")

    # Category breakdown
    lines.append("--- CATEGORY BREAKDOWN ---")
    for cat, data in analysis["categories"].items():
        status_marker = {"ready": "[OK]", "at_risk": "[!!]", "not_ready": "[XX]"}[data["status"]]
        bar_full = int(data["completion_rate"] / 5)
        bar = "#" * bar_full + "." * (20 - bar_full)
        lines.append(f"  {status_marker} {cat:<15} [{bar}] {data['completion_rate']:.0f}% ({data['completed']}/{data['total_items']})")
    lines.append("")

    # Incomplete items by severity
    high_risks = [r for r in analysis["risks"] if r["severity"] == "high"]
    medium_risks = [r for r in analysis["risks"] if r["severity"] == "medium"]

    if high_risks:
        lines.append("--- CRITICAL GAPS (must resolve) ---")
        for r in high_risks:
            lines.append(f"  [{r['category']}] {r['item']}")
        lines.append("")

    if medium_risks:
        lines.append("--- IMPORTANT GAPS (should resolve) ---")
        for r in medium_risks:
            lines.append(f"  [{r['category']}] {r['item']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Assess launch readiness")
    parser.add_argument("input", nargs="?", help="JSON file with checklist responses")
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1, help="Launch tier")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--interactive", action="store_true", help="Run interactive check")
    args = parser.parse_args()

    if args.interactive:
        checklist_data = run_interactive(args.tier)
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                checklist_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = assess_readiness(checklist_data, args.tier)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))

    sys.exit(0 if analysis["decision"] in ("GO", "CONDITIONAL GO") else 1)


if __name__ == "__main__":
    main()
