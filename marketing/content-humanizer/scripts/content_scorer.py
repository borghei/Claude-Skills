#!/usr/bin/env python3
"""
Content Humanization Scorer

Comprehensive scoring combining AI pattern detection, readability,
specificity, and voice consistency into a single humanization score.
Identifies the highest-impact fixes for making content sound human.

Usage:
    python content_scorer.py article.md
    python content_scorer.py article.md --json
    python content_scorer.py article.md --verbose
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


AI_FILLERS = [
    'delve', 'landscape', 'crucial', 'vital', 'pivotal', 'leverage', 'robust',
    'comprehensive', 'holistic', 'foster', 'facilitate', 'utilize', 'furthermore',
    'moreover', 'navigate', 'embark', 'streamline', 'cutting-edge', 'game-changer',
    'paradigm', 'synergy', 'ecosystem', 'empower', 'transformative', 'seamless',
    'tapestry', 'multifaceted', 'underscore',
]

HEDGING = [
    r"it'?s important to note", r"it'?s worth mentioning", r"one might argue",
    r"it goes without saying", r"needless to say", r"it should be noted",
]

VAGUE = [
    r'\bmany companies\b', r'\bstudies show\b', r'\bexperts say\b',
    r'\bleading brands\b', r'\bsignificantly improved?\b', r'\ba growing number\b',
]


def score_ai_patterns(text):
    """Score AI pattern density."""
    wc = len(text.split())
    filler_count = sum(len(re.findall(r'\b' + w + r'\b', text, re.IGNORECASE)) for w in AI_FILLERS)
    hedging_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in HEDGING)
    vague_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in VAGUE)

    total = filler_count + hedging_count + vague_count
    per_500 = round(total / max(wc, 1) * 500, 1)

    # Score (fewer patterns = higher score)
    if per_500 < 1:
        score = 100
    elif per_500 < 3:
        score = 80
    elif per_500 < 5:
        score = 60
    elif per_500 < 8:
        score = 40
    else:
        score = 20

    return {
        "score": score,
        "filler_count": filler_count,
        "hedging_count": hedging_count,
        "vague_count": vague_count,
        "total_tells": total,
        "per_500_words": per_500,
    }


def score_specificity(text):
    """Score content specificity."""
    # Count specific data points
    numbers = len(re.findall(r'\b\d+\.?\d*%|\$\d+|\d{1,3}(?:,\d{3})+', text))
    named_sources = len(re.findall(r'according to [A-Z]|per [A-Z]|\(\d{4}\)', text, re.IGNORECASE))
    named_entities = len(re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text))

    # Count vague claims
    vague = sum(len(re.findall(p, text, re.IGNORECASE)) for p in VAGUE)

    specificity = numbers + named_sources
    score = min((specificity * 10) + max(0, (100 - vague * 20)), 100)

    return {
        "score": score,
        "specific_numbers": numbers,
        "named_sources": named_sources,
        "vague_claims": vague,
    }


def score_rhythm(text):
    """Score sentence rhythm variety."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) >= 3]
    if len(sentences) < 5:
        return {"score": 50, "detail": "Not enough sentences"}

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    std = math.sqrt(sum((l - avg) ** 2 for l in lengths) / len(lengths))

    questions = sum(1 for s in sentences if '?' in s)
    short = sum(1 for l in lengths if l < 8)

    score = min(std * 10 + questions * 5 + short * 3, 100)

    return {
        "score": round(score),
        "std_deviation": round(std, 1),
        "questions": questions,
        "short_sentences": short,
    }


def score_voice_consistency(text):
    """Score voice consistency throughout the piece."""
    # Split into quarters and check for consistency
    words = text.split()
    if len(words) < 200:
        return {"score": 70, "detail": "Content too short for consistency check"}

    quarter = len(words) // 4
    quarters = [
        " ".join(words[:quarter]),
        " ".join(words[quarter:quarter*2]),
        " ".join(words[quarter*2:quarter*3]),
        " ".join(words[quarter*3:]),
    ]

    # Check contraction consistency
    contraction_rates = []
    for q in quarters:
        contractions = len(re.findall(r"\b\w+'(t|s|re|ve|ll|d|m)\b", q))
        wc = len(q.split())
        rate = contractions / max(wc, 1) * 100
        contraction_rates.append(rate)

    # Check "you" usage consistency
    you_rates = []
    for q in quarters:
        you_count = len(re.findall(r'\byou\b', q, re.IGNORECASE))
        wc = len(q.split())
        you_rates.append(you_count / max(wc, 1) * 100)

    # Score based on consistency (low variance = consistent)
    if contraction_rates:
        c_var = max(contraction_rates) - min(contraction_rates)
    else:
        c_var = 0
    if you_rates:
        y_var = max(you_rates) - min(you_rates)
    else:
        y_var = 0

    score = 100 - min(c_var * 10 + y_var * 10, 60)

    return {
        "score": round(max(score, 20)),
        "contraction_variance": round(c_var, 2),
        "you_usage_variance": round(y_var, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Score content humanization quality")
    parser.add_argument("file", help="Content file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    wc = len(text.split())

    ai = score_ai_patterns(text)
    spec = score_specificity(text)
    rhythm = score_rhythm(text)
    voice = score_voice_consistency(text)

    overall = round(
        ai["score"] * 0.35 +
        spec["score"] * 0.25 +
        rhythm["score"] * 0.25 +
        voice["score"] * 0.15
    )

    grade = "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D" if overall >= 35 else "F"

    if ai["per_500_words"] >= 8:
        action = "Full rewrite"
    elif ai["per_500_words"] >= 3:
        action = "Significant editing"
    else:
        action = "Minor polish"

    result = {
        "file": str(fp),
        "word_count": wc,
        "overall_score": overall,
        "grade": grade,
        "recommended_action": action,
        "ai_patterns": ai,
        "specificity": spec,
        "rhythm": rhythm,
        "voice_consistency": voice,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  HUMANIZATION SCORE: {overall}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  File: {fp} | Words: {wc}")
        print(f"  Action: {action}")
        print(f"\n  AI Patterns:      {ai['score']}/100 ({ai['total_tells']} tells, {ai['per_500_words']} per 500 words)")
        print(f"  Specificity:      {spec['score']}/100 ({spec['specific_numbers']} data points, {spec['vague_claims']} vague claims)")
        print(f"  Rhythm:           {rhythm['score']}/100 (std dev: {rhythm.get('std_deviation', 'N/A')})")
        print(f"  Voice Consistency: {voice['score']}/100")

        if args.verbose:
            print(f"\n  Breakdown:")
            print(f"    Filler words: {ai['filler_count']}")
            print(f"    Hedging phrases: {ai['hedging_count']}")
            print(f"    Vague claims: {ai['vague_count']}")
            print(f"    Named sources: {spec['named_sources']}")
            print(f"    Specific numbers: {spec['specific_numbers']}")

        # Top recommendations
        recs = []
        if ai["score"] < 60:
            recs.append(f"Remove {ai['filler_count']} AI filler words (delve, leverage, comprehensive, etc.)")
        if spec["score"] < 60:
            recs.append(f"Replace {spec['vague_claims']} vague claims with specific data or honest qualifications")
        if rhythm["score"] < 60:
            recs.append("Vary sentence length — add short punchy sentences and rhetorical questions")
        if voice["score"] < 60:
            recs.append("Maintain consistent voice — check contraction and formality level throughout")

        if recs:
            print(f"\n  Top Fixes:")
            for r in recs:
                print(f"    - {r}")
        print()


if __name__ == "__main__":
    main()
