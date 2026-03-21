#!/usr/bin/env python3
"""
SWOT Analyzer - Structured SWOT analysis with weighted scoring and cross-impact.

Performs SWOT analysis with impact/confidence weighting, generates cross-impact
strategies (SO/WO/ST/WT), and produces prioritized strategic recommendations.

Usage:
    python swot_analyzer.py --input swot_data.json
    python swot_analyzer.py --input swot_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_items(items):
    """Score SWOT items by impact * confidence and sort by priority."""
    scored = []
    for item in items:
        impact = item.get("impact", 5)
        confidence = item.get("confidence", 5)
        priority_score = round(impact * confidence / 10, 1)
        scored.append({
            "description": item.get("description", ""),
            "impact": impact,
            "confidence": confidence,
            "priority_score": priority_score,
            "category": item.get("category", "general"),
        })
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    return scored


def get_priority_label(score):
    """Convert priority score to label."""
    if score >= 7:
        return "Critical"
    elif score >= 4:
        return "Important"
    else:
        return "Monitor"


def generate_cross_impact(strengths, weaknesses, opportunities, threats):
    """Generate SO/WO/ST/WT strategic combinations."""
    strategies = {"SO": [], "WO": [], "ST": [], "WT": []}

    # SO: Use strengths to capture opportunities
    for s in strengths[:3]:
        for o in opportunities[:3]:
            strategies["SO"].append({
                "strategy": f"Leverage '{s['description']}' to pursue '{o['description']}'",
                "combined_score": round((s["priority_score"] + o["priority_score"]) / 2, 1),
                "type": "offensive",
            })

    # WO: Address weaknesses to capture opportunities
    for w in weaknesses[:3]:
        for o in opportunities[:3]:
            strategies["WO"].append({
                "strategy": f"Fix '{w['description']}' to unlock '{o['description']}'",
                "combined_score": round((w["priority_score"] + o["priority_score"]) / 2, 1),
                "type": "investment",
            })

    # ST: Use strengths to counter threats
    for s in strengths[:3]:
        for t in threats[:3]:
            strategies["ST"].append({
                "strategy": f"Use '{s['description']}' to defend against '{t['description']}'",
                "combined_score": round((s["priority_score"] + t["priority_score"]) / 2, 1),
                "type": "defensive",
            })

    # WT: Mitigate weaknesses exposed by threats
    for w in weaknesses[:3]:
        for t in threats[:3]:
            strategies["WT"].append({
                "strategy": f"Address '{w['description']}' before '{t['description']}' materializes",
                "combined_score": round((w["priority_score"] + t["priority_score"]) / 2, 1),
                "type": "survival",
            })

    # Sort each quadrant by combined score
    for key in strategies:
        strategies[key].sort(key=lambda x: x["combined_score"], reverse=True)
        strategies[key] = strategies[key][:5]  # Top 5 per quadrant

    return strategies


def calculate_overall_position(strengths, weaknesses, opportunities, threats):
    """Calculate overall strategic position score."""
    s_avg = sum(i["priority_score"] for i in strengths) / max(len(strengths), 1)
    w_avg = sum(i["priority_score"] for i in weaknesses) / max(len(weaknesses), 1)
    o_avg = sum(i["priority_score"] for i in opportunities) / max(len(opportunities), 1)
    t_avg = sum(i["priority_score"] for i in threats) / max(len(threats), 1)

    internal_score = round(s_avg - w_avg, 1)
    external_score = round(o_avg - t_avg, 1)
    overall = round((internal_score + external_score) / 2, 1)

    if internal_score > 1 and external_score > 1:
        posture = "Aggressive Growth (SO dominant)"
    elif internal_score > 1 and external_score <= 1:
        posture = "Diversification (ST dominant)"
    elif internal_score <= 1 and external_score > 1:
        posture = "Turnaround (WO dominant)"
    else:
        posture = "Defensive (WT dominant)"

    return {
        "internal_score": internal_score,
        "external_score": external_score,
        "overall_score": overall,
        "recommended_posture": posture,
        "strength_avg": round(s_avg, 1),
        "weakness_avg": round(w_avg, 1),
        "opportunity_avg": round(o_avg, 1),
        "threat_avg": round(t_avg, 1),
    }


def analyze_swot(data):
    """Run full SWOT analysis."""
    entity = data.get("entity", "Company")

    strengths = score_items(data.get("strengths", []))
    weaknesses = score_items(data.get("weaknesses", []))
    opportunities = score_items(data.get("opportunities", []))
    threats = score_items(data.get("threats", []))

    cross_impact = generate_cross_impact(strengths, weaknesses, opportunities, threats)
    position = calculate_overall_position(strengths, weaknesses, opportunities, threats)

    # Top priorities across all quadrants
    all_strategies = []
    for quadrant, strats in cross_impact.items():
        for s in strats:
            s["quadrant"] = quadrant
            all_strategies.append(s)
    all_strategies.sort(key=lambda x: x["combined_score"], reverse=True)

    results = {
        "timestamp": datetime.now().isoformat(),
        "entity": entity,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
        "cross_impact_strategies": cross_impact,
        "strategic_position": position,
        "top_priorities": all_strategies[:10],
        "summary": {
            "total_strengths": len(strengths),
            "total_weaknesses": len(weaknesses),
            "total_opportunities": len(opportunities),
            "total_threats": len(threats),
            "critical_items": sum(
                1 for items in [strengths, weaknesses, opportunities, threats]
                for i in items if i["priority_score"] >= 7
            ),
        },
    }

    return results


def format_text(results):
    """Format results as human-readable text."""
    lines = [
        "=" * 60,
        f"SWOT ANALYSIS: {results['entity']}",
        "=" * 60,
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        "STRATEGIC POSITION",
        f"  Internal Score: {results['strategic_position']['internal_score']} "
        f"(Strengths {results['strategic_position']['strength_avg']} vs "
        f"Weaknesses {results['strategic_position']['weakness_avg']})",
        f"  External Score: {results['strategic_position']['external_score']} "
        f"(Opportunities {results['strategic_position']['opportunity_avg']} vs "
        f"Threats {results['strategic_position']['threat_avg']})",
        f"  Overall: {results['strategic_position']['overall_score']}",
        f"  Recommended Posture: {results['strategic_position']['recommended_posture']}",
        "",
    ]

    for label, items in [
        ("STRENGTHS", results["strengths"]),
        ("WEAKNESSES", results["weaknesses"]),
        ("OPPORTUNITIES", results["opportunities"]),
        ("THREATS", results["threats"]),
    ]:
        lines.append(f"{label} ({len(items)} items)")
        for i in items:
            priority = get_priority_label(i["priority_score"])
            lines.append(
                f"  [{priority}] {i['description']} "
                f"(impact={i['impact']}, confidence={i['confidence']}, "
                f"score={i['priority_score']})"
            )
        lines.append("")

    lines.append("CROSS-IMPACT STRATEGIES")
    for quadrant, label in [
        ("SO", "Strengths x Opportunities (Offensive)"),
        ("WO", "Weaknesses x Opportunities (Investment)"),
        ("ST", "Strengths x Threats (Defensive)"),
        ("WT", "Weaknesses x Threats (Survival)"),
    ]:
        strats = results["cross_impact_strategies"].get(quadrant, [])
        lines.append(f"\n  {label}")
        for s in strats[:3]:
            lines.append(f"    [{s['combined_score']}] {s['strategy']}")

    lines.append("")
    lines.append("TOP 10 STRATEGIC PRIORITIES")
    for idx, p in enumerate(results["top_priorities"], 1):
        lines.append(f"  {idx}. [{p['quadrant']}] {p['strategy']} (score: {p['combined_score']})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="SWOT analysis with weighted scoring and cross-impact strategies"
    )
    parser.add_argument("--input", required=True, help="Path to JSON SWOT data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_swot(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
