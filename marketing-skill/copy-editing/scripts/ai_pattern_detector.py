#!/usr/bin/env python3
"""
AI Pattern Detector for Copy Editing

Detects AI-generated content markers relevant to editorial review.
Identifies filler words, hedging, structural uniformity, and provides
a pre-edit assessment for copy editors to know what they are working with.

Usage:
    python ai_pattern_detector.py article.md
    python ai_pattern_detector.py article.md --json
    python ai_pattern_detector.py article.md --verbose
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter


FILLER_CRITICAL = [
    'delve', 'landscape', 'crucial', 'vital', 'pivotal', 'leverage',
    'robust', 'comprehensive', 'holistic', 'foster', 'facilitate',
    'utilize', 'furthermore', 'moreover', 'navigate', 'embark',
    'tapestry', 'multifaceted', 'underscore',
]

FILLER_MEDIUM = [
    'streamline', 'optimize', 'innovative', 'cutting-edge', 'game-changer',
    'paradigm', 'synergy', 'ecosystem', 'empower', 'transformative',
    'seamless', 'elevate', 'spearhead', 'groundbreaking',
]

HEDGING = [
    "it's important to note", "it is important to note",
    "it's worth mentioning", "it is worth mentioning",
    "one might argue", "in many cases",
    "it goes without saying", "needless to say",
]

GENERIC_OPENERS = [
    r'^in today\'?s (digital|modern|fast-paced|competitive|evolving)',
    r'^in the (rapidly|ever|constantly) (evolving|changing)',
    r'^in an? (increasingly|highly|rapidly)',
]


def detect_patterns(text):
    """Detect all AI patterns."""
    wc = len(text.split())
    findings = []

    # Filler words
    for word in FILLER_CRITICAL:
        count = len(re.findall(r'\b' + word + r'\b', text, re.IGNORECASE))
        if count:
            findings.append({
                "category": "filler",
                "severity": "Critical",
                "item": word,
                "count": count,
                "fix": f"Replace '{word}' — see content humanizer replacement guide",
            })

    for word in FILLER_MEDIUM:
        count = len(re.findall(r'\b' + word + r'\b', text, re.IGNORECASE))
        if count:
            findings.append({
                "category": "filler",
                "severity": "Medium",
                "item": word,
                "count": count,
                "fix": f"Consider replacing '{word}' with plain-language alternative",
            })

    # Hedging
    for phrase in HEDGING:
        count = len(re.findall(re.escape(phrase), text, re.IGNORECASE))
        if count:
            findings.append({
                "category": "hedging",
                "severity": "Critical",
                "item": phrase,
                "count": count,
                "fix": f"Delete '{phrase}' and start with the actual point",
            })

    # Generic openers
    for pattern in GENERIC_OPENERS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            findings.append({
                "category": "generic_opener",
                "severity": "High",
                "item": "Generic AI opener detected",
                "count": 1,
                "fix": "Rewrite opening — lead with the problem or the answer",
            })

    # Em-dash overuse
    em_count = text.count('—') + text.count(' -- ')
    per_500 = round(em_count / max(wc, 1) * 500, 1)
    if per_500 > 2:
        findings.append({
            "category": "em_dash",
            "severity": "Medium",
            "item": f"Em-dash overuse: {em_count} ({per_500} per 500 words)",
            "count": em_count,
            "fix": "Replace some em-dashes with periods, commas, or parentheses",
        })

    # Sentence uniformity
    sents = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) >= 3]
    if len(sents) >= 10:
        lengths = [len(s.split()) for s in sents]
        std = math.sqrt(sum((l - sum(lengths)/len(lengths)) ** 2 for l in lengths) / len(lengths))
        if std < 3.5:
            findings.append({
                "category": "uniformity",
                "severity": "High",
                "item": f"Sentence length uniformity: std dev {round(std, 1)}",
                "count": 1,
                "fix": "Vary sentence length — add short sentences, fragments, and questions",
            })

    total = sum(f.get("count", 1) for f in findings)
    per_500_total = round(total / max(wc, 1) * 500, 1)

    if per_500_total < 3:
        assessment = "Light editing — minor AI patterns"
    elif per_500_total < 7:
        assessment = "Moderate editing — noticeable AI patterns throughout"
    else:
        assessment = "Heavy editing or rewrite — extensive AI patterns"

    return {
        "word_count": wc,
        "total_tells": total,
        "per_500_words": per_500_total,
        "assessment": assessment,
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Detect AI patterns for copy editing")
    parser.add_argument("file", help="Content file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    result = detect_patterns(text)
    result["file"] = str(fp)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  AI PATTERN SCAN — Pre-Edit Assessment")
        print(f"{'='*55}")
        print(f"  File: {fp} | Words: {result['word_count']}")
        print(f"  AI tells: {result['total_tells']} ({result['per_500_words']} per 500 words)")
        print(f"  Assessment: {result['assessment']}")

        if result["findings"]:
            # Group by category
            categories = {}
            for f in result["findings"]:
                cat = f["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(f)

            for cat, items in categories.items():
                total = sum(i.get("count", 1) for i in items)
                print(f"\n  {cat.upper()} ({total} instances):")
                for item in items:
                    sev = item["severity"]
                    if args.verbose:
                        print(f"    [{sev}] {item['item']} (x{item['count']})")
                        print(f"           Fix: {item['fix']}")
                    else:
                        print(f"    [{sev}] {item['item']} (x{item['count']})")
        else:
            print(f"\n  No AI patterns detected — content reads as human-written.")

        print()


if __name__ == "__main__":
    main()
