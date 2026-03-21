#!/usr/bin/env python3
"""
Ad Headline Generator & Scorer

Generates ad headline variations from a value proposition using
proven formula patterns, then scores each for platform compliance.

Usage:
    python headline_generator.py --value-prop "Reduce churn by 30%" --platform google --audience "SaaS teams"
    python headline_generator.py --value-prop "Reduce churn by 30%" --json
"""

import argparse
import json
import re
import sys

PLATFORM_LIMITS = {
    "google": 30,
    "meta": 40,
    "linkedin": 70,
    "twitter": 70,
    "tiktok": 100,
}

FORMULAS = {
    "benefit_first": [
        "{outcome} Without {pain}",
        "{outcome} in {timeframe}",
        "{outcome} — Guaranteed",
        "Get {outcome} Today",
        "Finally, {outcome}",
    ],
    "curiosity": [
        "Why Your {topic} Is Failing",
        "The {topic} Secret Nobody Shares",
        "What {audience} Get Wrong About {topic}",
        "Stop Making This {topic} Mistake",
    ],
    "social_proof": [
        "{number} Teams Trust {product}",
        "Join {number}+ {audience}",
        "How {company} Got {outcome}",
        "Used by {number} {audience}",
    ],
    "problem_agitation": [
        "Still Losing {metric}?",
        "Tired of {pain}?",
        "{pain} Is Costing You ${cost}",
        "Stop Wasting Time on {pain}",
    ],
    "direct": [
        "{product}: {outcome}",
        "{outcome}. Try Free.",
        "{product} for {audience}",
    ],
}


def generate_headlines(value_prop: str, platform: str = "google",
                       audience: str = "", product: str = "", **kwargs) -> dict:
    max_len = PLATFORM_LIMITS.get(platform, 30)

    # Parse value prop for components
    components = {
        "outcome": value_prop,
        "pain": kwargs.get("pain", "manual processes"),
        "timeframe": kwargs.get("timeframe", "30 days"),
        "topic": kwargs.get("topic", value_prop.split()[0] if value_prop else "growth"),
        "audience": audience or "teams",
        "product": product or "[Product]",
        "number": kwargs.get("number", "1,000"),
        "company": kwargs.get("company", "[Company]"),
        "metric": kwargs.get("metric", "customers"),
        "cost": kwargs.get("cost", "thousands"),
    }

    headlines = []
    for formula_type, templates in FORMULAS.items():
        for template in templates:
            try:
                headline = template.format(**components)
            except KeyError:
                continue

            score = 100
            issues = []

            # Length check
            if len(headline) > max_len:
                over = len(headline) - max_len
                score -= min(30, over * 3)
                issues.append(f"Over {platform} limit by {over} chars")

            # Quality checks
            if not re.search(r"\d", headline):
                score -= 5
            if headline.isupper():
                score -= 15
                issues.append("All caps")

            headlines.append({
                "text": headline,
                "formula": formula_type,
                "chars": len(headline),
                "max_chars": max_len,
                "within_limit": len(headline) <= max_len,
                "score": max(0, score),
                "issues": issues,
            })

    # Sort by score
    headlines.sort(key=lambda x: x["score"], reverse=True)

    # Filter to within-limit only for recommendation
    compliant = [h for h in headlines if h["within_limit"]]

    return {
        "platform": platform,
        "value_proposition": value_prop,
        "char_limit": max_len,
        "total_generated": len(headlines),
        "compliant_count": len(compliant),
        "top_headlines": compliant[:10],
        "all_headlines": headlines,
        "tips": [
            "Generate 15-20 headlines, select the best 8-10.",
            f"Keep under {max_len} characters for {platform}.",
            "Mix formula types: benefit, curiosity, social proof, problem.",
            "Pin your strongest headline to Position 1 (Google RSA).",
            "A/B test top 3-5 headlines with 1,000+ impressions each.",
        ],
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  AD HEADLINE GENERATOR", "=" * 60]
    lines.append(f"\n  Platform: {result['platform'].title()} (max {result['char_limit']} chars)")
    lines.append(f"  Value Prop: {result['value_proposition']}")
    lines.append(f"  Generated: {result['total_generated']} ({result['compliant_count']} within limit)")

    lines.append(f"\n  Top Headlines:")
    for i, h in enumerate(result["top_headlines"], 1):
        issues = f" -- {'; '.join(h['issues'])}" if h["issues"] else ""
        lines.append(f"    {i:>2}. [{h['chars']}/{h['max_chars']}] \"{h['text']}\" ({h['formula']}){issues}")

    lines.append(f"\n  Tips:")
    for t in result["tips"]:
        lines.append(f"    > {t}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate and score ad headlines from value proposition.")
    parser.add_argument("--value-prop", "-v", required=True, help="Core value proposition")
    parser.add_argument("--platform", "-p", default="google", choices=list(PLATFORM_LIMITS.keys()))
    parser.add_argument("--audience", "-a", default="")
    parser.add_argument("--product", default="")
    parser.add_argument("--pain", default="manual processes")
    parser.add_argument("--timeframe", default="30 days")
    parser.add_argument("--number", default="1,000")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    result = generate_headlines(
        args.value_prop, args.platform, args.audience, args.product,
        pain=args.pain, timeframe=args.timeframe, number=args.number,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
