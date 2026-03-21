#!/usr/bin/env python3
"""
Style Consistency Checker

Checks content for style consistency including Oxford comma usage,
heading capitalization, contraction consistency, number formatting,
punctuation patterns, and brand name formatting across one or more files.

Usage:
    python style_checker.py --file article.md
    python style_checker.py --files doc1.md doc2.md doc3.md --json
    python style_checker.py --file article.md --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path


def check_oxford_comma(text):
    """Check Oxford comma consistency."""
    # Pattern: X, Y, and Z (Oxford) vs X, Y and Z (no Oxford)
    with_oxford = len(re.findall(r'\w+,\s+\w+,\s+and\s+\w+', text))
    without_oxford = len(re.findall(r'\w+,\s+\w+\s+and\s+\w+', text)) - with_oxford

    if with_oxford > 0 and without_oxford > 0:
        return {
            "consistent": False,
            "with_oxford": with_oxford,
            "without_oxford": without_oxford,
            "detail": f"Mixed: {with_oxford} with Oxford comma, {without_oxford} without",
        }
    elif with_oxford > 0:
        return {"consistent": True, "style": "Oxford comma used", "count": with_oxford}
    elif without_oxford > 0:
        return {"consistent": True, "style": "No Oxford comma", "count": without_oxford}
    return {"consistent": True, "style": "No instances to check", "count": 0}


def check_heading_case(text):
    """Check heading capitalization consistency."""
    headings = re.findall(r'^#{1,6}\s+(.+)', text, re.MULTILINE)
    if len(headings) < 2:
        return {"consistent": True, "detail": "Not enough headings to check"}

    title_case = 0
    sentence_case = 0

    for h in headings:
        words = h.split()
        if len(words) < 2:
            continue
        # Check if non-first words are capitalized (title case signal)
        caps = sum(1 for w in words[1:] if w[0].isupper() and w.lower() not in
                   ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        if caps > len(words[1:]) * 0.5:
            title_case += 1
        else:
            sentence_case += 1

    if title_case > 0 and sentence_case > 0:
        return {
            "consistent": False,
            "title_case": title_case,
            "sentence_case": sentence_case,
            "detail": f"Mixed: {title_case} Title Case, {sentence_case} sentence case",
        }
    return {
        "consistent": True,
        "style": "Title Case" if title_case > sentence_case else "Sentence case",
    }


def check_contractions(text):
    """Check contraction consistency."""
    contractions = len(re.findall(r"\b\w+'(t|s|re|ve|ll|d|m)\b", text))
    full_forms = len(re.findall(
        r'\b(do not|does not|is not|are not|was not|were not|will not|'
        r'would not|could not|should not|cannot|have not|has not|'
        r'it is|he is|she is|that is|there is|we are|they are|you are)\b',
        text, re.IGNORECASE
    ))

    if contractions > 0 and full_forms > 0:
        return {
            "consistent": False,
            "contractions": contractions,
            "full_forms": full_forms,
            "detail": f"Mixed: {contractions} contractions, {full_forms} full forms",
        }
    return {
        "consistent": True,
        "style": "Contractions" if contractions > full_forms else "Full forms",
        "contractions": contractions,
        "full_forms": full_forms,
    }


def check_number_format(text):
    """Check number formatting consistency."""
    # Spelled out small numbers vs digits
    spelled = len(re.findall(r'\b(one|two|three|four|five|six|seven|eight|nine)\b', text, re.I))
    digits_small = len(re.findall(r'\b[1-9]\b', text))  # Single digits as numbers

    issues = []
    if spelled > 0 and digits_small > 0:
        issues.append(f"Mixed: {spelled} spelled out, {digits_small} as digits for 1-9")

    return {
        "consistent": len(issues) == 0,
        "spelled_small": spelled,
        "digit_small": digits_small,
        "issues": issues,
    }


def check_list_punctuation(text):
    """Check bullet list punctuation consistency."""
    list_items = re.findall(r'^\s*[\-\*]\s+(.+)$', text, re.MULTILINE)
    if len(list_items) < 3:
        return {"consistent": True, "detail": "Not enough list items"}

    with_period = sum(1 for item in list_items if item.strip().endswith('.'))
    without_period = len(list_items) - with_period

    if with_period > 0 and without_period > 0:
        return {
            "consistent": False,
            "with_period": with_period,
            "without_period": without_period,
            "detail": f"Mixed: {with_period} with period, {without_period} without",
        }
    return {
        "consistent": True,
        "style": "With periods" if with_period > without_period else "Without periods",
    }


def check_quote_style(text):
    """Check quotation mark consistency."""
    curly = len(re.findall(r'[\u201c\u201d\u2018\u2019]', text))
    straight = len(re.findall(r'(?<!\w)["\'](?!\w)', text))

    if curly > 0 and straight > 0:
        return {
            "consistent": False,
            "curly": curly,
            "straight": straight,
            "detail": f"Mixed: {curly} curly quotes, {straight} straight quotes",
        }
    return {"consistent": True, "style": "Curly" if curly > straight else "Straight"}


def check_dash_usage(text):
    """Check dash consistency (em-dash, en-dash, hyphen)."""
    em_proper = text.count('\u2014')  # —
    em_double = len(re.findall(r'(?<!\-)\-\-(?!\-)', text))  # --
    en_dash = text.count('\u2013')  # –
    spaced_em = len(re.findall(r'\s\u2014\s', text))
    unspaced_em = em_proper - spaced_em

    issues = []
    if em_proper > 0 and em_double > 0:
        issues.append(f"Mixed em-dash styles: {em_proper} proper (—), {em_double} double-hyphen (--)")
    if spaced_em > 0 and unspaced_em > 0:
        issues.append(f"Mixed em-dash spacing: {spaced_em} spaced, {unspaced_em} unspaced")

    return {
        "consistent": len(issues) == 0,
        "em_dashes": em_proper,
        "double_hyphens": em_double,
        "issues": issues,
    }


def analyze_file(filepath):
    """Run all style checks on a file."""
    text = filepath.read_text(encoding="utf-8", errors="replace")

    checks = {
        "oxford_comma": check_oxford_comma(text),
        "heading_case": check_heading_case(text),
        "contractions": check_contractions(text),
        "number_format": check_number_format(text),
        "list_punctuation": check_list_punctuation(text),
        "quote_style": check_quote_style(text),
        "dash_usage": check_dash_usage(text),
    }

    inconsistencies = sum(1 for c in checks.values() if not c.get("consistent", True))
    score = round((1 - inconsistencies / len(checks)) * 100)

    return {
        "file": str(filepath),
        "word_count": len(text.split()),
        "score": score,
        "inconsistencies": inconsistencies,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Check style consistency")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Single file to check")
    group.add_argument("--files", nargs="+", help="Multiple files to check")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    files = [Path(args.file)] if args.file else [Path(f) for f in args.files]
    results = []

    for fp in files:
        if not fp.exists():
            print(f"Warning: {fp} not found, skipping", file=sys.stderr)
            continue
        results.append(analyze_file(fp))

    if args.json:
        print(json.dumps({"files": results, "total": len(results)}, indent=2))
    else:
        for r in results:
            print(f"\n{'='*55}")
            print(f"  STYLE CHECK: {r['file']}")
            print(f"  Score: {r['score']}/100 | Inconsistencies: {r['inconsistencies']}")
            print(f"{'='*55}")

            for name, check in r["checks"].items():
                status = "PASS" if check.get("consistent", True) else "FAIL"
                detail = check.get("detail", check.get("style", ""))
                issues = check.get("issues", [])

                print(f"  [{status}] {name}: {detail}")
                if args.verbose and issues:
                    for issue in issues:
                        print(f"         {issue}")

        if len(results) > 1:
            avg = round(sum(r["score"] for r in results) / len(results))
            print(f"\n  Average consistency: {avg}/100 across {len(results)} files")
        print()


if __name__ == "__main__":
    main()
