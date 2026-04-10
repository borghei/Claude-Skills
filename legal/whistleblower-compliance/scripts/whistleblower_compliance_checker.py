#!/usr/bin/env python3
"""
Whistleblower Compliance Checker

Assesses an existing whistleblower system against regulatory requirements
for EU Directive 2019/1937, US SOX/Dodd-Frank, and UK PIDA.

Usage:
    python whistleblower_compliance_checker.py --jurisdiction EU --headcount 300 --sector financial
    python whistleblower_compliance_checker.py --jurisdiction US --headcount 5000 --sector healthcare --json
    python whistleblower_compliance_checker.py --jurisdiction UK --headcount 50 --sector technology --channels internal,external
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# Priority levels
CRITICAL = "CRITICAL"
IMPORTANT = "IMPORTANT"
IMPROVEMENT = "IMPROVEMENT"


# Jurisdiction-specific requirements
REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    "EU": {
        "name": "EU Directive 2019/1937",
        "headcount_threshold": 50,
        "public_sector_all": True,
        "acknowledgment_days": 7,
        "feedback_months": 3,
        "requires_internal_channel": True,
        "requires_confidentiality": True,
        "requires_gdpr": True,
        "requires_designated_person": True,
        "requires_dissemination": True,
        "regulated_sectors": ["financial", "transport", "nuclear", "defense", "healthcare",
                              "environment", "food_safety", "public_procurement"],
    },
    "US": {
        "name": "SOX Section 806 / Dodd-Frank",
        "headcount_threshold": 0,
        "public_sector_all": False,
        "acknowledgment_days": None,
        "feedback_months": None,
        "requires_internal_channel": True,
        "requires_confidentiality": True,
        "requires_gdpr": False,
        "requires_designated_person": True,
        "requires_dissemination": True,
        "filing_deadline_days": 180,
        "regulated_sectors": ["financial", "healthcare", "defense", "energy"],
    },
    "UK": {
        "name": "Public Interest Disclosure Act 1998",
        "headcount_threshold": 0,
        "public_sector_all": True,
        "acknowledgment_days": None,
        "feedback_months": None,
        "requires_internal_channel": True,
        "requires_confidentiality": True,
        "requires_gdpr": True,
        "requires_designated_person": True,
        "requires_dissemination": True,
        "regulated_sectors": ["financial", "healthcare", "nuclear", "defense"],
    },
}

# Sector-specific additional checks
SECTOR_CHECKS: Dict[str, List[str]] = {
    "financial": [
        "Anti-money laundering reporting integration",
        "Financial regulator notification procedures",
        "Market abuse reporting channel separation",
    ],
    "healthcare": [
        "Patient safety reporting integration",
        "Clinical governance alignment",
        "Professional body notification procedures",
    ],
    "defense": [
        "Security clearance considerations for designated persons",
        "Classified information handling procedures",
    ],
    "nuclear": [
        "Nuclear safety authority notification procedures",
        "Radiation safety incident integration",
    ],
}


def build_gap(phase: str, checkpoint: str, priority: str, detail: str) -> Dict[str, str]:
    """Build a structured gap finding."""
    return {
        "phase": phase,
        "checkpoint": checkpoint,
        "priority": priority,
        "detail": detail,
    }


def assess_applicability(
    jurisdiction: str, headcount: int, sector: str, reqs: Dict[str, Any]
) -> Tuple[List[Dict], int, int]:
    """Phase 1: Assess applicability (3 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 3

    # Check 1: Headcount threshold
    if headcount >= reqs["headcount_threshold"] or reqs["public_sector_all"]:
        passed += 1
    else:
        gaps.append(build_gap(
            "1. Applicability", "Headcount threshold", IMPROVEMENT,
            f"Organization has {headcount} employees; threshold is {reqs['headcount_threshold']}. "
            "Voluntary adoption still recommended."
        ))

    # Check 2: Jurisdiction applicability
    passed += 1  # Always applicable if user specified jurisdiction

    # Check 3: Sector determination
    if sector in reqs.get("regulated_sectors", []):
        passed += 1
    else:
        passed += 1  # Non-regulated sectors still pass, just no extra requirements

    return gaps, passed, total


def assess_reception_channel(
    channels: List[str], reqs: Dict[str, Any]
) -> Tuple[List[Dict], int, int]:
    """Phase 2: Assess reception channels (5 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 5

    has_internal = "internal" in channels
    has_external = "external" in channels
    has_any = has_internal or has_external

    # Check 1: System exists
    if has_any:
        passed += 1
    else:
        gaps.append(build_gap(
            "2. Reception Channel", "System existence", CRITICAL,
            "No whistleblower reporting channel exists. Mandatory under applicable regulation."
        ))

    # Check 2: Internal channel
    if has_internal:
        passed += 1
    else:
        gaps.append(build_gap(
            "2. Reception Channel", "Internal channel", CRITICAL if reqs["requires_internal_channel"] else IMPORTANT,
            "No internal reporting channel. Internal channels are the preferred first point of contact."
        ))

    # Check 3: External channel awareness
    if has_external:
        passed += 1
    else:
        gaps.append(build_gap(
            "2. Reception Channel", "External channel", IMPORTANT,
            "No external reporting channel or awareness of regulatory authority reporting options."
        ))

    # Check 4: Written/oral/in-person options
    if has_internal:
        passed += 1  # Assume basic channel supports at least one mode
    else:
        gaps.append(build_gap(
            "2. Reception Channel", "Multiple report modes", IMPROVEMENT,
            "Best practice: offer written, oral, and in-person reporting options."
        ))

    # Check 5: Anonymous reporting option
    if has_any:
        passed += 1  # Score as pass but flag improvement
        gaps.append(build_gap(
            "2. Reception Channel", "Anonymous reporting", IMPROVEMENT,
            "Consider enabling anonymous reporting to increase reporter confidence."
        ))
    else:
        total -= 1  # Skip if no channels at all

    return gaps, passed, total


def assess_designated_persons(has_designated: bool, reqs: Dict[str, Any]) -> Tuple[List[Dict], int, int]:
    """Phase 3: Assess designated persons (7 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 7

    if has_designated:
        passed += 4  # Existence, appointment, training baseline, contact info
        # Flag remaining items as improvements
        gaps.append(build_gap(
            "3. Designated Persons", "Independence verification", IMPORTANT,
            "Verify designated person(s) have no conflicts of interest and report independently."
        ))
        gaps.append(build_gap(
            "3. Designated Persons", "Backup designation", IMPROVEMENT,
            "Ensure backup designated person is appointed for absence/conflict scenarios."
        ))
        gaps.append(build_gap(
            "3. Designated Persons", "Specialized training", IMPROVEMENT,
            "Confirm designated persons receive annual training on investigation procedures."
        ))
    else:
        gaps.append(build_gap(
            "3. Designated Persons", "Person appointed", CRITICAL,
            "No designated person appointed for receiving and processing whistleblower reports."
        ))
        passed += 0

    return gaps, passed, total


def assess_verification_processing(
    has_ack_timeline: bool, has_feedback_timeline: bool, reqs: Dict[str, Any]
) -> Tuple[List[Dict], int, int]:
    """Phase 4: Assess verification and processing (8 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 8

    # Acknowledgment timeline
    if reqs.get("acknowledgment_days"):
        if has_ack_timeline:
            passed += 1
        else:
            gaps.append(build_gap(
                "4. Verification/Processing", "Acknowledgment timeline",
                CRITICAL,
                f"Reports must be acknowledged within {reqs['acknowledgment_days']} days."
            ))
    else:
        passed += 1  # Not required in this jurisdiction

    # Feedback timeline
    if reqs.get("feedback_months"):
        if has_feedback_timeline:
            passed += 1
        else:
            gaps.append(build_gap(
                "4. Verification/Processing", "Feedback timeline",
                CRITICAL,
                f"Feedback must be provided within {reqs['feedback_months']} months."
            ))
    else:
        passed += 1

    # Standard process checks (scored generously with improvement flags)
    passed += 3  # Triage process, investigation procedure, documentation
    gaps.append(build_gap(
        "4. Verification/Processing", "Written investigation procedure", IMPORTANT,
        "Ensure formal written investigation procedure exists with defined steps."
    ))
    gaps.append(build_gap(
        "4. Verification/Processing", "Case tracking system", IMPROVEMENT,
        "Implement case tracking with unique identifiers and audit trail."
    ))
    gaps.append(build_gap(
        "4. Verification/Processing", "Outcome communication", IMPORTANT,
        "Document and communicate investigation outcomes to the reporter."
    ))

    return gaps, passed, total


def assess_confidentiality(has_confidentiality: bool) -> Tuple[List[Dict], int, int]:
    """Phase 5: Assess confidentiality measures (9 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 9

    if has_confidentiality:
        passed += 5
        gaps.append(build_gap(
            "5. Confidentiality", "Access controls", IMPORTANT,
            "Verify only designated persons can access reporter identity information."
        ))
        gaps.append(build_gap(
            "5. Confidentiality", "Secure communication channel", IMPORTANT,
            "Ensure reporting channel uses encrypted/secure communication."
        ))
        gaps.append(build_gap(
            "5. Confidentiality", "Consent for identity disclosure", IMPROVEMENT,
            "Document process for obtaining reporter consent before identity disclosure."
        ))
        gaps.append(build_gap(
            "5. Confidentiality", "Penalty for breach", IMPROVEMENT,
            "Define disciplinary consequences for unauthorized identity disclosure."
        ))
    else:
        gaps.append(build_gap(
            "5. Confidentiality", "Confidentiality measures", CRITICAL,
            "No confidentiality measures in place. Reporter identity protection is mandatory."
        ))

    return gaps, passed, total


def assess_dissemination(has_dissemination: bool) -> Tuple[List[Dict], int, int]:
    """Phase 6: Assess dissemination and information (10 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 10

    if has_dissemination:
        passed += 5
        gaps.append(build_gap(
            "6. Dissemination", "Employee training", IMPORTANT,
            "All employees should receive training on whistleblower procedures."
        ))
        gaps.append(build_gap(
            "6. Dissemination", "Contractor/vendor coverage", IMPORTANT,
            "Extend whistleblower information to contractors and business partners."
        ))
        gaps.append(build_gap(
            "6. Dissemination", "Regular reminders", IMPROVEMENT,
            "Schedule periodic reminders about reporting channels and protections."
        ))
        gaps.append(build_gap(
            "6. Dissemination", "Multilingual availability", IMPROVEMENT,
            "Provide policy in all languages used by the workforce."
        ))
        gaps.append(build_gap(
            "6. Dissemination", "Website/intranet publication", IMPROVEMENT,
            "Publish policy on company intranet and/or public website."
        ))
    else:
        gaps.append(build_gap(
            "6. Dissemination", "Policy dissemination", CRITICAL,
            "Whistleblower policy not disseminated to personnel. Awareness is mandatory."
        ))

    return gaps, passed, total


def assess_data_protection(has_gdpr: bool, reqs: Dict[str, Any]) -> Tuple[List[Dict], int, int]:
    """Phase 7: Assess data protection/GDPR (12 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    total = 12

    if not reqs["requires_gdpr"]:
        # GDPR not applicable but basic data protection still relevant
        total = 6
        if has_gdpr:
            passed += 4
        else:
            passed += 2
            gaps.append(build_gap(
                "7. Data Protection", "Data protection measures", IMPORTANT,
                "Implement basic data protection for whistleblower report data."
            ))
        gaps.append(build_gap(
            "7. Data Protection", "Retention policy", IMPORTANT,
            "Define data retention period for whistleblower reports and investigation files."
        ))
        gaps.append(build_gap(
            "7. Data Protection", "Secure storage", IMPROVEMENT,
            "Ensure whistleblower data is stored securely with access controls."
        ))
    else:
        if has_gdpr:
            passed += 7
            gaps.append(build_gap(
                "7. Data Protection", "DPIA completion", IMPORTANT,
                "Complete Data Protection Impact Assessment for whistleblower processing."
            ))
            gaps.append(build_gap(
                "7. Data Protection", "Legal basis documentation", IMPORTANT,
                "Document legal basis for processing under Art. 6 GDPR."
            ))
            gaps.append(build_gap(
                "7. Data Protection", "Data subject rights", IMPROVEMENT,
                "Define procedures for handling data subject rights in whistleblower context."
            ))
            gaps.append(build_gap(
                "7. Data Protection", "Cross-border transfer", IMPROVEMENT,
                "Address cross-border data transfer requirements if applicable."
            ))
            gaps.append(build_gap(
                "7. Data Protection", "Retention schedule", IMPROVEMENT,
                "Implement automated retention and deletion schedule."
            ))
        else:
            gaps.append(build_gap(
                "7. Data Protection", "GDPR compliance", CRITICAL,
                "No GDPR measures for whistleblower data processing. Mandatory under EU/UK regulation."
            ))

    return gaps, passed, total


def assess_sector_specific(sector: str, reqs: Dict[str, Any]) -> Tuple[List[Dict], int, int]:
    """Phase 8: Assess sector-specific requirements (6 checkpoints)."""
    gaps: List[Dict] = []
    passed = 0
    checks = SECTOR_CHECKS.get(sector, [])
    total = max(len(checks), 2)

    if not checks:
        # Non-regulated sector: basic checks only
        passed += 2
        return gaps, passed, total

    for check in checks:
        gaps.append(build_gap(
            "8. Sector-Specific", check, IMPORTANT,
            f"Verify sector-specific requirement: {check}"
        ))

    passed += max(0, total - len(checks))
    return gaps, passed, total


def run_assessment(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the full compliance assessment."""
    jurisdiction = args.jurisdiction
    headcount = args.headcount
    sector = args.sector
    channels = [c.strip() for c in args.channels.split(",")] if args.channels else []
    reqs = REQUIREMENTS[jurisdiction]

    all_gaps: List[Dict] = []
    total_passed = 0
    total_checks = 0

    # Run all 8 phases
    phases = [
        ("1. Applicability", assess_applicability(jurisdiction, headcount, sector, reqs)),
        ("2. Reception Channel", assess_reception_channel(channels, reqs)),
        ("3. Designated Persons", assess_designated_persons(args.has_designated_person, reqs)),
        ("4. Verification/Processing", assess_verification_processing(
            args.has_acknowledgment_timeline, args.has_feedback_timeline, reqs)),
        ("5. Confidentiality", assess_confidentiality(args.has_confidentiality)),
        ("6. Dissemination", assess_dissemination(args.has_dissemination)),
        ("7. Data Protection", assess_data_protection(args.has_gdpr_measures, reqs)),
        ("8. Sector-Specific", assess_sector_specific(sector, reqs)),
    ]

    phase_results = []
    for phase_name, (gaps, passed, total) in phases:
        all_gaps.extend(gaps)
        total_passed += passed
        total_checks += total
        pct = round((passed / total) * 100, 1) if total > 0 else 100.0
        phase_results.append({
            "phase": phase_name,
            "passed": passed,
            "total": total,
            "score_pct": pct,
        })

    overall_score = round((total_passed / total_checks) * 100, 1) if total_checks > 0 else 0.0

    critical_count = sum(1 for g in all_gaps if g["priority"] == CRITICAL)
    important_count = sum(1 for g in all_gaps if g["priority"] == IMPORTANT)
    improvement_count = sum(1 for g in all_gaps if g["priority"] == IMPROVEMENT)

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "jurisdiction": jurisdiction,
        "regulation": reqs["name"],
        "headcount": headcount,
        "sector": sector,
        "channels": channels,
        "overall_score_pct": overall_score,
        "total_passed": total_passed,
        "total_checks": total_checks,
        "gap_summary": {
            "critical": critical_count,
            "important": important_count,
            "improvement": improvement_count,
            "total": len(all_gaps),
        },
        "phase_results": phase_results,
        "gaps": all_gaps,
    }


def format_text(result: Dict[str, Any]) -> str:
    """Format assessment result as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("WHISTLEBLOWER COMPLIANCE ASSESSMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"Date:          {result['assessment_date']}")
    lines.append(f"Jurisdiction:  {result['jurisdiction']} ({result['regulation']})")
    lines.append(f"Headcount:     {result['headcount']}")
    lines.append(f"Sector:        {result['sector']}")
    lines.append(f"Channels:      {', '.join(result['channels']) or 'None'}")
    lines.append("")
    lines.append(f"OVERALL SCORE: {result['overall_score_pct']}% "
                 f"({result['total_passed']}/{result['total_checks']} checks passed)")
    lines.append("")

    # Phase breakdown
    lines.append("-" * 70)
    lines.append("PHASE BREAKDOWN")
    lines.append("-" * 70)
    lines.append(f"{'Phase':<35} {'Score':>10} {'Passed':>10}")
    lines.append("-" * 70)
    for p in result["phase_results"]:
        lines.append(f"{p['phase']:<35} {p['score_pct']:>9.1f}% {p['passed']:>4}/{p['total']:<4}")

    # Gap summary
    lines.append("")
    lines.append("-" * 70)
    lines.append("GAP SUMMARY")
    lines.append("-" * 70)
    gs = result["gap_summary"]
    lines.append(f"  CRITICAL:    {gs['critical']}")
    lines.append(f"  IMPORTANT:   {gs['important']}")
    lines.append(f"  IMPROVEMENT: {gs['improvement']}")
    lines.append(f"  TOTAL:       {gs['total']}")

    # Detailed gaps by priority
    for priority in [CRITICAL, IMPORTANT, IMPROVEMENT]:
        priority_gaps = [g for g in result["gaps"] if g["priority"] == priority]
        if priority_gaps:
            lines.append("")
            lines.append(f"--- {priority} GAPS ---")
            for g in priority_gaps:
                lines.append(f"  [{g['phase']}] {g['checkpoint']}")
                lines.append(f"    {g['detail']}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assess whistleblower system compliance against regulatory requirements."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--jurisdiction", required=True, choices=["EU", "US", "UK"],
                        help="Regulatory jurisdiction")
    parser.add_argument("--headcount", required=True, type=int,
                        help="Number of employees")
    parser.add_argument("--sector", required=True,
                        help="Industry sector (financial, healthcare, technology, etc.)")
    parser.add_argument("--channels", default="none",
                        help="Comma-separated channel types: internal, external, none")
    parser.add_argument("--has-designated-person", action="store_true",
                        help="Designated person appointed")
    parser.add_argument("--has-confidentiality", action="store_true",
                        help="Confidentiality measures in place")
    parser.add_argument("--has-gdpr-measures", action="store_true",
                        help="GDPR/data protection measures implemented")
    parser.add_argument("--has-dissemination", action="store_true",
                        help="Policy disseminated to personnel")
    parser.add_argument("--has-acknowledgment-timeline", action="store_true",
                        help="7-day acknowledgment timeline met")
    parser.add_argument("--has-feedback-timeline", action="store_true",
                        help="3-month feedback timeline met")

    args = parser.parse_args()

    try:
        result = run_assessment(args)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
