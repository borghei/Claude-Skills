#!/usr/bin/env python3
"""
PHI Scope Checker — scan a healthtech product description for indicators of
Protected Health Information (PHI) handling and likely HIPAA scope.

Usage:
    python phi_scope_checker.py description.txt
    python phi_scope_checker.py description.txt --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Patterns that indicate PHI / HIPAA-relevant data handling
PHI_INDICATORS = [
    {
        "category": "Direct identifiers",
        "patterns": [
            r"\b(patient name|patient identifier|MRN|medical record number|SSN|social security|date of birth)\b",
            r"\b(address|email|phone number) (?:of|for)? patients?\b",
        ],
    },
    {
        "category": "Clinical data",
        "patterns": [
            r"\b(diagnos(?:is|es)|ICD[- ]?10|ICD[- ]?11|CPT|HCPCS|SNOMED)\b",
            r"\b(symptom|symptoms|condition|conditions|disease|diseases|disorder|disorders)\b",
            r"\b(medication|prescription|prescribe|prescribed|drug|drugs|treatment|therapy)\b",
            r"\b(lab result|lab results|blood test|imaging|x[- ]?ray|MRI|CT scan|biopsy)\b",
        ],
    },
    {
        "category": "Provider / care context",
        "patterns": [
            r"\b(physician|doctor|nurse|clinician|provider|care team|specialist)\b",
            r"\b(hospital|clinic|practice|health system|HCO|provider organization)\b",
            r"\b(visit|encounter|appointment|consultation|admission|discharge)\b",
        ],
    },
    {
        "category": "Health data sources",
        "patterns": [
            r"\b(EHR|EMR|electronic health record|electronic medical record)\b",
            r"\b(HL7|FHIR|CDA|continuity of care document|CCD)\b",
            r"\b(claims data|insurance claims|billing data|encounter data)\b",
            r"\b(remote patient monitoring|RPM|connected device|wearable for)\b",
        ],
    },
    {
        "category": "Payor / insurance context",
        "patterns": [
            r"\b(payor|insurer|insurance|health plan|Medicare|Medicaid|TRICARE)\b",
            r"\b(eligibility|prior authorization|claim|claims|copay|deductible)\b",
        ],
    },
]

# Role classification signals
COVERED_ENTITY_SIGNALS = [
    r"\bwe (?:are|operate as) (?:a|an) (?:health (?:care )?provider|covered entity|HCP|healthcare provider)\b",
    r"\bwe (?:provide|deliver) (?:medical|clinical|healthcare) (?:services|care)\b",
    r"\bour (?:physicians|doctors|clinicians)\b",
    r"\b(?:our|we run) (?:a |an )?(?:clinic|hospital|practice|health system)\b",
    r"\bwe bill (?:medicare|medicaid|insurance|payors?)\b",
]

BUSINESS_ASSOCIATE_SIGNALS = [
    r"\bon behalf of\b",
    r"\bunder a (?:BAA|business associate agreement)\b",
    r"\b(?:provide (?:services|software) to|serve|sell to) (?:hospitals|clinics|providers|payors|health (?:systems|plans))\b",
    r"\bour (?:customers|clients) are (?:hospitals|clinics|providers|payors|covered entities)\b",
    r"\b(EHR integration|integrate with EHR|integrate with Epic|integrate with Cerner|integrate with athena)\b",
]

CONSUMER_WELLNESS_SIGNALS = [
    r"\bdirect[- ]to[- ]consumer\b",
    r"\bD2C\b",
    r"\b(?:consumer|individual) (?:wellness|fitness|tracker|tracking)\b",
    r"\bpersonal (?:health|wellness|fitness)\b",
    r"\bnot a (?:medical|clinical) (?:product|service)\b",
]


def scan_phi_indicators(text):
    text_lower = text.lower()
    found = []
    for category in PHI_INDICATORS:
        matches = []
        for pattern in category["patterns"]:
            for m in re.finditer(pattern, text_lower, re.IGNORECASE):
                matches.append(m.group(0))
        if matches:
            found.append({
                "category": category["category"],
                "matches": list(set(matches))[:5],
            })
    return found


def classify_role(text):
    text_lower = text.lower()
    is_ce = any(re.search(p, text_lower, re.IGNORECASE) for p in COVERED_ENTITY_SIGNALS)
    is_ba = any(re.search(p, text_lower, re.IGNORECASE) for p in BUSINESS_ASSOCIATE_SIGNALS)
    is_consumer = any(re.search(p, text_lower, re.IGNORECASE) for p in CONSUMER_WELLNESS_SIGNALS)
    roles = []
    if is_ce:
        roles.append("Likely Covered Entity")
    if is_ba:
        roles.append("Likely Business Associate")
    if is_consumer and not (is_ce or is_ba):
        roles.append("Likely consumer-wellness (outside HIPAA scope)")
    if not roles:
        roles.append("Role unclear from description — needs explicit framing")
    return roles


def render_human(phi_indicators, roles, has_phi):
    lines = []
    lines.append("HIPAA / PHI Scope Scan")
    lines.append("=" * 60)
    lines.append("")

    lines.append("Likely role under HIPAA:")
    for r in roles:
        lines.append(f"  • {r}")
    lines.append("")

    if not has_phi:
        lines.append("PHI indicators detected: NONE")
        lines.append("")
        lines.append("Implications:")
        lines.append("  • If your product genuinely does not touch identifiable health information,")
        lines.append("    HIPAA may not apply.")
        lines.append("  • State laws (Washington 'My Health My Data', California CMIA, etc.)")
        lines.append("    may still apply to consumer health data.")
        lines.append("  • Re-evaluate scope as product evolves.")
    else:
        lines.append(f"PHI indicators detected ({len(phi_indicators)} categories):")
        for ind in phi_indicators:
            lines.append(f"  • {ind['category']}: {', '.join(ind['matches'])}")
        lines.append("")
        lines.append("Implications:")
        lines.append("  • Likely subject to HIPAA Privacy and Security Rules")
        lines.append("  • Need: BAAs with each Covered Entity you serve (if BA)")
        lines.append("  • Need: BAAs with each subcontractor that handles PHI (BA-of-BA)")
        lines.append("  • Need: encryption in transit and at rest, access controls, audit logs")
        lines.append("  • Need: breach-notification process within statutory timelines")
        lines.append("  • State laws may add additional requirements")
    lines.append("")
    lines.append("=" * 60)
    lines.append("REMINDER: This is a keyword scan, not legal advice.")
    lines.append("Engage HIPAA-specialist counsel before launch.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan a healthtech product description for HIPAA / PHI scope.")
    parser.add_argument("description", help="Path to a text file describing the product")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.description)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    phi_indicators = scan_phi_indicators(text)
    has_phi = len(phi_indicators) > 0
    roles = classify_role(text)

    if args.json:
        print(json.dumps({
            "description_excerpt": text[:200].strip(),
            "has_phi_indicators": has_phi,
            "phi_indicators": phi_indicators,
            "likely_roles": roles,
            "disclaimer": "Keyword scan only. Not legal advice. Engage HIPAA-specialist counsel.",
        }, indent=2))
    else:
        print(render_human(phi_indicators, roles, has_phi))
    return 0


if __name__ == "__main__":
    sys.exit(main())
