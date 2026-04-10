#!/usr/bin/env python3
"""
Privacy Regulation Checker

Determines which privacy regulations apply to an organization based on location,
data subjects, data types, and processing activities. Maps obligations per regulation
and flags gaps where current practices may not meet requirements.

Usage:
    python privacy_regulation_checker.py --org-location DE --data-subjects EU,US --data-types personal,sensitive --processing-activities marketing,analytics
    python privacy_regulation_checker.py --org-location US-CA --data-subjects EU,BR --data-types personal --processing-activities ecommerce --json
    python privacy_regulation_checker.py --org-location SG --data-subjects SG,AU --data-types health --processing-activities healthcare --current-practices consent_mechanism,breach_process
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple


REGULATIONS: Dict[str, Dict] = {
    "gdpr": {
        "name": "GDPR (EU)",
        "full_name": "General Data Protection Regulation (EU) 2016/679",
        "territorial_scope": ["EU"],
        "applies_when": "Processing personal data of EU/EEA residents, or organization established in EU",
        "dpo_required": True,
        "breach_notification_hours": 72,
        "max_penalty_pct": 4.0,
        "max_penalty_amount": "EUR 20M",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 60,
        "legal_bases": ["consent", "contract", "legal_obligation", "vital_interests", "public_task", "legitimate_interests"],
        "key_obligations": [
            "Lawful basis for processing (Art. 6)",
            "Data subject rights (Art. 15-22)",
            "Records of processing activities (Art. 30)",
            "Data Protection Impact Assessment (Art. 35)",
            "Data Protection Officer appointment (Art. 37)",
            "Breach notification within 72 hours (Art. 33)",
            "International transfer safeguards (Chapter V)",
            "Privacy by design and default (Art. 25)",
        ],
        "data_subject_rights": ["access", "rectification", "erasure", "restriction", "portability", "objection", "automated_decision"],
    },
    "ccpa": {
        "name": "CCPA/CPRA (California)",
        "full_name": "California Consumer Privacy Act / California Privacy Rights Act",
        "territorial_scope": ["US"],
        "applies_when": "For-profit business meeting revenue/data thresholds processing CA residents' data",
        "dpo_required": False,
        "breach_notification_hours": None,
        "max_penalty_pct": None,
        "max_penalty_amount": "USD 7,500 per violation",
        "dsr_deadline_days": 45,
        "dsr_extension_days": 45,
        "dsr_ack_business_days": 10,
        "legal_bases": ["notice_and_opt_out"],
        "key_obligations": [
            "Privacy notice at collection (§1798.100)",
            "Right to opt-out of sale/sharing (§1798.120)",
            "Do Not Sell or Share link (§1798.135)",
            "Honor Global Privacy Control signal",
            "Annual metrics disclosure",
            "Service provider contract requirements",
            "Risk assessments for high-risk processing (CPRA)",
            "Limit use of sensitive personal information",
        ],
        "data_subject_rights": ["access", "deletion", "correction", "opt_out_sale", "limit_sensitive", "portability"],
    },
    "lgpd": {
        "name": "LGPD (Brazil)",
        "full_name": "Lei Geral de Proteção de Dados (Law 13,709/2018)",
        "territorial_scope": ["BR"],
        "applies_when": "Processing personal data collected in Brazil or of individuals in Brazil",
        "dpo_required": True,
        "breach_notification_hours": None,
        "max_penalty_pct": 2.0,
        "max_penalty_amount": "BRL 50M per violation",
        "dsr_deadline_days": 15,
        "dsr_extension_days": 0,
        "legal_bases": ["consent", "legal_obligation", "public_policy", "research", "contract", "legitimate_interests",
                        "health_protection", "credit_protection", "life_protection", "regulatory_exercise"],
        "key_obligations": [
            "Lawful basis for processing (Art. 7)",
            "Data subject rights (Art. 18)",
            "DPO appointment (Art. 41) — called Encarregado",
            "International transfer restrictions (Art. 33)",
            "Breach notification to ANPD (Art. 48)",
            "Privacy Impact Assessment (Art. 38)",
            "Records of processing activities (Art. 37)",
        ],
        "data_subject_rights": ["access", "correction", "anonymization", "portability", "deletion", "information_sharing",
                                "consent_info", "objection", "review_automated"],
    },
    "popia": {
        "name": "POPIA (South Africa)",
        "full_name": "Protection of Personal Information Act 4 of 2013",
        "territorial_scope": ["ZA"],
        "applies_when": "Processing personal information of South African data subjects",
        "dpo_required": True,
        "breach_notification_hours": None,
        "max_penalty_pct": None,
        "max_penalty_amount": "ZAR 10M or imprisonment",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 0,
        "legal_bases": ["consent", "contract", "legal_obligation", "legitimate_interests", "public_law", "public_interest"],
        "key_obligations": [
            "Lawful processing conditions (Section 9-12)",
            "Information Officer registration (Section 55)",
            "Security safeguards (Section 19)",
            "Breach notification to Information Regulator (Section 22)",
            "Cross-border transfer restrictions (Section 72)",
            "Data subject rights (Section 23-25)",
        ],
        "data_subject_rights": ["access", "correction", "deletion", "objection"],
    },
    "pipeda": {
        "name": "PIPEDA (Canada)",
        "full_name": "Personal Information Protection and Electronic Documents Act",
        "territorial_scope": ["CA"],
        "applies_when": "Commercial activity involving personal information in Canada",
        "dpo_required": True,
        "breach_notification_hours": None,
        "max_penalty_pct": None,
        "max_penalty_amount": "CAD 100,000 per violation",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 30,
        "legal_bases": ["consent", "legitimate_purpose"],
        "key_obligations": [
            "10 fair information principles (Schedule 1)",
            "Meaningful consent requirements",
            "Breach notification to OPC and individuals",
            "Privacy Officer designation (Principle 1)",
            "Breach record-keeping",
            "Cross-border transfer accountability",
        ],
        "data_subject_rights": ["access", "correction", "withdrawal_consent", "complaint"],
    },
    "pdpa": {
        "name": "PDPA (Singapore)",
        "full_name": "Personal Data Protection Act 2012",
        "territorial_scope": ["SG"],
        "applies_when": "Organization collecting, using, or disclosing personal data in Singapore",
        "dpo_required": True,
        "breach_notification_hours": 72,
        "max_penalty_pct": None,
        "max_penalty_amount": "SGD 1M or 10% annual turnover",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 0,
        "legal_bases": ["consent", "legitimate_interests", "business_improvement", "contractual_necessity"],
        "key_obligations": [
            "Consent obligation",
            "Purpose limitation obligation",
            "Data Protection Officer appointment",
            "Notification obligation (data breaches)",
            "Transfer limitation obligation",
            "Data portability obligation",
            "Do Not Call Registry compliance",
        ],
        "data_subject_rights": ["access", "correction", "portability"],
    },
    "privacy_act_au": {
        "name": "Privacy Act (Australia)",
        "full_name": "Privacy Act 1988 (Cth) with 2024 amendments",
        "territorial_scope": ["AU"],
        "applies_when": "Organization with AUD 3M+ annual turnover handling personal information in Australia",
        "dpo_required": False,
        "breach_notification_hours": None,
        "max_penalty_pct": None,
        "max_penalty_amount": "AUD 50M or 30% turnover or 3x benefit",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 30,
        "legal_bases": ["consent", "reasonable_expectation"],
        "key_obligations": [
            "13 Australian Privacy Principles (APPs)",
            "Notifiable Data Breaches scheme (Part IIIC)",
            "Cross-border disclosure restrictions (APP 8)",
            "Privacy Impact Assessment (for high-risk activities)",
            "Direct marketing opt-out (APP 7)",
        ],
        "data_subject_rights": ["access", "correction", "complaint", "erasure"],
    },
    "pipl": {
        "name": "PIPL (China)",
        "full_name": "Personal Information Protection Law of the PRC",
        "territorial_scope": ["CN"],
        "applies_when": "Processing personal information of individuals in China",
        "dpo_required": True,
        "breach_notification_hours": None,
        "max_penalty_pct": 5.0,
        "max_penalty_amount": "CNY 50M or 5% annual revenue",
        "dsr_deadline_days": 15,
        "dsr_extension_days": 15,
        "legal_bases": ["consent", "contract", "legal_obligation", "public_health", "public_interest", "legitimate_interests"],
        "key_obligations": [
            "Separate consent for sensitive data and cross-border transfers",
            "Data localization (critical information infrastructure)",
            "Security assessment for cross-border transfers",
            "Personal Information Impact Assessment (Art. 55)",
            "DPO appointment for threshold processing",
            "Government access and cooperation requirements",
        ],
        "data_subject_rights": ["access", "correction", "deletion", "portability", "restriction", "automated_decision_explanation"],
    },
    "uk_gdpr": {
        "name": "UK GDPR",
        "full_name": "UK General Data Protection Regulation (retained EU law)",
        "territorial_scope": ["UK"],
        "applies_when": "Processing personal data of UK residents or organization established in UK",
        "dpo_required": True,
        "breach_notification_hours": 72,
        "max_penalty_pct": 4.0,
        "max_penalty_amount": "GBP 17.5M",
        "dsr_deadline_days": 30,
        "dsr_extension_days": 60,
        "legal_bases": ["consent", "contract", "legal_obligation", "vital_interests", "public_task", "legitimate_interests"],
        "key_obligations": [
            "Substantially mirrors GDPR obligations",
            "UK International Data Transfer Agreement (IDTA)",
            "UK Addendum to EU SCCs",
            "ICO registration and fee payment",
            "Breach notification to ICO within 72 hours",
            "UK-specific adequacy decisions for transfers",
        ],
        "data_subject_rights": ["access", "rectification", "erasure", "restriction", "portability", "objection", "automated_decision"],
    },
}

REGION_MAPPING = {
    "EU": ["gdpr"],
    "US": ["ccpa"],
    "US-CA": ["ccpa"],
    "BR": ["lgpd"],
    "ZA": ["popia"],
    "CA": ["pipeda"],
    "SG": ["pdpa"],
    "AU": ["privacy_act_au"],
    "CN": ["pipl"],
    "UK": ["uk_gdpr"],
}

EU_COUNTRIES = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
                "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
                "SI", "ES", "SE", "IS", "LI", "NO"}

CURRENT_PRACTICES_EXPECTED = {
    "consent_mechanism": "Consent collection and management",
    "breach_process": "Breach notification process",
    "retention_policy": "Data retention policy",
    "dpo_appointed": "Data Protection Officer appointed",
    "dsr_process": "Data subject request handling process",
    "privacy_notice": "Privacy notice published",
    "ropa": "Records of processing activities",
    "dpia_process": "Data protection impact assessment process",
    "transfer_mechanism": "International transfer safeguards",
    "vendor_management": "Processor/vendor DPA management",
}


def resolve_regions(locations: List[str]) -> Set[str]:
    """Resolve location codes to applicable regulation keys."""
    regs: Set[str] = set()
    for loc in locations:
        loc_upper = loc.upper().strip()
        if loc_upper in EU_COUNTRIES:
            regs.update(REGION_MAPPING.get("EU", []))
        elif loc_upper in REGION_MAPPING:
            regs.update(REGION_MAPPING[loc_upper])
        elif loc_upper == "EU":
            regs.update(REGION_MAPPING["EU"])
    return regs


def determine_applicable(org_location: str, data_subjects: List[str],
                         data_types: List[str], processing_activities: List[str]) -> List[Dict]:
    """Determine which regulations apply and why."""
    applicable = []
    from_org = resolve_regions([org_location])
    from_subjects = resolve_regions(data_subjects)
    all_regs = from_org | from_subjects

    for reg_key in sorted(all_regs):
        reg = REGULATIONS[reg_key]
        reasons = []
        if reg_key in from_org:
            reasons.append(f"Organization established in scope territory ({org_location})")
        if reg_key in from_subjects:
            matching = [s for s in data_subjects if reg_key in resolve_regions([s])]
            reasons.append(f"Data subjects located in: {', '.join(matching)}")

        risk_factors = []
        if "sensitive" in data_types or "health" in data_types or "biometric" in data_types:
            risk_factors.append("Processes sensitive/special category data — heightened obligations")
        if "children" in data_types:
            risk_factors.append("Processes children's data — additional consent requirements")
        if "profiling" in processing_activities:
            risk_factors.append("Profiling activity — may trigger DPIA and Art. 22 obligations")

        applicable.append({
            "regulation": reg_key,
            "name": reg["name"],
            "full_name": reg["full_name"],
            "reasons": reasons,
            "risk_factors": risk_factors,
            "obligations": reg["key_obligations"],
            "data_subject_rights": reg["data_subject_rights"],
            "dsr_deadline_days": reg["dsr_deadline_days"],
            "dsr_extension_days": reg.get("dsr_extension_days", 0),
            "breach_notification_hours": reg.get("breach_notification_hours"),
            "dpo_required": reg["dpo_required"],
            "max_penalty": reg.get("max_penalty_amount", "N/A"),
        })
    return applicable


def gap_analysis(applicable: List[Dict], current_practices: List[str]) -> List[Dict]:
    """Analyze gaps between current practices and regulatory requirements."""
    gaps = []
    practice_set = set(p.strip().lower() for p in current_practices)

    required_map = {
        "consent_mechanism": ["gdpr", "lgpd", "popia", "pipeda", "pdpa", "pipl", "uk_gdpr"],
        "breach_process": ["gdpr", "ccpa", "lgpd", "popia", "pipeda", "pdpa", "privacy_act_au", "pipl", "uk_gdpr"],
        "retention_policy": ["gdpr", "ccpa", "lgpd", "popia", "pipeda", "pdpa", "privacy_act_au", "pipl", "uk_gdpr"],
        "dpo_appointed": ["gdpr", "lgpd", "popia", "pipeda", "pdpa", "pipl", "uk_gdpr"],
        "dsr_process": ["gdpr", "ccpa", "lgpd", "popia", "pipeda", "pdpa", "privacy_act_au", "pipl", "uk_gdpr"],
        "privacy_notice": ["gdpr", "ccpa", "lgpd", "popia", "pipeda", "pdpa", "privacy_act_au", "pipl", "uk_gdpr"],
        "ropa": ["gdpr", "lgpd", "uk_gdpr"],
        "dpia_process": ["gdpr", "lgpd", "pipl", "uk_gdpr"],
        "transfer_mechanism": ["gdpr", "lgpd", "popia", "pipl", "uk_gdpr"],
        "vendor_management": ["gdpr", "ccpa", "lgpd", "uk_gdpr"],
    }

    applicable_keys = {a["regulation"] for a in applicable}

    for practice_key, required_by in required_map.items():
        affected_regs = [r for r in required_by if r in applicable_keys]
        if not affected_regs:
            continue
        if practice_key not in practice_set:
            risk = "critical" if len(affected_regs) >= 3 else ("high" if len(affected_regs) >= 2 else "medium")
            gaps.append({
                "practice": practice_key,
                "description": CURRENT_PRACTICES_EXPECTED.get(practice_key, practice_key),
                "missing": True,
                "required_by": [REGULATIONS[r]["name"] for r in affected_regs],
                "risk": risk,
            })
    return sorted(gaps, key=lambda g: {"critical": 0, "high": 1, "medium": 2}.get(g["risk"], 3))


def format_text(applicable: List[Dict], gaps: Optional[List[Dict]] = None) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("PRIVACY REGULATION APPLICABILITY REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    if not applicable:
        lines.append("\nNo applicable regulations identified for the given parameters.")
        return "\n".join(lines)

    lines.append(f"\nApplicable Regulations: {len(applicable)}\n")

    for reg in applicable:
        lines.append("-" * 50)
        lines.append(f"  {reg['name']}")
        lines.append(f"  {reg['full_name']}")
        lines.append(f"  Reasons:")
        for r in reg["reasons"]:
            lines.append(f"    - {r}")
        if reg["risk_factors"]:
            lines.append(f"  Risk Factors:")
            for rf in reg["risk_factors"]:
                lines.append(f"    ! {rf}")
        lines.append(f"  DPO Required: {'Yes' if reg['dpo_required'] else 'No'}")
        lines.append(f"  DSR Deadline: {reg['dsr_deadline_days']} days (ext. +{reg['dsr_extension_days']}d)")
        breach = reg.get("breach_notification_hours")
        lines.append(f"  Breach Notification: {f'{breach} hours' if breach else 'As soon as reasonably possible'}")
        lines.append(f"  Max Penalty: {reg['max_penalty']}")
        lines.append(f"  Key Obligations:")
        for ob in reg["obligations"]:
            lines.append(f"    - {ob}")
        lines.append(f"  Data Subject Rights: {', '.join(reg['data_subject_rights'])}")
        lines.append("")

    if gaps is not None:
        lines.append("=" * 70)
        lines.append("GAP ANALYSIS")
        lines.append("=" * 70)
        if not gaps:
            lines.append("\nNo gaps identified — all expected practices in place.")
        else:
            for g in gaps:
                risk_icon = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]"}.get(g["risk"], "[?]")
                lines.append(f"\n{risk_icon} {g['risk'].upper()}: {g['description']}")
                lines.append(f"    Status: MISSING")
                lines.append(f"    Required by: {', '.join(g['required_by'])}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Determine applicable privacy regulations for an organization"
    )
    parser.add_argument("--org-location", required=True, help="Organization HQ (ISO code: DE, US-CA, SG, etc.)")
    parser.add_argument("--data-subjects", required=True, help="Data subject locations (comma-separated: EU,US,BR)")
    parser.add_argument("--data-types", required=True, help="Data types (comma-separated: personal,sensitive,financial,health,biometric,children)")
    parser.add_argument("--processing-activities", required=True, help="Activities (comma-separated: marketing,analytics,hr,ecommerce,profiling,healthcare,research)")
    parser.add_argument("--current-practices", default=None, help="Current practices for gap analysis (comma-separated)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    try:
        subjects = [s.strip() for s in args.data_subjects.split(",")]
        data_types = [d.strip() for d in args.data_types.split(",")]
        activities = [a.strip() for a in args.processing_activities.split(",")]

        applicable = determine_applicable(args.org_location, subjects, data_types, activities)

        gaps = None
        if args.current_practices:
            practices = [p.strip() for p in args.current_practices.split(",")]
            gaps = gap_analysis(applicable, practices)

        if args.json:
            output = {
                "report_date": datetime.now().isoformat(),
                "parameters": {
                    "org_location": args.org_location,
                    "data_subjects": subjects,
                    "data_types": data_types,
                    "processing_activities": activities,
                },
                "applicable_regulations": applicable,
                "total_applicable": len(applicable),
            }
            if gaps is not None:
                output["gap_analysis"] = gaps
                output["total_gaps"] = len(gaps)
            print(json.dumps(output, indent=2))
        else:
            print(format_text(applicable, gaps))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
