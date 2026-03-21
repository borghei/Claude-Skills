#!/usr/bin/env python3
"""
Pricing Psychology Analyzer

Analyzes pricing page structure for psychological optimization:
anchoring, decoy effect, charm pricing, framing, and tier design.

Usage:
    python pricing_psychology_analyzer.py pricing.json
    python pricing_psychology_analyzer.py pricing.json --json
    python pricing_psychology_analyzer.py --sample

Input JSON:
{
    "tiers": [
        {"name": "Starter", "price": 19, "billing": "monthly", "features": 5, "highlighted": false},
        {"name": "Pro", "price": 49, "billing": "monthly", "features": 15, "highlighted": true},
        {"name": "Enterprise", "price": 99, "billing": "monthly", "features": 30, "highlighted": false}
    ],
    "annual_discount_pct": 20,
    "has_free_tier": false,
    "currency": "USD"
}
"""

import argparse
import json
import sys
from pathlib import Path

SAMPLE = {
    "tiers": [
        {"name": "Starter", "price": 19, "billing": "monthly", "features": 5, "highlighted": False},
        {"name": "Pro", "price": 49, "billing": "monthly", "features": 15, "highlighted": True},
        {"name": "Enterprise", "price": 149, "billing": "monthly", "features": 50, "highlighted": False},
    ],
    "annual_discount_pct": 20,
    "has_free_tier": False,
    "currency": "USD",
}


def analyze_pricing(data: dict) -> dict:
    tiers = data.get("tiers", [])
    annual_discount = data.get("annual_discount_pct", 0)
    has_free = data.get("has_free_tier", False)
    currency = data.get("currency", "USD")

    checks = []
    score = 50
    recommendations = []

    # Tier count
    if len(tiers) == 3:
        checks.append({"name": "Good-Better-Best", "status": "PASS", "detail": "3 tiers (optimal)"})
        score += 10
    elif len(tiers) == 2:
        checks.append({"name": "Tier Count", "status": "WARN", "detail": "2 tiers -- add a 3rd for decoy effect"})
        recommendations.append("Add a 3rd tier to enable decoy pricing. The middle tier should be the target.")
    elif len(tiers) > 4:
        checks.append({"name": "Tier Count", "status": "WARN", "detail": f"{len(tiers)} tiers -- too many options causes choice paralysis"})
        recommendations.append("Reduce to 3-4 tiers. Paradox of choice: more options = fewer decisions.")
    elif len(tiers) == 4:
        checks.append({"name": "Tier Count", "status": "PASS", "detail": "4 tiers (acceptable)"})
        score += 5

    # Highlighted tier
    highlighted = [t for t in tiers if t.get("highlighted")]
    if highlighted:
        checks.append({"name": "Recommended Plan", "status": "PASS", "detail": f"'{highlighted[0]['name']}' highlighted"})
        score += 10
    else:
        checks.append({"name": "Recommended Plan", "status": "FAIL", "detail": "No plan highlighted"})
        recommendations.append("Highlight the target tier as 'Most Popular' or 'Recommended'. Default effect drives selection.")
        score -= 10

    # Charm pricing
    prices = [t.get("price", 0) for t in tiers if t.get("price", 0) > 0]
    charm_priced = [p for p in prices if p % 10 == 9 or str(p).endswith(("9", "99", "95", "97"))]

    if charm_priced:
        checks.append({"name": "Charm Pricing", "status": "PASS", "detail": f"Prices ending in 9: {charm_priced}"})
        score += 8
    elif prices:
        round_prices = [p for p in prices if p % 10 == 0]
        if round_prices:
            checks.append({"name": "Round Pricing", "status": "INFO", "detail": f"Round numbers: {round_prices} (premium positioning)"})
            score += 3
        else:
            recommendations.append("Use charm pricing ($49 not $50) for consumer, or round numbers ($100) for premium/enterprise.")

    # Anchoring
    if len(prices) >= 2:
        price_range = max(prices) - min(prices)
        ratio = max(prices) / min(prices) if min(prices) > 0 else 0

        if ratio >= 3:
            checks.append({"name": "Price Anchoring", "status": "PASS", "detail": f"High-to-low ratio: {ratio:.1f}x (strong anchor)"})
            score += 10
        elif ratio >= 2:
            checks.append({"name": "Price Anchoring", "status": "OK", "detail": f"Ratio: {ratio:.1f}x (moderate anchor)"})
            score += 5
        else:
            checks.append({"name": "Price Anchoring", "status": "WARN", "detail": f"Ratio: {ratio:.1f}x (weak anchor)"})
            recommendations.append("Increase price spread between tiers for stronger anchoring effect.")

    # Decoy analysis
    if len(tiers) >= 3:
        sorted_tiers = sorted(tiers, key=lambda t: t.get("price", 0))
        mid = sorted_tiers[1]
        low = sorted_tiers[0]
        high = sorted_tiers[2]

        mid_price = mid.get("price", 0)
        low_price = low.get("price", 0)
        high_price = high.get("price", 0)
        mid_features = mid.get("features", 0)
        low_features = low.get("features", 0)
        high_features = high.get("features", 0)

        if mid_price > 0 and low_price > 0:
            value_low = low_features / low_price if low_price > 0 else 0
            value_mid = mid_features / mid_price if mid_price > 0 else 0

            if value_mid > value_low * 1.3:
                checks.append({"name": "Decoy Effect", "status": "PASS", "detail": f"Middle tier ({mid['name']}) has better value ratio"})
                score += 10
            else:
                recommendations.append("Adjust features/pricing so middle tier is clearly the best value per dollar.")

    # Annual discount
    if annual_discount > 0:
        checks.append({"name": "Annual Billing", "status": "PASS", "detail": f"{annual_discount}% discount"})
        score += 5
        if annual_discount < 15:
            recommendations.append("Increase annual discount to 15-25% to drive commitment.")
        elif annual_discount > 30:
            recommendations.append("Annual discount above 30% may signal pricing is too high monthly.")
    else:
        recommendations.append("Offer annual billing with 15-25% discount. Reduces churn and pain of paying.")

    # Free tier
    if has_free:
        checks.append({"name": "Zero-Price Effect", "status": "PASS", "detail": "Free tier available"})
        score += 5
    else:
        recommendations.append("Consider a free tier or free trial. 'Free' is disproportionately attractive (zero-price effect).")

    # Pennies-a-day
    if prices:
        min_price = min(prices)
        daily = round(min_price / 30, 2)
        recommendations.append(f"Consider daily framing: '${daily}/day' feels cheaper than '${min_price}/month' (pennies-a-day effect).")

    score = max(0, min(100, score))

    return {
        "tier_count": len(tiers),
        "score": score,
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F",
        "checks": checks,
        "tier_summary": [{"name": t["name"], "price": t.get("price", 0), "features": t.get("features", 0), "highlighted": t.get("highlighted", False)} for t in tiers],
        "recommendations": recommendations,
        "psychology_principles_applied": [c["name"] for c in checks if c["status"] == "PASS"],
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  PRICING PSYCHOLOGY ANALYZER", "=" * 55]
    lines.append(f"\n  Score: {result['score']}/100 ({result['grade']}) | Tiers: {result['tier_count']}")

    lines.append(f"\n  Tiers:")
    for t in result["tier_summary"]:
        hl = " [HIGHLIGHTED]" if t["highlighted"] else ""
        lines.append(f"    {t['name']}: ${t['price']}/mo ({t['features']} features){hl}")

    lines.append(f"\n  Psychology Checks:")
    for c in result["checks"]:
        icon = {"PASS": "+", "WARN": "!", "FAIL": "X", "OK": "~", "INFO": "i"}
        lines.append(f"    [{icon.get(c['status'], '?')}] {c['name']}: {c['detail']}")

    lines.append(f"\n  Principles Applied: {', '.join(result['psychology_principles_applied'])}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"    {i}. {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze pricing page psychology.")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE
    elif args.file:
        try:
            data = json.loads(Path(args.file).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_pricing(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
