#!/usr/bin/env python3
"""
Investor Update Validator — score a draft monthly investor update against a rubric.

Usage:
    python investor_update_validator.py update.md
    python investor_update_validator.py update.md --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Each rule: (label, pattern flags, weight, hint)
RULES = [
    {
        "label": "Has highlights / wins section",
        "patterns": [r"\bhighlight", r"\bwins?\b", r"\bgood news\b"],
        "weight": 10,
        "hint": "Open with what went well — concrete and specific.",
    },
    {
        "label": "Has lowlights / challenges / risks section",
        "patterns": [r"\b(lowlight|challenge|risk|concern|setback|miss(ed)?|behind)\b"],
        "weight": 15,
        "hint": "Be transparent about what isn't going well. Updates that are all-good-news lose investor trust.",
    },
    {
        "label": "Has metrics with numbers",
        "patterns": [
            r"\$[\d,]+",
            r"\b\d+(\.\d+)?%",
            r"\bMRR\b|\bARR\b|\bGMV\b|\bDAU\b|\bMAU\b|\bNPS\b|\bCAC\b|\bLTV\b",
            r"\bgrowth\b.*\d",
        ],
        "weight": 15,
        "hint": "Include hard numbers — MRR/ARR, growth rate, key product metric, runway months.",
    },
    {
        "label": "Has runway / cash position",
        "patterns": [r"\brunway\b", r"\bcash\b", r"\bburn\b", r"\bmonths? (?:of )?(?:runway|cash)\b"],
        "weight": 10,
        "hint": "State runway in months (or 'profitable' if applicable). Investors expect this.",
    },
    {
        "label": "Has asks / how can investors help",
        "patterns": [r"\b(asks?|how (?:you|investors?) can help|introductions|intros)\b"],
        "weight": 15,
        "hint": "Be specific. 'Help with hiring' is too vague; 'Intros to senior backend engineers in NYC who've shipped a billing system' is actionable.",
    },
    {
        "label": "Has team / hiring update",
        "patterns": [r"\b(team|hiring|hires?|headcount|departures?|new (?:hire|joiner))\b"],
        "weight": 10,
        "hint": "Cover headcount changes, key hires, key departures.",
    },
    {
        "label": "Has product / shipped section",
        "patterns": [r"\b(product|shipped|launched|released|roadmap|features?)\b"],
        "weight": 10,
        "hint": "What did you ship? What's coming next?",
    },
    {
        "label": "Has sales / GTM update",
        "patterns": [r"\b(sales|customers?|pipeline|new logos?|gtm|revenue|deals?)\b"],
        "weight": 10,
        "hint": "Cover top-line: new customers, key expansions, churn if relevant.",
    },
    {
        "label": "Has explicit asks list (numbered or bulleted)",
        "patterns": [r"^[\s]*[0-9]+[.)]\s.*help", r"^[\s]*[-*]\s.*(?:intro|help|advice|hire)", r"^\s*ask\s*\d+"],
        "weight": 5,
        "hint": "Make asks scan-able — numbered or bulleted, not buried in prose.",
    },
]

# Anti-patterns — patterns that lower the score
ANTI_PATTERNS = [
    {
        "label": "All-positive update (no negative signal detected)",
        "trigger": lambda text: not re.search(
            r"\b(challenge|risk|concern|setback|miss(ed)?|behind|slow|short|tough|hard|bad)\b",
            text.lower(),
        ),
        "penalty": 15,
        "hint": "Updates that read all-positive are red flags; investors trust transparent founders more.",
    },
    {
        "label": "No specific asks — only vague 'let us know if you can help'",
        "trigger": lambda text: re.search(r"\b(asks?|help)\b", text.lower())
        and not re.search(r"\bintro(?:duction)?s?\s+to\b", text.lower()),
        "penalty": 10,
        "hint": "Asks that aren't specific produce no help. Be specific.",
    },
    {
        "label": "Update is over 1500 words",
        "trigger": lambda text: len(re.findall(r"\w+", text)) > 1500,
        "penalty": 10,
        "hint": "Most investors won't read past 600-800 words. Trim.",
    },
]


def validate(text):
    score = 0
    matched = []
    missing = []
    for rule in RULES:
        if any(re.search(p, text, re.IGNORECASE | re.MULTILINE) for p in rule["patterns"]):
            score += rule["weight"]
            matched.append(rule["label"])
        else:
            missing.append({"label": rule["label"], "hint": rule["hint"], "weight": rule["weight"]})

    penalties = []
    for ap in ANTI_PATTERNS:
        if ap["trigger"](text):
            score -= ap["penalty"]
            penalties.append({"label": ap["label"], "penalty": ap["penalty"], "hint": ap["hint"]})

    score = max(0, min(100, score))
    word_count = len(re.findall(r"\w+", text))

    return {
        "score": score,
        "word_count": word_count,
        "matched": matched,
        "missing": missing,
        "penalties": penalties,
    }


def render_human(result):
    lines = [f"Investor Update Validation"]
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Score: {result['score']} / 100")
    lines.append(f"Word count: {result['word_count']}")
    lines.append("")
    if result["matched"]:
        lines.append(f"Sections present ({len(result['matched'])}):")
        for m in result["matched"]:
            lines.append(f"  PASS  {m}")
        lines.append("")
    if result["missing"]:
        lines.append(f"Missing or weak sections ({len(result['missing'])}):")
        for m in result["missing"]:
            lines.append(f"  FAIL  {m['label']} (-{m['weight']})")
            lines.append(f"        Hint: {m['hint']}")
        lines.append("")
    if result["penalties"]:
        lines.append(f"Penalties applied ({len(result['penalties'])}):")
        for p in result["penalties"]:
            lines.append(f"  PEN   {p['label']} (-{p['penalty']})")
            lines.append(f"        Hint: {p['hint']}")
        lines.append("")
    if result["score"] >= 80:
        lines.append("Verdict: strong update — ready to send.")
    elif result["score"] >= 60:
        lines.append("Verdict: solid update — close 1-2 gaps before sending.")
    else:
        lines.append("Verdict: structural gaps — address missing sections before sending.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate a draft investor update.")
    parser.add_argument("update", help="Path to update markdown file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.update)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    result = validate(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
