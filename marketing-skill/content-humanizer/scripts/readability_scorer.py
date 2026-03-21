#!/usr/bin/env python3
"""
Readability Scorer for Content Humanizer

Scores content readability focusing on metrics relevant to humanization:
sentence variety, paragraph structure diversity, passive voice rate,
and overall reading ease. Identifies areas where AI patterns reduce
readability and human feel.

Usage:
    python readability_scorer.py article.md
    python readability_scorer.py article.md --json
    python readability_scorer.py article.md --verbose
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


def count_syllables(word):
    """Estimate syllable count."""
    word = word.lower().strip('.,!?;:()[]{}"\'-')
    if len(word) <= 3:
        return 1
    count = 0
    prev = False
    for c in word:
        v = c in 'aeiouy'
        if v and not prev:
            count += 1
        prev = v
    if word.endswith('e') and count > 1:
        count -= 1
    return max(count, 1)


def get_sentences(text):
    """Split into sentences."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip() and len(s.split()) >= 3]


def flesch_ease(text):
    """Calculate Flesch Reading Ease."""
    words = text.split()
    wc = len(words)
    sc = len(get_sentences(text))
    if wc == 0 or sc == 0:
        return 0
    syl = sum(count_syllables(w) for w in words)
    return round(206.835 - 1.015 * (wc / sc) - 84.6 * (syl / wc), 1)


def analyze_variety(text):
    """Analyze sentence and paragraph variety."""
    sentences = get_sentences(text)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    # Sentence length variety
    if len(sentences) >= 5:
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        std = math.sqrt(sum((l - avg) ** 2 for l in lengths) / len(lengths))

        # Sentence type variety
        questions = sum(1 for s in sentences if s.strip().endswith('?'))
        fragments = sum(1 for s in sentences if len(s.split()) < 6)
        long_sents = sum(1 for s in sentences if len(s.split()) > 25)
    else:
        avg, std = 0, 0
        questions, fragments, long_sents = 0, 0, 0

    # Paragraph structure variety
    para_types = set()
    for p in paragraphs:
        sents = len(get_sentences(p))
        if sents == 1:
            para_types.add("single_sentence")
        elif sents <= 3:
            para_types.add("short")
        elif sents <= 5:
            para_types.add("medium")
        else:
            para_types.add("long")

        if '?' in p.split('.')[0] if p.split('.') else False:
            para_types.add("question_lead")
        if re.search(r'^\s*[-*]', p, re.MULTILINE):
            para_types.add("list")

    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg, 1),
        "sentence_std_dev": round(std, 1),
        "questions": questions,
        "fragments": fragments,
        "long_sentences": long_sents,
        "paragraph_count": len(paragraphs),
        "paragraph_types": list(para_types),
        "paragraph_variety_score": min(len(para_types) * 20, 100),
    }


def detect_passive(text):
    """Detect passive voice."""
    sentences = get_sentences(text)
    passive = 0
    for s in sentences:
        if re.search(r'\b(is|are|was|were|been|being)\s+\w+(ed|en)\b', s, re.IGNORECASE):
            passive += 1
    rate = round(passive / max(len(sentences), 1) * 100, 1)
    return {"count": passive, "rate": rate, "total_sentences": len(sentences)}


def score_humanness(flesch, variety, passive):
    """Calculate humanness-adjusted readability score."""
    score = 0

    # Flesch (target 60-70, 25 points)
    if 55 <= flesch <= 75:
        score += 25
    elif 45 <= flesch <= 80:
        score += 15
    else:
        score += 5

    # Sentence variety (25 points)
    std = variety.get("sentence_std_dev", 0)
    if std >= 6:
        score += 25
    elif std >= 4:
        score += 15
    else:
        score += 5

    # Paragraph variety (25 points)
    score += variety.get("paragraph_variety_score", 0) * 0.25

    # Passive voice (25 points, lower is better)
    rate = passive.get("rate", 0)
    if rate < 10:
        score += 25
    elif rate < 20:
        score += 15
    else:
        score += 5

    return round(min(score, 100), 1)


def main():
    parser = argparse.ArgumentParser(description="Score readability for humanization")
    parser.add_argument("file", help="Content file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    # Strip markdown
    clean = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
    clean = re.sub(r'```.*?```', '', clean, flags=re.DOTALL)

    flesch = flesch_ease(clean)
    variety = analyze_variety(clean)
    passive = detect_passive(clean)
    score = score_humanness(flesch, variety, passive)

    result = {
        "file": str(fp),
        "word_count": len(clean.split()),
        "readability_score": score,
        "flesch_reading_ease": flesch,
        "variety": variety,
        "passive_voice": passive,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"
        print(f"\n{'='*55}")
        print(f"  HUMANNESS READABILITY: {score}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  Flesch Reading Ease: {flesch}")
        print(f"  Sentence variety: std dev {variety['sentence_std_dev']} ({variety['sentence_count']} sentences)")
        print(f"  Questions: {variety['questions']} | Fragments: {variety['fragments']} | Long: {variety['long_sentences']}")
        print(f"  Paragraph types: {', '.join(variety['paragraph_types'])}")
        print(f"  Passive voice: {passive['rate']}% ({passive['count']}/{passive['total_sentences']})")

        recs = []
        if variety['sentence_std_dev'] < 4:
            recs.append("Vary sentence length more — mix short punchy with longer flowing sentences")
        if variety['questions'] == 0:
            recs.append("Add rhetorical questions to engage the reader")
        if variety['fragments'] == 0:
            recs.append("Use intentional fragments for emphasis")
        if passive['rate'] > 15:
            recs.append(f"Reduce passive voice from {passive['rate']}% to under 10%")
        if len(variety['paragraph_types']) < 3:
            recs.append("Diversify paragraph structures — use single-sentence, list, and question-lead paragraphs")

        if recs:
            print(f"\n  Recommendations:")
            for r in recs:
                print(f"    - {r}")
        print()


if __name__ == "__main__":
    main()
