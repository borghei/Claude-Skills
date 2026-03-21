#!/usr/bin/env python3
"""
Copy Editing Readability Scorer

Scores content for editorial readability including Flesch Reading Ease,
sentence complexity, paragraph structure, passive voice rate, filler
word density, and web-optimized formatting checks.

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


def strip_formatting(text):
    """Remove markdown formatting."""
    t = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', t)
    t = re.sub(r'\*([^*]+)\*', r'\1', t)
    t = re.sub(r'```.*?```', '', t, flags=re.DOTALL)
    t = re.sub(r'`[^`]+`', '', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'^\|.*\|$', '', t, flags=re.MULTILINE)
    return t.strip()


def count_syllables(word):
    """Estimate syllables."""
    w = word.lower().strip('.,!?;:()[]"\'-')
    if len(w) <= 3:
        return 1
    count = 0
    prev = False
    for c in w:
        v = c in 'aeiouy'
        if v and not prev:
            count += 1
        prev = v
    if w.endswith('e') and count > 1:
        count -= 1
    return max(count, 1)


def sentences(text):
    """Get sentences."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip() and len(s.split()) >= 3]


def flesch(words, sents, syls):
    """Flesch Reading Ease."""
    if words == 0 or sents == 0:
        return 0
    return round(206.835 - 1.015 * (words / sents) - 84.6 * (syls / words), 1)


FILLER_WORDS = [
    'very', 'really', 'extremely', 'incredibly', 'quite', 'rather',
    'somewhat', 'just', 'actually', 'basically', 'essentially',
    'literally', 'simply', 'totally', 'absolutely', 'definitely',
]

WEAK_VERBS = [
    'utilize', 'implement', 'leverage', 'facilitate', 'optimize',
    'streamline', 'enhance', 'maximize', 'synergize',
]


def analyze(text):
    """Full readability analysis."""
    clean = strip_formatting(text)
    words = clean.split()
    wc = len(words)
    sents = sentences(clean)
    sc = len(sents)
    syls = sum(count_syllables(w) for w in words)

    fre = flesch(wc, sc, syls)
    fkg = round(0.39 * (wc / max(sc, 1)) + 11.8 * (syls / max(wc, 1)) - 15.59, 1) if wc > 0 else 0

    # Sentence analysis
    lengths = [len(s.split()) for s in sents] if sents else [0]
    avg_sent = round(sum(lengths) / max(len(lengths), 1), 1)
    std_sent = round(math.sqrt(sum((l - avg_sent) ** 2 for l in lengths) / max(len(lengths), 1)), 1) if len(lengths) > 1 else 0
    long_sents = sum(1 for l in lengths if l > 30)

    # Passive voice
    passive = sum(1 for s in sents if re.search(r'\b(is|are|was|were|been|being)\s+\w+(ed|en)\b', s, re.I))
    passive_rate = round(passive / max(sc, 1) * 100, 1)

    # Filler words
    filler_count = sum(len(re.findall(r'\b' + w + r'\b', clean, re.I)) for w in FILLER_WORDS)
    filler_per_1000 = round(filler_count / max(wc, 1) * 1000, 1)

    # Weak verbs
    weak_count = sum(len(re.findall(r'\b' + w + r'\b', clean, re.I)) for w in WEAK_VERBS)

    # Paragraphs
    paras = [p.strip() for p in re.split(r'\n\s*\n', clean) if p.strip()]
    para_sents = [len(sentences(p)) for p in paras]
    long_paras = sum(1 for c in para_sents if c > 5)

    # Subheading frequency
    headings = len(re.findall(r'^#{1,6}\s+', text, re.MULTILINE))
    words_per_heading = round(wc / max(headings, 1))

    # Score
    score = 0
    checks = {}

    # Flesch (25 pts)
    if 55 <= fre <= 75:
        score += 25
        checks["flesch"] = ("PASS", f"Flesch: {fre} (web-friendly range)")
    elif 45 <= fre <= 80:
        score += 15
        checks["flesch"] = ("PASS", f"Flesch: {fre} (acceptable)")
    else:
        score += 5
        checks["flesch"] = ("FAIL", f"Flesch: {fre} (target 60-70)")

    # Sentence length (20 pts)
    if 12 <= avg_sent <= 22:
        score += 20
        checks["sentence_length"] = ("PASS", f"Avg {avg_sent} words/sentence")
    else:
        score += 8
        checks["sentence_length"] = ("FAIL", f"Avg {avg_sent} words/sentence (target 15-20)")

    # Sentence variety (15 pts)
    if std_sent >= 5:
        score += 15
        checks["sentence_variety"] = ("PASS", f"Good variety (std dev {std_sent})")
    elif std_sent >= 3:
        score += 10
        checks["sentence_variety"] = ("PASS", f"Moderate variety (std dev {std_sent})")
    else:
        score += 3
        checks["sentence_variety"] = ("FAIL", f"Low variety (std dev {std_sent}, target >5)")

    # Passive voice (15 pts)
    if passive_rate < 10:
        score += 15
        checks["passive_voice"] = ("PASS", f"Passive: {passive_rate}%")
    elif passive_rate < 20:
        score += 8
        checks["passive_voice"] = ("FAIL", f"Passive: {passive_rate}% (target <10%)")
    else:
        score += 3
        checks["passive_voice"] = ("FAIL", f"Passive: {passive_rate}% (excessive)")

    # Filler words (10 pts)
    if filler_per_1000 < 5:
        score += 10
        checks["filler_words"] = ("PASS", f"{filler_count} filler words ({filler_per_1000}/1000)")
    else:
        score += 3
        checks["filler_words"] = ("FAIL", f"{filler_count} filler words ({filler_per_1000}/1000)")

    # Paragraph length (10 pts)
    if long_paras == 0:
        score += 10
        checks["paragraph_length"] = ("PASS", "All paragraphs under 5 sentences")
    else:
        score += 3
        checks["paragraph_length"] = ("FAIL", f"{long_paras} paragraphs exceed 5 sentences")

    # Formatting (5 pts)
    if words_per_heading <= 350:
        score += 5
        checks["heading_frequency"] = ("PASS", f"Heading every ~{words_per_heading} words")
    else:
        checks["heading_frequency"] = ("FAIL", f"Heading every ~{words_per_heading} words (target <350)")

    return {
        "word_count": wc,
        "sentence_count": sc,
        "score": min(score, 100),
        "flesch_reading_ease": fre,
        "flesch_kincaid_grade": fkg,
        "avg_sentence_length": avg_sent,
        "sentence_std_dev": std_sent,
        "long_sentences": long_sents,
        "passive_voice_rate": passive_rate,
        "filler_word_count": filler_count,
        "weak_verb_count": weak_count,
        "long_paragraphs": long_paras,
        "words_per_heading": words_per_heading,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Score readability for copy editing")
    parser.add_argument("file", help="Content file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    result = analyze(text)
    result["file"] = str(fp)

    grade = "A" if result["score"] >= 80 else "B" if result["score"] >= 65 else "C" if result["score"] >= 50 else "D"

    if args.json:
        # Convert checks tuples to dicts for JSON
        result["checks"] = {k: {"status": v[0], "detail": v[1]} for k, v in result["checks"].items()}
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  READABILITY: {result['score']}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  Words: {result['word_count']} | Sentences: {result['sentence_count']}")
        print(f"  Flesch: {result['flesch_reading_ease']} | Grade: {result['flesch_kincaid_grade']}")

        for key, (status, detail) in result["checks"].items():
            print(f"  [{status}] {detail}")

        if args.verbose:
            print(f"\n  Details:")
            print(f"    Long sentences (>30 words): {result['long_sentences']}")
            print(f"    Weak verbs: {result['weak_verb_count']}")
            print(f"    Filler words: {result['filler_word_count']}")

        print()


if __name__ == "__main__":
    main()
