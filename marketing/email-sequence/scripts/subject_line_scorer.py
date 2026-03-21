#!/usr/bin/env python3
"""
Email Sequence Subject Line Scorer

Scores email sequence subject lines for open-rate potential,
deliverability risk, and A/B testing readiness. Optimized for
automated/lifecycle emails (welcome, nurture, trial expiration).

Usage:
    python subject_line_scorer.py "Your trial ends tomorrow"
    python subject_line_scorer.py --file subjects.txt --json
"""

import argparse
import json
import re
import sys

SPAM_TRIGGERS = [
    "free", "guarantee", "act now", "limited time", "urgent",
    "click here", "buy now", "order now", "risk-free", "no obligation",
    "100%", "amazing", "incredible", "miracle", "cash bonus",
    "earn extra", "million", "congratulations", "winner",
]

SEQUENCE_TYPE_KEYWORDS = {
    "welcome": ["welcome", "get started", "confirm", "activate", "first steps"],
    "trial_expiration": ["trial", "expires", "ending", "last day", "access", "lose"],
    "nurture": ["how", "guide", "framework", "mistake", "learn", "discover"],
    "re_engagement": ["miss", "away", "back", "update", "new", "changed"],
    "post_purchase": ["thank", "receipt", "invoice", "getting started", "next steps"],
}

MOBILE_TRUNCATION = 35
DESKTOP_TRUNCATION = 50


def detect_sequence_type(subject: str) -> str:
    lower = subject.lower()
    scores = {}
    for stype, keywords in SEQUENCE_TYPE_KEYWORDS.items():
        scores[stype] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


def score_subject(subject: str) -> dict:
    result = {
        "subject_line": subject,
        "char_count": len(subject),
        "word_count": len(subject.split()),
        "detected_type": detect_sequence_type(subject),
        "scores": {},
        "issues": [],
        "tips": [],
    }

    score = 100

    # Length check
    if len(subject) <= MOBILE_TRUNCATION:
        result["scores"]["length"] = 95
        result["tips"].append("Good length: visible on mobile without truncation.")
    elif len(subject) <= DESKTOP_TRUNCATION:
        result["scores"]["length"] = 80
        result["tips"].append("May truncate on mobile. Consider shortening to under 35 chars.")
    elif len(subject) <= 70:
        result["scores"]["length"] = 60
        result["issues"].append("Subject will truncate on most devices.")
        score -= 10
    else:
        result["scores"]["length"] = 30
        result["issues"].append("Subject is too long and will be cut off.")
        score -= 20

    # Spam triggers
    lower = subject.lower()
    found = [w for w in SPAM_TRIGGERS if w in lower]
    if not found:
        result["scores"]["spam_safety"] = 100
    else:
        result["scores"]["spam_safety"] = max(0, 100 - len(found) * 15)
        result["issues"].append(f"Spam triggers found: {', '.join(found)}")
        score -= len(found) * 10

    # Personalization check
    has_personalization = bool(re.search(r"\{|\[name\]|\[company\]", subject, re.IGNORECASE))
    if has_personalization:
        result["scores"]["personalization"] = 90
        result["tips"].append("Personalization token detected -- good for open rates.")
    else:
        result["scores"]["personalization"] = 50
        result["tips"].append("Consider adding personalization ({name}, {company}).")

    # Preview text complement check
    has_colon_setup = ":" in subject or " -- " in subject or " - " in subject
    result["scores"]["structure"] = 80 if has_colon_setup else 65

    # Urgency (appropriate for trial/re-engagement)
    urgency_words = ["last", "ending", "expires", "final", "today", "tomorrow", "hours left"]
    has_urgency = any(w in lower for w in urgency_words)
    if has_urgency and result["detected_type"] in ("trial_expiration", "re_engagement"):
        result["scores"]["urgency_fit"] = 90
        result["tips"].append("Appropriate urgency for this sequence type.")
    elif has_urgency:
        result["scores"]["urgency_fit"] = 60
        result["issues"].append("Urgency language may not fit this sequence type.")
        score -= 5

    # Caps and punctuation
    if re.search(r"\b[A-Z]{4,}\b", subject):
        non_acronyms = [w for w in re.findall(r"\b[A-Z]{4,}\b", subject) if w not in ("SALE", "FREE", "RSVP")]
        if non_acronyms:
            result["issues"].append(f"ALL CAPS words: {', '.join(non_acronyms)}")
            score -= 10
    if subject.count("!") > 1:
        result["issues"].append("Multiple exclamation marks reduce deliverability.")
        score -= 10

    # A/B test readiness
    words = subject.split()
    is_testable = 3 <= len(words) <= 8 and len(subject) <= 50
    result["ab_test_ready"] = is_testable
    if is_testable:
        result["tips"].append("Good length for A/B testing (recommend 3+ variants per email).")

    result["overall_score"] = max(0, min(100, score))
    result["grade"] = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"

    return result


def format_human(results: list) -> str:
    lines = ["\n" + "=" * 55, "  EMAIL SEQUENCE SUBJECT LINE SCORER", "=" * 55]
    for r in results:
        lines.append(f"\n  \"{r['subject_line']}\"")
        lines.append(f"  Score: {r['overall_score']}/100 ({r['grade']}) | Type: {r['detected_type']} | {r['char_count']} chars")
        if r["issues"]:
            for i in r["issues"]:
                lines.append(f"    ! {i}")
        if r["tips"]:
            for t in r["tips"]:
                lines.append(f"    + {t}")
        lines.append(f"    A/B Ready: {'Yes' if r['ab_test_ready'] else 'No (adjust length)'}")
        lines.append("-" * 55)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score email sequence subject lines.")
    parser.add_argument("subject", nargs="?", help="Subject line to score")
    parser.add_argument("--file", "-f", help="File with one subject per line")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    subjects = []
    if args.file:
        with open(args.file) as f:
            subjects = [l.strip() for l in f if l.strip()]
    elif args.subject:
        subjects = [args.subject]
    else:
        parser.print_help()
        sys.exit(1)

    results = [score_subject(s) for s in subjects]
    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
