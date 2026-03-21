#!/usr/bin/env python3
"""
Headline Scorer

Scores marketing headlines for clarity, benefit strength,
specificity, and conversion potential.

Usage:
    python headline_scorer.py "Build landing pages in minutes without writing code"
    python headline_scorer.py --file headlines.txt --json
"""

import argparse
import json
import re
import sys

POWER_WORDS = [
    "free", "new", "proven", "guaranteed", "instant", "exclusive",
    "secret", "discover", "revolutionary", "breakthrough", "simple",
    "easy", "fast", "powerful", "ultimate", "complete", "essential",
]

ACTION_VERBS = [
    "build", "create", "get", "start", "grow", "reduce", "cut", "save",
    "boost", "increase", "automate", "ship", "hire", "scale", "stop",
    "eliminate", "transform", "unlock", "achieve", "discover", "join",
]

VAGUE_WORDS = [
    "innovative", "cutting-edge", "best-in-class", "world-class",
    "industry-leading", "state-of-the-art", "next-generation",
    "synergy", "holistic", "leverage", "optimize", "solutions",
    "ecosystem", "paradigm",
]

WE_PATTERNS = re.compile(r"^(we |our |at \w+)", re.IGNORECASE)
YOU_PATTERNS = re.compile(r"\b(you|your|you're)\b", re.IGNORECASE)


def score_headline(headline: str) -> dict:
    words = headline.split()
    lower = headline.lower()
    result = {
        "headline": headline,
        "word_count": len(words),
        "char_count": len(headline),
        "scores": {},
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
    }

    total = 100

    # Length
    wc = len(words)
    if 6 <= wc <= 12:
        result["scores"]["length"] = 95
        result["strengths"].append("Optimal headline length (6-12 words).")
    elif 4 <= wc <= 15:
        result["scores"]["length"] = 75
    elif wc < 4:
        result["scores"]["length"] = 50
        result["weaknesses"].append("Headline may be too short to convey full value.")
        total -= 8
    else:
        result["scores"]["length"] = 45
        result["weaknesses"].append("Headline is too long. Cut to 6-12 words.")
        total -= 12

    # Specificity
    has_number = bool(re.search(r"\d+", headline))
    has_specific_metric = bool(re.search(r"\d+%|\d+ (hours|minutes|days|weeks|x|teams|customers)", headline, re.IGNORECASE))
    has_timeframe = bool(re.search(r"in \d+ (minutes|hours|days|weeks|months)", headline, re.IGNORECASE))

    specificity_score = 40
    if has_specific_metric:
        specificity_score += 35
        result["strengths"].append("Specific metric makes claim believable.")
    if has_number:
        specificity_score += 15
    if has_timeframe:
        specificity_score += 10
        result["strengths"].append("Timeframe adds credibility.")

    found_vague = [w for w in VAGUE_WORDS if w in lower]
    if found_vague:
        specificity_score -= 20
        result["weaknesses"].append(f"Vague words: {', '.join(found_vague)}. Replace with specifics.")
        total -= 10

    result["scores"]["specificity"] = min(100, specificity_score)

    # Benefit clarity
    has_action = any(lower.startswith(v) or f" {v} " in lower for v in ACTION_VERBS)
    has_benefit = bool(re.search(r"(without|in \d|save|reduce|increase|grow|cut|boost|get|achieve)", lower))
    has_pain_removal = bool(re.search(r"(without|no |stop |eliminate|never )", lower))

    benefit_score = 40
    if has_action:
        benefit_score += 20
        result["strengths"].append("Starts with or contains an action verb.")
    if has_benefit:
        benefit_score += 25
    if has_pain_removal:
        benefit_score += 15
        result["strengths"].append("Includes pain removal framing (strong for conversion).")

    result["scores"]["benefit_clarity"] = min(100, benefit_score)

    # Customer focus
    starts_with_we = bool(WE_PATTERNS.match(headline))
    has_you = bool(YOU_PATTERNS.search(headline))

    if starts_with_we:
        result["weaknesses"].append("Starts with 'We/Our' -- lead with the customer's world instead.")
        total -= 8
    if has_you:
        result["strengths"].append("Uses 'you/your' -- customer-focused language.")

    # Emotional resonance
    power_found = [w for w in POWER_WORDS if w in lower]
    emotional_score = 50
    if power_found:
        emotional_score += min(30, len(power_found) * 10)
    if "?" in headline:
        emotional_score += 10
        result["strengths"].append("Question format creates curiosity.")

    result["scores"]["emotional_pull"] = min(100, emotional_score)

    # Overall
    weights = {"length": 0.15, "specificity": 0.30, "benefit_clarity": 0.35, "emotional_pull": 0.20}
    weighted = sum(result["scores"].get(k, 50) * w for k, w in weights.items())
    total = min(100, max(0, int(weighted)))

    result["overall_score"] = total
    result["grade"] = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F"

    if not result["suggestions"]:
        if total < 70:
            result["suggestions"].append("Try formula: '[Achieve outcome] without [pain point]'")
            result["suggestions"].append("Add a specific number or metric for credibility.")
        else:
            result["suggestions"].append("Test 2-3 variants of this headline via A/B testing.")

    return result


def format_human(results: list) -> str:
    lines = ["\n" + "=" * 60, "  HEADLINE SCORER", "=" * 60]
    for r in results:
        lines.append(f"\n  \"{r['headline']}\"")
        lines.append(f"  Score: {r['overall_score']}/100 ({r['grade']}) | {r['word_count']} words, {r['char_count']} chars")
        for k, v in r["scores"].items():
            lines.append(f"    {k.replace('_', ' ').title()}: {v}/100")
        for s in r["strengths"]:
            lines.append(f"    + {s}")
        for w in r["weaknesses"]:
            lines.append(f"    - {w}")
        for s in r["suggestions"]:
            lines.append(f"    > {s}")
        lines.append("-" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score marketing headlines for conversion potential.")
    parser.add_argument("headline", nargs="?")
    parser.add_argument("--file", "-f")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    headlines = []
    if args.file:
        with open(args.file) as f:
            headlines = [l.strip() for l in f if l.strip()]
    elif args.headline:
        headlines = [args.headline]
    else:
        parser.print_help()
        sys.exit(1)

    results = [score_headline(h) for h in headlines]
    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
