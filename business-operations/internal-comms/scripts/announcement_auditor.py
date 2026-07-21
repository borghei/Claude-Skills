#!/usr/bin/env python3
"""Audit a draft internal announcement for clarity, jargon, and missing elements.

Usage:
    python3 announcement_auditor.py --input draft.json [--min-score 75] [--format text|json]

Input JSON shape:
    {"title": "...", "body": "...", "audience": "all-staff", "channel": "email"}
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

# Words that signal abstraction where a concrete verb belongs.
JARGON = [
    "synergy", "synergies", "leverage", "leveraging", "realign", "realigning",
    "operationalize", "operationalise", "ideate", "bandwidth", "circle back",
    "double down", "north star", "paradigm", "holistic", "streamline",
    "right-size", "rightsize", "restructure", "optimize headcount",
    "value-add", "learnings", "cadence", "workstream", "operating model",
    "best-in-class", "world-class", "transformational", "strategic imperative",
]

HEDGES = [
    "somewhat", "fairly", "arguably", "possibly", "perhaps", "we believe",
    "it seems", "may or may not", "at this time", "going forward",
    "in due course", "as appropriate", "where possible",
]

# Cue phrases proving each required element is present.
ELEMENT_CUES: Dict[str, List[str]] = {
    "what_changed": [
        r"\bwe (are|will be|have decided to)\b", r"\bis changing\b", r"\bchanging to\b",
        r"\beffective\b", r"\bstarting (on )?\b", r"\bas of\b", r"\bwe will move\b",
        r"\bwe're moving\b", r"\bwe are moving\b", r"\bnew\b.{0,20}\bpolicy\b",
    ],
    "why": [
        r"\bbecause\b", r"\bthe reason\b", r"\bwhy\b", r"\bin order to\b",
        r"\bso that\b", r"\bthis is driven by\b", r"\bwe made this (call|decision)\b",
    ],
    "who_is_affected": [
        r"\baffect(s|ed|ing)?\b", r"\bapplies to\b", r"\bif you (are|work|report)\b",
        r"\bfor (everyone|all|those) (in|on|who)\b", r"\bnothing changes for\b",
        r"\bimpact(s|ed)?\b",
    ],
    "what_to_do": [
        r"\bplease\b", r"\byou (need|should|must) (to )?\b", r"\bno action (is )?(needed|required)\b",
        r"\baction required\b", r"\bby (monday|tuesday|wednesday|thursday|friday|\d)",
        r"\bcomplete\b", r"\bconfirm\b", r"\bsign up\b",
    ],
    "where_to_ask": [
        r"#[a-z0-9\-_]+", r"\bquestions?\b.{0,40}\b(to|at|in|via)\b", r"\bask\b",
        r"\breach out to\b", r"\boffice hours\b", r"\bemail\b.{0,20}@",
    ],
}

VOWEL_GROUPS = re.compile(r"[aeiouy]+")


def split_sentences(text: str) -> List[str]:
    """Split body text into sentences on terminal punctuation."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def count_syllables(word: str) -> int:
    """Approximate the syllable count of a single word."""
    word = word.lower().strip("'\"().,;:!?")
    if not word:
        return 0
    groups = VOWEL_GROUPS.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1 and not word.endswith(("le", "ee")):
        count -= 1
    return max(count, 1)


def reading_grade(text: str) -> float:
    """Return an approximate Flesch-Kincaid grade level for the text."""
    sentences = split_sentences(text)
    words = re.findall(r"[A-Za-z']+", text)
    if not sentences or not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    grade = (0.39 * (len(words) / len(sentences))
             + 11.8 * (syllables / len(words)) - 15.59)
    return round(max(grade, 0.0), 1)


def find_terms(text: str, terms: List[str]) -> List[str]:
    """Return which of the given terms appear in the text, case-insensitively."""
    lowered = text.lower()
    return sorted({t for t in terms if t in lowered})


def check_elements(text: str) -> Dict[str, bool]:
    """Test the draft for each of the five required announcement elements."""
    lowered = text.lower()
    return {
        name: any(re.search(pat, lowered) for pat in cues)
        for name, cues in ELEMENT_CUES.items()
    }


def long_sentences(text: str, limit: int = 30) -> List[str]:
    """Return sentences longer than the given word limit."""
    out = []
    for s in split_sentences(text):
        if len(re.findall(r"[A-Za-z']+", s)) > limit:
            out.append(s if len(s) <= 120 else s[:117] + "...")
    return out


def score_draft(data: Dict[str, Any]) -> Dict[str, Any]:
    """Audit an announcement draft and return findings plus a 0-100 score."""
    body = str(data.get("body", "")).strip()
    if not body:
        raise ValueError("input JSON must contain a non-empty 'body' field")

    words = re.findall(r"[A-Za-z']+", body)
    word_count = len(words)
    elements = check_elements(body)
    jargon_hits = find_terms(body, JARGON)
    hedge_hits = find_terms(body, HEDGES)
    grade = reading_grade(body)
    longs = long_sentences(body)
    jargon_density = round(100.0 * len(jargon_hits) / word_count, 2) if word_count else 0.0

    score = 100
    for name, present in elements.items():
        if not present:
            score -= 12
    if grade > 12:
        score -= 10
    elif grade > 10:
        score -= 4
    if jargon_density > 2.0:
        score -= 12
    elif jargon_hits:
        score -= 4
    score -= min(len(hedge_hits) * 3, 9)
    score -= min(len(longs) * 3, 12)
    if word_count > 900:
        score -= 8
    score = max(score, 0)

    fixes: List[str] = []
    labels = {
        "what_changed": "State what is changing and the effective date in the first paragraph.",
        "why": "Give the actual reason, including the constraint that forced the decision.",
        "who_is_affected": "Name the affected groups and say explicitly who is unaffected.",
        "what_to_do": "Give an action with a deadline, or write 'no action needed'.",
        "where_to_ask": "Name a person or channel for questions and a response commitment.",
    }
    for name, present in elements.items():
        if not present:
            fixes.append(labels[name])
    if grade > 12:
        fixes.append(f"Reading grade {grade} is too high; target grade 8-10 for all-staff sends.")
    if jargon_density > 2.0:
        fixes.append(f"Jargon density {jargon_density}% exceeds 2%; replace abstractions with plain verbs.")
    if longs:
        fixes.append(f"{len(longs)} sentence(s) exceed 30 words; split them.")

    return {
        "title": data.get("title", "(untitled)"),
        "audience": data.get("audience", "unspecified"),
        "channel": data.get("channel", "unspecified"),
        "word_count": word_count,
        "sentence_count": len(split_sentences(body)),
        "reading_grade": grade,
        "jargon_density_pct": jargon_density,
        "jargon_terms": jargon_hits,
        "hedging_terms": hedge_hits,
        "long_sentences": longs,
        "elements": elements,
        "score": score,
        "fixes": fixes,
    }


def output(result: Dict[str, Any], fmt: str, min_score: int) -> None:
    """Print the audit result as JSON or human-readable text."""
    if fmt == "json":
        result["passed"] = result["score"] >= min_score
        print(json.dumps(result, indent=2))
        return

    print(f"Announcement audit: {result['title']}")
    print(f"  audience={result['audience']}  channel={result['channel']}")
    print(f"  {result['word_count']} words / {result['sentence_count']} sentences"
          f"  grade={result['reading_grade']}  jargon={result['jargon_density_pct']}%")
    print("\nRequired elements:")
    for name, present in result["elements"].items():
        print(f"  [{'PASS' if present else 'FAIL'}] {name.replace('_', ' ')}")
    if result["jargon_terms"]:
        print(f"\nJargon found: {', '.join(result['jargon_terms'])}")
    if result["hedging_terms"]:
        print(f"Hedging found: {', '.join(result['hedging_terms'])}")
    if result["long_sentences"]:
        print(f"\nSentences over 30 words ({len(result['long_sentences'])}):")
        for s in result["long_sentences"]:
            print(f"  - {s}")
    print(f"\nScore: {result['score']}/100 (threshold {min_score}) -> "
          f"{'PASS' if result['score'] >= min_score else 'REWRITE'}")
    if result["fixes"]:
        print("\nFixes:")
        for f in result["fixes"]:
            print(f"  - {f}")


def main() -> None:
    """Parse arguments, run the audit, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Audit a draft internal announcement for clarity and completeness.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file with title, body, audience, channel")
    parser.add_argument("--min-score", type=int, default=75,
                        help="Pass threshold out of 100 (default: 75)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        result = score_draft(data)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format, args.min_score)


if __name__ == "__main__":
    main()
