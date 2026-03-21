#!/usr/bin/env python3
"""
CTA Optimizer

Analyzes and scores call-to-action text for strength,
friction level, and conversion potential.

Usage:
    python cta_optimizer.py "Start my free trial"
    python cta_optimizer.py --file ctas.txt --json
"""

import argparse
import json
import re
import sys

STRONG_CTAS = {
    "start": 90, "get": 85, "create": 85, "build": 85, "try": 80,
    "discover": 80, "claim": 85, "unlock": 80, "see": 75, "join": 80,
    "book": 75, "download": 75, "access": 80, "activate": 85,
}

WEAK_CTAS = {
    "submit": 30, "click here": 25, "click": 30, "send": 35,
    "go": 40, "enter": 35, "continue": 40,
}

MODERATE_CTAS = {
    "learn more": 50, "sign up": 60, "get started": 65,
    "contact us": 45, "request": 55, "register": 55,
    "subscribe": 55, "buy now": 60, "order": 55,
}

FRICTION_REDUCERS = [
    "free", "no credit card", "no card", "cancel anytime",
    "2 minutes", "instant", "no commitment", "risk-free",
    "money-back", "guarantee", "try", "no obligation",
]

OWNERSHIP_WORDS = ["my", "your", "our"]


def score_cta(cta: str) -> dict:
    lower = cta.lower().strip()
    words = lower.split()
    result = {
        "cta": cta,
        "word_count": len(words),
        "scores": {},
        "analysis": {},
        "improvements": [],
    }

    # Action strength
    first_word = words[0] if words else ""
    action_score = 50

    if first_word in STRONG_CTAS:
        action_score = STRONG_CTAS[first_word]
        result["analysis"]["action_strength"] = "strong"
    elif lower in WEAK_CTAS or first_word in WEAK_CTAS:
        action_score = WEAK_CTAS.get(lower, WEAK_CTAS.get(first_word, 35))
        result["analysis"]["action_strength"] = "weak"
        result["improvements"].append(f"Replace '{first_word}' with a stronger verb (start, get, create, build).")
    elif lower in MODERATE_CTAS or first_word in MODERATE_CTAS:
        action_score = MODERATE_CTAS.get(lower, MODERATE_CTAS.get(first_word, 55))
        result["analysis"]["action_strength"] = "moderate"
    else:
        action_score = 55
        result["analysis"]["action_strength"] = "unknown"

    result["scores"]["action_strength"] = action_score

    # Specificity -- does it tell them what they get?
    has_what = len(words) > 2
    has_benefit_word = bool(re.search(r"(trial|demo|guide|report|analysis|dashboard|account|plan|checklist|template)", lower))

    specificity = 40
    if has_what and has_benefit_word:
        specificity = 90
        result["analysis"]["specificity"] = "high -- tells user what they receive"
    elif has_what:
        specificity = 65
        result["analysis"]["specificity"] = "medium -- action but vague outcome"
        result["improvements"].append("Add what they get: 'Start my free trial' > 'Start'")
    else:
        specificity = 35
        result["analysis"]["specificity"] = "low -- too generic"
        result["improvements"].append("Expand CTA: [Action Verb] + [What They Get]")

    result["scores"]["specificity"] = specificity

    # Ownership language
    has_ownership = any(w in words for w in OWNERSHIP_WORDS)
    if has_ownership:
        result["scores"]["ownership"] = 85
        result["analysis"]["ownership"] = "Uses ownership language ('my/your') -- increases click rate"
    else:
        result["scores"]["ownership"] = 50
        result["improvements"].append("Try ownership: 'Start free trial' -> 'Start my free trial'")

    # Friction assessment
    friction_signals = [f for f in FRICTION_REDUCERS if f in lower]
    if friction_signals:
        result["scores"]["friction"] = 90
        result["analysis"]["friction_level"] = "low -- friction reducers present"
    elif any(w in lower for w in ["buy", "purchase", "pay", "subscribe", "commit"]):
        result["scores"]["friction"] = 35
        result["analysis"]["friction_level"] = "high -- purchase commitment"
    else:
        result["scores"]["friction"] = 60
        result["analysis"]["friction_level"] = "medium"
        result["improvements"].append("Add supporting text below CTA: 'No credit card required' or 'Free for 14 days'")

    # Length
    if 3 <= len(words) <= 6:
        result["scores"]["length"] = 90
    elif len(words) <= 2:
        result["scores"]["length"] = 55
        result["improvements"].append("CTA is too short. Aim for 3-6 words.")
    else:
        result["scores"]["length"] = 60
        result["improvements"].append("CTA is long. Trim to 3-6 words.")

    # Overall
    weights = {"action_strength": 0.30, "specificity": 0.25, "ownership": 0.15, "friction": 0.15, "length": 0.15}
    overall = sum(result["scores"].get(k, 50) * w for k, w in weights.items())
    result["overall_score"] = round(overall)
    result["grade"] = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"

    if not result["improvements"]:
        result["improvements"].append("Strong CTA. A/B test against 2-3 variants.")

    return result


def format_human(results: list) -> str:
    lines = ["\n" + "=" * 55, "  CTA OPTIMIZER", "=" * 55]
    for r in results:
        lines.append(f"\n  \"{r['cta']}\"")
        lines.append(f"  Score: {r['overall_score']}/100 ({r['grade']})")
        for k, v in r["analysis"].items():
            lines.append(f"    {k.replace('_', ' ').title()}: {v}")
        for imp in r["improvements"]:
            lines.append(f"    > {imp}")
        lines.append("-" * 55)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score and optimize CTA copy.")
    parser.add_argument("cta", nargs="?")
    parser.add_argument("--file", "-f")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    ctas = []
    if args.file:
        with open(args.file) as f:
            ctas = [l.strip() for l in f if l.strip()]
    elif args.cta:
        ctas = [args.cta]
    else:
        parser.print_help()
        sys.exit(1)

    results = [score_cta(c) for c in ctas]
    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
