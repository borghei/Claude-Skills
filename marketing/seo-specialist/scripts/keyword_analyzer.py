#!/usr/bin/env python3
"""
SEO Keyword Analyzer

Analyzes keywords for search intent, estimates difficulty tier, classifies
commercial value, and prioritizes by SEO opportunity. Supports CSV input
with volume/difficulty data or plain keyword lists.

Usage:
    python keyword_analyzer.py --keywords keywords.csv --json
    python keyword_analyzer.py --keyword "cloud cost optimization"
    python keyword_analyzer.py --keywords keywords.csv --sort opportunity
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


INTENT_PATTERNS = {
    "informational": [
        r'\b(what is|what are|how to|how do|how does|why is|why do|guide|'
        r'tutorial|explain|definition|meaning|example|examples|overview|'
        r'introduction|difference between|learn)\b'
    ],
    "commercial": [
        r'\b(best|top|review|reviews|comparison|vs|versus|alternative|'
        r'alternatives|compare|which|rating|recommended|software|tool|'
        r'tools|platform|service)\b'
    ],
    "transactional": [
        r'\b(buy|purchase|price|pricing|cost|discount|deal|coupon|order|'
        r'subscribe|sign up|free trial|download|get started|hire|book)\b'
    ],
    "navigational": [
        r'\b(login|log in|sign in|dashboard|account|support|contact|'
        r'official|docs|documentation|api|download)\b'
    ],
}

CONTENT_TYPE_MAP = {
    "informational": "Blog post, tutorial, guide, or explainer",
    "commercial": "Comparison page, review, or buyer's guide",
    "transactional": "Product page, pricing page, or landing page",
    "navigational": "Homepage, product page, or documentation",
}


def classify_intent(keyword):
    """Classify search intent of a keyword."""
    kw = keyword.lower()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(len(re.findall(p, kw)) for p in patterns)
        scores[intent] = score
    if max(scores.values()) == 0:
        return "informational"
    return max(scores, key=scores.get)


def estimate_difficulty_tier(keyword, difficulty=None):
    """Estimate keyword difficulty tier."""
    if difficulty is not None:
        if difficulty <= 20:
            return {"tier": "Easy", "score": difficulty, "note": "Quick win opportunity"}
        elif difficulty <= 40:
            return {"tier": "Moderate", "score": difficulty, "note": "Achievable with good content"}
        elif difficulty <= 60:
            return {"tier": "Hard", "score": difficulty, "note": "Requires strong DA + content depth"}
        else:
            return {"tier": "Very Hard", "score": difficulty, "note": "Needs authority building first"}

    # Heuristic based on keyword characteristics
    word_count = len(keyword.split())
    if word_count >= 4:
        return {"tier": "Easy-Moderate", "score": None, "note": "Long-tail — likely lower competition"}
    elif word_count == 3:
        return {"tier": "Moderate", "score": None, "note": "Mid-tail keyword"}
    elif word_count == 2:
        return {"tier": "Hard", "score": None, "note": "Short-tail — likely competitive"}
    else:
        return {"tier": "Very Hard", "score": None, "note": "Single word — extremely competitive"}


def classify_commercial_value(keyword, intent):
    """Estimate commercial value of a keyword."""
    kw = keyword.lower()

    high_value_signals = len(re.findall(
        r'\b(pricing|buy|purchase|cost|enterprise|saas|software|platform|'
        r'agency|consultant|service|professional|business)\b', kw
    ))

    if intent == "transactional" or high_value_signals >= 2:
        return "High"
    elif intent == "commercial" or high_value_signals >= 1:
        return "Medium"
    elif intent == "informational":
        return "Low"
    else:
        return "Medium"


def calculate_opportunity_score(volume, difficulty_tier, commercial_value, intent):
    """Calculate composite opportunity score."""
    # Volume factor (0-30)
    if volume is not None:
        if volume >= 5000:
            vol_score = 30
        elif volume >= 1000:
            vol_score = 25
        elif volume >= 500:
            vol_score = 20
        elif volume >= 100:
            vol_score = 15
        elif volume >= 50:
            vol_score = 10
        else:
            vol_score = 5
    else:
        vol_score = 15  # Unknown, assume moderate

    # Difficulty factor (0-30, inverted)
    diff_map = {"Easy": 30, "Easy-Moderate": 25, "Moderate": 20, "Hard": 10, "Very Hard": 5}
    diff_score = diff_map.get(difficulty_tier, 15)

    # Commercial value factor (0-25)
    comm_map = {"High": 25, "Medium": 15, "Low": 8}
    comm_score = comm_map.get(commercial_value, 10)

    # Intent factor (0-15)
    intent_map = {"transactional": 15, "commercial": 12, "informational": 8, "navigational": 5}
    intent_score = intent_map.get(intent, 8)

    return vol_score + diff_score + comm_score + intent_score


def analyze_keyword(keyword, volume=None, difficulty=None):
    """Complete analysis of a single keyword."""
    intent = classify_intent(keyword)
    diff = estimate_difficulty_tier(keyword, difficulty)
    commercial = classify_commercial_value(keyword, intent)
    opportunity = calculate_opportunity_score(volume, diff["tier"], commercial, intent)

    result = {
        "keyword": keyword,
        "word_count": len(keyword.split()),
        "intent": intent,
        "content_type": CONTENT_TYPE_MAP[intent],
        "difficulty": diff,
        "commercial_value": commercial,
        "opportunity_score": opportunity,
    }

    if volume is not None:
        result["volume"] = volume

    # Priority
    if opportunity >= 75:
        result["priority"] = "High"
    elif opportunity >= 55:
        result["priority"] = "Medium"
    else:
        result["priority"] = "Low"

    return result


def load_csv(filepath):
    """Load keywords from CSV."""
    keywords = []
    with open(filepath, 'r', encoding='utf-8') as f:
        # Try as CSV with headers
        sample = f.read(1024)
        f.seek(0)

        if ',' in sample or '\t' in sample:
            dialect = csv.Sniffer().sniff(sample, delimiters=',\t')
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                entry = {}
                for key in ['keyword', 'Keyword', 'query', 'Query', 'term']:
                    if key in row:
                        entry["keyword"] = row[key].strip()
                        break
                if "keyword" not in entry:
                    entry["keyword"] = list(row.values())[0].strip()

                for key in ['volume', 'Volume', 'search_volume', 'Search Volume', 'vol']:
                    if key in row and row[key]:
                        try:
                            entry["volume"] = int(str(row[key]).replace(',', '').strip())
                        except (ValueError, AttributeError):
                            pass

                for key in ['difficulty', 'Difficulty', 'KD', 'kd', 'keyword_difficulty']:
                    if key in row and row[key]:
                        try:
                            entry["difficulty"] = int(str(row[key]).replace(',', '').strip())
                        except (ValueError, AttributeError):
                            pass

                if entry.get("keyword"):
                    keywords.append(entry)
        else:
            for line in f:
                kw = line.strip()
                if kw:
                    keywords.append({"keyword": kw})

    return keywords


def main():
    parser = argparse.ArgumentParser(
        description="Analyze keywords for SEO opportunity"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--keywords", help="CSV file with keywords")
    group.add_argument("--keyword", help="Single keyword to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--sort", choices=["opportunity", "volume", "keyword", "difficulty"],
        default="opportunity", help="Sort by (default: opportunity)"
    )
    args = parser.parse_args()

    if args.keyword:
        result = analyze_keyword(args.keyword)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  KEYWORD: {args.keyword}")
            print(f"{'='*60}")
            print(f"  Intent: {result['intent']}")
            print(f"  Content type: {result['content_type']}")
            print(f"  Difficulty: {result['difficulty']['tier']}")
            print(f"  Commercial value: {result['commercial_value']}")
            print(f"  Opportunity score: {result['opportunity_score']}/100")
            print(f"  Priority: {result['priority']}")
            print()
        return

    filepath = Path(args.keywords)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    data = load_csv(filepath)
    results = [
        analyze_keyword(e["keyword"], e.get("volume"), e.get("difficulty"))
        for e in data
    ]

    sort_keys = {
        "opportunity": lambda x: x["opportunity_score"],
        "volume": lambda x: x.get("volume", 0) or 0,
        "keyword": lambda x: x["keyword"],
        "difficulty": lambda x: x["difficulty"].get("score", 50) or 50,
    }
    results.sort(key=sort_keys[args.sort], reverse=(args.sort != "keyword"))

    if args.json:
        print(json.dumps({"total": len(results), "keywords": results}, indent=2))
    else:
        print(f"\n{'='*75}")
        print(f"  KEYWORD ANALYSIS — {len(results)} keywords (sorted by {args.sort})")
        print(f"{'='*75}")
        print(f"  {'Keyword':<35} {'Intent':<14} {'Difficulty':<12} {'Value':<8} {'Score'}")
        print(f"  {'-'*35} {'-'*14} {'-'*12} {'-'*8} {'-'*5}")
        for r in results:
            kw = r['keyword'][:34]
            print(f"  {kw:<35} {r['intent']:<14} {r['difficulty']['tier']:<12} {r['commercial_value']:<8} {r['opportunity_score']}")

        high = sum(1 for r in results if r["priority"] == "High")
        med = sum(1 for r in results if r["priority"] == "Medium")
        low = sum(1 for r in results if r["priority"] == "Low")
        print(f"\n  Priority: {high} High / {med} Medium / {low} Low")
        print()


if __name__ == "__main__":
    main()
