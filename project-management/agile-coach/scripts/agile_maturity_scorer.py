#!/usr/bin/env python3
"""Agile Maturity Scorer - Score organizational agile maturity across 6 dimensions.

Reads an assessment file and produces a scored report with level classification,
gap analysis, and prioritized improvement recommendations aligned with the
Kanban Maturity Model and standard agile maturity frameworks.

Usage:
    python agile_maturity_scorer.py --assessment assessment.json
    python agile_maturity_scorer.py --assessment assessment.json --json
    python agile_maturity_scorer.py --example
"""

import argparse
import json
import sys


DIMENSIONS = [
    "values_and_mindset",
    "team_practices",
    "technical_excellence",
    "product_ownership",
    "leadership_support",
    "continuous_improvement",
]

DIMENSION_LABELS = {
    "values_and_mindset": "Values & Mindset",
    "team_practices": "Team Practices",
    "technical_excellence": "Technical Excellence",
    "product_ownership": "Product Ownership",
    "leadership_support": "Leadership Support",
    "continuous_improvement": "Continuous Improvement",
}

LEVEL_NAMES = {
    1: "Initial",
    2: "Repeatable",
    3: "Defined",
    4: "Managed",
    5: "Optimizing",
}

LEVEL_DESCRIPTIONS = {
    1: "Ad-hoc processes, hero-dependent delivery, limited visibility into work.",
    2: "Basic Scrum/Kanban in place, team-level practices established, some metrics tracked.",
    3: "Consistent practices across teams, cross-team coordination, CI/CD culture emerging.",
    4: "Quantitative management, predictable outcomes, business-aligned delivery.",
    5: "Innovation culture, market responsiveness, organizational learning embedded.",
}

IMPROVEMENT_ACTIONS = {
    "values_and_mindset": {
        1: "Start with agile values workshops; share success stories from other organizations.",
        2: "Run agile mindset training for all team members; introduce team working agreements.",
        3: "Embed agile values in performance reviews; create communities of practice for knowledge sharing.",
        4: "Develop internal agile champions program; align agile values with company mission.",
        5: "Foster innovation culture; enable teams to experiment and learn from failure safely.",
    },
    "team_practices": {
        1: "Establish basic Scrum ceremonies (standup, planning, review, retro) with coaching support.",
        2: "Standardize ceremony formats; introduce Definition of Done; start tracking velocity.",
        3: "Cross-team ceremony alignment; introduce Scrum-of-Scrums; standardize estimation practices.",
        4: "Optimize ceremonies based on metrics; reduce ceremony overhead; self-facilitating teams.",
        5: "Teams autonomously adapt practices; ceremonies evolved to fit context; practices shared across org.",
    },
    "technical_excellence": {
        1: "Set up basic CI pipeline; introduce code reviews; establish coding standards.",
        2: "Automate unit testing; introduce TDD practices; set up staging environments.",
        3: "Full CI/CD pipeline; automated integration testing; feature flags; infrastructure as code.",
        4: "Canary deployments; chaos engineering; comprehensive observability; zero-downtime deploys.",
        5: "Self-healing systems; automated security scanning; continuous architecture evolution.",
    },
    "product_ownership": {
        1: "Identify a dedicated Product Owner; create a basic product backlog.",
        2: "Regular backlog refinement; connect stories to user outcomes; stakeholder feedback loops.",
        3: "Outcome-driven roadmapping; product discovery practices; hypothesis-driven development.",
        4: "Continuous discovery; data-driven prioritization; customer-centric OKRs at every level.",
        5: "Market-responsive product strategy; real-time customer feedback integration; portfolio-level alignment.",
    },
    "leadership_support": {
        1: "Secure executive sponsor for agile transformation; educate leadership on agile principles.",
        2: "Leadership participates in PI planning or sprint reviews; resources allocated for coaching.",
        3: "Leadership models agile behaviors; impediment removal happens within 48 hours.",
        4: "Servant leadership embedded; leaders create environment for teams to self-organize.",
        5: "Decentralized decision-making; leaders focus on strategy and vision; teams fully empowered.",
    },
    "continuous_improvement": {
        1: "Run basic retrospectives; start capturing action items.",
        2: "Retro action items tracked and completed; improvement experiments initiated.",
        3: "Metrics-driven improvement; improvement items in sprint backlog; cross-team learning.",
        4: "Systematic experimentation; improvement velocity tracked; lean thinking pervasive.",
        5: "Kaizen culture; improvement is everyone's job; organization learns faster than competitors.",
    },
}


def load_assessment(path: str) -> dict:
    """Load assessment data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def validate_assessment(data: dict) -> list:
    """Validate assessment structure."""
    errors = []
    if "organization" not in data:
        errors.append("Missing 'organization' field")
    if "dimensions" not in data or not isinstance(data.get("dimensions"), dict):
        errors.append("Missing or invalid 'dimensions' object")
        return errors
    for dim in DIMENSIONS:
        score = data["dimensions"].get(dim)
        if score is None:
            errors.append(f"Missing dimension: '{dim}'")
        elif not isinstance(score, (int, float)) or score < 1 or score > 5:
            errors.append(f"'{dim}' must be 1-5, got {score}")
    return errors


def score_maturity(data: dict) -> dict:
    """Calculate maturity scores and generate recommendations."""
    org = data.get("organization", "Unknown")
    dims = data["dimensions"]
    teams_assessed = data.get("teams_assessed", "N/A")

    # Calculate overall score
    scores = [dims[d] for d in DIMENSIONS]
    overall = round(sum(scores) / len(scores), 2)
    level = max(1, min(5, round(overall)))

    # Dimension detail
    dim_detail = {}
    for dim in DIMENSIONS:
        s = dims[dim]
        dim_level = max(1, min(5, round(s)))
        dim_detail[dim] = {
            "label": DIMENSION_LABELS[dim],
            "score": s,
            "level": dim_level,
            "level_name": LEVEL_NAMES[dim_level],
        }

    # Gap analysis: identify dimensions furthest from target
    target_level = min(level + 1, 5)
    gaps = []
    for dim in DIMENSIONS:
        gap = target_level - dims[dim]
        if gap > 0:
            gaps.append({
                "dimension": DIMENSION_LABELS[dim],
                "current_score": dims[dim],
                "target": target_level,
                "gap": round(gap, 1),
                "priority": "High" if gap >= 2 else "Medium" if gap >= 1 else "Low",
            })
    gaps.sort(key=lambda x: x["gap"], reverse=True)

    # Improvement recommendations
    recommendations = []
    for dim in DIMENSIONS:
        current_level = max(1, min(5, round(dims[dim])))
        if current_level < 5:
            action = IMPROVEMENT_ACTIONS[dim].get(current_level, "Continue optimizing practices.")
            recommendations.append({
                "dimension": DIMENSION_LABELS[dim],
                "current_level": current_level,
                "action": action,
            })

    # Framework recommendation
    if overall < 2:
        framework_rec = "Start with Kanban (minimal process overhead); focus on making work visible before adding ceremonies."
    elif overall < 3:
        framework_rec = "Scrum is recommended for product teams; Kanban for operations. Do not attempt scaling frameworks yet."
    elif overall < 4:
        framework_rec = "Teams are ready for lightweight scaling (LeSS, Nexus). Consider SAFe Essential only if >8 teams need coordination."
    else:
        framework_rec = "Organization is mature enough for portfolio-level agility (SAFe Portfolio, Enterprise Kanban, or custom hybrid)."

    return {
        "organization": org,
        "teams_assessed": teams_assessed,
        "overall_score": overall,
        "overall_level": level,
        "overall_level_name": LEVEL_NAMES[level],
        "level_description": LEVEL_DESCRIPTIONS[level],
        "dimensions": dim_detail,
        "target_level": target_level,
        "gap_analysis": gaps,
        "recommendations": recommendations,
        "framework_recommendation": framework_rec,
    }


def print_report(result: dict) -> None:
    """Print human-readable maturity report."""
    print(f"\nAgile Maturity Assessment: {result['organization']}")
    print(f"Teams Assessed: {result['teams_assessed']}")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']:.1f} / 5.0 (Level {result['overall_level']}: {result['overall_level_name']})")
    print(f"  {result['level_description']}")
    print()

    print("Dimension Scores:")
    for dim in DIMENSIONS:
        info = result["dimensions"][dim]
        bar = "#" * (info["score"] * 4) + "-" * (20 - info["score"] * 4)
        print(f"  {info['label']:<25} {info['score']}/5  [{bar}]  Level {info['level']}: {info['level_name']}")

    if result["gap_analysis"]:
        print(f"\nGap Analysis (target: Level {result['target_level']}):")
        for g in result["gap_analysis"]:
            print(f"  [{g['priority']}] {g['dimension']}: {g['current_score']:.0f} -> {g['target']} (gap: {g['gap']:.1f})")

    print(f"\nFramework Recommendation:")
    print(f"  {result['framework_recommendation']}")

    print(f"\nImprovement Actions:")
    for r in result["recommendations"][:3]:
        print(f"  [{r['dimension']}]")
        print(f"    {r['action']}")

    print()


def print_example() -> None:
    """Print example assessment JSON."""
    example = {
        "organization": "Acme Corp",
        "teams_assessed": 5,
        "dimensions": {
            "values_and_mindset": 2,
            "team_practices": 3,
            "technical_excellence": 2,
            "product_ownership": 2,
            "leadership_support": 3,
            "continuous_improvement": 2,
        },
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Score organizational agile maturity across 6 dimensions."
    )
    parser.add_argument("--assessment", type=str, help="Path to assessment JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example assessment JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.assessment:
        parser.error("--assessment is required (use --example to see the expected format)")

    data = load_assessment(args.assessment)
    errors = validate_assessment(data)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    result = score_maturity(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
