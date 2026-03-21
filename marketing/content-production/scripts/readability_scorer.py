#!/usr/bin/env python3
"""
Content Readability Scorer

Comprehensive readability analysis including Flesch Reading Ease,
Flesch-Kincaid Grade Level, sentence length analysis, paragraph
analysis, passive voice detection, and web readability scoring.

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


def strip_markdown(text):
    """Remove markdown formatting for analysis."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^\s*[\-\*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def count_syllables(word):
    """Estimate syllable count."""
    word = word.lower().strip('.,!?;:()[]{}"\'-')
    if len(word) <= 3:
        return 1
    count = 0
    vowels = 'aeiouy'
    prev = False
    for c in word:
        v = c in vowels
        if v and not prev:
            count += 1
        prev = v
    if word.endswith('e') and count > 1:
        count -= 1
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        count += 1
    return max(count, 1)


def get_sentences(text):
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]


def get_paragraphs(text):
    """Split text into paragraphs."""
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def flesch_reading_ease(words, sentences, syllables):
    """Calculate Flesch Reading Ease score."""
    if words == 0 or sentences == 0:
        return 0
    return round(206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words), 1)


def flesch_kincaid_grade(words, sentences, syllables):
    """Calculate Flesch-Kincaid Grade Level."""
    if words == 0 or sentences == 0:
        return 0
    return round(0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59, 1)


def detect_passive_voice(text):
    """Detect passive voice constructions."""
    passive_patterns = [
        r'\b(is|are|was|were|been|being)\s+\w+ed\b',
        r'\b(is|are|was|were|been|being)\s+\w+en\b',
        r'\b(got|get|gets|getting)\s+\w+ed\b',
    ]
    count = 0
    examples = []
    sentences = get_sentences(text)
    for sent in sentences:
        for pattern in passive_patterns:
            if re.search(pattern, sent, re.IGNORECASE):
                count += 1
                if len(examples) < 5:
                    examples.append(sent[:80] + "..." if len(sent) > 80 else sent)
                break
    return count, examples


def analyze_sentence_variety(sentences):
    """Analyze sentence length variety."""
    if not sentences:
        return {}

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    # Classify
    short = sum(1 for l in lengths if l < 10)
    medium = sum(1 for l in lengths if 10 <= l <= 20)
    long_s = sum(1 for l in lengths if l > 20)
    very_long = sum(1 for l in lengths if l > 30)

    return {
        "average_length": round(avg, 1),
        "std_deviation": round(std_dev, 1),
        "shortest": min(lengths),
        "longest": max(lengths),
        "distribution": {
            "short_under_10": short,
            "medium_10_to_20": medium,
            "long_over_20": long_s,
            "very_long_over_30": very_long,
        },
        "variety_rating": "Good" if std_dev > 5 else "Moderate" if std_dev > 3 else "Low (monotonous)",
    }


def score_web_readability(flesch, avg_sentence, passive_rate, para_analysis):
    """Calculate web-specific readability score 0-100."""
    score = 0

    # Flesch Reading Ease (target 60-70 for web)
    if 55 <= flesch <= 75:
        score += 30
    elif 45 <= flesch <= 80:
        score += 20
    else:
        score += 10

    # Sentence length (target 15-20 avg)
    if 12 <= avg_sentence <= 22:
        score += 25
    elif 10 <= avg_sentence <= 25:
        score += 15
    else:
        score += 5

    # Passive voice (target < 10%)
    if passive_rate < 10:
        score += 20
    elif passive_rate < 20:
        score += 10
    else:
        score += 5

    # Paragraph length
    if para_analysis.get("avg_sentences", 0) <= 4:
        score += 25
    elif para_analysis.get("avg_sentences", 0) <= 6:
        score += 15
    else:
        score += 5

    return min(score, 100)


def main():
    parser = argparse.ArgumentParser(description="Score content readability")
    parser.add_argument("file", help="Content file to analyze")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    raw_text = fp.read_text(encoding="utf-8", errors="replace")
    text = strip_markdown(raw_text)

    words_list = text.split()
    word_count = len(words_list)
    sentences = get_sentences(text)
    sentence_count = len(sentences)
    syllable_count = sum(count_syllables(w) for w in words_list)
    paragraphs = get_paragraphs(text)

    # Core scores
    fre = flesch_reading_ease(word_count, sentence_count, syllable_count)
    fkg = flesch_kincaid_grade(word_count, sentence_count, syllable_count)

    # Sentence analysis
    variety = analyze_sentence_variety(sentences)
    avg_sentence_len = variety.get("average_length", 0)

    # Passive voice
    passive_count, passive_examples = detect_passive_voice(text)
    passive_rate = round(passive_count / max(sentence_count, 1) * 100, 1)

    # Paragraph analysis
    para_sentence_counts = [len(get_sentences(p)) for p in paragraphs]
    para_analysis = {
        "count": len(paragraphs),
        "avg_sentences": round(sum(para_sentence_counts) / max(len(para_sentence_counts), 1), 1),
        "long_paragraphs": sum(1 for c in para_sentence_counts if c > 5),
    }

    # Web readability score
    web_score = score_web_readability(fre, avg_sentence_len, passive_rate, para_analysis)

    # Reading level label
    if fre >= 80:
        level = "Easy (6th grade)"
    elif fre >= 60:
        level = "Standard (8th-9th grade)"
    elif fre >= 40:
        level = "Difficult (College level)"
    else:
        level = "Very Difficult (Graduate level)"

    result = {
        "file": str(fp),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": len(paragraphs),
        "flesch_reading_ease": fre,
        "flesch_kincaid_grade": fkg,
        "reading_level": level,
        "web_readability_score": web_score,
        "sentence_variety": variety,
        "passive_voice": {
            "count": passive_count,
            "rate": passive_rate,
            "examples": passive_examples,
        },
        "paragraph_analysis": para_analysis,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        grade = "A" if web_score >= 80 else "B" if web_score >= 65 else "C" if web_score >= 50 else "D"
        print(f"\n{'='*55}")
        print(f"  READABILITY SCORE: {web_score}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  File: {fp}")
        print(f"  Words: {word_count} | Sentences: {sentence_count} | Paragraphs: {len(paragraphs)}")
        print(f"\n  Flesch Reading Ease: {fre} ({level})")
        print(f"  Flesch-Kincaid Grade: {fkg}")
        print(f"  Avg sentence length: {avg_sentence_len} words")
        print(f"  Sentence variety: {variety.get('variety_rating', 'N/A')} (std dev: {variety.get('std_deviation', 0)})")
        print(f"  Passive voice: {passive_count} instances ({passive_rate}%)")
        print(f"  Avg paragraph: {para_analysis['avg_sentences']} sentences")
        print(f"  Long paragraphs (>5 sentences): {para_analysis['long_paragraphs']}")

        if args.verbose and passive_examples:
            print(f"\n  Passive voice examples:")
            for ex in passive_examples:
                print(f"    - {ex}")

        # Recommendations
        recs = []
        if fre < 50:
            recs.append("Simplify language — target Flesch 60-70 for web content")
        if avg_sentence_len > 22:
            recs.append("Shorten sentences — target 15-20 words average")
        if passive_rate > 15:
            recs.append(f"Reduce passive voice from {passive_rate}% to under 10%")
        if para_analysis["long_paragraphs"] > 0:
            recs.append(f"Break up {para_analysis['long_paragraphs']} long paragraphs (max 4 sentences)")
        if variety.get("std_deviation", 0) < 4:
            recs.append("Vary sentence length more — mix short and long for rhythm")

        if recs:
            print(f"\n  Recommendations:")
            for r in recs:
                print(f"    - {r}")

        print()


if __name__ == "__main__":
    main()
