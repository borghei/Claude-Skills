#!/usr/bin/env python3
"""Idea Scorer - Score and rank product ideas using weighted criteria.

Reads a list of ideas with scores across 5 criteria and produces a
weighted ranking with recommendations for validation.

Usage:
    python idea_scorer.py --ideas ideas.json
    python idea_scorer.py --ideas ideas.json --json
    python idea_scorer.py --example
"""

import argparse
import json
import sys


DEFAULT_WEIGHTS = {
    "customer_impact": 0.30,
    "strategic_alignment": 0.25,
    "feasibility": 0.20,
    "speed_to_validate": 0.15,
    "differentiation": 0.10,
}


VALIDATION_BY_RISK = {
    "value": "Value risk: fake-door or landing-page test, or 5 problem interviews, before building.",
    "usability": "Usability risk: put a clickable prototype in front of 5 target users and watch them try it.",
    "feasibility": "Feasibility risk: 2-3 day technical spike on real data to prove the core mechanism.",
    "viability": "Viability risk: price or cost test, plus a review with legal, finance or sales.",
}
RISK_KEYWORDS = {
    "feasibility": ("we can", "accurately", "technically", "predict", "integrat", "scale", "latency", "build"),
    "viability": ("pay", "price", "revenue", "margin", "cost", "legal", "compliance", "sales"),
    "usability": ("complete", "understand", "find", "skip", "learn", "confus", "navigate", "figure out"),
}


def classify_assumption(text: str) -> str:
    """Map an assumption to value/usability/feasibility/viability risk by keywords."""
    lowered = str(text).lower()
    for risk, words in RISK_KEYWORDS.items():
        if any(w in lowered for w in words):
            return risk
    return "value"


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def score_ideas(data: dict) -> dict:
    ideas = data.get("ideas", [])
    weights = data.get("weights", DEFAULT_WEIGHTS)
    context = data.get("context", {})

    results = []
    for idea in ideas:
        name = idea.get("name", "Untitled")
        scores = idea.get("scores", {})

        weighted_score = 0
        for criterion, weight in weights.items():
            raw = scores.get(criterion, 5)
            raw = max(1, min(10, raw))
            weighted_score += raw * weight

        weighted_score = round(weighted_score, 2)

        weakest = min(scores.items(), key=lambda x: x[1]) if scores else ("unknown", 5)
        # The validation step tests the riskiest assumption, so it follows the assumption's
        # risk type: explicit "assumption_type", else keywords in the assumption text.
        assumption = idea.get("riskiest_assumption", "TBD")
        risk_type = idea.get("assumption_type") or classify_assumption(assumption)
        validation_focus = VALIDATION_BY_RISK[risk_type]
        confidence = idea.get("confidence")

        results.append({
            "rank": 0,
            "name": name,
            "source": idea.get("source", "Unknown"),
            "description": idea.get("description", ""),
            "weighted_score": weighted_score,
            "scores": scores,
            "effort": idea.get("effort", "M"),
            "riskiest_assumption": assumption,
            "assumption_type": risk_type,
            "confidence": confidence,
            "validation_suggestion": validation_focus,
            "weakest_criterion": weakest[0],
        })

    results.sort(key=lambda x: x["weighted_score"], reverse=True)
    for i, r in enumerate(results, 1):
        r["rank"] = i

    return {
        "context": context,
        "weights": weights,
        "total_ideas": len(results),
        "ideas": results,
        "top_5": results[:5],
    }


def print_report(result: dict) -> None:
    ctx = result.get("context", {})
    if ctx:
        print(f"\nIdea Scoring: {ctx.get('target_outcome', 'Product Ideation')}")
    else:
        print(f"\nIdea Scoring Results")
    print("=" * 70)

    print(f"\nRanking ({result['total_ideas']} ideas):")
    print(f"  {'Rank':>4} {'Name':<25} {'Source':<10} {'Score':>6} {'Effort':<6} {'Weakest'}")
    print(f"  {'-'*4} {'-'*25} {'-'*10} {'-'*6} {'-'*6} {'-'*20}")
    for idea in result["ideas"]:
        name = idea["name"][:23] + ".." if len(idea["name"]) > 25 else idea["name"]
        print(f"  {idea['rank']:>4} {name:<25} {idea['source']:<10} {idea['weighted_score']:>6.2f} {idea['effort']:<6} {idea['weakest_criterion']}")

    print(f"\nTop 5 Details:")
    for idea in result["top_5"]:
        print(f"\n  #{idea['rank']} {idea['name']} (Score: {idea['weighted_score']:.2f})")
        if idea["description"]:
            print(f"     {idea['description'][:80]}")
        print(f"     Riskiest Assumption ({idea['assumption_type']}): {idea['riskiest_assumption']}")
        if idea["confidence"] is None:
            print("     Confidence: not stated - say what evidence the scores rest on")
        elif idea["confidence"] < 5:
            print(f"     Confidence: {idea['confidence']}/10 - low; test this bet before ranking it")
        print(f"     Validation: {idea['validation_suggestion']}")
    print()


def print_example() -> None:
    example = {
        "context": {"target_outcome": "Reduce time-to-value from 14 days to 3 days"},
        "ideas": [
            {
                "name": "Guided Onboarding Wizard",
                "source": "PM",
                "description": "Step-by-step wizard for first-time setup",
                "effort": "M",
                "riskiest_assumption": "Users will complete the wizard rather than skip it",
                "confidence": 7,
                "scores": {"customer_impact": 9, "strategic_alignment": 8, "feasibility": 7, "speed_to_validate": 6, "differentiation": 5},
            },
            {
                "name": "Smart Defaults Engine",
                "source": "Engineer",
                "description": "Auto-configure settings based on industry and company size",
                "effort": "L",
                "riskiest_assumption": "We can accurately predict useful defaults from limited signup data",
                "confidence": 3,
                "scores": {"customer_impact": 7, "strategic_alignment": 7, "feasibility": 5, "speed_to_validate": 4, "differentiation": 8},
            },
            {
                "name": "Interactive Demo Mode",
                "source": "Designer",
                "description": "Pre-populated demo environment users can explore before committing",
                "effort": "S",
                "riskiest_assumption": "Exploring a demo translates to higher activation",
                "scores": {"customer_impact": 6, "strategic_alignment": 6, "feasibility": 8, "speed_to_validate": 9, "differentiation": 6},
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Score and rank product ideas.")
    parser.add_argument("--ideas", type=str, help="Path to ideas JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.ideas:
        parser.error("--ideas is required")

    data = load_data(args.ideas)
    result = score_ideas(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        print(f"error: bad input ({type(exc).__name__}): {exc}", file=sys.stderr)
        sys.exit(2)
