#!/usr/bin/env python3
"""
Market Landscape Mapper - Map competitive landscape across configurable dimensions.

Classifies competitors by tier, calculates positioning scores, identifies
whitespace opportunities, and generates landscape summary reports.

Usage:
    python market_landscape_mapper.py --input competitors.json
    python market_landscape_mapper.py --input competitors.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    """Load competitor data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def classify_tier(competitor):
    """Classify competitor into Tier 1/2/3 based on ICP overlap and threat level."""
    icp_overlap = competitor.get("icp_overlap", "low").lower()
    same_problem = competitor.get("same_problem", False)

    if icp_overlap == "high" and same_problem:
        return 1
    elif icp_overlap in ("high", "medium") or same_problem:
        return 2
    else:
        return 3


def calculate_dimension_scores(competitor, dimensions):
    """Calculate average score across tracked dimensions."""
    scores = competitor.get("scores", {})
    total = 0
    count = 0
    dimension_results = {}
    for dim in dimensions:
        val = scores.get(dim)
        if val is not None:
            dimension_results[dim] = val
            total += val
            count += 1
    avg = round(total / count, 1) if count > 0 else 0
    return dimension_results, avg


def find_whitespace(competitors, dimensions):
    """Identify dimensions where no competitor scores above 7/10."""
    whitespace = []
    for dim in dimensions:
        max_score = 0
        for c in competitors:
            score = c.get("scores", {}).get(dim, 0)
            if score > max_score:
                max_score = score
        if max_score < 7:
            whitespace.append({"dimension": dim, "max_competitor_score": max_score})
    return whitespace


def calculate_threat_score(competitor):
    """Calculate overall threat score based on tier, funding, growth, and market share."""
    tier = competitor.get("tier", 3)
    funding = min(competitor.get("funding_millions", 0) / 100, 1.0)
    growth = min(competitor.get("growth_rate_pct", 0) / 100, 1.0)
    market_share = min(competitor.get("market_share_pct", 0) / 50, 1.0)

    tier_weight = {1: 1.0, 2: 0.6, 3: 0.3}.get(tier, 0.3)
    score = (tier_weight * 0.3 + funding * 0.2 + growth * 0.3 + market_share * 0.2) * 100
    return round(min(score, 100), 1)


def get_threat_level(score):
    """Convert threat score to label."""
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


def analyze_landscape(data):
    """Run full landscape analysis."""
    competitors = data.get("competitors", [])
    dimensions = data.get("dimensions", [
        "product", "pricing", "market_share", "brand", "technology",
        "customer_success", "integrations", "geographic_reach"
    ])
    company_name = data.get("company_name", "Your Company")
    company_scores = data.get("company_scores", {})

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company_name,
        "dimensions_tracked": dimensions,
        "competitor_count": len(competitors),
        "competitors": [],
        "tier_summary": {1: 0, 2: 0, 3: 0},
        "whitespace_opportunities": [],
        "top_threats": [],
        "positioning_gaps": [],
    }

    for comp in competitors:
        tier = classify_tier(comp)
        comp["tier"] = tier
        results["tier_summary"][tier] += 1

        dim_scores, avg_score = calculate_dimension_scores(comp, dimensions)
        threat_score = calculate_threat_score(comp)

        entry = {
            "name": comp.get("name", "Unknown"),
            "tier": tier,
            "dimension_scores": dim_scores,
            "average_score": avg_score,
            "threat_score": threat_score,
            "threat_level": get_threat_level(threat_score),
            "icp_overlap": comp.get("icp_overlap", "unknown"),
            "funding_millions": comp.get("funding_millions", 0),
            "headcount": comp.get("headcount", 0),
        }
        results["competitors"].append(entry)

    # Sort by threat score
    results["competitors"].sort(key=lambda x: x["threat_score"], reverse=True)
    results["top_threats"] = [
        {"name": c["name"], "threat_score": c["threat_score"], "tier": c["tier"]}
        for c in results["competitors"][:5]
    ]

    # Find whitespace
    results["whitespace_opportunities"] = find_whitespace(competitors, dimensions)

    # Positioning gaps (dimensions where company scores below average competitor)
    for dim in dimensions:
        company_val = company_scores.get(dim, 0)
        comp_vals = [c.get("scores", {}).get(dim, 0) for c in competitors if c.get("scores", {}).get(dim)]
        if comp_vals:
            avg_comp = sum(comp_vals) / len(comp_vals)
            if company_val < avg_comp:
                results["positioning_gaps"].append({
                    "dimension": dim,
                    "company_score": company_val,
                    "avg_competitor_score": round(avg_comp, 1),
                    "gap": round(avg_comp - company_val, 1),
                })

    results["positioning_gaps"].sort(key=lambda x: x["gap"], reverse=True)

    return results


def format_text(results):
    """Format results as human-readable text."""
    lines = [
        "=" * 60,
        "COMPETITIVE LANDSCAPE MAP",
        "=" * 60,
        f"Company: {results['company']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        f"Competitors Tracked: {results['competitor_count']}",
        f"Dimensions: {', '.join(results['dimensions_tracked'])}",
        "",
        "TIER DISTRIBUTION",
        f"  Tier 1 (Direct Threats):   {results['tier_summary'][1]}",
        f"  Tier 2 (Adjacent Watch):   {results['tier_summary'][2]}",
        f"  Tier 3 (Monitor Only):     {results['tier_summary'][3]}",
        "",
        "TOP THREATS",
    ]

    for t in results["top_threats"]:
        lines.append(f"  {t['name']}: Threat Score {t['threat_score']}/100 (Tier {t['tier']})")

    lines.append("")
    lines.append("COMPETITOR DETAIL")
    for c in results["competitors"]:
        lines.append(f"\n  {c['name']} (Tier {c['tier']})")
        lines.append(f"    Threat: {c['threat_level']} ({c['threat_score']}/100)")
        lines.append(f"    ICP Overlap: {c['icp_overlap']}")
        lines.append(f"    Avg Score: {c['average_score']}/10")
        if c["dimension_scores"]:
            for dim, score in c["dimension_scores"].items():
                lines.append(f"      {dim}: {score}/10")

    if results["whitespace_opportunities"]:
        lines.append("")
        lines.append("WHITESPACE OPPORTUNITIES (no competitor scores > 7/10)")
        for w in results["whitespace_opportunities"]:
            lines.append(f"  {w['dimension']}: max competitor score = {w['max_competitor_score']}/10")

    if results["positioning_gaps"]:
        lines.append("")
        lines.append("POSITIONING GAPS (your score < competitor average)")
        for g in results["positioning_gaps"]:
            lines.append(
                f"  {g['dimension']}: You={g['company_score']}, "
                f"Competitors avg={g['avg_competitor_score']}, Gap={g['gap']}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Map competitive landscape across configurable dimensions"
    )
    parser.add_argument("--input", required=True, help="Path to JSON file with competitor data")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_landscape(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
