#!/usr/bin/env python3
"""Trend Evaluator - Evaluate marketing trends for relevance and actionability.

Scores trends on relevance, competitor adoption, timing, risk, and brand
alignment to determine which trends are worth pursuing.

Usage:
    python trend_evaluator.py trends.json
    python trend_evaluator.py trends.json --json
    python trend_evaluator.py --demo
"""

import argparse
import json
import sys


CRITERIA = {
    "relevance": {"weight": 25, "description": "Is this trend relevant to our audience?"},
    "competitor_adoption": {"weight": 15, "description": "Are competitors acting on it?"},
    "timing": {"weight": 20, "description": "Can we be early or best?"},
    "risk": {"weight": 15, "description": "What is the downside risk?"},
    "brand_alignment": {"weight": 15, "description": "Does it align with our brand?"},
    "resource_fit": {"weight": 10, "description": "Do we have resources to execute?"},
}


def evaluate_trend(trend):
    """Evaluate a single trend against criteria."""
    name = trend.get("name", "Unnamed Trend")
    scores = trend.get("scores", {})

    weighted_total = 0
    max_total = 0
    criteria_results = []

    for criterion, config in CRITERIA.items():
        score = scores.get(criterion, 3)  # Default to neutral 3
        score = max(1, min(5, score))
        weight = config["weight"]
        weighted = (score / 5) * weight

        weighted_total += weighted
        max_total += weight

        criteria_results.append({
            "criterion": criterion,
            "score": score,
            "weight": weight,
            "weighted_score": round(weighted, 1),
            "description": config["description"],
        })

    percentage = (weighted_total / max(max_total, 1)) * 100

    # Action recommendation
    if percentage >= 75:
        action = "PURSUE"
        rationale = "Strong alignment across criteria. Allocate resources to capitalize."
    elif percentage >= 55:
        action = "EXPERIMENT"
        rationale = "Promising but uncertain. Run a small test before committing."
    elif percentage >= 35:
        action = "MONITOR"
        rationale = "Not ready to act. Track developments and reassess quarterly."
    else:
        action = "SKIP"
        rationale = "Poor fit for current situation. Focus resources elsewhere."

    return {
        "trend": name,
        "description": trend.get("description", ""),
        "category": trend.get("category", ""),
        "score": round(percentage, 1),
        "action": action,
        "rationale": rationale,
        "criteria": criteria_results,
    }


def evaluate_trends(trends):
    """Evaluate multiple trends and rank them."""
    results = [evaluate_trend(t) for t in trends]
    results.sort(key=lambda x: x["score"], reverse=True)

    # Action summary
    actions = {}
    for r in results:
        actions[r["action"]] = actions.get(r["action"], 0) + 1

    return {
        "evaluated": len(results),
        "action_summary": actions,
        "trends": results,
        "top_pursue": [r["trend"] for r in results if r["action"] == "PURSUE"][:3],
        "top_experiment": [r["trend"] for r in results if r["action"] == "EXPERIMENT"][:3],
    }


def get_demo_data():
    return [
        {"name": "AI-generated content at scale", "category": "content", "description": "Using AI tools to produce marketing content", "scores": {"relevance": 5, "competitor_adoption": 4, "timing": 3, "risk": 3, "brand_alignment": 4, "resource_fit": 4}},
        {"name": "Short-form video marketing", "category": "social", "description": "TikTok, Reels, Shorts for B2B", "scores": {"relevance": 3, "competitor_adoption": 3, "timing": 4, "risk": 2, "brand_alignment": 3, "resource_fit": 2}},
        {"name": "Privacy-first analytics", "category": "analytics", "description": "Server-side tracking and cookieless measurement", "scores": {"relevance": 5, "competitor_adoption": 2, "timing": 5, "risk": 1, "brand_alignment": 5, "resource_fit": 3}},
        {"name": "Community-led growth", "category": "community", "description": "Building owned community as growth channel", "scores": {"relevance": 4, "competitor_adoption": 3, "timing": 4, "risk": 2, "brand_alignment": 4, "resource_fit": 2}},
        {"name": "Web3 / blockchain marketing", "category": "emerging", "description": "NFTs, token-gated content, decentralized", "scores": {"relevance": 1, "competitor_adoption": 1, "timing": 2, "risk": 5, "brand_alignment": 1, "resource_fit": 1}},
    ]


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("TREND EVALUATION REPORT")
    lines.append("=" * 65)
    lines.append(f"Trends Evaluated: {analysis['evaluated']}")
    lines.append(f"Actions: {', '.join(f'{k}: {v}' for k, v in analysis['action_summary'].items())}")
    lines.append("")

    lines.append(f"{'Rank':>4} {'Trend':<35} {'Score':>6} {'Action':>12}")
    lines.append("-" * 60)

    for i, t in enumerate(analysis["trends"], 1):
        lines.append(f"{i:>4} {t['trend']:<35} {t['score']:>5.0f}% {t['action']:>12}")

    lines.append("")

    # Details for top trends
    for t in analysis["trends"][:3]:
        lines.append(f"--- {t['trend']} ({t['action']}) ---")
        lines.append(f"  {t['rationale']}")
        for c in t["criteria"]:
            bar = "#" * c["score"] + "." * (5 - c["score"])
            lines.append(f"  {c['criterion']:<25} [{bar}] {c['score']}/5")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Evaluate marketing trends for relevance and actionability")
    parser.add_argument("input", nargs="?", help="JSON file with trends to evaluate")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        trends = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            trends = data if isinstance(data, list) else data.get("trends", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = evaluate_trends(trends)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
