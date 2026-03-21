#!/usr/bin/env python3
"""
AI SEO Keyword Analyzer

Analyzes keywords for AI search optimization potential. Classifies intent,
estimates AI Overview likelihood, scores competition signals, and prioritizes
keywords by AI citation opportunity.

Usage:
    python keyword_analyzer.py --keywords keywords.csv --json
    python keyword_analyzer.py --keywords keywords.csv --sort ai_score
    python keyword_analyzer.py --keyword "what is cloud cost optimization"
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


# Intent classification patterns
INTENT_PATTERNS = {
    "informational": [
        r'\b(what is|what are|how to|how do|why is|why do|guide|tutorial|'
        r'explain|definition|meaning|example|examples|overview|introduction|'
        r'difference between|compared to)\b'
    ],
    "commercial": [
        r'\b(best|top|review|reviews|comparison|vs|versus|alternative|'
        r'alternatives|compare|which|rating|ratings|recommended)\b'
    ],
    "transactional": [
        r'\b(buy|purchase|price|pricing|cost|discount|deal|coupon|order|'
        r'subscribe|sign up|free trial|download|get started)\b'
    ],
    "navigational": [
        r'\b(login|log in|sign in|dashboard|account|support|contact|'
        r'official|site|website|app|docs|documentation)\b'
    ],
}

# AI Overview likelihood factors
AI_OVERVIEW_TRIGGERS = [
    r'\b(what is|what are|how to|how do|why|when|where|who)\b',
    r'\b(definition|meaning|explain|difference|vs|versus)\b',
    r'\b(best practices|steps|process|guide|tips)\b',
    r'\b(statistics|data|numbers|percentage|rate)\b',
]

# Content format mapping by intent
FORMAT_RECOMMENDATIONS = {
    "informational": {
        "primary": "Definition block + numbered steps",
        "schema": "FAQPage, HowTo, or Article",
        "ai_format": "Lead with 1-2 sentence definition, then structured steps",
    },
    "commercial": {
        "primary": "Comparison table + pros/cons lists",
        "schema": "Product, Review, or FAQPage",
        "ai_format": "Structured comparison with clear recommendation",
    },
    "transactional": {
        "primary": "Product details + pricing table",
        "schema": "Product with Offer",
        "ai_format": "Direct answer with pricing and CTA",
    },
    "navigational": {
        "primary": "Direct answer with link",
        "schema": "Organization or WebSite",
        "ai_format": "Brand-focused answer with official link",
    },
}


def classify_intent(keyword):
    """Classify search intent of a keyword."""
    keyword_lower = keyword.lower()
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, keyword_lower))
            score += matches
        scores[intent] = score

    # Default to informational if no strong signal
    if max(scores.values()) == 0:
        return "informational"

    return max(scores, key=scores.get)


def estimate_ai_overview_likelihood(keyword):
    """Estimate probability of AI Overview appearing for this query."""
    keyword_lower = keyword.lower()
    triggers = 0

    for pattern in AI_OVERVIEW_TRIGGERS:
        if re.search(pattern, keyword_lower):
            triggers += 1

    # Question format bonus
    if keyword_lower.strip().endswith('?') or keyword_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
        triggers += 1

    # Long-tail bonus (more words = more likely informational = more AI Overview)
    word_count = len(keyword.split())
    if word_count >= 4:
        triggers += 1
    if word_count >= 6:
        triggers += 1

    # Normalize to 0-100
    likelihood = min(triggers * 20, 100)

    if likelihood >= 80:
        label = "Very High"
    elif likelihood >= 60:
        label = "High"
    elif likelihood >= 40:
        label = "Medium"
    elif likelihood >= 20:
        label = "Low"
    else:
        label = "Very Low"

    return {"score": likelihood, "label": label, "triggers": triggers}


def score_ai_citation_opportunity(keyword, intent, ai_likelihood):
    """Score the AI citation opportunity for a keyword."""
    score = 0

    # Intent scoring (informational and commercial get cited most)
    intent_scores = {
        "informational": 30,
        "commercial": 25,
        "transactional": 10,
        "navigational": 5,
    }
    score += intent_scores.get(intent, 10)

    # AI Overview likelihood contribution
    score += ai_likelihood["score"] * 0.4

    # Word count factor (longer queries = more specific = better citation chance)
    word_count = len(keyword.split())
    if 3 <= word_count <= 6:
        score += 15
    elif word_count > 6:
        score += 10
    elif word_count <= 2:
        score += 5

    # Question format bonus
    if any(keyword.lower().startswith(w) for w in ['what', 'how', 'why', 'when', 'where', 'who']):
        score += 10

    return min(round(score, 1), 100)


def analyze_keyword(keyword, volume=None, difficulty=None):
    """Full analysis of a single keyword."""
    intent = classify_intent(keyword)
    ai_likelihood = estimate_ai_overview_likelihood(keyword)
    ai_score = score_ai_citation_opportunity(keyword, intent, ai_likelihood)
    format_rec = FORMAT_RECOMMENDATIONS.get(intent, FORMAT_RECOMMENDATIONS["informational"])

    result = {
        "keyword": keyword,
        "word_count": len(keyword.split()),
        "intent": intent,
        "ai_overview_likelihood": ai_likelihood,
        "ai_citation_score": ai_score,
        "recommended_format": format_rec,
    }

    if volume is not None:
        result["volume"] = volume
    if difficulty is not None:
        result["difficulty"] = difficulty

    # Priority classification
    if ai_score >= 70:
        result["priority"] = "High"
    elif ai_score >= 45:
        result["priority"] = "Medium"
    else:
        result["priority"] = "Low"

    return result


def load_keywords_from_csv(filepath):
    """Load keywords from CSV file."""
    keywords = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            # Try as simple list
            f.seek(0)
            for line in f:
                kw = line.strip()
                if kw:
                    keywords.append({"keyword": kw})
            return keywords

        for row in reader:
            entry = {}
            # Try common column names
            for key in ['keyword', 'Keyword', 'query', 'Query', 'term', 'Term']:
                if key in row:
                    entry["keyword"] = row[key]
                    break

            if "keyword" not in entry:
                # Use first column
                first_key = list(row.keys())[0]
                entry["keyword"] = row[first_key]

            for key in ['volume', 'Volume', 'search_volume', 'Search Volume']:
                if key in row and row[key]:
                    try:
                        entry["volume"] = int(row[key].replace(',', ''))
                    except (ValueError, AttributeError):
                        pass

            for key in ['difficulty', 'Difficulty', 'KD', 'kd']:
                if key in row and row[key]:
                    try:
                        entry["difficulty"] = int(row[key])
                    except (ValueError, AttributeError):
                        pass

            if entry.get("keyword"):
                keywords.append(entry)

    return keywords


def main():
    parser = argparse.ArgumentParser(
        description="Analyze keywords for AI search optimization potential"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--keywords", help="Path to CSV file with keywords"
    )
    group.add_argument(
        "--keyword", help="Single keyword to analyze"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--sort", choices=["ai_score", "volume", "keyword"],
        default="ai_score",
        help="Sort results by (default: ai_score)"
    )
    args = parser.parse_args()

    if args.keyword:
        result = analyze_keyword(args.keyword)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  KEYWORD ANALYSIS: {args.keyword}")
            print(f"{'='*60}")
            print(f"  Intent: {result['intent']}")
            print(f"  AI Overview Likelihood: {result['ai_overview_likelihood']['label']} ({result['ai_overview_likelihood']['score']}%)")
            print(f"  AI Citation Score: {result['ai_citation_score']}/100")
            print(f"  Priority: {result['priority']}")
            print(f"\n  Recommended Format:")
            print(f"    Content: {result['recommended_format']['primary']}")
            print(f"    Schema: {result['recommended_format']['schema']}")
            print(f"    AI Optimization: {result['recommended_format']['ai_format']}")
            print()
        return

    # CSV mode
    filepath = Path(args.keywords)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    keyword_data = load_keywords_from_csv(filepath)
    if not keyword_data:
        print("Error: No keywords found in file", file=sys.stderr)
        sys.exit(1)

    results = []
    for entry in keyword_data:
        result = analyze_keyword(
            entry["keyword"],
            volume=entry.get("volume"),
            difficulty=entry.get("difficulty"),
        )
        results.append(result)

    # Sort
    if args.sort == "ai_score":
        results.sort(key=lambda x: x["ai_citation_score"], reverse=True)
    elif args.sort == "volume":
        results.sort(key=lambda x: x.get("volume", 0) or 0, reverse=True)
    elif args.sort == "keyword":
        results.sort(key=lambda x: x["keyword"])

    if args.json:
        print(json.dumps({"keywords": results, "total": len(results)}, indent=2))
    else:
        print(f"\n{'='*70}")
        print(f"  AI KEYWORD ANALYSIS — {len(results)} keywords")
        print(f"{'='*70}")
        print(f"  {'Keyword':<40} {'Intent':<14} {'AI Score':<10} {'Priority'}")
        print(f"  {'-'*40} {'-'*14} {'-'*10} {'-'*8}")
        for r in results:
            print(f"  {r['keyword'][:39]:<40} {r['intent']:<14} {r['ai_citation_score']:<10} {r['priority']}")

        # Summary
        high = sum(1 for r in results if r["priority"] == "High")
        medium = sum(1 for r in results if r["priority"] == "Medium")
        low = sum(1 for r in results if r["priority"] == "Low")
        print(f"\n  Summary: {high} High / {medium} Medium / {low} Low priority")
        print()


if __name__ == "__main__":
    main()
