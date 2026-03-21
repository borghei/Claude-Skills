#!/usr/bin/env python3
"""
Headline Analyzer

Analyzes headlines for SEO effectiveness, click-worthiness, emotional
impact, and readability. Scores headlines 0-100 and provides specific
improvement recommendations.

Usage:
    python headline_analyzer.py --headline "10 Ways to Reduce Cloud Costs in 2026"
    python headline_analyzer.py --headlines headlines.txt --json
    python headline_analyzer.py --headline "My Title" --keyword "cloud costs"
"""

import argparse
import json
import re
import sys
from pathlib import Path


POWER_WORDS = {
    "urgency": ["now", "today", "immediately", "hurry", "fast", "quick", "instant"],
    "exclusivity": ["secret", "insider", "exclusive", "hidden", "little-known", "underground"],
    "value": ["free", "save", "proven", "guaranteed", "essential", "ultimate", "complete"],
    "curiosity": ["surprising", "unexpected", "strange", "weird", "shocking", "bizarre"],
    "authority": ["expert", "research", "study", "data", "science", "official", "definitive"],
    "emotion": ["amazing", "brilliant", "terrible", "devastating", "incredible", "powerful"],
}

WEAK_WORDS = [
    "things", "stuff", "nice", "good", "bad", "great", "awesome", "cool",
    "interesting", "important", "very", "really", "basically",
]

HEADLINE_FORMULAS = {
    "number_list": r'^\d+\s+',
    "how_to": r'^how\s+to\b',
    "question": r'\?$',
    "why": r'^why\s+',
    "what": r'^what\s+',
    "guide": r'\bguide\b',
    "vs_comparison": r'\bvs\.?\b|\bversus\b',
    "year": r'\b202[4-9]\b|\b203\d\b',
}


def analyze_headline(headline, keyword=None):
    """Analyze a single headline."""
    hl = headline.strip()
    hl_lower = hl.lower()
    words = hl_lower.split()
    word_count = len(words)
    char_count = len(hl)

    checks = {}

    # Length (characters)
    checks["char_length"] = {
        "value": char_count,
        "pass": 40 <= char_count <= 65,
        "detail": f"{char_count} chars (target: 50-60 for SEO, max 65)",
    }

    # Word count
    checks["word_count"] = {
        "value": word_count,
        "pass": 6 <= word_count <= 12,
        "detail": f"{word_count} words (optimal: 6-12)",
    }

    # Number presence
    has_number = bool(re.search(r'\d+', hl))
    checks["has_number"] = {
        "pass": has_number,
        "detail": "Contains a number" if has_number else "No number — numbered headlines get 36% higher CTR",
    }

    # Power words
    found_power = []
    for category, pw_list in POWER_WORDS.items():
        for word in pw_list:
            if word in hl_lower:
                found_power.append(f"{word} ({category})")
    checks["power_words"] = {
        "pass": len(found_power) >= 1,
        "count": len(found_power),
        "found": found_power[:5],
        "detail": f"{len(found_power)} power words found" + (f": {', '.join(found_power[:3])}" if found_power else ""),
    }

    # Weak words
    found_weak = [w for w in WEAK_WORDS if w in words]
    checks["no_weak_words"] = {
        "pass": len(found_weak) == 0,
        "found": found_weak,
        "detail": f"{len(found_weak)} weak words" + (f": {', '.join(found_weak)}" if found_weak else " — clean"),
    }

    # Formula match
    matched_formula = None
    for name, pattern in HEADLINE_FORMULAS.items():
        if re.search(pattern, hl_lower):
            matched_formula = name
            break
    checks["proven_formula"] = {
        "pass": matched_formula is not None,
        "formula": matched_formula,
        "detail": f"Matches '{matched_formula}' formula" if matched_formula else "No proven headline formula detected",
    }

    # Front-loaded keyword
    if keyword:
        kw = keyword.lower()
        in_headline = kw in hl_lower
        front_loaded = hl_lower.startswith(kw) or hl_lower.find(kw) < char_count * 0.4
        checks["keyword_placement"] = {
            "pass": in_headline and front_loaded,
            "in_headline": in_headline,
            "front_loaded": front_loaded,
            "detail": f"Keyword {'front-loaded' if front_loaded else 'present but not front-loaded' if in_headline else 'MISSING'}",
        }

    # Emotional score (based on power words + formula)
    emotional_score = len(found_power) * 15 + (20 if has_number else 0) + (15 if matched_formula else 0)
    emotional_score = min(emotional_score, 100)
    checks["emotional_impact"] = {
        "value": emotional_score,
        "pass": emotional_score >= 30,
        "detail": f"Emotional impact: {emotional_score}/100",
    }

    # Capitalization
    is_title_case = hl[0].isupper()
    checks["proper_case"] = {
        "pass": is_title_case,
        "detail": "Proper capitalization" if is_title_case else "Starts with lowercase",
    }

    # Calculate score
    passed = sum(1 for c in checks.values() if c.get("pass", False))
    score = round((passed / len(checks)) * 100, 1)

    # Grade
    grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D" if score >= 35 else "F"

    return {
        "headline": hl,
        "score": score,
        "grade": grade,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze headlines for SEO and CTR")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--headline", help="Single headline to analyze")
    group.add_argument("--headlines", help="File with headlines (one per line)")
    parser.add_argument("--keyword", help="Target keyword for placement check")
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

    results = [analyze_headline(h, args.keyword) for h in headlines]

    if args.json:
        print(json.dumps({"headlines": results, "total": len(results)}, indent=2))
    else:
        for r in results:
            print(f"\n{'='*60}")
            print(f"  HEADLINE: {r['headline']}")
            print(f"  Score: {r['score']}/100 (Grade: {r['grade']})")
            print(f"{'='*60}")
            for key, check in r["checks"].items():
                status = "PASS" if check.get("pass") else "FAIL"
                print(f"  [{status}] {key}: {check['detail']}")

        if len(results) > 1:
            avg = round(sum(r["score"] for r in results) / len(results), 1)
            best = max(results, key=lambda r: r["score"])
            print(f"\n  Average score: {avg}/100")
            print(f"  Best: \"{best['headline']}\" ({best['score']}/100)")
        print()


if __name__ == "__main__":
    main()
