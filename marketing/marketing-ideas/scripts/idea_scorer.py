#!/usr/bin/env python3
"""Idea Scorer - Score and prioritize marketing ideas by impact, effort, and alignment.

Filters and ranks ideas from the marketing ideas library based on stage,
budget, goal, and team capacity constraints.

Usage:
    python idea_scorer.py ideas.json --stage growth --budget medium --goal leads
    python idea_scorer.py ideas.json --json
    python idea_scorer.py --demo
"""

import argparse
import json
import sys


EFFORT_MAP = {"low": 1, "medium": 2, "high": 3}
IMPACT_MAP = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
STAGE_MAP = {"pre_launch": 0, "early": 1, "growth": 2, "scale": 3}
BUDGET_MAP = {"free": 0, "low": 1, "medium": 2, "high": 3}


def score_idea(idea, filters):
    """Score a single idea against filters and constraints."""
    # Base score from impact and effort
    impact_score = IMPACT_MAP.get(idea.get("impact", "medium"), 2)
    effort_score = EFFORT_MAP.get(idea.get("effort", "medium"), 2)

    # Impact-to-effort ratio (higher impact, lower effort = better)
    base_score = (impact_score * 2) / max(effort_score, 1)

    # Stage alignment bonus
    stage_bonus = 0
    idea_stages = idea.get("stages", [])
    if filters.get("stage") and filters["stage"] in idea_stages:
        stage_bonus = 2
    elif not idea_stages:
        stage_bonus = 1

    # Budget alignment
    budget_bonus = 0
    idea_budget = BUDGET_MAP.get(idea.get("budget", "medium"), 2)
    filter_budget = BUDGET_MAP.get(filters.get("budget", "medium"), 2)
    if idea_budget <= filter_budget:
        budget_bonus = 1
    else:
        budget_bonus = -2  # Penalize over-budget ideas

    # Goal alignment
    goal_bonus = 0
    idea_goals = idea.get("goals", [])
    if filters.get("goal") and filters["goal"] in idea_goals:
        goal_bonus = 3

    # Timeline alignment
    timeline_bonus = 0
    if filters.get("timeline"):
        idea_timeline = idea.get("timeline", "medium")
        if filters["timeline"] == "quick" and idea_timeline in ("quick", "1-4_weeks"):
            timeline_bonus = 2
        elif filters["timeline"] == "medium" and idea_timeline in ("medium", "1-3_months"):
            timeline_bonus = 1

    total_score = base_score + stage_bonus + budget_bonus + goal_bonus + timeline_bonus

    return {
        "name": idea.get("name", "Unnamed"),
        "description": idea.get("description", ""),
        "category": idea.get("category", ""),
        "impact": idea.get("impact", "medium"),
        "effort": idea.get("effort", "medium"),
        "budget": idea.get("budget", "medium"),
        "timeline": idea.get("timeline", "medium"),
        "base_score": round(base_score, 2),
        "total_score": round(total_score, 2),
        "stage_match": filters.get("stage") in idea_stages if idea_stages else True,
        "budget_match": idea_budget <= filter_budget,
        "goal_match": filters.get("goal") in idea_goals if idea_goals else False,
    }


def filter_and_rank(ideas, filters, top_n=10):
    """Filter, score, and rank ideas."""
    scored = [score_idea(idea, filters) for idea in ideas]

    # Filter out over-budget if strict
    if filters.get("strict_budget"):
        scored = [s for s in scored if s["budget_match"]]

    # Sort by total score
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # Category distribution
    categories = {}
    for s in scored:
        cat = s["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "filters_applied": filters,
        "total_ideas_evaluated": len(ideas),
        "ideas_after_filter": len(scored),
        "top_ideas": scored[:top_n],
        "category_distribution": categories,
        "recommendation": _generate_recommendation(scored[:top_n], filters),
    }


def _generate_recommendation(top_ideas, filters):
    """Generate a recommendation summary."""
    if not top_ideas:
        return "No ideas match your constraints. Try relaxing budget or timeline filters."

    quick_wins = [i for i in top_ideas if i.get("effort") == "low" and i.get("total_score", 0) > 3]
    high_impact = [i for i in top_ideas if i.get("impact") in ("high", "very_high")]

    recs = []
    if quick_wins:
        recs.append(f"Start with quick wins: {', '.join(i['name'] for i in quick_wins[:3])}")
    if high_impact:
        recs.append(f"Highest impact opportunities: {', '.join(i['name'] for i in high_impact[:3])}")
    recs.append(f"Focus on top {min(3, len(top_ideas))} ideas before expanding.")

    return " | ".join(recs)


def get_demo_data():
    return {
        "ideas": [
            {"name": "Easy keyword targeting", "category": "content_seo", "impact": "medium", "effort": "low", "budget": "free", "timeline": "medium", "stages": ["early", "growth"], "goals": ["leads", "authority"]},
            {"name": "Programmatic SEO", "category": "content_seo", "impact": "high", "effort": "high", "budget": "high", "timeline": "long", "stages": ["growth", "scale"], "goals": ["leads"]},
            {"name": "Google Search Ads", "category": "paid", "impact": "high", "effort": "medium", "budget": "medium", "timeline": "quick", "stages": ["growth", "scale"], "goals": ["leads"]},
            {"name": "Founder newsletter", "category": "email", "impact": "high", "effort": "low", "budget": "free", "timeline": "quick", "stages": ["early", "growth"], "goals": ["authority", "retention"]},
            {"name": "Free calculator", "category": "lead_magnet", "impact": "high", "effort": "medium", "budget": "low", "timeline": "medium", "stages": ["early", "growth"], "goals": ["leads"]},
            {"name": "LinkedIn thought leadership", "category": "social", "impact": "high", "effort": "medium", "budget": "free", "timeline": "long", "stages": ["early", "growth", "scale"], "goals": ["authority"]},
            {"name": "Retargeting ads", "category": "paid", "impact": "high", "effort": "low", "budget": "low", "timeline": "quick", "stages": ["growth", "scale"], "goals": ["leads"]},
            {"name": "Community building", "category": "social", "impact": "high", "effort": "high", "budget": "medium", "timeline": "long", "stages": ["growth", "scale"], "goals": ["retention", "authority"]},
            {"name": "Viral loop", "category": "plg", "impact": "very_high", "effort": "high", "budget": "high", "timeline": "long", "stages": ["growth", "scale"], "goals": ["leads", "retention"]},
            {"name": "Content repurposing", "category": "content_seo", "impact": "high", "effort": "low", "budget": "free", "timeline": "quick", "stages": ["early", "growth", "scale"], "goals": ["leads", "authority"]},
        ],
        "filters": {"stage": "growth", "budget": "medium", "goal": "leads", "timeline": "quick"},
    }


def format_report(results):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("MARKETING IDEA PRIORITIZATION")
    lines.append("=" * 65)

    f = results["filters_applied"]
    lines.append(f"Filters: stage={f.get('stage','any')}, budget={f.get('budget','any')}, goal={f.get('goal','any')}")
    lines.append(f"Evaluated: {results['total_ideas_evaluated']} ideas")
    lines.append("")

    lines.append("--- TOP IDEAS ---")
    lines.append(f"{'Rank':>4} {'Idea':<30} {'Impact':>8} {'Effort':>8} {'Score':>7} {'Match':>6}")
    lines.append("-" * 68)

    for i, idea in enumerate(results["top_ideas"], 1):
        match = "Y" if idea["goal_match"] else "N"
        lines.append(
            f"{i:>4} {idea['name']:<30} {idea['impact']:>8} {idea['effort']:>8} "
            f"{idea['total_score']:>7.1f} {match:>6}"
        )
    lines.append("")

    if results["recommendation"]:
        lines.append(f"Recommendation: {results['recommendation']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score and prioritize marketing ideas")
    parser.add_argument("input", nargs="?", help="JSON file with ideas")
    parser.add_argument("--stage", choices=["pre_launch", "early", "growth", "scale"])
    parser.add_argument("--budget", choices=["free", "low", "medium", "high"])
    parser.add_argument("--goal", choices=["leads", "authority", "retention", "awareness", "revenue"])
    parser.add_argument("--timeline", choices=["quick", "medium", "long"])
    parser.add_argument("--top", type=int, default=10, help="Number of top ideas to show")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
        ideas = data["ideas"]
        filters = data["filters"]
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            ideas = data if isinstance(data, list) else data.get("ideas", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        filters = {}
    else:
        parser.print_help()
        sys.exit(1)

    # Override filters with CLI args
    if args.stage:
        filters["stage"] = args.stage
    if args.budget:
        filters["budget"] = args.budget
    if args.goal:
        filters["goal"] = args.goal
    if args.timeline:
        filters["timeline"] = args.timeline

    results = filter_and_rank(ideas, filters, args.top)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()
