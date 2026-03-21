#!/usr/bin/env python3
"""
AI Pattern Detector

Detects AI-generated content patterns including filler words, hedging
chains, structural uniformity, specificity vacuum, em-dash overuse,
false certainty, and generic conclusions. Produces a severity-scored
audit report.

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


# Tier 1 — Instant tells (Critical)
TIER1_FILLERS = [
    'delve', 'landscape', 'crucial', 'vital', 'pivotal', 'leverage', 'robust',
    'comprehensive', 'holistic', 'foster', 'facilitate', 'utilize', 'furthermore',
    'moreover', 'navigate', 'embark', 'tapestry', 'multifaceted', 'underscore',
]

# Tier 2 — Suspicious in clusters (Medium)
TIER2_FILLERS = [
    'streamline', 'optimize', 'innovative', 'cutting-edge', 'game-changer',
    'paradigm', 'synergy', 'ecosystem', 'empower', 'unlock', 'harness',
    'transformative', 'seamless', 'elevate', 'spearhead', 'groundbreaking',
]

# Hedging phrases (Critical)
HEDGING_PATTERNS = [
    r"it'?s important to note that",
    r"it'?s worth mentioning that",
    r"one might argue that",
    r"in many cases",
    r"it goes without saying",
    r"needless to say",
    r"it should be noted that",
    r"it bears mentioning",
    r"arguably",
]

# Vague claims (Critical)
VAGUE_PATTERNS = [
    (r'\bmany companies\b', "many companies"),
    (r'\bstudies show\b', "studies show"),
    (r'\bexperts say\b', "experts say"),
    (r'\bleading brands\b', "leading brands"),
    (r'\bsignificantly improved?\b', "significantly improved"),
    (r'\ba growing number\b', "a growing number"),
    (r'\bbest practices suggest\b', "best practices suggest"),
    (r'\bindustry leaders\b', "industry leaders"),
    (r'\bwide range of\b', "wide range of"),
]

# Generic conclusion starters (Medium)
GENERIC_CONCLUSIONS = [
    r'in (this|the) (article|post|guide),?\s+we (explored|discussed|covered)',
    r'by implementing these strategies',
    r'in conclusion,?\s+(it|we|the)',
    r'to sum up',
    r'as we\'?ve seen',
]


def find_all_with_context(text, pattern, context_chars=60):
    """Find all matches with surrounding context."""
    matches = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        start = max(0, m.start() - context_chars)
        end = min(len(text), m.end() + context_chars)
        context = text[start:end].replace('\n', ' ')
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        matches.append({
            "match": m.group(),
            "position": m.start(),
            "context": context,
        })
    return matches


def analyze_filler_words(text):
    """Detect AI filler words."""
    issues = []
    word_count = len(text.split())

    for word in TIER1_FILLERS:
        matches = find_all_with_context(text, r'\b' + word + r'\b')
        for m in matches:
            issues.append({
                "category": "filler_word_tier1",
                "severity": "Critical",
                "word": word,
                "context": m["context"],
                "position": m["position"],
            })

    for word in TIER2_FILLERS:
        matches = find_all_with_context(text, r'\b' + word + r'\b')
        for m in matches:
            issues.append({
                "category": "filler_word_tier2",
                "severity": "Medium",
                "word": word,
                "context": m["context"],
                "position": m["position"],
            })

    tier1_count = sum(1 for i in issues if i["severity"] == "Critical")
    tier2_count = sum(1 for i in issues if i["severity"] == "Medium")
    total_per_1000 = round((tier1_count + tier2_count) / max(word_count, 1) * 1000, 1)

    return {
        "tier1_count": tier1_count,
        "tier2_count": tier2_count,
        "total": tier1_count + tier2_count,
        "per_1000_words": total_per_1000,
        "issues": issues,
    }


def analyze_hedging(text):
    """Detect hedging chains."""
    issues = []
    for pattern in HEDGING_PATTERNS:
        matches = find_all_with_context(text, pattern)
        for m in matches:
            issues.append({
                "category": "hedging",
                "severity": "Critical",
                "match": m["match"],
                "context": m["context"],
            })
    return {"count": len(issues), "issues": issues}


def analyze_vague_claims(text):
    """Detect vague/unattributed claims."""
    issues = []
    for pattern, label in VAGUE_PATTERNS:
        matches = find_all_with_context(text, pattern)
        for m in matches:
            issues.append({
                "category": "vague_claim",
                "severity": "Critical",
                "claim": label,
                "context": m["context"],
            })
    return {"count": len(issues), "issues": issues}


def analyze_structure_uniformity(text):
    """Analyze paragraph structure for uniformity."""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text)
                  if p.strip() and not p.strip().startswith('#')]

    if len(paragraphs) < 4:
        return {"uniform": False, "detail": "Not enough paragraphs to analyze"}

    # Measure sentence counts per paragraph
    sentence_counts = []
    for p in paragraphs:
        sents = len([s for s in re.split(r'[.!?]+', p) if s.strip()])
        sentence_counts.append(sents)

    # Check if most paragraphs have the same sentence count
    from collections import Counter
    count_freq = Counter(sentence_counts)
    most_common_count, most_common_freq = count_freq.most_common(1)[0]
    uniformity_rate = most_common_freq / len(paragraphs)

    uniform = uniformity_rate > 0.6

    issues = []
    if uniform:
        issues.append({
            "category": "structural_uniformity",
            "severity": "Critical",
            "detail": f"{round(uniformity_rate * 100)}% of paragraphs have {most_common_count} sentences — AI fingerprint",
        })

    return {
        "total_paragraphs": len(paragraphs),
        "uniformity_rate": round(uniformity_rate, 2),
        "most_common_sentence_count": most_common_count,
        "uniform": uniform,
        "issues": issues,
    }


def analyze_em_dashes(text):
    """Check for em-dash overuse."""
    em_count = text.count('—') + text.count(' -- ')
    word_count = len(text.split())
    per_500 = round(em_count / max(word_count, 1) * 500, 1)

    issues = []
    if per_500 > 2:
        issues.append({
            "category": "em_dash_overuse",
            "severity": "Medium",
            "detail": f"{em_count} em-dashes ({per_500} per 500 words) — AI fingerprint threshold is 2 per 500",
        })

    return {"count": em_count, "per_500_words": per_500, "issues": issues}


def analyze_sentence_variety(text):
    """Check sentence length variety."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) >= 3]
    if len(sentences) < 5:
        return {"variety": "N/A", "issues": []}

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    issues = []
    if std_dev < 4:
        issues.append({
            "category": "sentence_uniformity",
            "severity": "Medium",
            "detail": f"Sentence length std dev: {round(std_dev, 1)} — below 4 indicates metronomic AI rhythm",
        })

    return {
        "average_length": round(avg, 1),
        "std_deviation": round(std_dev, 1),
        "issues": issues,
    }


def analyze_generic_conclusions(text):
    """Check for generic AI conclusion patterns."""
    issues = []
    # Check last 500 words
    last_500 = " ".join(text.split()[-500:])
    for pattern in GENERIC_CONCLUSIONS:
        if re.search(pattern, last_500, re.IGNORECASE):
            issues.append({
                "category": "generic_conclusion",
                "severity": "Medium",
                "detail": "Conclusion follows a generic AI pattern — rewrite with unique exit line",
            })
            break

    return {"issues": issues}


def calculate_score(all_issues, word_count):
    """Calculate AI pattern score (higher = more human)."""
    total_per_500 = len(all_issues) / max(word_count, 1) * 500

    if total_per_500 < 1:
        return 95
    elif total_per_500 < 3:
        return 80
    elif total_per_500 < 5:
        return 60
    elif total_per_500 < 8:
        return 40
    else:
        return 20


def main():
    parser = argparse.ArgumentParser(description="Detect AI content patterns")
    parser.add_argument("file", help="Content file to analyze")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    word_count = len(text.split())

    fillers = analyze_filler_words(text)
    hedging = analyze_hedging(text)
    vague = analyze_vague_claims(text)
    structure = analyze_structure_uniformity(text)
    em_dashes = analyze_em_dashes(text)
    sentences = analyze_sentence_variety(text)
    conclusions = analyze_generic_conclusions(text)

    all_issues = (
        fillers["issues"] + hedging["issues"] + vague["issues"] +
        structure.get("issues", []) + em_dashes["issues"] +
        sentences["issues"] + conclusions["issues"]
    )

    score = calculate_score(all_issues, word_count)
    total_tells = len(all_issues)
    per_500 = round(total_tells / max(word_count, 1) * 500, 1)

    if per_500 < 3:
        recommendation = "Minor edits needed"
    elif per_500 < 7:
        recommendation = "Significant editing required"
    else:
        recommendation = "Full rewrite recommended"

    result = {
        "file": str(fp),
        "word_count": word_count,
        "humanness_score": score,
        "total_ai_tells": total_tells,
        "tells_per_500_words": per_500,
        "recommendation": recommendation,
        "categories": {
            "filler_words": {"tier1": fillers["tier1_count"], "tier2": fillers["tier2_count"]},
            "hedging_chains": hedging["count"],
            "vague_claims": vague["count"],
            "structural_uniformity": structure.get("uniform", False),
            "em_dash_overuse": em_dashes["per_500_words"] > 2,
            "sentence_uniformity": sentences.get("std_deviation", 0) < 4 if sentences.get("std_deviation") else False,
        },
        "all_issues": all_issues if args.verbose else None,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  AI PATTERN AUDIT")
        print(f"{'='*55}")
        print(f"  File: {fp} | Words: {word_count}")
        print(f"  Humanness Score: {score}/100")
        print(f"  AI Tells: {total_tells} ({per_500} per 500 words)")
        print(f"  Recommendation: {recommendation}")

        print(f"\n  Category Breakdown:")
        print(f"    Filler words (Tier 1): {fillers['tier1_count']}")
        print(f"    Filler words (Tier 2): {fillers['tier2_count']}")
        print(f"    Hedging chains: {hedging['count']}")
        print(f"    Vague claims: {vague['count']}")
        print(f"    Em-dash rate: {em_dashes['per_500_words']} per 500 words")
        print(f"    Structural uniformity: {'Yes (AI pattern)' if structure.get('uniform') else 'No (varied)'}")
        std = sentences.get("std_deviation", "N/A")
        print(f"    Sentence variety: std dev {std}")

        if args.verbose and all_issues:
            print(f"\n  Detailed Issues:")
            for i, issue in enumerate(all_issues, 1):
                ctx = issue.get("context", issue.get("detail", ""))
                print(f"    {i}. [{issue['severity']}] {issue['category']}: {ctx[:80]}")

        print()


if __name__ == "__main__":
    main()
