#!/usr/bin/env python3
"""Competitive Landscape Mapper - Map and analyze competitive positioning.

Analyzes competitors across positioning, messaging, features, and pricing
to identify gaps and opportunities.

Usage:
    python competitive_landscape_mapper.py competitors.json
    python competitive_landscape_mapper.py competitors.json --json
    python competitive_landscape_mapper.py --demo
"""

import argparse
import json
import sys


def analyze_landscape(data):
    """Analyze competitive landscape from competitor data."""
    our_product = data.get("our_product", {})
    competitors = data.get("competitors", [])
    all_players = [our_product] + competitors if our_product else competitors

    # Feature comparison
    all_features = set()
    for player in all_players:
        all_features.update(player.get("features", []))

    feature_matrix = {}
    for feature in sorted(all_features):
        feature_matrix[feature] = {}
        for player in all_players:
            name = player.get("name", "Unknown")
            feature_matrix[feature][name] = feature in player.get("features", [])

    # Unique features per player
    unique_features = {}
    for player in all_players:
        name = player.get("name", "Unknown")
        player_features = set(player.get("features", []))
        other_features = set()
        for other in all_players:
            if other.get("name") != name:
                other_features.update(other.get("features", []))
        unique = player_features - other_features
        unique_features[name] = list(unique)

    # Feature coverage
    our_features = set(our_product.get("features", [])) if our_product else set()
    feature_gaps = []
    for comp in competitors:
        comp_features = set(comp.get("features", []))
        gaps = comp_features - our_features
        if gaps:
            feature_gaps.append({
                "competitor": comp.get("name", "Unknown"),
                "features_they_have": list(gaps),
                "count": len(gaps),
            })

    # Pricing analysis
    pricing = []
    for player in all_players:
        price = player.get("starting_price")
        if price is not None:
            pricing.append({
                "name": player.get("name", "Unknown"),
                "starting_price": price,
                "pricing_model": player.get("pricing_model", "unknown"),
            })
    pricing.sort(key=lambda x: x["starting_price"])

    # Positioning analysis
    positioning = []
    all_categories = set()
    all_audiences = set()
    for player in all_players:
        cat = player.get("category", "unknown")
        audience = player.get("target_audience", "unknown")
        all_categories.add(cat)
        all_audiences.add(audience)
        positioning.append({
            "name": player.get("name", "Unknown"),
            "category": cat,
            "target_audience": audience,
            "key_differentiator": player.get("key_differentiator", ""),
            "tagline": player.get("tagline", ""),
        })

    # Competitive tiers
    tiers = {"direct": [], "adjacent": [], "status_quo": []}
    for comp in competitors:
        tier = comp.get("tier", "direct")
        tiers[tier].append(comp.get("name", "Unknown"))

    # SWOT per competitor
    competitor_analysis = []
    for comp in competitors:
        strengths = comp.get("strengths", [])
        weaknesses = comp.get("weaknesses", [])
        competitor_analysis.append({
            "name": comp.get("name", "Unknown"),
            "tier": comp.get("tier", "direct"),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feature_count": len(comp.get("features", [])),
            "unique_features": unique_features.get(comp.get("name"), []),
        })

    # Opportunity gaps
    opportunities = []
    if len(all_categories) > 1:
        opportunities.append("Category positioning is fragmented - opportunity to own a specific category.")
    if feature_gaps:
        top_gaps = sorted(feature_gaps, key=lambda x: x["count"], reverse=True)
        for gap in top_gaps[:3]:
            opportunities.append(f"{gap['competitor']} has {gap['count']} features we lack: {', '.join(gap['features_they_have'][:3])}")
    our_unique = unique_features.get(our_product.get("name", ""), [])
    if our_unique:
        opportunities.append(f"We uniquely offer: {', '.join(our_unique[:5])}. Emphasize in positioning.")

    return {
        "summary": {
            "total_competitors": len(competitors),
            "total_features_in_market": len(all_features),
            "our_feature_count": len(our_features),
            "categories_in_market": list(all_categories),
            "audiences_targeted": list(all_audiences),
        },
        "tiers": tiers,
        "positioning": positioning,
        "pricing": pricing,
        "feature_gaps": sorted(feature_gaps, key=lambda x: x["count"], reverse=True),
        "unique_features": unique_features,
        "competitor_analysis": competitor_analysis,
        "opportunities": opportunities,
    }


def get_demo_data():
    return {
        "our_product": {
            "name": "OurProduct",
            "category": "analytics platform",
            "target_audience": "product managers",
            "features": ["funnel analysis", "cohort analysis", "real-time dashboard", "custom events", "api access", "slack integration"],
            "starting_price": 99,
            "pricing_model": "per_seat",
            "key_differentiator": "No-code analytics for PMs",
            "tagline": "Analytics without engineering",
        },
        "competitors": [
            {"name": "Amplitude", "tier": "direct", "category": "product analytics", "target_audience": "product teams", "features": ["funnel analysis", "cohort analysis", "behavioral analytics", "experimentation", "cdp"], "starting_price": 0, "pricing_model": "usage", "strengths": ["market leader", "deep analytics"], "weaknesses": ["complex setup", "expensive at scale"]},
            {"name": "Mixpanel", "tier": "direct", "category": "product analytics", "target_audience": "product teams", "features": ["funnel analysis", "cohort analysis", "a/b testing", "messaging"], "starting_price": 0, "pricing_model": "usage", "strengths": ["easy to use", "good free tier"], "weaknesses": ["limited enterprise features", "data governance"]},
            {"name": "Spreadsheets", "tier": "status_quo", "category": "manual analysis", "target_audience": "everyone", "features": ["custom formulas", "charts"], "starting_price": 0, "pricing_model": "free", "strengths": ["familiar", "flexible"], "weaknesses": ["manual", "error-prone", "not real-time"]},
        ],
    }


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("COMPETITIVE LANDSCAPE MAP")
    lines.append("=" * 65)

    s = analysis["summary"]
    lines.append(f"Competitors:        {s['total_competitors']}")
    lines.append(f"Features in market: {s['total_features_in_market']}")
    lines.append(f"Our features:       {s['our_feature_count']}")
    lines.append("")

    # Tiers
    lines.append("--- COMPETITIVE TIERS ---")
    for tier, names in analysis["tiers"].items():
        if names:
            lines.append(f"  {tier.title()}: {', '.join(names)}")
    lines.append("")

    # Positioning
    lines.append("--- POSITIONING ---")
    for p in analysis["positioning"]:
        lines.append(f"  {p['name']}: {p['category']} for {p['target_audience']}")
        if p.get("key_differentiator"):
            lines.append(f"    Differentiator: {p['key_differentiator']}")
    lines.append("")

    # Pricing
    if analysis["pricing"]:
        lines.append("--- PRICING ---")
        for p in analysis["pricing"]:
            lines.append(f"  {p['name']}: ${p['starting_price']}/mo ({p['pricing_model']})")
        lines.append("")

    # Feature gaps
    if analysis["feature_gaps"]:
        lines.append("--- FEATURE GAPS ---")
        for gap in analysis["feature_gaps"][:5]:
            lines.append(f"  {gap['competitor']} has: {', '.join(gap['features_they_have'][:5])}")
        lines.append("")

    # Opportunities
    if analysis["opportunities"]:
        lines.append("--- OPPORTUNITIES ---")
        for opp in analysis["opportunities"]:
            lines.append(f"  * {opp}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Map and analyze competitive positioning")
    parser.add_argument("input", nargs="?", help="JSON file with competitive data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_landscape(data)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
