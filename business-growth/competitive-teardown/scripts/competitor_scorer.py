#!/usr/bin/env python3
"""
Competitor Scorer

Score competitors across a 12-dimension rubric and generate a numeric
comparison scorecard with gap analysis and strategic recommendations.

Usage:
    python competitor_scorer.py competitor_data.json
    python competitor_scorer.py competitor_data.json --json
"""

import argparse
import json
import sys


DIMENSIONS = [
    "features", "pricing", "ux_design", "performance", "documentation",
    "support", "integrations", "security", "scalability", "brand",
    "community", "innovation",
]

DIMENSION_LABELS = {
    "features": "Features",
    "pricing": "Pricing",
    "ux_design": "UX / Design",
    "performance": "Performance",
    "documentation": "Documentation",
    "support": "Support",
    "integrations": "Integrations",
    "security": "Security",
    "scalability": "Scalability",
    "brand": "Brand",
    "community": "Community",
    "innovation": "Innovation",
}


def score_competitors(data: dict, custom_weights: dict = None) -> dict:
    """Score competitors across 12 dimensions."""
    competitors = data.get("competitors", [])
    if not competitors:
        return {"error": "No competitor data provided."}

    weights = custom_weights or {d: 1.0 / len(DIMENSIONS) for d in DIMENSIONS}
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}

    scorecards = []
    for comp in competitors:
        name = comp.get("name", "Unknown")
        scores = comp.get("scores", {})
        evidence = comp.get("evidence", {})

        dimension_scores = []
        raw_total = 0
        weighted_total = 0.0

        for dim in DIMENSIONS:
            score = scores.get(dim, 0)
            score = max(0, min(5, score))
            weight = weights.get(dim, 1.0 / len(DIMENSIONS))
            weighted = score * weight * len(DIMENSIONS)

            dimension_scores.append({
                "dimension": dim,
                "label": DIMENSION_LABELS.get(dim, dim),
                "score": score,
                "weight": round(weight, 4),
                "weighted_score": round(weighted, 2),
                "evidence": evidence.get(dim, ""),
            })
            raw_total += score
            weighted_total += weighted

        scorecards.append({
            "name": name,
            "raw_total": raw_total,
            "max_possible": len(DIMENSIONS) * 5,
            "weighted_total": round(weighted_total, 2),
            "percentage": round((raw_total / (len(DIMENSIONS) * 5)) * 100, 1),
            "dimensions": dimension_scores,
        })

    scorecards.sort(key=lambda x: x["weighted_total"], reverse=True)

    # Gap analysis (compare first two)
    gaps = []
    if len(scorecards) >= 2:
        leader = scorecards[0]
        for other in scorecards[1:]:
            comp_gaps = []
            for i, dim in enumerate(DIMENSIONS):
                leader_score = leader["dimensions"][i]["score"]
                other_score = other["dimensions"][i]["score"]
                diff = leader_score - other_score
                if abs(diff) >= 1:
                    comp_gaps.append({
                        "dimension": DIMENSION_LABELS.get(dim, dim),
                        "leader_score": leader_score,
                        "other_score": other_score,
                        "gap": diff,
                        "direction": "leader ahead" if diff > 0 else "other ahead",
                    })
            gaps.append({
                "comparison": f"{leader['name']} vs {other['name']}",
                "gaps": sorted(comp_gaps, key=lambda x: abs(x["gap"]), reverse=True),
            })

    # Strategic recommendations
    recommendations = _generate_recommendations(scorecards)

    return {
        "scorecards": scorecards,
        "ranking": [{"rank": i + 1, "name": s["name"], "score": s["raw_total"],
                      "percentage": s["percentage"]} for i, s in enumerate(scorecards)],
        "gap_analysis": gaps,
        "recommendations": recommendations,
    }


def _generate_recommendations(scorecards: list) -> list:
    """Generate strategic recommendations from scorecard analysis."""
    recs = []
    if not scorecards:
        return recs

    # Find dimensions where your product (first entry typically) scores lowest
    if scorecards:
        first = scorecards[0]
        weak_dims = sorted(first["dimensions"], key=lambda x: x["score"])[:3]
        for dim in weak_dims:
            if dim["score"] <= 2:
                recs.append({
                    "priority": "HIGH",
                    "dimension": dim["label"],
                    "recommendation": f"{first['name']} scores {dim['score']}/5 on {dim['label']}. This is a significant gap that competitors can exploit.",
                })

        strong_dims = sorted(first["dimensions"], key=lambda x: x["score"], reverse=True)[:3]
        for dim in strong_dims:
            if dim["score"] >= 4:
                recs.append({
                    "priority": "LEVERAGE",
                    "dimension": dim["label"],
                    "recommendation": f"{first['name']} leads on {dim['label']} ({dim['score']}/5). Feature this in positioning and battle cards.",
                })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("COMPETITOR SCORECARD -- 12-Dimension Analysis")
    lines.append("=" * 70)

    lines.append(f"\n--- Ranking ---")
    for r in result["ranking"]:
        bar = "#" * int(r["percentage"] / 5)
        lines.append(f"  {r['rank']}. {r['name']:<25} {r['score']:>3}/60  ({r['percentage']:>5.1f}%)  {bar}")

    for sc in result["scorecards"]:
        lines.append(f"\n--- {sc['name']} ---")
        lines.append(f"{'Dimension':<16} {'Score':>6} {'Evidence'}")
        for d in sc["dimensions"]:
            ev = d["evidence"][:50] + "..." if len(d["evidence"]) > 50 else d["evidence"]
            lines.append(f"{d['label']:<16} {d['score']:>4}/5  {ev}")
        lines.append(f"{'TOTAL':<16} {sc['raw_total']:>4}/60 ({sc['percentage']:.1f}%)")

    if result["gap_analysis"]:
        lines.append(f"\n--- Gap Analysis ---")
        for ga in result["gap_analysis"]:
            lines.append(f"\n  {ga['comparison']}:")
            for g in ga["gaps"][:5]:
                lines.append(f"    {g['dimension']:<16} {g['leader_score']} vs {g['other_score']} (gap: {g['gap']:+d})")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['dimension']}: {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score competitors across a 12-dimension rubric and generate comparison scorecard."
    )
    parser.add_argument("input_file", help="JSON file with competitor dimension scores")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--weights", type=str, default=None,
                        help="Custom dimension weights as JSON string")

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

    custom_weights = None
    if args.weights:
        try:
            custom_weights = json.loads(args.weights)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --weights argument.", file=sys.stderr)
            sys.exit(1)

    result = score_competitors(data, custom_weights)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
