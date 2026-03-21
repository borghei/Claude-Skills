#!/usr/bin/env python3
"""Narrative Consistency Checker - Check communications for contradictions and tone mismatches.

Analyzes two or more communication texts (e.g., investor update and all-hands deck)
for factual inconsistencies, tone mismatches, and narrative contradictions. Uses keyword
and phrase analysis to detect conflicting signals.

Usage:
    python narrative_consistency_checker.py --texts investor_update.txt allhands_deck.txt
    python narrative_consistency_checker.py --texts doc1.txt doc2.txt doc3.txt --json
    python narrative_consistency_checker.py --text1 "We are growing efficiently" --text2 "We are hiring aggressively" --json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from collections import Counter

# Contradiction signal pairs - if one text uses signals from column A and another
# from column B on the same topic, flag as potential contradiction
CONTRADICTION_SIGNALS = [
    {"topic": "Growth Strategy", "signal_a": ["efficient growth", "capital efficient", "lean", "disciplined spending", "cost reduction", "cutting costs"],
     "signal_b": ["hiring aggressively", "aggressive expansion", "rapid growth", "scaling fast", "doubling the team", "massive investment"]},
    {"topic": "Revenue Health", "signal_a": ["strong pipeline", "accelerating revenue", "exceeding targets", "beating plan", "record quarter"],
     "signal_b": ["sales struggling", "missed targets", "pipeline thin", "below forecast", "revenue miss", "underperforming"]},
    {"topic": "Team Stability", "signal_a": ["world-class team", "strong culture", "low turnover", "talent magnet", "best team"],
     "signal_b": ["high turnover", "hiring challenges", "attrition", "retention issues", "people leaving", "morale issues"]},
    {"topic": "Market Position", "signal_a": ["market leader", "dominant position", "winning", "category leader", "outpacing competitors"],
     "signal_b": ["competitive threat", "losing deals", "market share declining", "competitive pressure", "behind competitors"]},
    {"topic": "Financial Health", "signal_a": ["strong runway", "well capitalized", "financially healthy", "cash positive"],
     "signal_b": ["runway concerns", "need to raise", "burn rate high", "cash tight", "bridge round", "extending runway"]},
    {"topic": "Product Status", "signal_a": ["product-market fit", "customers love", "high NPS", "strong adoption", "product led"],
     "signal_b": ["product issues", "churn increasing", "feature gaps", "product behind", "customers frustrated", "NPS declining"]},
]

# Tone categories
TONE_SIGNALS = {
    "optimistic": ["excited", "thrilled", "incredible", "amazing", "outstanding", "breakthrough", "record", "transformative", "revolutionary"],
    "measured": ["progressing", "improving", "on track", "steady", "developing", "building", "iterating"],
    "cautious": ["challenging", "headwinds", "adjusting", "recalibrating", "learning", "pivoting"],
    "urgent": ["critical", "must", "immediately", "crisis", "emergency", "urgent", "deadline", "risk"],
    "transparent": ["missed", "failed", "mistake", "learned", "honest", "acknowledge", "fell short"],
}


def analyze_text(text, label):
    """Analyze a single text for signals and tone."""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    word_count = len(words)

    # Find contradiction signals present
    signals_found = []
    for pair in CONTRADICTION_SIGNALS:
        for signal in pair["signal_a"]:
            if signal in text_lower:
                signals_found.append({"topic": pair["topic"], "signal": signal, "side": "a"})
        for signal in pair["signal_b"]:
            if signal in text_lower:
                signals_found.append({"topic": pair["topic"], "signal": signal, "side": "b"})

    # Detect tone
    tone_scores = {}
    for tone, keywords in TONE_SIGNALS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            tone_scores[tone] = count

    primary_tone = max(tone_scores, key=tone_scores.get) if tone_scores else "neutral"

    # Extract numbers/metrics mentioned
    metrics = re.findall(r'[\$€£]?\d+[\d,]*\.?\d*[%KMBx]?', text)

    return {
        "label": label,
        "word_count": word_count,
        "signals_found": signals_found,
        "tone_scores": tone_scores,
        "primary_tone": primary_tone,
        "metrics_mentioned": metrics[:20]  # Cap at 20
    }


def find_contradictions(analyses):
    """Compare analyses across texts to find contradictions."""
    contradictions = []
    tone_mismatches = []

    # Check for signal contradictions between texts
    for i in range(len(analyses)):
        for j in range(i + 1, len(analyses)):
            a_signals = analyses[i]["signals_found"]
            b_signals = analyses[j]["signals_found"]

            for topic in set(s["topic"] for s in a_signals + b_signals):
                a_sides = set(s["side"] for s in a_signals if s["topic"] == topic)
                b_sides = set(s["side"] for s in b_signals if s["topic"] == topic)

                if "a" in a_sides and "b" in b_sides:
                    a_terms = [s["signal"] for s in a_signals if s["topic"] == topic and s["side"] == "a"]
                    b_terms = [s["signal"] for s in b_signals if s["topic"] == topic and s["side"] == "b"]
                    contradictions.append({
                        "topic": topic,
                        "text_a": analyses[i]["label"],
                        "text_a_says": a_terms,
                        "text_b": analyses[j]["label"],
                        "text_b_says": b_terms,
                        "severity": "HIGH",
                        "recommendation": f"Resolve {topic} narrative: {analyses[i]['label']} signals positive while {analyses[j]['label']} signals negative"
                    })
                elif "b" in a_sides and "a" in b_sides:
                    a_terms = [s["signal"] for s in a_signals if s["topic"] == topic and s["side"] == "b"]
                    b_terms = [s["signal"] for s in b_signals if s["topic"] == topic and s["side"] == "a"]
                    contradictions.append({
                        "topic": topic,
                        "text_a": analyses[i]["label"],
                        "text_a_says": a_terms,
                        "text_b": analyses[j]["label"],
                        "text_b_says": b_terms,
                        "severity": "HIGH",
                        "recommendation": f"Resolve {topic} narrative: {analyses[i]['label']} signals negative while {analyses[j]['label']} signals positive"
                    })

            # Check tone mismatch
            tone_a = analyses[i]["primary_tone"]
            tone_b = analyses[j]["primary_tone"]
            if tone_a != tone_b:
                severity = "LOW"
                if (tone_a in ["optimistic", "measured"] and tone_b in ["urgent", "cautious"]) or \
                   (tone_b in ["optimistic", "measured"] and tone_a in ["urgent", "cautious"]):
                    severity = "MEDIUM"
                tone_mismatches.append({
                    "text_a": analyses[i]["label"],
                    "tone_a": tone_a,
                    "text_b": analyses[j]["label"],
                    "tone_b": tone_b,
                    "severity": severity,
                    "recommendation": f"Tone gap between {analyses[i]['label']} ({tone_a}) and {analyses[j]['label']} ({tone_b})"
                })

    return contradictions, tone_mismatches


def check_consistency(texts_with_labels):
    """Main analysis function."""
    analyses = []
    for label, text in texts_with_labels:
        analyses.append(analyze_text(text, label))

    contradictions, tone_mismatches = find_contradictions(analyses)

    # Overall consistency score
    contradiction_penalty = len(contradictions) * 15
    tone_penalty = sum(5 if t["severity"] == "MEDIUM" else 2 for t in tone_mismatches)
    consistency_score = max(0, 100 - contradiction_penalty - tone_penalty)

    return {
        "check_date": datetime.now().strftime("%Y-%m-%d"),
        "documents_analyzed": len(analyses),
        "consistency_score": consistency_score,
        "consistency_rating": "CONSISTENT" if consistency_score >= 80 else "CONCERNS" if consistency_score >= 50 else "CONTRADICTIONS FOUND",
        "contradictions": contradictions,
        "tone_mismatches": tone_mismatches,
        "document_summaries": [
            {"label": a["label"], "word_count": a["word_count"], "primary_tone": a["primary_tone"],
             "signals_count": len(a["signals_found"]), "metrics_count": len(a["metrics_mentioned"])}
            for a in analyses
        ],
        "recommendations": [c["recommendation"] for c in contradictions] +
                          [t["recommendation"] for t in tone_mismatches if t["severity"] != "LOW"]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"NARRATIVE CONSISTENCY CHECK")
    print(f"Date: {result['check_date']}")
    print(f"Documents: {result['documents_analyzed']}")
    print(f"{'='*70}\n")

    print(f"CONSISTENCY SCORE: {result['consistency_score']}/100 ({result['consistency_rating']})\n")

    print("DOCUMENT SUMMARIES:")
    print("-" * 50)
    for d in result["document_summaries"]:
        print(f"  {d['label']}: {d['word_count']} words, tone: {d['primary_tone']}, {d['signals_count']} signals")

    if result["contradictions"]:
        print(f"\nCONTRADICTIONS FOUND ({len(result['contradictions'])}):")
        print("-" * 50)
        for c in result["contradictions"]:
            print(f"  [{c['severity']}] {c['topic']}")
            print(f"    {c['text_a']} says: {', '.join(c['text_a_says'])}")
            print(f"    {c['text_b']} says: {', '.join(c['text_b_says'])}")

    if result["tone_mismatches"]:
        print(f"\nTONE MISMATCHES ({len(result['tone_mismatches'])}):")
        for t in result["tone_mismatches"]:
            print(f"  [{t['severity']}] {t['text_a']} ({t['tone_a']}) vs {t['text_b']} ({t['tone_b']})")

    if result["recommendations"]:
        print(f"\nRECOMMENDATIONS:")
        for r in result["recommendations"]:
            print(f"  -> {r}")
    else:
        print(f"\nNo contradictions or significant tone mismatches detected.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Check communications for narrative contradictions")
    parser.add_argument("--texts", nargs="+", help="File paths to check (2+)")
    parser.add_argument("--text1", help="First text string (alternative to files)")
    parser.add_argument("--text2", help="Second text string (alternative to files)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    texts_with_labels = []

    if args.texts:
        for path in args.texts:
            if not os.path.exists(path):
                print(f"Error: File not found: {path}", file=sys.stderr)
                sys.exit(1)
            with open(path, "r") as f:
                texts_with_labels.append((os.path.basename(path), f.read()))
    elif args.text1 and args.text2:
        texts_with_labels.append(("Text 1", args.text1))
        texts_with_labels.append(("Text 2", args.text2))
    else:
        print("Error: Provide either --texts with file paths or --text1 and --text2", file=sys.stderr)
        sys.exit(1)

    if len(texts_with_labels) < 2:
        print("Error: At least 2 texts required for comparison", file=sys.stderr)
        sys.exit(1)

    result = check_consistency(texts_with_labels)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
