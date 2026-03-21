#!/usr/bin/env python3
"""Org Health Scorer - Score 8 dimensions with traffic lights and stage-adjusted weighting.

Calculates overall organizational health from 8 dimension scores with stage-appropriate
weighting. Produces traffic light dashboard, cascade risk analysis, and priorities.

Usage:
    python org_health_scorer.py --stage series-a --financial 7.5 --revenue 5.8 --product 7.2 --engineering 5.0 --people 3.5 --operations 6.0 --security 7.8 --market 5.5
    python org_health_scorer.py --stage seed --financial 6 --revenue 4 --product 8 --engineering 7 --people 6 --operations 5 --security 4 --market 6 --json
"""

import argparse
import json
import sys
from datetime import datetime

DIMENSIONS = {
    "financial": {"name": "Financial Health", "owner": "CFO", "cascade_to": ["people", "engineering", "product"]},
    "revenue": {"name": "Revenue Health", "owner": "CRO", "cascade_to": ["financial", "people", "market"]},
    "product": {"name": "Product Health", "owner": "CPO", "cascade_to": ["revenue", "market", "people"]},
    "engineering": {"name": "Engineering Health", "owner": "CTO", "cascade_to": ["product", "revenue"]},
    "people": {"name": "People Health", "owner": "CHRO", "cascade_to": ["engineering", "product", "revenue"]},
    "operations": {"name": "Operational Health", "owner": "COO", "cascade_to": ["all"]},
    "security": {"name": "Security Health", "owner": "CISO", "cascade_to": ["revenue", "financial"]},
    "market": {"name": "Market Health", "owner": "CMO", "cascade_to": ["revenue", "financial"]}
}

STAGE_WEIGHTS = {
    "seed": {"financial": 0.20, "revenue": 0.10, "product": 0.25, "engineering": 0.15, "people": 0.10, "operations": 0.05, "security": 0.05, "market": 0.10},
    "series-a": {"financial": 0.15, "revenue": 0.20, "product": 0.20, "engineering": 0.15, "people": 0.10, "operations": 0.10, "security": 0.05, "market": 0.05},
    "series-b": {"financial": 0.15, "revenue": 0.20, "product": 0.15, "engineering": 0.15, "people": 0.15, "operations": 0.10, "security": 0.05, "market": 0.05},
    "series-c": {"financial": 0.15, "revenue": 0.20, "product": 0.10, "engineering": 0.10, "people": 0.15, "operations": 0.15, "security": 0.10, "market": 0.05},
    "growth": {"financial": 0.15, "revenue": 0.20, "product": 0.10, "engineering": 0.10, "people": 0.15, "operations": 0.15, "security": 0.10, "market": 0.05}
}


def get_traffic_light(score):
    if score >= 7:
        return "GREEN"
    elif score >= 4:
        return "YELLOW"
    return "RED"


def score_health(stage, scores):
    weights = STAGE_WEIGHTS.get(stage, STAGE_WEIGHTS["series-a"])

    dimension_results = []
    weighted_total = 0.0

    for dim_key, dim_info in DIMENSIONS.items():
        score = scores.get(dim_key, 5.0)
        weight = weights.get(dim_key, 0.1)
        weighted_score = score * weight
        weighted_total += weighted_score
        traffic = get_traffic_light(score)

        dimension_results.append({
            "dimension": dim_info["name"],
            "key": dim_key,
            "owner": dim_info["owner"],
            "score": score,
            "weight": weight,
            "weighted_score": round(weighted_score, 2),
            "traffic_light": traffic
        })

    overall = round(weighted_total, 1)
    overall_traffic = get_traffic_light(overall)

    # Cascade analysis
    red_dimensions = [d for d in dimension_results if d["traffic_light"] == "RED"]
    yellow_dimensions = [d for d in dimension_results if d["traffic_light"] == "YELLOW"]

    cascade_warnings = []
    for red in red_dimensions:
        cascades = DIMENSIONS[red["key"]]["cascade_to"]
        at_risk = []
        for cascade_key in cascades:
            if cascade_key == "all":
                at_risk = [d["dimension"] for d in dimension_results if d["key"] != red["key"]]
                break
            matching = [d for d in dimension_results if d["key"] == cascade_key and d["traffic_light"] in ("YELLOW", "RED")]
            at_risk.extend([m["dimension"] for m in matching])
        if at_risk:
            cascade_warnings.append({
                "source": red["dimension"],
                "source_score": red["score"],
                "at_risk_dimensions": at_risk,
                "type": "SYSTEMIC" if len(at_risk) >= 2 else "ISOLATED",
                "recommendation": f"Address {red['dimension']} ({red['owner']}) first -- cascading to {', '.join(at_risk)}"
            })

    # Priorities
    priorities = sorted(dimension_results, key=lambda d: d["score"])
    top_priorities = []
    for p in priorities[:3]:
        if p["traffic_light"] in ("RED", "YELLOW"):
            top_priorities.append({
                "dimension": p["dimension"],
                "score": p["score"],
                "traffic_light": p["traffic_light"],
                "owner": p["owner"],
                "urgency": "Immediate (30 days)" if p["traffic_light"] == "RED" else "This quarter"
            })

    # Data gaps (dimensions at exactly 5.0 might be defaults)
    data_gaps = [d["dimension"] for d in dimension_results if d["score"] == 5.0]

    return {
        "diagnostic_date": datetime.now().strftime("%Y-%m-%d"),
        "company_stage": stage,
        "overall_score": overall,
        "overall_traffic_light": overall_traffic,
        "trend": "Requires baseline for trend analysis",
        "dimensions": dimension_results,
        "cascade_warnings": cascade_warnings,
        "top_priorities": top_priorities,
        "data_gaps": data_gaps,
        "red_count": len(red_dimensions),
        "yellow_count": len(yellow_dimensions),
        "green_count": len([d for d in dimension_results if d["traffic_light"] == "GREEN"])
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"ORG HEALTH DIAGNOSTIC -- {result['diagnostic_date']}")
    print(f"Stage: {result['company_stage']}   Overall: {result['overall_score']}/10   [{result['overall_traffic_light']}]")
    print(f"{'='*70}\n")

    print("DIMENSION SCORES")
    print("-" * 60)
    for d in sorted(result["dimensions"], key=lambda x: -x["score"]):
        light = {"GREEN": "G", "YELLOW": "Y", "RED": "R"}[d["traffic_light"]]
        bar = "#" * int(d["score"]) + "." * (10 - int(d["score"]))
        print(f"  [{light}] {d['dimension']:<25s} {d['score']:>4.1f}  {bar}  ({d['owner']}, weight: {d['weight']})")

    print(f"\n  Summary: {result['green_count']} Green, {result['yellow_count']} Yellow, {result['red_count']} Red")

    if result["top_priorities"]:
        print(f"\nTOP PRIORITIES (address in order)")
        print("-" * 60)
        for i, p in enumerate(result["top_priorities"], 1):
            print(f"  [{p['traffic_light'][0]}] {i}. {p['dimension']}: {p['score']}/10")
            print(f"       Owner: {p['owner']}  |  Timeline: {p['urgency']}")

    if result["cascade_warnings"]:
        print(f"\nCASCADE WARNINGS")
        print("-" * 60)
        for cw in result["cascade_warnings"]:
            print(f"  [{cw['type']}] {cw['source']} ({cw['source_score']}/10) -> {', '.join(cw['at_risk_dimensions'])}")
            print(f"    {cw['recommendation']}")

    if result["data_gaps"]:
        print(f"\nDATA GAPS (scores at default 5.0 -- may need verification)")
        for dg in result["data_gaps"]:
            print(f"  [?] {dg}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Score organizational health across 8 dimensions")
    parser.add_argument("--stage", required=True, choices=list(STAGE_WEIGHTS.keys()))
    parser.add_argument("--financial", type=float, required=True, help="Financial health (1-10)")
    parser.add_argument("--revenue", type=float, required=True, help="Revenue health (1-10)")
    parser.add_argument("--product", type=float, required=True, help="Product health (1-10)")
    parser.add_argument("--engineering", type=float, required=True, help="Engineering health (1-10)")
    parser.add_argument("--people", type=float, required=True, help="People health (1-10)")
    parser.add_argument("--operations", type=float, required=True, help="Operational health (1-10)")
    parser.add_argument("--security", type=float, required=True, help="Security health (1-10)")
    parser.add_argument("--market", type=float, required=True, help="Market health (1-10)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    scores = {
        "financial": args.financial, "revenue": args.revenue, "product": args.product,
        "engineering": args.engineering, "people": args.people, "operations": args.operations,
        "security": args.security, "market": args.market
    }

    for key, val in scores.items():
        if val < 1 or val > 10:
            print(f"Error: {key} must be between 1 and 10", file=sys.stderr)
            sys.exit(1)

    result = score_health(args.stage, scores)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
