#!/usr/bin/env python3
"""
AI Content Citability Scorer

Analyzes content for AI search citability signals including extractability,
attribution quality, schema presence, and structural patterns that AI systems
prefer when selecting sources for generated answers.

Usage:
    python content_scorer.py page.html
    python content_scorer.py page.md --json
    python content_scorer.py page.html --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_pattern(text, pattern):
    """Count regex pattern matches in text."""
    return len(re.findall(pattern, text, re.IGNORECASE))


def analyze_extractability(text, lines):
    """Score content extractability for AI systems."""
    scores = {}

    # Check for definition block in first 200 words
    words = text.split()
    first_200 = " ".join(words[:200]) if len(words) >= 200 else text
    has_definition = bool(re.search(
        r'\b(is|refers to|means|defined as|describes)\b.*\.',
        first_200, re.IGNORECASE
    ))
    scores["definition_in_first_200_words"] = {
        "pass": has_definition,
        "detail": "Clear definition found in opening" if has_definition
        else "No definition block detected in first 200 words"
    }

    # Check for numbered lists / steps
    numbered_steps = count_pattern(text, r'^\s*\d+[\.\)]\s+', )
    numbered_re = re.findall(r'^\s*\d+[\.\)]\s+', text, re.MULTILINE)
    num_steps = len(numbered_re)
    scores["numbered_steps"] = {
        "pass": num_steps >= 3,
        "count": num_steps,
        "detail": f"{num_steps} numbered steps found"
    }

    # Check for FAQ patterns (Q&A pairs)
    faq_patterns = (
        count_pattern(text, r'#{1,3}\s+(what|how|why|when|where|who|is|can|do|does)\b') +
        count_pattern(text, r'\*\*(what|how|why|when|where|who|is|can|do|does)\b[^*]+\*\*')
    )
    scores["faq_patterns"] = {
        "pass": faq_patterns >= 2,
        "count": faq_patterns,
        "detail": f"{faq_patterns} FAQ-style question headings found"
    }

    # Check for comparison tables
    table_rows = count_pattern(text, r'^\s*\|.*\|.*\|')
    table_re = re.findall(r'^\s*\|.*\|.*\|', text, re.MULTILINE)
    table_count = len(table_re)
    scores["comparison_tables"] = {
        "pass": table_count >= 4,
        "count": table_count,
        "detail": f"{table_count} table rows found"
    }

    # Check for attributed statistics
    stat_patterns = count_pattern(
        text,
        r'(according to|per |based on|reported by|published by|survey|study|research)\s+[A-Z].*\d'
    )
    scores["attributed_statistics"] = {
        "pass": stat_patterns >= 2,
        "count": stat_patterns,
        "detail": f"{stat_patterns} attributed statistics found"
    }

    # Check for self-contained H2 sections
    h2_sections = re.split(r'^##\s+', text, flags=re.MULTILINE)
    h2_count = max(0, len(h2_sections) - 1)
    scores["h2_sections"] = {
        "pass": h2_count >= 3,
        "count": h2_count,
        "detail": f"{h2_count} H2 sections found"
    }

    # Check for schema markup presence
    has_schema = bool(re.search(
        r'(application/ld\+json|schema\.org|@type|@context)',
        text, re.IGNORECASE
    ))
    scores["schema_markup"] = {
        "pass": has_schema,
        "detail": "Schema markup detected" if has_schema
        else "No schema markup found"
    }

    return scores


def analyze_authority(text):
    """Score authority signals for AI citation preference."""
    scores = {}

    # Author attribution
    has_author = bool(re.search(
        r'(author|written by|by\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',
        text, re.IGNORECASE
    ))
    scores["author_attribution"] = {
        "pass": has_author,
        "detail": "Author attribution detected" if has_author
        else "No author attribution found"
    }

    # Source citations
    citations = count_pattern(
        text,
        r'(according to|source:|cited from|published in|reported by|\(\d{4}\))'
    )
    scores["source_citations"] = {
        "pass": citations >= 3,
        "count": citations,
        "detail": f"{citations} source citations found"
    }

    # Date signals
    has_dates = bool(re.search(
        r'(202[4-6]|last updated|published|modified)',
        text, re.IGNORECASE
    ))
    scores["recency_signals"] = {
        "pass": has_dates,
        "detail": "Date/recency signals found" if has_dates
        else "No recency signals detected"
    }

    # Vague claims (negative signal)
    vague_claims = count_pattern(
        text,
        r'\b(many companies|studies show|experts say|leading brands|significantly improved|a growing number)\b'
    )
    scores["vague_claims"] = {
        "pass": vague_claims == 0,
        "count": vague_claims,
        "detail": f"{vague_claims} vague/unattributed claims found" if vague_claims
        else "No vague claims detected"
    }

    return scores


def analyze_ai_patterns(text):
    """Detect AI-generated content patterns that reduce citability."""
    scores = {}

    # AI filler words
    ai_fillers = count_pattern(
        text,
        r'\b(delve|landscape|crucial|leverage|robust|comprehensive|holistic|'
        r'foster|facilitate|utilize|furthermore|moreover|navigate|streamline|'
        r'cutting-edge|game-changer|paradigm|synergy|ecosystem|empower|'
        r'transformative|seamless)\b'
    )
    word_count = len(text.split())
    ai_density = (ai_fillers / max(word_count, 1)) * 1000

    scores["ai_filler_words"] = {
        "pass": ai_fillers <= 3,
        "count": ai_fillers,
        "per_1000_words": round(ai_density, 1),
        "detail": f"{ai_fillers} AI filler words detected ({round(ai_density, 1)} per 1000 words)"
    }

    # Em-dash overuse
    em_dashes = text.count("—") + text.count("--")
    em_per_500 = (em_dashes / max(word_count, 1)) * 500
    scores["em_dash_overuse"] = {
        "pass": em_per_500 <= 2,
        "count": em_dashes,
        "per_500_words": round(em_per_500, 1),
        "detail": f"{em_dashes} em-dashes ({round(em_per_500, 1)} per 500 words)"
    }

    # Hedging chains
    hedging = count_pattern(
        text,
        r"(it'?s important to note|it'?s worth mentioning|one might argue|"
        r"in many cases|it goes without saying|needless to say)"
    )
    scores["hedging_chains"] = {
        "pass": hedging == 0,
        "count": hedging,
        "detail": f"{hedging} hedging phrases found"
    }

    return scores


def calculate_overall_score(extractability, authority, ai_patterns):
    """Calculate weighted overall citability score 0-100."""
    total = 0
    max_score = 0

    # Extractability: 50% weight
    for key, val in extractability.items():
        max_score += 50 / len(extractability)
        if val["pass"]:
            total += 50 / len(extractability)

    # Authority: 30% weight
    for key, val in authority.items():
        max_score += 30 / len(authority)
        if val["pass"]:
            total += 30 / len(authority)

    # AI patterns: 20% weight (inverted — passing means fewer AI tells)
    for key, val in ai_patterns.items():
        max_score += 20 / len(ai_patterns)
        if val["pass"]:
            total += 20 / len(ai_patterns)

    return round(total, 1)


def grade_score(score):
    """Convert numeric score to letter grade."""
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def main():
    parser = argparse.ArgumentParser(
        description="Score content for AI search citability"
    )
    parser.add_argument("file", help="Path to content file (HTML or Markdown)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed per-check results"
    )
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    text = filepath.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    word_count = len(text.split())

    extractability = analyze_extractability(text, lines)
    authority = analyze_authority(text)
    ai_patterns = analyze_ai_patterns(text)
    overall_score = calculate_overall_score(extractability, authority, ai_patterns)
    grade = grade_score(overall_score)

    # Build recommendations
    recommendations = []
    for key, val in extractability.items():
        if not val["pass"]:
            recommendations.append(f"Extractability: Improve {key.replace('_', ' ')}")
    for key, val in authority.items():
        if not val["pass"]:
            recommendations.append(f"Authority: Improve {key.replace('_', ' ')}")
    for key, val in ai_patterns.items():
        if not val["pass"]:
            recommendations.append(f"AI Patterns: Fix {key.replace('_', ' ')}")

    result = {
        "file": str(filepath),
        "word_count": word_count,
        "overall_score": overall_score,
        "grade": grade,
        "extractability": extractability,
        "authority": authority,
        "ai_patterns": ai_patterns,
        "recommendations": recommendations,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  AI CITABILITY SCORE: {overall_score}/100 (Grade: {grade})")
        print(f"{'='*60}")
        print(f"  File: {filepath}")
        print(f"  Word count: {word_count}")
        print()

        passed = sum(1 for v in extractability.values() if v["pass"])
        print(f"  Extractability: {passed}/{len(extractability)} checks passed")

        passed = sum(1 for v in authority.values() if v["pass"])
        print(f"  Authority: {passed}/{len(authority)} checks passed")

        passed = sum(1 for v in ai_patterns.values() if v["pass"])
        print(f"  AI Patterns: {passed}/{len(ai_patterns)} checks passed")

        if args.verbose:
            print(f"\n  --- Extractability Details ---")
            for key, val in extractability.items():
                status = "PASS" if val["pass"] else "FAIL"
                print(f"  [{status}] {key}: {val['detail']}")

            print(f"\n  --- Authority Details ---")
            for key, val in authority.items():
                status = "PASS" if val["pass"] else "FAIL"
                print(f"  [{status}] {key}: {val['detail']}")

            print(f"\n  --- AI Pattern Details ---")
            for key, val in ai_patterns.items():
                status = "PASS" if val["pass"] else "FAIL"
                print(f"  [{status}] {key}: {val['detail']}")

        if recommendations:
            print(f"\n  --- Recommendations ---")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print()


if __name__ == "__main__":
    main()
