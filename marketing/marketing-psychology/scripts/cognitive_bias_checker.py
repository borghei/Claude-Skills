#!/usr/bin/env python3
"""
Cognitive Bias Checker

Identifies cognitive biases being leveraged (or missed) in
marketing copy, pricing pages, and landing pages.

Usage:
    python cognitive_bias_checker.py page.txt
    python cognitive_bias_checker.py page.html --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

HTML_TAG = re.compile(r"<[^>]+>")

BIASES = {
    "anchoring": {
        "patterns": [
            re.compile(r"(was|originally|compare|usually|valued at|worth)\s*\$?\d+", re.IGNORECASE),
            re.compile(r"\$\d+.*\$\d+"),
            re.compile(r"(starting at|from|as low as)\s*\$?\d+", re.IGNORECASE),
        ],
        "description": "First number sets frame for all subsequent numbers",
        "application": "Show higher price first, then your price",
        "risk": "low",
    },
    "loss_aversion": {
        "patterns": [
            re.compile(r"(don't miss|lose|losing|miss out|without|left behind|cost of inaction|fall behind)", re.IGNORECASE),
            re.compile(r"(stop (losing|wasting|missing)|what you'll lose)", re.IGNORECASE),
        ],
        "description": "People feel losses 2x more than equivalent gains",
        "application": "Frame as 'stop losing X' instead of 'gain X'",
        "risk": "medium",
    },
    "social_proof": {
        "patterns": [
            re.compile(r"\d+\s*(teams|companies|customers|users|people|businesses)", re.IGNORECASE),
            re.compile(r"(most popular|best.?seller|trending|top rated|#1)", re.IGNORECASE),
            re.compile(r"(trusted|used|loved|chosen)\s*by", re.IGNORECASE),
        ],
        "description": "People follow the actions of others",
        "application": "Show customer counts, 'Most Popular' labels",
        "risk": "low",
    },
    "paradox_of_choice": {
        "patterns": [
            re.compile(r"(recommended|popular|best value|suggested)", re.IGNORECASE),
            re.compile(r"(simple|easy choice|just pick|one plan)", re.IGNORECASE),
        ],
        "description": "Too many options leads to decision paralysis",
        "application": "Limit to 3 tiers, highlight recommended plan",
        "risk": "low",
    },
    "decoy_effect": {
        "patterns": [
            re.compile(r"(\$\d+.*\$\d+.*\$\d+)", re.IGNORECASE),
            re.compile(r"(basic|starter|plus|pro|enterprise|premium)", re.IGNORECASE),
        ],
        "description": "A dominated option makes target option look better",
        "application": "Add a 3rd tier that makes middle tier obvious best value",
        "risk": "low",
    },
    "endowment_effect": {
        "patterns": [
            re.compile(r"(your (dashboard|account|data|workspace|plan|trial))", re.IGNORECASE),
            re.compile(r"(personalized|customized|tailored) for you", re.IGNORECASE),
            re.compile(r"(keep|save) your", re.IGNORECASE),
        ],
        "description": "People value things more once they feel ownership",
        "application": "Free trials, 'your dashboard', saved progress",
        "risk": "low",
    },
    "framing_effect": {
        "patterns": [
            re.compile(r"(save|saving|savings)\s*\$?\d+", re.IGNORECASE),
            re.compile(r"\d+%\s*(off|discount|savings|cheaper)", re.IGNORECASE),
            re.compile(r"(\$\d+/day|\$\d+\.?\d*/day|per day|daily)", re.IGNORECASE),
        ],
        "description": "Same info presented differently changes decisions",
        "application": "'$3.29/day' feels cheaper than '$99/month'",
        "risk": "low",
    },
    "zeigarnik_effect": {
        "patterns": [
            re.compile(r"(step \d of|progress|(\d+%|almost) (complete|done|there))", re.IGNORECASE),
            re.compile(r"(you're \d|one step|almost done|nearly there|halfway)", re.IGNORECASE),
        ],
        "description": "Incomplete tasks create mental tension to finish",
        "application": "Progress bars, 'Step 2 of 3', '80% complete'",
        "risk": "low",
    },
    "scarcity_bias": {
        "patterns": [
            re.compile(r"(limited|only \d|last chance|ending|expires|deadline|few (remaining|left|available))", re.IGNORECASE),
            re.compile(r"(\d+ (spots|seats|slots) (left|remaining))", re.IGNORECASE),
        ],
        "description": "Limited availability increases perceived value",
        "application": "Real constraints: limited spots, deadline pricing",
        "risk": "high -- only ethical if scarcity is real",
    },
    "default_effect": {
        "patterns": [
            re.compile(r"(pre.?selected|default|recommended|suggested|auto)", re.IGNORECASE),
            re.compile(r"(annual|yearly) (billing|plan|subscription)", re.IGNORECASE),
        ],
        "description": "People tend to accept the default option",
        "application": "Pre-select annual billing, recommended plan",
        "risk": "medium -- must not be deceptive",
    },
    "charm_pricing": {
        "patterns": [
            re.compile(r"\$\d+\.(99|95|97)"),
            re.compile(r"\$\d*9\b"),
        ],
        "description": "Prices ending in 9 feel significantly cheaper (left-digit effect)",
        "application": "$49 instead of $50 for consumer; round numbers for premium",
        "risk": "low",
    },
}


def check_biases(text: str) -> dict:
    plain = HTML_TAG.sub(" ", text)
    plain = re.sub(r"\s+", " ", plain).strip()

    detected = {}
    not_detected = {}

    for name, config in BIASES.items():
        matches = []
        for pattern in config["patterns"]:
            for m in pattern.finditer(plain):
                matches.append(m.group().strip())

        if matches:
            detected[name] = {
                "evidence": list(set(matches))[:4],
                "description": config["description"],
                "risk": config["risk"],
            }
        else:
            not_detected[name] = {
                "description": config["description"],
                "application": config["application"],
            }

    # Ethical assessment
    high_risk = [name for name, info in detected.items() if "high" in info["risk"]]
    ethical_notes = []
    if high_risk:
        ethical_notes.append(f"High-risk biases detected: {', '.join(high_risk)}. Ensure these are applied ethically (real scarcity, real constraints).")
    if "scarcity_bias" in detected:
        ethical_notes.append("Scarcity MUST be genuine. Fake scarcity erodes trust and can violate advertising standards.")

    score = len(detected) * 10
    score = min(100, score)

    return {
        "biases_detected": len(detected),
        "biases_total": len(BIASES),
        "score": score,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F",
        "detected": detected,
        "opportunities": not_detected,
        "ethical_notes": ethical_notes,
        "top_opportunities": list(not_detected.keys())[:5],
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  COGNITIVE BIAS CHECKER", "=" * 60]
    lines.append(f"\n  Score: {result['score']}/100 ({result['grade']})")
    lines.append(f"  Biases Detected: {result['biases_detected']}/{result['biases_total']}")

    if result["detected"]:
        lines.append(f"\n  Active Biases:")
        for name, info in result["detected"].items():
            evidence = ", ".join(info["evidence"][:3])
            risk = f" [RISK: {info['risk']}]" if "high" in info["risk"] else ""
            lines.append(f"    [+] {name.replace('_', ' ').title()}{risk}")
            lines.append(f"        {info['description']}")
            lines.append(f"        Evidence: {evidence}")

    if result["top_opportunities"]:
        lines.append(f"\n  Opportunities (not yet applied):")
        for name in result["top_opportunities"]:
            info = result["opportunities"][name]
            lines.append(f"    [-] {name.replace('_', ' ').title()}")
            lines.append(f"        How: {info['application']}")

    if result["ethical_notes"]:
        lines.append(f"\n  Ethical Notes:")
        for note in result["ethical_notes"]:
            lines.append(f"    !! {note}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check marketing copy for cognitive bias application.")
    parser.add_argument("file", help="Text or HTML file")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        text = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    result = check_biases(text)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
