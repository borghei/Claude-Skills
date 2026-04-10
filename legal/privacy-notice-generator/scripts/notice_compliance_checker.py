#!/usr/bin/env python3
"""
Privacy Notice Compliance Checker

Validates a privacy notice text against Art. 13/14 GDPR requirements.
Checks for mandatory disclosure elements, jurisdiction-specific requirements,
and notice type-specific sections. Outputs compliance score and findings.

Usage:
    python notice_compliance_checker.py privacy_notice.md
    python notice_compliance_checker.py privacy_notice.md --jurisdiction DE
    python notice_compliance_checker.py privacy_notice.md --jurisdiction FR --notice-type website
    python notice_compliance_checker.py privacy_notice.md --jurisdiction DE --notice-type employee --json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Art. 13 mandatory elements with search patterns
ART13_CHECKS: List[Dict] = [
    {
        "id": "controller_identity",
        "name": "Controller identity and contact details",
        "article": "Art. 13(1)(a)",
        "patterns": [r"controller", r"who we are", r"responsible\s+(for|party)", r"data\s+controller",
                     r"operated\s+by", r"company\s+name", r"registered\s+(address|office)"],
        "weight": 10,
        "category": "mandatory",
    },
    {
        "id": "dpo_contact",
        "name": "Data Protection Officer contact details",
        "article": "Art. 13(1)(b)",
        "patterns": [r"data\s+protection\s+officer", r"\bDPO\b", r"dpo@", r"datenschutzbeauftragte"],
        "weight": 8,
        "category": "mandatory",
    },
    {
        "id": "purposes",
        "name": "Purposes of processing",
        "article": "Art. 13(1)(c)",
        "patterns": [r"purpose", r"why\s+we\s+(process|collect|use)", r"reason.*process",
                     r"we\s+(use|process|collect)\s+your\s+(personal\s+)?data"],
        "weight": 10,
        "category": "mandatory",
    },
    {
        "id": "legal_bases",
        "name": "Legal bases for processing",
        "article": "Art. 13(1)(c)",
        "patterns": [r"legal\s+basis", r"lawful\s+basis", r"Art\.?\s*6", r"legitimate\s+interest",
                     r"consent", r"contractual\s+necessity", r"legal\s+obligation"],
        "weight": 10,
        "category": "mandatory",
    },
    {
        "id": "recipients",
        "name": "Recipients or categories of recipients",
        "article": "Art. 13(1)(e)",
        "patterns": [r"recipient", r"who\s+receives", r"share.*data", r"disclose.*to",
                     r"third\s+part(y|ies)", r"service\s+provider", r"processor"],
        "weight": 8,
        "category": "mandatory",
    },
    {
        "id": "transfers",
        "name": "International transfers information",
        "article": "Art. 13(1)(f)",
        "patterns": [r"transfer", r"outside\s+(the\s+)?(EU|EEA)", r"third\s+countr",
                     r"international", r"adequacy", r"standard\s+contractual", r"SCC"],
        "weight": 7,
        "category": "mandatory",
    },
    {
        "id": "retention",
        "name": "Retention periods or criteria",
        "article": "Art. 13(2)(a)",
        "patterns": [r"retention", r"how\s+long", r"storage\s+period", r"keep.*data",
                     r"delet(e|ion)", r"retain", r"stored\s+for"],
        "weight": 8,
        "category": "mandatory",
    },
    {
        "id": "right_access",
        "name": "Right of access",
        "article": "Art. 13(2)(b) / Art. 15",
        "patterns": [r"right.*access", r"Art\.?\s*15", r"copy\s+of\s+your\s+data",
                     r"request.*access", r"obtain.*data"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_rectification",
        "name": "Right to rectification",
        "article": "Art. 13(2)(b) / Art. 16",
        "patterns": [r"rectification", r"correction", r"Art\.?\s*16", r"correct.*data",
                     r"inaccurate"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_erasure",
        "name": "Right to erasure",
        "article": "Art. 13(2)(b) / Art. 17",
        "patterns": [r"erasure", r"right\s+to\s+be\s+forgotten", r"Art\.?\s*17",
                     r"delet(e|ion)\s+of\s+your\s+data", r"request.*delet"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_restriction",
        "name": "Right to restriction of processing",
        "article": "Art. 13(2)(b) / Art. 18",
        "patterns": [r"restriction", r"Art\.?\s*18", r"restrict.*process", r"limit.*process"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_portability",
        "name": "Right to data portability",
        "article": "Art. 13(2)(b) / Art. 20",
        "patterns": [r"portability", r"Art\.?\s*20", r"machine.?readable",
                     r"structured.*format", r"transfer.*data.*to\s+another"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_objection",
        "name": "Right to object",
        "article": "Art. 13(2)(b) / Art. 21",
        "patterns": [r"right\s+to\s+object", r"Art\.?\s*21", r"object\s+to\s+process",
                     r"Widerspruch"],
        "weight": 5,
        "category": "mandatory",
    },
    {
        "id": "right_automated",
        "name": "Automated decision-making disclosure",
        "article": "Art. 13(2)(f) / Art. 22",
        "patterns": [r"automated\s+decision", r"Art\.?\s*22", r"profiling",
                     r"automated\s+process.*legal", r"solely\s+automated"],
        "weight": 6,
        "category": "mandatory",
    },
    {
        "id": "consent_withdrawal",
        "name": "Right to withdraw consent",
        "article": "Art. 13(2)(c) / Art. 7(3)",
        "patterns": [r"withdraw.*consent", r"revoke.*consent", r"Art\.?\s*7\s*\(3\)",
                     r"withdrawal\s+does\s+not\s+affect"],
        "weight": 6,
        "category": "mandatory",
    },
    {
        "id": "sa_complaint",
        "name": "Right to complain to supervisory authority",
        "article": "Art. 13(2)(d)",
        "patterns": [r"supervisory\s+authority", r"complain", r"lodge\s+a\s+complaint",
                     r"Aufsichtsbeh", r"CNIL", r"ICO", r"DPC", r"Garante",
                     r"AEPD", r"Autoriteit", r"APD", r"DSB", r"BfDI"],
        "weight": 7,
        "category": "mandatory",
    },
]

# General quality checks
GENERAL_CHECKS: List[Dict] = [
    {
        "id": "art21_prominence",
        "name": "Art. 21 right to object is prominently displayed",
        "patterns": [r"(###|##)\s*.*(object|Widerspruch)", r"\*\*.*right\s+to\s+object.*\*\*",
                     r"prominently", r"separately\s+(from|listed)"],
        "weight": 4,
        "category": "general",
    },
    {
        "id": "no_placeholders",
        "name": "No placeholder text remaining",
        "patterns": [],  # Special check - inverse
        "weight": 5,
        "category": "general",
    },
    {
        "id": "plain_language",
        "name": "Plain language indicators",
        "patterns": [r"\byou\b", r"\byour\b", r"\byour\s+data\b", r"\byour\s+personal\b"],
        "weight": 3,
        "category": "general",
    },
    {
        "id": "version_date",
        "name": "Notice has version date",
        "patterns": [r"last\s+updated", r"version", r"effective\s+date", r"date.*notice"],
        "weight": 3,
        "category": "general",
    },
]

# Jurisdiction-specific checks
JURISDICTION_CHECKS: Dict[str, List[Dict]] = {
    "DE": [
        {"id": "de_widerspruch", "name": "Art. 21 DSGVO Widerspruchsrecht separate section",
         "patterns": [r"Widerspruch", r"Art\.?\s*21\s*(DSGVO|GDPR)"], "weight": 5},
        {"id": "de_tdddg", "name": "TDDDG telecom/telemedia reference (if applicable)",
         "patterns": [r"TDDDG", r"TTDSG", r"Telemedien", r"telemedia"], "weight": 3},
        {"id": "de_bdsg", "name": "BDSG reference for employee/DPO provisions",
         "patterns": [r"BDSG", r"Bundesdatenschutz", r"§\s*26", r"§\s*38"], "weight": 3},
    ],
    "FR": [
        {"id": "fr_cnil", "name": "CNIL reference or guidance compliance",
         "patterns": [r"CNIL", r"Commission\s+Nationale"], "weight": 4},
        {"id": "fr_lil", "name": "Loi Informatique et Libertés reference",
         "patterns": [r"Loi\s+Informatique", r"LIL", r"Informatique\s+et\s+Libert"], "weight": 3},
    ],
    "UK": [
        {"id": "uk_ico", "name": "ICO reference as supervisory authority",
         "patterns": [r"ICO", r"Information\s+Commissioner"], "weight": 4},
        {"id": "uk_gdpr_ref", "name": "UK GDPR (not EU GDPR) references",
         "patterns": [r"UK\s+GDPR", r"Data\s+Protection\s+Act\s+2018"], "weight": 3},
        {"id": "uk_pecr", "name": "PECR reference for cookies/electronic marketing",
         "patterns": [r"PECR", r"Privacy\s+and\s+Electronic\s+Communications"], "weight": 3},
    ],
    "IT": [
        {"id": "it_garante", "name": "Garante reference",
         "patterns": [r"Garante", r"garanteprivacy"], "weight": 4},
    ],
    "ES": [
        {"id": "es_aepd", "name": "AEPD reference",
         "patterns": [r"AEPD", r"Agencia\s+Espa"], "weight": 4},
        {"id": "es_lopdgdd", "name": "LOPDGDD reference",
         "patterns": [r"LOPDGDD", r"Ley\s+Org.nica\s+3/2018"], "weight": 3},
    ],
    "NL": [
        {"id": "nl_ap", "name": "AP (Autoriteit Persoonsgegevens) reference",
         "patterns": [r"Autoriteit\s+Persoons", r"\bAP\b.*persoons"], "weight": 4},
    ],
    "AT": [
        {"id": "at_dsb", "name": "DSB (Datenschutzbehörde) reference",
         "patterns": [r"DSB", r"Datenschutzbeh.rde"], "weight": 4},
    ],
    "BE": [
        {"id": "be_apd", "name": "APD/GBA reference",
         "patterns": [r"APD", r"GBA", r"Gegevensbescherming"], "weight": 4},
    ],
    "IE": [
        {"id": "ie_dpc", "name": "DPC (Data Protection Commission) reference",
         "patterns": [r"DPC", r"Data\s+Protection\s+Commission"], "weight": 4},
    ],
}

# Type-specific checks
TYPE_CHECKS: Dict[str, List[Dict]] = {
    "website": [
        {"id": "web_cookies", "name": "Cookie/tracking technology section",
         "patterns": [r"cookie", r"tracking", r"analytics", r"pixel"], "weight": 5},
    ],
    "applicant": [
        {"id": "app_retention", "name": "Application data retention period specified",
         "patterns": [r"6\s*month", r"applicat.*retain", r"talent\s+pool", r"recruit.*retention"], "weight": 5},
        {"id": "app_bdsg26", "name": "Employment law basis for applicant data (DE: §26 BDSG)",
         "patterns": [r"§\s*26\s*BDSG", r"employment\s+law", r"recruit.*basis"], "weight": 4},
    ],
    "employee": [
        {"id": "emp_works_council", "name": "Works council notification (DE/AT)",
         "patterns": [r"works\s+council", r"Betriebsrat", r"employee\s+representative"], "weight": 4},
        {"id": "emp_monitoring", "name": "IT monitoring disclosure",
         "patterns": [r"monitor", r"surveillance", r"BYOD", r"device\s+management"], "weight": 4},
    ],
    "b2b": [
        {"id": "b2b_art14", "name": "Art. 14 source of data disclosure",
         "patterns": [r"Art\.?\s*14", r"source.*data", r"not\s+collect.*directly",
                     r"obtained\s+from", r"indirect.*collection"], "weight": 6},
    ],
    "b2c": [
        {"id": "b2c_soft_optin", "name": "Soft opt-in rules for existing customers",
         "patterns": [r"soft\s+opt.?in", r"existing\s+customer.*market", r"similar\s+products"], "weight": 4},
    ],
}


def check_patterns(text: str, patterns: List[str]) -> bool:
    """Check if any pattern matches in text."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def count_placeholders(text: str) -> int:
    """Count remaining placeholder markers."""
    return len(re.findall(r"\[PLACEHOLDER", text, re.IGNORECASE)) + \
           len(re.findall(r"\{\{.*?\}\}", text))


def run_checks(text: str, jurisdiction: Optional[str] = None,
               notice_type: Optional[str] = None) -> Dict:
    """Run all compliance checks against notice text."""
    findings = {
        "missing": [],
        "present": [],
        "general_findings": [],
        "jurisdiction_findings": [],
        "type_findings": [],
    }
    total_weight = 0
    earned_weight = 0

    # Art. 13 mandatory checks
    for check in ART13_CHECKS:
        total_weight += check["weight"]
        if check_patterns(text, check["patterns"]):
            earned_weight += check["weight"]
            findings["present"].append({
                "id": check["id"], "name": check["name"],
                "article": check["article"], "status": "present",
            })
        else:
            findings["missing"].append({
                "id": check["id"], "name": check["name"],
                "article": check["article"], "status": "missing",
                "severity": "must-fix",
            })

    # General checks
    for check in GENERAL_CHECKS:
        total_weight += check["weight"]
        if check["id"] == "no_placeholders":
            count = count_placeholders(text)
            if count == 0:
                earned_weight += check["weight"]
                findings["general_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "pass", "detail": "No placeholder text found",
                })
            else:
                findings["general_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "fail", "detail": f"{count} placeholder(s) remaining",
                    "severity": "must-fix",
                })
        elif check_patterns(text, check["patterns"]):
            earned_weight += check["weight"]
            findings["general_findings"].append({
                "id": check["id"], "name": check["name"], "status": "pass",
            })
        else:
            findings["general_findings"].append({
                "id": check["id"], "name": check["name"], "status": "fail",
                "severity": "should-improve",
            })

    # Jurisdiction-specific checks
    if jurisdiction and jurisdiction in JURISDICTION_CHECKS:
        for check in JURISDICTION_CHECKS[jurisdiction]:
            total_weight += check["weight"]
            if check_patterns(text, check["patterns"]):
                earned_weight += check["weight"]
                findings["jurisdiction_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "pass", "jurisdiction": jurisdiction,
                })
            else:
                findings["jurisdiction_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "fail", "jurisdiction": jurisdiction,
                    "severity": "should-improve",
                })

    # Type-specific checks
    if notice_type and notice_type in TYPE_CHECKS:
        for check in TYPE_CHECKS[notice_type]:
            total_weight += check["weight"]
            if check_patterns(text, check["patterns"]):
                earned_weight += check["weight"]
                findings["type_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "pass", "notice_type": notice_type,
                })
            else:
                findings["type_findings"].append({
                    "id": check["id"], "name": check["name"],
                    "status": "fail", "notice_type": notice_type,
                    "severity": "should-improve",
                })

    score = round((earned_weight / total_weight) * 100) if total_weight > 0 else 0

    return {
        "score": score,
        "total_checks": len(ART13_CHECKS) + len(GENERAL_CHECKS) +
                        len(JURISDICTION_CHECKS.get(jurisdiction, [])) +
                        len(TYPE_CHECKS.get(notice_type, [])),
        "mandatory_present": len(findings["present"]),
        "mandatory_missing": len(findings["missing"]),
        "findings": findings,
    }


def format_text_report(results: Dict, jurisdiction: Optional[str],
                       notice_type: Optional[str]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("PRIVACY NOTICE COMPLIANCE CHECK")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if jurisdiction:
        lines.append(f"Jurisdiction: {jurisdiction}")
    if notice_type:
        lines.append(f"Notice Type: {notice_type}")
    lines.append("=" * 60)

    score = results["score"]
    grade = "EXCELLENT" if score >= 90 else ("GOOD" if score >= 75 else ("NEEDS WORK" if score >= 50 else "INSUFFICIENT"))
    lines.append(f"\n  Compliance Score: {score}/100 ({grade})")
    lines.append(f"  Art. 13/14 Elements: {results['mandatory_present']}/{results['mandatory_present'] + results['mandatory_missing']} present")
    lines.append(f"  Total Checks: {results['total_checks']}")

    f = results["findings"]

    if f["missing"]:
        lines.append(f"\n{'!' * 60}")
        lines.append("  MISSING MANDATORY ELEMENTS (must-fix)")
        lines.append(f"{'!' * 60}")
        for item in f["missing"]:
            lines.append(f"  [X] {item['name']}")
            lines.append(f"      Reference: {item['article']}")

    general_fails = [g for g in f["general_findings"] if g["status"] == "fail"]
    if general_fails:
        lines.append(f"\n{'-' * 60}")
        lines.append("  GENERAL FINDINGS")
        lines.append(f"{'-' * 60}")
        for item in general_fails:
            detail = f" — {item['detail']}" if "detail" in item else ""
            lines.append(f"  [!] {item['name']}{detail}")

    jur_fails = [j for j in f["jurisdiction_findings"] if j["status"] == "fail"]
    if jur_fails:
        lines.append(f"\n{'-' * 60}")
        lines.append(f"  JURISDICTION FINDINGS ({jurisdiction})")
        lines.append(f"{'-' * 60}")
        for item in jur_fails:
            lines.append(f"  [!] {item['name']}")

    type_fails = [t for t in f["type_findings"] if t["status"] == "fail"]
    if type_fails:
        lines.append(f"\n{'-' * 60}")
        lines.append(f"  TYPE-SPECIFIC FINDINGS ({notice_type})")
        lines.append(f"{'-' * 60}")
        for item in type_fails:
            lines.append(f"  [!] {item['name']}")

    if not f["missing"] and not general_fails and not jur_fails and not type_fails:
        lines.append("\n  All checks passed.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a privacy notice against Art. 13/14 GDPR requirements"
    )
    parser.add_argument("notice_file", help="Path to privacy notice file (markdown or text)")
    parser.add_argument("--jurisdiction", choices=list(JURISDICTION_CHECKS.keys()),
                        help="Jurisdiction for local requirements")
    parser.add_argument("--notice-type", choices=list(TYPE_CHECKS.keys()),
                        help="Notice type for type-specific checks")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    try:
        notice_path = Path(args.notice_file)
        if not notice_path.exists():
            print(f"Error: File not found: {args.notice_file}", file=sys.stderr)
            sys.exit(1)

        text = notice_path.read_text(encoding="utf-8")
        if not text.strip():
            print("Error: Notice file is empty.", file=sys.stderr)
            sys.exit(1)

        results = run_checks(text, args.jurisdiction, args.notice_type)
        results["file"] = str(notice_path)
        results["check_date"] = datetime.now().isoformat()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_text_report(results, args.jurisdiction, args.notice_type))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
