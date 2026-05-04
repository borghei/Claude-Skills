#!/usr/bin/env python3
"""
Student Data Compliance Checker — scan an edtech product description for
indicators of student-data handling and the regulatory regimes likely to apply.

Usage:
    python student_data_compliance_checker.py description.txt
    python student_data_compliance_checker.py description.txt --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


SIGNALS = [
    {
        "regime": "FERPA (US Family Educational Rights and Privacy Act)",
        "applies_when": "School / district holds education records and shares them with the edtech as a 'school official' under FERPA",
        "patterns": [
            r"\b(student record|education record|grade|grades|transcript|GPA|attendance)\b",
            r"\b(school district|district|public school|charter school|college|university)\b",
            r"\b(K[- ]?12|kindergarten|elementary|middle school|high school|grade school)\b",
            r"\b(LMS|SIS|student information system|learning management)\b",
        ],
        "implication": "FERPA likely applies via 'school official' exception. School (district) is data controller; edtech is school official with limited use rights. Direct-to-parent disclosures generally require consent.",
    },
    {
        "regime": "COPPA (US Children's Online Privacy Protection Act)",
        "applies_when": "You collect personal information online from children under 13",
        "patterns": [
            r"\b(under 13|under age 13|children under|minors|kids|child|toddler|preschool)\b",
            r"\b(elementary|kindergarten|grade [1-5]\b)\b",
            r"\bage[- ]?gate|parental consent|verifiable parental consent\b",
        ],
        "implication": "COPPA requires verifiable parental consent for collection of personal information from US users under 13. School-authorization is one accepted basis when used in a school context.",
    },
    {
        "regime": "GDPR-K (EU GDPR for children)",
        "applies_when": "EU minors' data, with age threshold varying 13-16 by member state",
        "patterns": [
            r"\b(EU|Europe|European Union|GDPR)\b",
            r"\b(EU students|European students|EU schools)\b",
        ],
        "implication": "EU GDPR applies to all EU residents. For minors (threshold 13-16 depending on member state), age-appropriate consent and parental consent rules apply.",
    },
    {
        "regime": "State laws (US)",
        "applies_when": "Operating in specific US states with student-data laws",
        "patterns": [
            r"\b(SOPIPA|California|Illinois|New York|Texas|Connecticut|Colorado)\b",
            r"\b(student privacy|student data law|data privacy agreement|DPA)\b",
        ],
        "implication": "Many states have specific student-data laws beyond FERPA: California SOPIPA, NY Ed Law 2-d, Illinois SOPPA, Connecticut, Colorado, etc. State-by-state review may be required.",
    },
    {
        "regime": "Higher Education / Adult Learners",
        "applies_when": "Higher ed students (18+) and corporate L&D",
        "patterns": [
            r"\b(university|college|higher education|undergraduate|graduate)\b",
            r"\b(corporate|enterprise|workforce|employee|professional development|L&D|learning and development)\b",
        ],
        "implication": "FERPA still applies to higher ed (institution as data controller). For corporate / professional learning, GDPR / state privacy laws (CCPA / CPRA / etc.) apply rather than FERPA / COPPA.",
    },
]


def detect(text):
    text_lower = text.lower()
    found = []
    for signal in SIGNALS:
        matched = []
        for pattern in signal["patterns"]:
            for m in re.finditer(pattern, text_lower, re.IGNORECASE):
                matched.append(m.group(0))
        if matched:
            found.append({
                "regime": signal["regime"],
                "applies_when": signal["applies_when"],
                "matched_terms": list(set(matched))[:5],
                "implication": signal["implication"],
            })
    return found


def render_human(triggers):
    lines = []
    lines.append("Student Data Compliance Scope Scan")
    lines.append("=" * 60)
    if not triggers:
        lines.append("No clear student-data compliance regimes detected.")
        lines.append("If the product touches learners or schools, re-describe and re-run.")
        return "\n".join(lines)
    lines.append(f"Detected {len(triggers)} candidate regime(s):")
    lines.append("")
    for i, t in enumerate(triggers, 1):
        lines.append(f"{i}. {t['regime']}")
        lines.append(f"   Applies when: {t['applies_when']}")
        lines.append(f"   Matched terms: {', '.join(t['matched_terms'])}")
        lines.append(f"   Implication: {t['implication']}")
        lines.append("")
    lines.append("=" * 60)
    lines.append("REMINDER: Keyword scan. Not legal advice.")
    lines.append("Engage edtech / privacy specialist counsel for binding decisions.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan an edtech product description for student-data compliance regimes.")
    parser.add_argument("description", help="Path to a text file describing the product")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.description)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    triggers = detect(text)

    if args.json:
        print(json.dumps({
            "description_excerpt": text[:200].strip(),
            "regimes": triggers,
            "disclaimer": "Keyword scan only. Not legal advice.",
        }, indent=2))
    else:
        print(render_human(triggers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
