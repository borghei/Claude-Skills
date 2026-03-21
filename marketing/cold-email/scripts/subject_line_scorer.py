#!/usr/bin/env python3
"""
Subject Line Scorer for Cold Email

Scores cold email subject lines on deliverability, open-rate potential,
and spam risk using deterministic heuristics. No API calls.

Usage:
    python subject_line_scorer.py "your subject line here"
    python subject_line_scorer.py "your subject line here" --json
    python subject_line_scorer.py --file subjects.txt
    python subject_line_scorer.py --file subjects.txt --json
"""

import argparse
import json
import re
import sys

# --- Spam trigger words (weighted) ---
SPAM_TRIGGERS_HIGH = [
    "free", "guarantee", "act now", "limited time", "urgent", "winner",
    "congratulations", "click here", "buy now", "order now", "risk-free",
    "no obligation", "100%", "amazing", "incredible", "miracle",
    "once in a lifetime", "exclusive deal", "cash", "bonus",
]
SPAM_TRIGGERS_MEDIUM = [
    "discount", "offer", "deal", "save", "sale", "lowest price",
    "bargain", "cheap", "earn", "profit", "income", "opportunity",
    "subscribe", "trial", "promotion", "special", "new", "announcing",
]

# --- Patterns that kill opens ---
KILL_PATTERNS = {
    "all_caps_word": re.compile(r"\b[A-Z]{3,}\b"),
    "exclamation": re.compile(r"!"),
    "question_ad": re.compile(r"^(Are you|Do you|Have you|Is your|Can you)\b", re.IGNORECASE),
    "emoji": re.compile(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]"),
    "fake_re_fwd": re.compile(r"^(re:|fwd?:)\s", re.IGNORECASE),
    "multiple_punctuation": re.compile(r"[!?]{2,}|\.{3,}"),
    "dollar_sign": re.compile(r"\$\d"),
    "percent_off": re.compile(r"\d+%\s*(off|discount|savings)", re.IGNORECASE),
}

# --- Positive patterns ---
POSITIVE_PATTERNS = {
    "short_two_three_words": lambda s: 2 <= len(s.split()) <= 4,
    "lowercase_natural": lambda s: s == s.lower() or (s[0].isupper() and s[1:] == s[1:].lower()),
    "personalization_token": lambda s: bool(re.search(r"\{|{{|\[name\]|\[company\]", s, re.IGNORECASE)),
    "specific_trigger": lambda s: bool(re.search(r"(your |re: |about )", s, re.IGNORECASE)),
    "question_format_good": lambda s: s.endswith("?") and len(s.split()) <= 5,
}


def score_subject_line(subject: str) -> dict:
    """Score a subject line on multiple dimensions (0-100)."""
    results = {
        "subject_line": subject,
        "length_chars": len(subject),
        "word_count": len(subject.split()),
        "scores": {},
        "flags": [],
        "suggestions": [],
    }

    total_score = 100.0

    # --- Length scoring ---
    char_len = len(subject)
    if char_len == 0:
        return {**results, "overall_score": 0, "grade": "F", "flags": ["Empty subject line"]}

    if char_len <= 5:
        length_score = 40
        results["suggestions"].append("Subject line may be too short to convey meaning.")
    elif 6 <= char_len <= 20:
        length_score = 95
    elif 21 <= char_len <= 40:
        length_score = 85
    elif 41 <= char_len <= 50:
        length_score = 70
    elif 51 <= char_len <= 60:
        length_score = 55
        results["suggestions"].append("Subject may truncate on mobile (35-45 chars visible).")
    else:
        length_score = 35
        results["suggestions"].append("Subject line is too long. Keep under 50 characters.")

    results["scores"]["length"] = length_score

    # --- Spam trigger scoring ---
    lower = subject.lower()
    spam_score = 100
    found_spam = []
    for word in SPAM_TRIGGERS_HIGH:
        if word in lower:
            spam_score -= 15
            found_spam.append(f"'{word}' (high-risk)")
    for word in SPAM_TRIGGERS_MEDIUM:
        if word in lower:
            spam_score -= 8
            found_spam.append(f"'{word}' (medium-risk)")
    spam_score = max(0, spam_score)
    results["scores"]["spam_risk"] = spam_score
    if found_spam:
        results["flags"].append(f"Spam trigger words detected: {', '.join(found_spam)}")

    # --- Kill pattern scoring ---
    pattern_score = 100
    for name, pattern in KILL_PATTERNS.items():
        if isinstance(pattern, type(re.compile(""))):
            if pattern.search(subject):
                deduction = 15
                if name == "fake_re_fwd":
                    deduction = 25
                    results["flags"].append("Fake Re:/Fwd: prefix destroys trust.")
                elif name == "all_caps_word":
                    caps_words = pattern.findall(subject)
                    # Allow common acronyms
                    non_acronyms = [w for w in caps_words if w not in ("CEO", "CTO", "CMO", "CRO", "VP", "API", "SaaS", "B2B", "B2C", "AI", "ML", "ROI", "KPI", "CRM", "ERP", "SDK", "PM")]
                    if non_acronyms:
                        results["flags"].append(f"ALL CAPS words detected: {', '.join(non_acronyms)}")
                    else:
                        deduction = 0
                elif name == "emoji":
                    results["flags"].append("Emojis in cold email subject lines reduce open rates.")
                elif name == "exclamation":
                    results["flags"].append("Exclamation marks trigger spam filters.")
                elif name == "question_ad":
                    results["flags"].append("Question format sounds like an ad. Try a statement instead.")
                elif name == "multiple_punctuation":
                    results["flags"].append("Excessive punctuation triggers spam filters.")
                elif name == "dollar_sign":
                    results["flags"].append("Dollar amounts in subject lines trigger spam filters.")
                elif name == "percent_off":
                    results["flags"].append("Percentage discounts in subject lines look like spam.")
                pattern_score -= deduction

    pattern_score = max(0, pattern_score)
    results["scores"]["pattern_quality"] = pattern_score

    # --- Positive signal scoring ---
    positive_score = 50  # baseline
    for name, check in POSITIVE_PATTERNS.items():
        try:
            if check(subject):
                positive_score += 10
                if name == "short_two_three_words":
                    results["suggestions"].append("Good: Short subject lines look like internal emails.")
                elif name == "personalization_token":
                    results["suggestions"].append("Good: Personalization tokens increase open rates.")
        except Exception:
            pass
    positive_score = min(100, positive_score)
    results["scores"]["positive_signals"] = positive_score

    # --- Calculate overall ---
    weights = {
        "length": 0.20,
        "spam_risk": 0.30,
        "pattern_quality": 0.30,
        "positive_signals": 0.20,
    }
    overall = sum(results["scores"][k] * weights[k] for k in weights)
    results["overall_score"] = round(overall, 1)

    # Grade
    if overall >= 85:
        results["grade"] = "A"
    elif overall >= 70:
        results["grade"] = "B"
    elif overall >= 55:
        results["grade"] = "C"
    elif overall >= 40:
        results["grade"] = "D"
    else:
        results["grade"] = "F"

    if not results["suggestions"]:
        results["suggestions"].append("Subject line looks solid. Test with A/B variants.")

    return results


def format_human(result: dict) -> str:
    """Format result for human reading."""
    lines = []
    lines.append(f"\n  Subject: \"{result['subject_line']}\"")
    lines.append(f"  Overall Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    lines.append(f"  Length: {result['length_chars']} chars, {result['word_count']} words")
    lines.append("")
    lines.append("  Component Scores:")
    for k, v in result["scores"].items():
        label = k.replace("_", " ").title()
        lines.append(f"    {label}: {v}/100")
    if result["flags"]:
        lines.append("")
        lines.append("  Warnings:")
        for f in result["flags"]:
            lines.append(f"    - {f}")
    if result["suggestions"]:
        lines.append("")
        lines.append("  Suggestions:")
        for s in result["suggestions"]:
            lines.append(f"    + {s}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score cold email subject lines for deliverability and open-rate potential."
    )
    parser.add_argument("subject", nargs="?", help="Subject line to score")
    parser.add_argument("--file", "-f", help="File with one subject line per line")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    args = parser.parse_args()

    subjects = []
    if args.file:
        try:
            with open(args.file, "r") as fh:
                subjects = [line.strip() for line in fh if line.strip()]
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.subject:
        subjects = [args.subject]
    else:
        parser.print_help()
        sys.exit(1)

    results = [score_subject_line(s) for s in subjects]

    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print("\n" + "=" * 60)
        print("  COLD EMAIL SUBJECT LINE SCORER")
        print("=" * 60)
        for r in results:
            print(format_human(r))
            print("-" * 60)


if __name__ == "__main__":
    main()
