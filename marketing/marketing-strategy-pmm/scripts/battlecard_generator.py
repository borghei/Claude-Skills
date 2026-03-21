#!/usr/bin/env python3
"""Battlecard Generator - Generate competitive battlecard documents from data.

Creates structured sales battlecards from competitor data including
positioning, strengths/weaknesses, talk tracks, and objection handling.

Usage:
    python battlecard_generator.py competitor.json
    python battlecard_generator.py competitor.json --json
    python battlecard_generator.py --demo
"""

import argparse
import json
import sys
from datetime import datetime


def generate_battlecard(competitor_data, our_product=None):
    """Generate a structured battlecard from competitor data."""
    name = competitor_data.get("name", "Competitor")
    our_name = our_product.get("name", "Our Product") if our_product else "Our Product"

    battlecard = {
        "competitor": name,
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "overview": {
            "name": name,
            "founded": competitor_data.get("founded", "Unknown"),
            "funding": competitor_data.get("funding", "Unknown"),
            "size": competitor_data.get("employees", "Unknown"),
            "headquarters": competitor_data.get("headquarters", "Unknown"),
            "website": competitor_data.get("website", ""),
        },
        "positioning": {
            "their_claim": competitor_data.get("tagline", ""),
            "their_category": competitor_data.get("category", ""),
            "their_target": competitor_data.get("target_audience", ""),
            "reality": competitor_data.get("positioning_reality", ""),
        },
        "strengths": competitor_data.get("strengths", []),
        "weaknesses": competitor_data.get("weaknesses", []),
        "our_advantages": [],
        "feature_comparison": [],
        "when_we_win": competitor_data.get("when_we_win", []),
        "when_we_lose": competitor_data.get("when_we_lose", []),
        "pricing": {
            "their_pricing": competitor_data.get("pricing", "Unknown"),
            "our_pricing": our_product.get("pricing", "Unknown") if our_product else "Unknown",
            "price_positioning": "",
        },
        "objection_handling": [],
        "discovery_questions": [],
        "landmines": [],
    }

    # Build feature comparison
    our_features = set(our_product.get("features", [])) if our_product else set()
    their_features = set(competitor_data.get("features", []))

    all_features = sorted(our_features | their_features)
    for feature in all_features:
        battlecard["feature_comparison"].append({
            "feature": feature,
            "we_have": feature in our_features,
            "they_have": feature in their_features,
        })

    # Our advantages
    our_unique = our_features - their_features
    for feature in our_unique:
        battlecard["our_advantages"].append({
            "advantage": feature,
            "evidence": f"We offer {feature} which {name} does not",
        })

    # Generate objection handling
    objections = competitor_data.get("common_objections", [])
    for obj in objections:
        battlecard["objection_handling"].append({
            "objection": obj.get("objection", ""),
            "response": obj.get("response", ""),
            "proof_point": obj.get("proof_point", ""),
        })

    # Discovery questions (to position against this competitor)
    battlecard["discovery_questions"] = competitor_data.get("discovery_questions", [
        f"Have you evaluated {name}? What did you think of their approach?",
        "What is most important to you: [our strength] or [their strength]?",
        "How important is [our unique feature] to your evaluation?",
        "What concerns you about switching from your current solution?",
    ])

    # Landmines (things to plant that hurt competitor)
    for weakness in competitor_data.get("weaknesses", []):
        battlecard["landmines"].append(
            f"Ask about their experience with {weakness.lower()} - this is where {name} struggles."
        )

    # Price positioning
    their_price = competitor_data.get("starting_price")
    our_price = our_product.get("starting_price") if our_product else None
    if their_price and our_price:
        if our_price < their_price:
            battlecard["pricing"]["price_positioning"] = f"We are more affordable (${our_price} vs ${their_price})"
        elif our_price > their_price:
            battlecard["pricing"]["price_positioning"] = f"We cost more but deliver [{our_product.get('value_justification', 'better ROI')}]"
        else:
            battlecard["pricing"]["price_positioning"] = "Price parity - compete on value and fit"

    return battlecard


def get_demo_data():
    return {
        "competitor": {
            "name": "CompetitorX",
            "founded": "2019",
            "funding": "Series C ($85M)",
            "employees": "450",
            "headquarters": "San Francisco, CA",
            "website": "https://competitorx.com",
            "tagline": "The all-in-one analytics platform",
            "category": "product analytics",
            "target_audience": "enterprise product teams",
            "positioning_reality": "Strong for large enterprises but complex setup and high cost",
            "strengths": ["Enterprise features", "Deep integrations", "Strong brand", "Large customer base"],
            "weaknesses": ["Complex onboarding", "Expensive", "Slow support", "Requires engineering resources"],
            "features": ["funnel analysis", "cohort analysis", "a/b testing", "enterprise sso", "data warehouse sync"],
            "starting_price": 499,
            "pricing": "$499/mo starter, custom enterprise",
            "when_we_win": ["Customer values ease of use", "SMB or mid-market deal", "No dedicated analytics engineer"],
            "when_we_lose": ["Large enterprise with analytics team", "Need deep data warehouse integration", "Existing CompetitorX customer"],
            "common_objections": [
                {"objection": "CompetitorX has more features", "response": "They do have more features, but our customers get value 5x faster because they can self-serve without engineering.", "proof_point": "90-second median time-to-first-insight"},
                {"objection": "CompetitorX is the market leader", "response": "They are established, but our approach is purpose-built for teams without dedicated analytics engineers.", "proof_point": "4.8/5 satisfaction from non-technical PMs"},
            ],
        },
        "our_product": {
            "name": "FlowMetrics",
            "features": ["funnel analysis", "cohort analysis", "real-time dashboard", "no-code queries", "slack alerts"],
            "starting_price": 99,
            "pricing": "$99/mo starter, $299/mo pro",
            "value_justification": "faster time-to-value and lower total cost",
        },
    }


def format_battlecard(card):
    """Format human-readable battlecard."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"COMPETITIVE BATTLECARD: {card['competitor']}")
    lines.append(f"Generated: {card['generated_date']}")
    lines.append("=" * 65)

    o = card["overview"]
    lines.append(f"\nCompany: {o['name']} | Founded: {o['founded']} | Funding: {o['funding']} | Size: {o['size']}")

    p = card["positioning"]
    lines.append(f"\n--- POSITIONING ---")
    lines.append(f"  They say: \"{p['their_claim']}\"")
    lines.append(f"  Reality:  {p['reality']}")

    lines.append(f"\n--- STRENGTHS ---")
    for s in card["strengths"]:
        lines.append(f"  + {s}")

    lines.append(f"\n--- WEAKNESSES ---")
    for w in card["weaknesses"]:
        lines.append(f"  - {w}")

    lines.append(f"\n--- OUR ADVANTAGES ---")
    for a in card["our_advantages"]:
        lines.append(f"  > {a['advantage']}: {a['evidence']}")

    lines.append(f"\n--- FEATURE COMPARISON ---")
    lines.append(f"  {'Feature':<30} {'Us':>4} {'Them':>6}")
    lines.append("  " + "-" * 42)
    for f in card["feature_comparison"]:
        us = "Yes" if f["we_have"] else "No"
        them = "Yes" if f["they_have"] else "No"
        lines.append(f"  {f['feature']:<30} {us:>4} {them:>6}")

    lines.append(f"\n--- WHEN WE WIN ---")
    for w in card["when_we_win"]:
        lines.append(f"  * {w}")

    lines.append(f"\n--- WHEN WE LOSE ---")
    for l in card["when_we_lose"]:
        lines.append(f"  * {l}")

    if card["objection_handling"]:
        lines.append(f"\n--- OBJECTION HANDLING ---")
        for obj in card["objection_handling"]:
            lines.append(f"  Q: \"{obj['objection']}\"")
            lines.append(f"  A: {obj['response']}")
            if obj.get("proof_point"):
                lines.append(f"     Proof: {obj['proof_point']}")
            lines.append("")

    if card["landmines"]:
        lines.append(f"--- LANDMINES TO PLANT ---")
        for lm in card["landmines"]:
            lines.append(f"  * {lm}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate competitive battlecard documents")
    parser.add_argument("input", nargs="?", help="JSON file with competitor data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Generate demo battlecard")
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

    competitor = data.get("competitor", data)
    our_product = data.get("our_product")

    card = generate_battlecard(competitor, our_product)

    if args.json_output:
        print(json.dumps(card, indent=2))
    else:
        print(format_battlecard(card))


if __name__ == "__main__":
    main()
