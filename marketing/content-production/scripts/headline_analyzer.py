#!/usr/bin/env python3
"""
Production Headline Analyzer

Analyzes and scores headline options for content production. Checks
SEO length compliance, power word usage, number presence, emotional
impact, and formula matching. Recommends the best headline from a set.

Usage:
    python headline_analyzer.py --headline "10 Ways to Cut Cloud Costs in 2026"
    python headline_analyzer.py --headlines headlines.txt --json
    python headline_analyzer.py --headline "Title Here" --keyword "cloud costs"
"""

import argparse
import json
import re
import sys
from pathlib import Path


POWER_WORDS = [
    'proven', 'ultimate', 'complete', 'essential', 'free', 'new', 'easy',
    'fast', 'quick', 'simple', 'guaranteed', 'powerful', 'secret', 'insider',
    'surprising', 'unexpected', 'amazing', 'incredible', 'best', 'top',
    'guide', 'step', 'hack', 'strategy', 'framework', 'checklist', 'template',
]

WEAK_WORDS = [
    'things', 'stuff', 'nice', 'good', 'bad', 'great', 'awesome', 'interesting',
    'important', 'very', 'really', 'basically', 'actually',
]

FORMULAS = {
    "number_list": (r'^\d+\s+', "Numbered list — high CTR format"),
    "how_to": (r'^how\s+to\b', "How-to — matches informational intent"),
    "question": (r'\?$', "Question — triggers curiosity"),
    "year": (r'\b202[4-9]\b', "Year tag — signals freshness"),
    "guide": (r'\bguide\b', "Guide label — promises comprehensiveness"),
    "comparison": (r'\bvs\.?\b|\bversus\b', "Comparison — matches commercial intent"),
    "colon_format": (r':', "Colon format — establishes topic then value"),
}


def score_headline(headline, keyword=None):
    """Score a headline 0-100."""
    hl = headline.strip()
    hl_lower = hl.lower()
    words = hl_lower.split()
    chars = len(hl)
    score = 0
    checks = []

    # Character length (max 30 points)
    if 45 <= chars <= 60:
        score += 30
        checks.append(("PASS", f"Length: {chars} chars (optimal)"))
    elif 35 <= chars <= 65:
        score += 20
        checks.append(("PASS", f"Length: {chars} chars (acceptable)"))
    else:
        score += 5
        checks.append(("FAIL", f"Length: {chars} chars (target 50-60)"))

    # Number (15 points)
    if re.search(r'\d+', hl):
        score += 15
        checks.append(("PASS", "Contains number"))
    else:
        checks.append(("FAIL", "No number — adds 36% CTR lift"))

    # Power words (15 points)
    found = [w for w in POWER_WORDS if w in hl_lower]
    if found:
        score += 15
        checks.append(("PASS", f"Power words: {', '.join(found[:3])}"))
    else:
        checks.append(("FAIL", "No power words detected"))

    # No weak words (10 points)
    weak = [w for w in WEAK_WORDS if w in words]
    if not weak:
        score += 10
        checks.append(("PASS", "No weak words"))
    else:
        checks.append(("FAIL", f"Weak words: {', '.join(weak)}"))

    # Formula match (15 points)
    matched = None
    for name, (pattern, desc) in FORMULAS.items():
        if re.search(pattern, hl_lower):
            matched = desc
            break
    if matched:
        score += 15
        checks.append(("PASS", f"Formula: {matched}"))
    else:
        checks.append(("FAIL", "No proven formula pattern"))

    # Keyword (15 points)
    if keyword:
        kw = keyword.lower()
        if kw in hl_lower:
            pos = hl_lower.find(kw)
            if pos < chars * 0.4:
                score += 15
                checks.append(("PASS", "Keyword front-loaded"))
            else:
                score += 10
                checks.append(("PASS", "Keyword present but not front-loaded"))
        else:
            checks.append(("FAIL", f"Keyword '{keyword}' missing"))
    else:
        score += 8  # Neutral if no keyword given

    return {
        "headline": hl,
        "score": min(score, 100),
        "grade": "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D" if score >= 35 else "F",
        "char_count": chars,
        "word_count": len(words),
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze headlines for production")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--headline", help="Single headline")
    group.add_argument("--headlines", help="File with headlines")
    parser.add_argument("--keyword")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    headlines = []
    if args.headline:
        headlines = [args.headline]
    else:
        fp = Path(args.headlines)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        headlines = [l.strip() for l in fp.read_text().splitlines() if l.strip()]

    results = [score_headline(h, args.keyword) for h in headlines]

    if args.json:
        print(json.dumps({"headlines": results}, indent=2))
    else:
        for r in results:
            print(f"\n  {'='*55}")
            print(f"  {r['headline']}")
            print(f"  Score: {r['score']}/100 (Grade: {r['grade']}) | {r['char_count']} chars")
            for status, detail in r["checks"]:
                print(f"  [{status}] {detail}")

        if len(results) > 1:
            best = max(results, key=lambda r: r["score"])
            print(f"\n  RECOMMENDED: \"{best['headline']}\" ({best['score']}/100)")
        print()


if __name__ == "__main__":
    main()
