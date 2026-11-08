#!/usr/bin/env python3
"""
Landing Page CTA Analyzer

Analyzes CTA placement, copy strength, friction level,
and conversion optimization on landing pages.

A CTA counts as above the fold when at most FOLD_WORDS visible words come before
it (the first screen of a landing page holds roughly that much copy).

Usage:
    python cta_analyzer.py page.html
    python cta_analyzer.py page.html --format json

Exit codes: 0 no blocking issue, 1 no CTA, no CTA above the fold or a vague
CTA label, 2 missing, unreadable or non-HTML input.
"""

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

BUTTON_PATTERN = re.compile(r'<(button|a)\b[^>]*?(?:class\s*=\s*["\']?[^"\'>]*\b(?:btn|button|cta)|role\s*=\s*["\']?button)[^>]*>(.*?)</\1>', re.IGNORECASE | re.DOTALL)
NON_VISIBLE = re.compile(r"<(script|style|template|noscript|head)\b.*?</\1\s*>|<!--.*?-->", re.IGNORECASE | re.DOTALL)
FOLD_WORDS = 60
LINK_CTA_PATTERN = re.compile(r'<a[^>]+href[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")

STRONG_VERBS = {"start", "get", "create", "build", "try", "claim", "join", "book", "download", "access", "order", "reserve", "see", "compare"}
# Labels that name nothing the visitor gets; they score as vague whatever the first word is.
VAGUE_LABELS = {"learn more", "read more", "discover", "discover more", "explore", "explore more",
                "click here", "more", "find out more", "see more", "submit", "unlock", "unlock now"}
WEAK_VERBS = {"submit", "click", "send", "go", "enter", "continue"}
FRICTION_REDUCERS = ["no credit card", "free", "cancel anytime", "no commitment", "money-back", "risk-free", "2 minutes", "instant"]


def label_text(fragment: str) -> str:
    """Visible label of a button or link: tags dropped, entities decoded, whitespace collapsed."""
    return " ".join(unescape(HTML_TAG.sub(" ", fragment)).split())


def extract_ctas(html: str) -> list:
    """Buttons and CTA-like links, each once, in page order (head, scripts and styles ignored)."""
    body = NON_VISIBLE.sub(lambda m: " " * len(m.group(0)), html)  # same length, so offsets still match
    ctas, seen = [], set()
    for match in BUTTON_PATTERN.finditer(body):
        text = label_text(match.group(2))
        if text and len(text) < 60:
            seen.add(match.start())
            ctas.append({"text": text, "position_char": match.start(), "type": "button"})
    for match in LINK_CTA_PATTERN.finditer(body):  # a link already found as a button is not counted twice
        text, tag = label_text(match.group(1)), match.group(0).lower()
        if match.start() not in seen and text and len(text) < 60 and \
                any(kw in tag for kw in ["btn", "button", "cta", "trial", "demo", "signup", "start"]):
            ctas.append({"text": text, "position_char": match.start(), "type": "link"})
    ctas.sort(key=lambda c: c["position_char"])
    for c in ctas:
        c["words_before"] = len(HTML_TAG.sub(" ", body[:c["position_char"]]).split())
    return ctas


def analyze_cta(cta_text: str) -> dict:
    lower = cta_text.lower()
    words = lower.split()
    first_word = words[0] if words else ""

    strength = "moderate"
    label = " ".join(re.sub(r"[^\w' ]+", " ", lower).split())
    if label in VAGUE_LABELS:
        strength = "vague"
    elif first_word in STRONG_VERBS:
        strength = "strong"
    elif first_word in WEAK_VERBS:
        strength = "weak"

    has_ownership = any(w in words for w in ["my", "your"])
    has_benefit = len(words) > 2

    score = 50
    if strength == "strong":
        score += 25
    elif strength == "weak":
        score -= 15
    elif strength == "vague":
        score -= 30
    if has_ownership:
        score += 10
    if has_benefit:
        score += 15

    return {
        "text": cta_text,
        "strength": strength,
        "has_ownership_language": has_ownership,
        "describes_what_you_get": has_benefit,
        "word_count": len(words),
        "score": min(100, max(0, score)),
    }


def analyze_page(html: str) -> dict:
    ctas = extract_ctas(html)
    total_words = max(1, len(HTML_TAG.sub(" ", NON_VISIBLE.sub(" ", html)).split()))

    # Check for friction reducers near CTAs
    lower_html = html.lower()
    friction_found = [f for f in FRICTION_REDUCERS if f in lower_html]

    # Estimate CTA positions (early = above fold, middle, late)
    cta_analyses = []
    for cta in ctas:
        position_pct = cta["words_before"] / total_words * 100
        zone = "above_fold" if cta["words_before"] <= FOLD_WORDS else "mid_page" if position_pct < 60 else "bottom"
        analysis = analyze_cta(cta["text"])
        analysis["zone"] = zone
        analysis["position_pct"] = round(position_pct, 1)
        cta_analyses.append(analysis)

    # Scoring
    issues = []
    recommendations = []
    score = 50

    # CTA count
    if len(ctas) == 0:
        issues.append("No CTAs found on the page.")
        score -= 30
    elif len(ctas) == 1:
        issues.append("Only 1 CTA. Best practice: 2-3 CTAs throughout the page.")
        score -= 10
    elif 2 <= len(ctas) <= 4:
        score += 15
    else:
        recommendations.append(f"{len(ctas)} CTAs found -- ensure they don't compete. All should drive the same action.")

    # Above fold CTA
    above_fold = [c for c in cta_analyses if c["zone"] == "above_fold"]
    if above_fold:
        score += 15
    else:
        issues.append("No CTA above the fold. Primary CTA must be visible without scrolling.")
        score -= 15

    # CTA consistency
    cta_texts = [c["text"].lower() for c in cta_analyses]
    unique_texts = set(cta_texts)
    if len(unique_texts) > 2 and len(ctas) > 1:
        issues.append(f"{len(unique_texts)} different CTA texts. Use consistent CTAs driving one action.")
        score -= 10

    # Friction reducers
    if friction_found:
        score += 10
        recommendations.append(f"Good: Friction reducers detected: {', '.join(friction_found)}")
    else:
        recommendations.append("Add friction reducers near CTAs: 'No credit card required', 'Free for 14 days', etc.")
        score -= 5

    # CTA strength
    strong_ctas = [c for c in cta_analyses if c["strength"] == "strong"]
    vague_ctas = [c for c in cta_analyses if c["strength"] == "vague"]
    if vague_ctas:
        issues.append(f"Vague CTA label: {', '.join([c['text'] for c in vague_ctas][:3])}")
        recommendations.append(f"Rename vague CTAs to a verb plus what the visitor gets: {', '.join([c['text'] for c in vague_ctas][:3])}")
    weak_ctas = [c for c in cta_analyses if c["strength"] == "weak"]
    if weak_ctas:
        recommendations.append(f"Strengthen weak CTAs: {', '.join([c['text'] for c in weak_ctas][:3])}")

    score = max(0, min(100, score))

    return {
        "total_ctas": len(ctas),
        "score": score,
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F",
        "ctas": cta_analyses,
        "friction_reducers_found": friction_found,
        "placement": {
            "above_fold": len(above_fold),
            "mid_page": len([c for c in cta_analyses if c["zone"] == "mid_page"]),
            "bottom": len([c for c in cta_analyses if c["zone"] == "bottom"]),
        },
        "issues": issues,
        "recommendations": recommendations,
        "blocking": bool(not ctas or not above_fold or vague_ctas),
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  LANDING PAGE CTA ANALYZER", "=" * 55]
    lines.append(f"\n  Score: {result['score']}/100 ({result['grade']}) | CTAs Found: {result['total_ctas']}")
    p = result["placement"]
    lines.append(f"  Placement: Above-fold: {p['above_fold']} | Mid-page: {p['mid_page']} | Bottom: {p['bottom']}")

    if result["ctas"]:
        lines.append(f"\n  CTA Analysis:")
        for c in result["ctas"]:
            lines.append(f"    \"{c['text']}\" | {c['strength']} | {c['zone']} ({c['position_pct']}%) | Score: {c['score']}")

    if result["issues"]:
        lines.append(f"\n  Issues:")
        for i in result["issues"]:
            lines.append(f"    ! {i}")

    lines.append(f"\n  Recommendations:")
    for r in result["recommendations"]:
        lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def load(path: str) -> str:
    """Read an HTML page; exit 2 on a missing, unreadable or non-HTML file."""
    try:
        html = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not re.search(r"<(html|body|main|section|div|h1|p)\b", html, re.IGNORECASE):
        print(f"Error: {path} does not look like an HTML page", file=sys.stderr)
        sys.exit(2)
    return html


def main():
    parser = argparse.ArgumentParser(description="Analyze CTA placement and quality on landing pages.")
    parser.add_argument("file", help="HTML file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="same as --format json")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    if args.format == "json":
        args.json_output = True

    html = load(args.file)

    result = analyze_page(html)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    sys.exit(1 if result["blocking"] else 0)


if __name__ == "__main__":
    main()
