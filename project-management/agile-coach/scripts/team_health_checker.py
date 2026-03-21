#!/usr/bin/env python3
"""Team Health Checker - Evaluate team health across multiple dimensions.

Reads a YAML/JSON team health survey and produces a scored report with
recommendations. Based on the Spotify Squad Health Check model adapted
for general agile teams.

Usage:
    python team_health_checker.py --survey survey.json
    python team_health_checker.py --survey survey.json --json
    python team_health_checker.py --example
"""

import argparse
import json
import sys
from datetime import datetime


DIMENSIONS = [
    "psychological_safety",
    "delivery_pace",
    "code_quality",
    "learning",
    "collaboration",
    "fun",
    "mission_clarity",
    "autonomy",
    "support",
    "sustainable_pace",
]

DIMENSION_LABELS = {
    "psychological_safety": "Psychological Safety",
    "delivery_pace": "Delivery Pace",
    "code_quality": "Code & Quality",
    "learning": "Learning & Growth",
    "collaboration": "Collaboration",
    "fun": "Fun & Engagement",
    "mission_clarity": "Mission Clarity",
    "autonomy": "Autonomy",
    "support": "Support & Tools",
    "sustainable_pace": "Sustainable Pace",
}

RECOMMENDATIONS = {
    "psychological_safety": "Run a team agreement workshop; introduce blameless post-mortems; leader models vulnerability by sharing own mistakes.",
    "delivery_pace": "Review WIP limits; identify and remove top 3 blockers; check if sprint commitments are realistic.",
    "code_quality": "Introduce pair programming sessions; increase code review coverage; invest in CI/CD pipeline improvements.",
    "learning": "Allocate 10% time for learning; start a book club or tech talk series; create individual development plans.",
    "collaboration": "Introduce mob programming; create cross-functional pairing rotations; improve documentation for shared context.",
    "fun": "Plan team social events; celebrate wins publicly; introduce team rituals (e.g., Friday demos).",
    "mission_clarity": "Revisit team charter; connect sprint goals to product vision; share customer impact stories regularly.",
    "autonomy": "Reduce approval gates; empower team to make technical decisions; increase ownership of end-to-end features.",
    "support": "Audit tooling satisfaction; address top infrastructure pain points; ensure management removes escalated blockers.",
    "sustainable_pace": "Review overtime trends; protect sprint capacity from ad-hoc requests; check vacation usage rates.",
}


def load_survey(path: str) -> dict:
    """Load survey data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def validate_survey(data: dict) -> list:
    """Validate survey structure and return list of errors."""
    errors = []
    if "team" not in data:
        errors.append("Missing 'team' field")
    if "respondents" not in data or not isinstance(data.get("respondents"), list):
        errors.append("Missing or invalid 'respondents' list")
        return errors
    for i, resp in enumerate(data["respondents"]):
        if "name" not in resp:
            errors.append(f"Respondent {i}: missing 'name'")
        if "scores" not in resp or not isinstance(resp.get("scores"), dict):
            errors.append(f"Respondent {i}: missing or invalid 'scores'")
            continue
        for dim in DIMENSIONS:
            score = resp["scores"].get(dim)
            if score is None:
                errors.append(f"Respondent {i} ({resp.get('name', '?')}): missing score for '{dim}'")
            elif not isinstance(score, (int, float)) or score < 1 or score > 5:
                errors.append(f"Respondent {i} ({resp.get('name', '?')}): '{dim}' score must be 1-5, got {score}")
    return errors


def analyze_health(data: dict) -> dict:
    """Analyze team health from survey data."""
    respondents = data["respondents"]
    n = len(respondents)

    dimension_scores = {}
    for dim in DIMENSIONS:
        scores = [r["scores"][dim] for r in respondents if dim in r.get("scores", {})]
        if scores:
            avg = sum(scores) / len(scores)
            spread = max(scores) - min(scores)
            dimension_scores[dim] = {
                "average": round(avg, 2),
                "min": min(scores),
                "max": max(scores),
                "spread": spread,
                "responses": len(scores),
            }

    overall = sum(d["average"] for d in dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0

    # Classify health
    if overall >= 4.0:
        status = "Thriving"
    elif overall >= 3.0:
        status = "Healthy"
    elif overall >= 2.0:
        status = "At Risk"
    else:
        status = "Critical"

    # Find strengths and concerns
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1]["average"], reverse=True)
    strengths = [(dim, info) for dim, info in sorted_dims[:3]]
    concerns = [(dim, info) for dim, info in sorted_dims[-3:] if info["average"] < 3.5]

    # High-spread dimensions (disagreement)
    high_spread = [(dim, info) for dim, info in dimension_scores.items() if info["spread"] >= 3]

    # Generate recommendations
    recs = []
    for dim, info in concerns:
        recs.append({
            "dimension": DIMENSION_LABELS.get(dim, dim),
            "score": info["average"],
            "action": RECOMMENDATIONS.get(dim, "Investigate root cause with the team."),
        })

    return {
        "team": data.get("team", "Unknown"),
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "respondent_count": n,
        "overall_score": round(overall, 2),
        "status": status,
        "dimensions": dimension_scores,
        "strengths": [{"dimension": DIMENSION_LABELS.get(d, d), "score": i["average"]} for d, i in strengths],
        "concerns": [{"dimension": DIMENSION_LABELS.get(d, d), "score": i["average"]} for d, i in concerns],
        "high_disagreement": [{"dimension": DIMENSION_LABELS.get(d, d), "spread": i["spread"]} for d, i in high_spread],
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable health check report."""
    print(f"\nTeam Health Check: {result['team']}")
    print(f"Date: {result['date']}  |  Respondents: {result['respondent_count']}")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']:.1f} / 5.0  ({result['status']})")
    print()

    print("Dimension Scores:")
    for dim in DIMENSIONS:
        info = result["dimensions"].get(dim, {})
        label = DIMENSION_LABELS.get(dim, dim)
        avg = info.get("average", 0)
        bar = "#" * int(avg * 4) + "-" * (20 - int(avg * 4))
        indicator = ""
        if info.get("spread", 0) >= 3:
            indicator = "  [!] High disagreement"
        print(f"  {label:<25} {avg:.1f}  [{bar}]{indicator}")

    if result["strengths"]:
        print(f"\nStrengths:")
        for s in result["strengths"]:
            print(f"  + {s['dimension']} ({s['score']:.1f})")

    if result["concerns"]:
        print(f"\nConcerns:")
        for c in result["concerns"]:
            print(f"  - {c['dimension']} ({c['score']:.1f})")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for r in result["recommendations"]:
            print(f"  [{r['dimension']} @ {r['score']:.1f}]")
            print(f"    {r['action']}")

    print()


def print_example() -> None:
    """Print example survey JSON."""
    example = {
        "team": "Team Alpha",
        "date": "2026-03-21",
        "respondents": [
            {
                "name": "Alice",
                "scores": {
                    "psychological_safety": 4, "delivery_pace": 3, "code_quality": 4,
                    "learning": 3, "collaboration": 5, "fun": 4,
                    "mission_clarity": 4, "autonomy": 3, "support": 3, "sustainable_pace": 2,
                },
            },
            {
                "name": "Bob",
                "scores": {
                    "psychological_safety": 3, "delivery_pace": 4, "code_quality": 3,
                    "learning": 2, "collaboration": 4, "fun": 3,
                    "mission_clarity": 3, "autonomy": 2, "support": 4, "sustainable_pace": 3,
                },
            },
            {
                "name": "Carol",
                "scores": {
                    "psychological_safety": 5, "delivery_pace": 3, "code_quality": 4,
                    "learning": 4, "collaboration": 4, "fun": 5,
                    "mission_clarity": 5, "autonomy": 4, "support": 3, "sustainable_pace": 2,
                },
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate team health across 10 dimensions with recommendations."
    )
    parser.add_argument("--survey", type=str, help="Path to survey JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example survey JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.survey:
        parser.error("--survey is required (use --example to see the expected format)")

    data = load_survey(args.survey)
    errors = validate_survey(data)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    result = analyze_health(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
