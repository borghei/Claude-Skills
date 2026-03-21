#!/usr/bin/env python3
"""
Persuasion Auditor

Audits marketing copy for the application of Cialdini's 7
principles of persuasion plus key behavioral economics principles.

Usage:
    python persuasion_auditor.py page.txt
    python persuasion_auditor.py page.html --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

HTML_TAG = re.compile(r"<[^>]+>")

PRINCIPLES = {
    "reciprocity": {
        "patterns": [
            re.compile(r"(free guide|free tool|free audit|free template|free trial|free ebook|free download|complimentary|bonus)", re.IGNORECASE),
            re.compile(r"(here's|we've created|download|get your free|take this)", re.IGNORECASE),
        ],
        "description": "Give value before asking for anything in return",
        "example": "Free tool, guide, or audit offered before the ask",
    },
    "commitment_consistency": {
        "patterns": [
            re.compile(r"(step 1|get started|start with|begin by|first step|quiz|assessment)", re.IGNORECASE),
            re.compile(r"(you've already|you started|continue|pick up where|your progress)", re.IGNORECASE),
        ],
        "description": "Small commitments leading to larger ones",
        "example": "Quiz > Email > Trial > Paid progression",
    },
    "social_proof": {
        "patterns": [
            re.compile(r"(trusted by|used by|loved by|join)\s+\d+", re.IGNORECASE),
            re.compile(r"\d+\s*(teams|companies|customers|users|businesses|people)", re.IGNORECASE),
            re.compile(r"(testimonial|review|rating|\d\.\d\s*/\s*5|stars)", re.IGNORECASE),
            re.compile(r'".+"\s*[-—]\s*\w+', re.IGNORECASE),
            re.compile(r"(most popular|best.?seller|trending|top rated)", re.IGNORECASE),
        ],
        "description": "Show others like them are choosing this",
        "example": "'Trusted by 2,847 teams' or named testimonials",
    },
    "authority": {
        "patterns": [
            re.compile(r"(expert|certified|award|featured in|as seen|published|recognized|accredited)", re.IGNORECASE),
            re.compile(r"(phd|md|professor|researcher|author of|years of experience|\d+ years)", re.IGNORECASE),
            re.compile(r"(forbes|techcrunch|wall street|nyt|bloomberg|y combinator)", re.IGNORECASE),
        ],
        "description": "Credible expertise signals",
        "example": "Featured in Forbes, 15 years experience, certified expert",
    },
    "liking": {
        "patterns": [
            re.compile(r"(our team|our story|meet the|about us|behind the scenes|we believe|our mission)", re.IGNORECASE),
            re.compile(r"(built by|created by|founded by|designed for|made for)", re.IGNORECASE),
        ],
        "description": "Build rapport and shared identity",
        "example": "'Built by marketers, for marketers' or team stories",
    },
    "scarcity": {
        "patterns": [
            re.compile(r"(limited|only \d|last chance|ending soon|expires|deadline|sold out|waitlist|few remaining)", re.IGNORECASE),
            re.compile(r"(\d+ (spots|seats|slots) (left|remaining|available))", re.IGNORECASE),
        ],
        "description": "Limited availability increases perceived value",
        "example": "'Only 5 spots remaining' or deadline-based pricing",
    },
    "unity": {
        "patterns": [
            re.compile(r"(community|together|us|tribe|family|insider|member|exclusive group)", re.IGNORECASE),
            re.compile(r"(fellow|like you|people like you|others in your|your peers)", re.IGNORECASE),
        ],
        "description": "Shared identity and belonging",
        "example": "'Join the community' or 'fellow founders'",
    },
}

BEHAVIORAL_ECONOMICS = {
    "loss_aversion": {
        "patterns": [
            re.compile(r"(don't miss|losing|miss out|without|stop losing|left behind|fall behind|cost of)", re.IGNORECASE),
        ],
        "description": "Frame as what they lose, not just what they gain",
    },
    "anchoring": {
        "patterns": [
            re.compile(r"(was \$|originally \$|compare|usually \$|valued at|worth \$|\$\d+.*\$\d+)", re.IGNORECASE),
        ],
        "description": "First number sets expectations for subsequent prices",
    },
    "endowment_effect": {
        "patterns": [
            re.compile(r"(your (dashboard|account|data|workspace|profile)|personalized|customized for you)", re.IGNORECASE),
        ],
        "description": "Ownership feeling increases perceived value",
    },
    "zero_price_effect": {
        "patterns": [
            re.compile(r"(free tier|free plan|free forever|no cost|\$0|completely free)", re.IGNORECASE),
        ],
        "description": "'Free' is disproportionately attractive vs. cheap",
    },
}


def audit_persuasion(text: str) -> dict:
    plain = HTML_TAG.sub(" ", text)
    plain = re.sub(r"\s+", " ", plain).strip()

    found_principles = {}
    missing_principles = {}

    for name, config in PRINCIPLES.items():
        matches = []
        for pattern in config["patterns"]:
            for m in pattern.finditer(plain):
                matches.append(m.group().strip())

        if matches:
            found_principles[name] = {
                "found": True,
                "matches": list(set(matches))[:5],
                "description": config["description"],
            }
        else:
            missing_principles[name] = {
                "found": False,
                "description": config["description"],
                "example": config["example"],
            }

    found_behavioral = {}
    for name, config in BEHAVIORAL_ECONOMICS.items():
        matches = []
        for pattern in config["patterns"]:
            for m in pattern.finditer(plain):
                matches.append(m.group().strip())
        if matches:
            found_behavioral[name] = {
                "found": True,
                "matches": list(set(matches))[:3],
                "description": config["description"],
            }

    total_principles = len(PRINCIPLES)
    found_count = len(found_principles)
    coverage = round(found_count / total_principles * 100)

    # Score
    score = found_count * 12 + len(found_behavioral) * 5
    score = min(100, score)

    recs = []
    if "social_proof" not in found_principles:
        recs.append("Add social proof: customer counts, testimonials with names and metrics, or review scores.")
    if "reciprocity" not in found_principles:
        recs.append("Add reciprocity: offer something valuable (free tool, guide, audit) before the ask.")
    if "scarcity" not in found_principles:
        recs.append("Consider genuine scarcity: limited spots, deadline pricing, or waitlist. Only if real.")
    if "authority" not in found_principles:
        recs.append("Add authority signals: media mentions, certifications, expert endorsements.")
    if "loss_aversion" not in found_behavioral:
        recs.append("Frame benefits as loss avoidance: 'Stop losing X' is stronger than 'Gain X'.")

    if found_count >= 5:
        recs.insert(0, "Strong persuasion coverage. A/B test to see which principles drive the most conversions.")

    return {
        "cialdini_coverage": f"{found_count}/{total_principles}",
        "coverage_pct": coverage,
        "score": score,
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F",
        "principles_found": found_principles,
        "principles_missing": missing_principles,
        "behavioral_economics_found": found_behavioral,
        "recommendations": recs,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  PERSUASION AUDITOR (Cialdini + Behavioral Economics)", "=" * 60]
    lines.append(f"\n  Score: {result['score']}/100 ({result['grade']})")
    lines.append(f"  Cialdini Coverage: {result['cialdini_coverage']} principles ({result['coverage_pct']}%)")

    lines.append(f"\n  Principles Found:")
    for name, info in result["principles_found"].items():
        matches = ", ".join(info["matches"][:3])
        lines.append(f"    [+] {name.replace('_', ' ').title()}: {info['description']}")
        lines.append(f"        Evidence: {matches}")

    if result["principles_missing"]:
        lines.append(f"\n  Principles Missing:")
        for name, info in result["principles_missing"].items():
            lines.append(f"    [-] {name.replace('_', ' ').title()}: {info['description']}")
            lines.append(f"        Add: {info['example']}")

    if result["behavioral_economics_found"]:
        lines.append(f"\n  Behavioral Economics Applied:")
        for name, info in result["behavioral_economics_found"].items():
            lines.append(f"    [+] {name.replace('_', ' ').title()}: {info['description']}")

    lines.append(f"\n  Recommendations:")
    for r in result["recommendations"]:
        lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit marketing copy for persuasion principles.")
    parser.add_argument("file", help="Text or HTML file to audit")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        text = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    result = audit_persuasion(text)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
