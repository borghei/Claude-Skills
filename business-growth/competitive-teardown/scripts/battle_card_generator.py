#!/usr/bin/env python3
"""
Battle Card Generator

Generate a one-page battle card from competitor profile data for sales
team use. Includes positioning, strengths/weaknesses, landmine questions,
objection handling, and pricing comparison.

Usage:
    python battle_card_generator.py competitor_profile.json
    python battle_card_generator.py competitor_profile.json --json
    python battle_card_generator.py competitor_profile.json --format markdown
"""

import argparse
import json
import sys
from datetime import date


def generate_battle_card(data: dict, output_format: str = "text") -> dict:
    """Generate battle card from competitor profile."""
    competitor = data.get("competitor", {})
    your_product = data.get("your_product", {})

    comp_name = competitor.get("name", "Competitor")
    your_name = your_product.get("name", "Your Product")

    # Threat assessment
    threat_score = 0
    if competitor.get("market_share_growing", False):
        threat_score += 2
    if competitor.get("recent_funding", False):
        threat_score += 1
    if competitor.get("targeting_your_icp", False):
        threat_score += 2
    if competitor.get("price_advantage", False):
        threat_score += 1
    if competitor.get("feature_parity", False):
        threat_score += 2

    if threat_score >= 6:
        threat_level = "CRITICAL"
    elif threat_score >= 4:
        threat_level = "HIGH"
    elif threat_score >= 2:
        threat_level = "MEDIUM"
    else:
        threat_level = "LOW"

    # Build battle card
    card = {
        "competitor_name": comp_name,
        "your_product_name": your_name,
        "last_updated": date.today().isoformat(),
        "threat_level": threat_level,
        "threat_score": threat_score,
        "positioning": {
            "their_positioning": competitor.get("positioning", "Not specified"),
            "your_positioning_against_them": your_product.get("positioning_vs", "Not specified"),
        },
        "where_they_win": competitor.get("strengths", [])[:5],
        "where_we_win": your_product.get("advantages", [])[:5],
        "landmine_questions": _generate_landmines(competitor),
        "objection_handling": _build_objection_handling(competitor, your_product),
        "pricing_comparison": {
            "their_pricing": competitor.get("pricing", {}),
            "your_pricing": your_product.get("pricing", {}),
        },
        "customer_quotes": your_product.get("switcher_quotes", [])[:2],
        "key_differentiators": your_product.get("differentiators", [])[:3],
    }

    return card


def _generate_landmines(competitor: dict) -> list:
    """Generate landmine questions that expose competitor weaknesses."""
    landmines = []
    weaknesses = competitor.get("weaknesses", [])

    for w in weaknesses[:5]:
        area = w.get("area", "this area")
        detail = w.get("detail", "")
        landmines.append({
            "question": f"How does {competitor.get('name', 'the competitor')} handle {area}?",
            "why_it_works": detail or f"They are weak in {area}.",
        })

    if not landmines:
        landmines.append({
            "question": "Can you show me customer case studies in my industry?",
            "why_it_works": "Tests whether they have relevant customer proof.",
        })

    return landmines


def _build_objection_handling(competitor: dict, your_product: dict) -> list:
    """Build objection handling responses."""
    objections = []
    comp_name = competitor.get("name", "They")

    if competitor.get("price_advantage", False):
        objections.append({
            "objection": f"{comp_name} is cheaper",
            "response": your_product.get("price_response",
                        "Compare total cost of ownership including implementation, training, and ongoing support. Our customers see ROI within [X] months."),
        })

    for feat in competitor.get("unique_features", [])[:3]:
        objections.append({
            "objection": f"{comp_name} has {feat.get('name', 'this feature')}",
            "response": feat.get("counter", f"We address this through {feat.get('alternative', 'our approach')}."),
        })

    if competitor.get("market_leader", False):
        objections.append({
            "objection": f"Everyone uses {comp_name}",
            "response": your_product.get("market_response",
                        "Market share does not mean best fit. Here is what makes us different for your specific use case."),
        })

    return objections


def format_text(card: dict) -> str:
    """Format battle card as text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"BATTLE CARD: {card['competitor_name']}")
    lines.append(f"Last Updated: {card['last_updated']}")
    lines.append(f"Threat Level: {card['threat_level']}")
    lines.append("=" * 60)

    pos = card["positioning"]
    lines.append(f"\nTHEIR POSITIONING: {pos['their_positioning']}")
    lines.append(f"OUR POSITIONING:   {pos['your_positioning_against_them']}")

    lines.append(f"\nWHERE THEY WIN:")
    for s in card["where_they_win"]:
        if isinstance(s, dict):
            lines.append(f"  - {s.get('point', s)}")
        else:
            lines.append(f"  - {s}")

    lines.append(f"\nWHERE WE WIN:")
    for a in card["where_we_win"]:
        if isinstance(a, dict):
            lines.append(f"  + {a.get('point', a)}")
        else:
            lines.append(f"  + {a}")

    lines.append(f"\nLANDMINE QUESTIONS:")
    for lm in card["landmine_questions"]:
        lines.append(f"  Q: \"{lm['question']}\"")
        lines.append(f"     Why: {lm['why_it_works']}")

    lines.append(f"\nOBJECTION HANDLING:")
    for obj in card["objection_handling"]:
        lines.append(f"  \"{obj['objection']}\"")
        lines.append(f"  -> {obj['response']}")

    if card["customer_quotes"]:
        lines.append(f"\nCUSTOMER QUOTES:")
        for q in card["customer_quotes"]:
            if isinstance(q, dict):
                lines.append(f"  \"{q.get('quote', '')}\" -- {q.get('attribution', '')}")
            else:
                lines.append(f"  \"{q}\"")

    lines.append("")
    return "\n".join(lines)


def format_markdown(card: dict) -> str:
    """Format battle card as markdown."""
    lines = []
    lines.append(f"# Battle Card: {card['competitor_name']}")
    lines.append(f"\n**Last Updated:** {card['last_updated']}  ")
    lines.append(f"**Threat Level:** {card['threat_level']}")

    pos = card["positioning"]
    lines.append(f"\n## Positioning")
    lines.append(f"**Their positioning:** {pos['their_positioning']}  ")
    lines.append(f"**Our positioning:** {pos['your_positioning_against_them']}")

    lines.append(f"\n## Where They Win")
    for s in card["where_they_win"]:
        text = s.get("point", s) if isinstance(s, dict) else s
        lines.append(f"- {text}")

    lines.append(f"\n## Where We Win")
    for a in card["where_we_win"]:
        text = a.get("point", a) if isinstance(a, dict) else a
        lines.append(f"- {text}")

    lines.append(f"\n## Landmine Questions")
    for lm in card["landmine_questions"]:
        lines.append(f"- **\"{lm['question']}\"** -- {lm['why_it_works']}")

    lines.append(f"\n## Objection Handling")
    for obj in card["objection_handling"]:
        lines.append(f"- **\"{obj['objection']}\"** -> {obj['response']}")

    if card["customer_quotes"]:
        lines.append(f"\n## Customer Quotes")
        for q in card["customer_quotes"]:
            if isinstance(q, dict):
                lines.append(f"> \"{q.get('quote', '')}\" -- {q.get('attribution', '')}")
            else:
                lines.append(f"> \"{q}\"")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a one-page battle card from competitor profile data."
    )
    parser.add_argument("input_file", help="JSON file with competitor profile data")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--format", choices=["text", "markdown"], default="text",
                        help="Output format (default: text)")

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

    card = generate_battle_card(data, args.format)

    if args.json:
        print(json.dumps(card, indent=2))
    elif args.format == "markdown":
        print(format_markdown(card))
    else:
        print(format_text(card))


if __name__ == "__main__":
    main()
