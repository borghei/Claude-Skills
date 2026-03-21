#!/usr/bin/env python3
"""Experiment Prioritizer - Prioritize growth experiments using ICE/RICE scoring.

Scores experiment ideas using ICE (Impact, Confidence, Ease) or RICE
(Reach, Impact, Confidence, Effort) frameworks, ranks them, and generates
a prioritized experiment roadmap.

Usage:
    python experiment_prioritizer.py experiments.json
    python experiment_prioritizer.py experiments.json --framework rice --json
    python experiment_prioritizer.py --demo
"""

import argparse
import json
import sys


def score_ice(experiments):
    """Score experiments using ICE framework."""
    results = []
    for exp in experiments:
        impact = exp.get("impact", 5)
        confidence = exp.get("confidence", 5)
        ease = exp.get("ease", 5)

        # Validate scores
        impact = max(1, min(10, impact))
        confidence = max(1, min(10, confidence))
        ease = max(1, min(10, ease))

        ice_score = (impact + confidence + ease) / 3

        results.append({
            "name": exp.get("name", "Unnamed"),
            "hypothesis": exp.get("hypothesis", ""),
            "metric": exp.get("metric", ""),
            "impact": impact,
            "confidence": confidence,
            "ease": ease,
            "ice_score": round(ice_score, 2),
            "category": _categorize_score(ice_score, "ice"),
        })

    results.sort(key=lambda x: x["ice_score"], reverse=True)
    return results


def score_rice(experiments):
    """Score experiments using RICE framework."""
    results = []
    for exp in experiments:
        reach = exp.get("reach", 1000)  # Users affected per quarter
        impact = exp.get("impact", 1)  # 0.25, 0.5, 1, 2, 3
        confidence = exp.get("confidence", 80)  # Percentage
        effort = exp.get("effort", 1)  # Person-months

        # Validate
        impact = max(0.25, min(3, impact))
        confidence = max(10, min(100, confidence))
        effort = max(0.25, min(12, effort))

        rice_score = (reach * impact * (confidence / 100)) / effort

        results.append({
            "name": exp.get("name", "Unnamed"),
            "hypothesis": exp.get("hypothesis", ""),
            "metric": exp.get("metric", ""),
            "reach": reach,
            "impact": impact,
            "confidence": confidence,
            "effort": effort,
            "rice_score": round(rice_score, 1),
            "category": _categorize_score(rice_score, "rice"),
        })

    results.sort(key=lambda x: x["rice_score"], reverse=True)
    return results


def _categorize_score(score, framework):
    if framework == "ice":
        if score >= 8:
            return "must_do"
        elif score >= 6:
            return "should_do"
        elif score >= 4:
            return "could_do"
        return "backlog"
    else:  # RICE
        if score >= 5000:
            return "must_do"
        elif score >= 1000:
            return "should_do"
        elif score >= 200:
            return "could_do"
        return "backlog"


def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """Calculate required sample size per variant (normal approximation)."""
    # Z-scores
    z_alpha = 1.96 if alpha == 0.05 else 2.576  # 95% or 99%
    z_beta = 0.842 if power == 0.8 else 1.282  # 80% or 90%

    effect = baseline_rate * mde
    n = 2 * ((z_alpha + z_beta) ** 2) * baseline_rate * (1 - baseline_rate) / (effect ** 2)
    return int(n) + 1


def generate_roadmap(scored_experiments, capacity_per_sprint=3):
    """Generate a sprint-based experiment roadmap."""
    sprints = []
    remaining = list(scored_experiments)
    sprint_num = 1

    while remaining:
        sprint = {
            "sprint": sprint_num,
            "experiments": remaining[:capacity_per_sprint],
        }
        sprints.append(sprint)
        remaining = remaining[capacity_per_sprint:]
        sprint_num += 1

    return sprints


def get_demo_data():
    return [
        {"name": "Onboarding checklist v2", "hypothesis": "Adding progress bar increases activation by 15%", "metric": "7-day activation", "impact": 8, "confidence": 7, "ease": 9},
        {"name": "Referral incentive test", "hypothesis": "Offering $10 credit doubles referral rate", "metric": "referral rate", "impact": 6, "confidence": 8, "ease": 7},
        {"name": "Pricing page redesign", "hypothesis": "Simplified pricing increases signup by 20%", "metric": "signup rate", "impact": 9, "confidence": 5, "ease": 4},
        {"name": "Email win-back sequence", "hypothesis": "4-email sequence reactivates 10% of churned", "metric": "reactivation rate", "impact": 5, "confidence": 6, "ease": 8},
        {"name": "Social proof on landing page", "hypothesis": "Adding testimonials increases conversion by 10%", "metric": "landing page CVR", "impact": 6, "confidence": 7, "ease": 9},
        {"name": "Free tool launch", "hypothesis": "Free calculator drives 500 signups/month", "metric": "monthly signups", "impact": 7, "confidence": 4, "ease": 3},
        {"name": "In-app upgrade prompt", "hypothesis": "Context-triggered prompt increases upgrades by 25%", "metric": "upgrade rate", "impact": 8, "confidence": 6, "ease": 6},
    ]


def format_report(scored, framework, roadmap=None):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"EXPERIMENT PRIORITIZATION ({framework.upper()} Framework)")
    lines.append("=" * 70)

    score_key = f"{framework}_score"

    if framework == "ice":
        lines.append(f"{'Rank':>4} {'Experiment':<30} {'I':>3} {'C':>3} {'E':>3} {'ICE':>6} {'Category':>10}")
        lines.append("-" * 65)
        for i, exp in enumerate(scored, 1):
            lines.append(
                f"{i:>4} {exp['name']:<30} {exp['impact']:>3} {exp['confidence']:>3} "
                f"{exp['ease']:>3} {exp[score_key]:>6.1f} {exp['category']:>10}"
            )
    else:
        lines.append(f"{'Rank':>4} {'Experiment':<25} {'R':>6} {'I':>4} {'C':>4} {'E':>4} {'RICE':>8} {'Cat':>10}")
        lines.append("-" * 70)
        for i, exp in enumerate(scored, 1):
            lines.append(
                f"{i:>4} {exp['name']:<25} {exp['reach']:>6} {exp['impact']:>4} "
                f"{exp['confidence']:>4} {exp['effort']:>4} {exp[score_key]:>8.0f} {exp['category']:>10}"
            )

    lines.append("")

    # Category summary
    categories = {}
    for exp in scored:
        cat = exp["category"]
        categories[cat] = categories.get(cat, 0) + 1
    lines.append("--- CATEGORY SUMMARY ---")
    for cat, count in sorted(categories.items()):
        lines.append(f"  {cat}: {count} experiments")
    lines.append("")

    # Roadmap
    if roadmap:
        lines.append("--- SPRINT ROADMAP ---")
        for sprint in roadmap:
            names = [e["name"] for e in sprint["experiments"]]
            lines.append(f"  Sprint {sprint['sprint']}: {', '.join(names)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Prioritize growth experiments with ICE/RICE")
    parser.add_argument("input", nargs="?", help="JSON file with experiment data")
    parser.add_argument("--framework", choices=["ice", "rice"], default="ice", help="Scoring framework")
    parser.add_argument("--capacity", type=int, default=3, help="Experiments per sprint")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        experiments = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            experiments = data if isinstance(data, list) else data.get("experiments", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    if args.framework == "ice":
        scored = score_ice(experiments)
    else:
        scored = score_rice(experiments)

    roadmap = generate_roadmap(scored, args.capacity)

    if args.json_output:
        print(json.dumps({"experiments": scored, "roadmap": roadmap}, indent=2))
    else:
        print(format_report(scored, args.framework, roadmap))


if __name__ == "__main__":
    main()
