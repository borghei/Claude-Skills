#!/usr/bin/env python3
"""
Tool Idea Scorer

Score free tool ideas against the 6-factor evaluation framework
(search volume, competition, build effort, lead capture potential,
SEO value, viral potential) and rank candidates.

Usage:
    python tool_idea_scorer.py tool_ideas.json
    python tool_idea_scorer.py tool_ideas.json --json
"""

import argparse
import json
import sys


FACTORS = [
    {"key": "search_volume", "label": "Search Volume", "max": 5},
    {"key": "competition", "label": "Competition (lack of)", "max": 5},
    {"key": "build_effort", "label": "Build Effort (ease)", "max": 5},
    {"key": "lead_capture", "label": "Lead Capture Potential", "max": 5},
    {"key": "seo_value", "label": "SEO Value", "max": 5},
    {"key": "viral_potential", "label": "Viral Potential", "max": 5},
]

THRESHOLDS = {
    "build_immediately": 25,
    "strong_candidate": 20,
    "conditional": 15,
}


def score_ideas(data: dict) -> dict:
    """Score and rank tool ideas."""
    ideas = data.get("ideas", [])
    if not ideas:
        return {"error": "No tool ideas provided."}

    scored = []
    for idea in ideas:
        name = idea.get("name", "Unknown")
        tool_type = idea.get("type", "unknown")
        scores = idea.get("scores", {})

        factor_scores = []
        total = 0
        for factor in FACTORS:
            score = min(5, max(0, scores.get(factor["key"], 0)))
            factor_scores.append({
                "factor": factor["label"],
                "key": factor["key"],
                "score": score,
                "max": factor["max"],
            })
            total += score

        # Decision
        if total >= THRESHOLDS["build_immediately"]:
            decision = "BUILD IMMEDIATELY"
            rationale = "Strong across all factors. Prioritize development."
        elif total >= THRESHOLDS["strong_candidate"]:
            decision = "STRONG CANDIDATE"
            rationale = "Validate search volume before committing resources."
        elif total >= THRESHOLDS["conditional"]:
            decision = "CONDITIONAL"
            rationale = "Build only if resources are available and strategic fit is strong."
        else:
            decision = "DO NOT BUILD"
            rationale = "Score too low. Rethink concept or find a different angle."

        # Strengths and weaknesses
        sorted_factors = sorted(factor_scores, key=lambda x: x["score"], reverse=True)
        strengths = [f for f in sorted_factors if f["score"] >= 4]
        weaknesses = [f for f in sorted_factors if f["score"] <= 2]

        scored.append({
            "name": name,
            "type": tool_type,
            "total_score": total,
            "max_score": 30,
            "percentage": round(total / 30 * 100, 1),
            "decision": decision,
            "rationale": rationale,
            "factor_scores": factor_scores,
            "strengths": [f["factor"] for f in strengths],
            "weaknesses": [f["factor"] for f in weaknesses],
        })

    scored.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "total_ideas_evaluated": len(scored),
        "build_immediately": sum(1 for s in scored if s["decision"] == "BUILD IMMEDIATELY"),
        "strong_candidates": sum(1 for s in scored if s["decision"] == "STRONG CANDIDATE"),
        "ranked_ideas": scored,
        "recommendations": _generate_recommendations(scored),
    }


def _generate_recommendations(ideas: list) -> list:
    """Generate recommendations."""
    recs = []
    top = [i for i in ideas if i["decision"] == "BUILD IMMEDIATELY"]
    if top:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Start with '{top[0]['name']}' -- highest score ({top[0]['total_score']}/30).",
        })
    elif ideas:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": f"No clear winner. Consider improving the top idea '{ideas[0]['name']}' concept to address weaknesses: {', '.join(ideas[0]['weaknesses'][:2])}.",
        })

    # Common weakness
    all_weaknesses = []
    for i in ideas:
        all_weaknesses.extend(i["weaknesses"])
    if all_weaknesses:
        from collections import Counter
        common = Counter(all_weaknesses).most_common(1)
        if common:
            recs.append({
                "priority": "MEDIUM",
                "recommendation": f"Common weakness across ideas: '{common[0][0]}'. Address this in concept refinement.",
            })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("TOOL IDEA SCORER -- 6-Factor Evaluation")
    lines.append("=" * 60)

    lines.append(f"\nIdeas Evaluated: {result['total_ideas_evaluated']}")
    lines.append(f"Build Immediately: {result['build_immediately']}")
    lines.append(f"Strong Candidates: {result['strong_candidates']}")

    for idea in result["ranked_ideas"]:
        lines.append(f"\n--- {idea['name']} ({idea['type']}) ---")
        lines.append(f"Score: {idea['total_score']}/30 ({idea['percentage']}%)")
        lines.append(f"Decision: {idea['decision']}")
        lines.append(f"Rationale: {idea['rationale']}")

        lines.append(f"  Factors:")
        for f in idea["factor_scores"]:
            bar = "#" * f["score"] + "." * (5 - f["score"])
            lines.append(f"    {f['factor']:<25} [{bar}] {f['score']}/5")

        if idea["strengths"]:
            lines.append(f"  Strengths: {', '.join(idea['strengths'])}")
        if idea["weaknesses"]:
            lines.append(f"  Weaknesses: {', '.join(idea['weaknesses'])}")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score free tool ideas against the 6-factor evaluation framework."
    )
    parser.add_argument("input_file", help="JSON file with tool ideas and scores")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = score_ideas(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
