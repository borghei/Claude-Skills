#!/usr/bin/env python3
"""
DPIA Threshold Checker

Evaluates whether a GDPR Article 35 Data Protection Impact Assessment is
required based on processing activity description. Checks Art. 35(3) mandatory
triggers and 9 EDPB criteria with two-criterion presumption rule.

Usage:
    python dpia_threshold_checker.py --activity "AI-based credit scoring of retail customers"
    python dpia_threshold_checker.py --input processing.json --json
    python dpia_threshold_checker.py --template > processing.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Art. 35(3) mandatory triggers
ART35_TRIGGERS: Dict[str, Dict[str, Any]] = {
    "automated_decision_making": {"article": "Art. 35(3)(a)", "description": "Systematic and extensive evaluation based on automated processing producing legal/significant effects", "keywords": ["automated decision", "credit scor", "profiling", "algorithmic decision", "automated processing", "legal effect", "significant effect", "ai-based decision", "machine learning decision", "automated reject", "automated approv", "scoring model", "risk scoring", "eligibility determination"]},
    "large_scale_special_category": {"article": "Art. 35(3)(b)", "description": "Large-scale processing of special categories (Art. 9) or criminal data (Art. 10)", "keywords": ["health data", "genetic data", "biometric", "racial", "ethnic origin", "political opinion", "religious belief", "trade union", "sexual orientation", "criminal record", "criminal conviction", "offence data", "medical record", "patient data", "health record", "special category", "sensitive data"]},
    "systematic_monitoring": {"article": "Art. 35(3)(c)", "description": "Systematic monitoring of a publicly accessible area on a large scale", "keywords": ["cctv", "video surveillance", "public area monitoring", "facial recognition", "public space", "smart city", "traffic monitoring", "crowd monitoring", "body camera", "drone surveillance", "public wifi tracking", "location tracking public"]},
}

# 9 EDPB criteria (WP 248 rev.01)
EDPB_CRITERIA: Dict[str, Dict[str, Any]] = {
    "evaluation_scoring": {"number": 1, "description": "Evaluation or scoring, including profiling and predicting", "keywords": ["scoring", "profiling", "rating", "ranking", "evaluation", "prediction", "behavioral analysis", "personality assessment", "credit score", "risk assessment", "performance score"]},
    "automated_decision_legal_effect": {"number": 2, "description": "Automated decision-making with legal or similarly significant effect", "keywords": ["automated decision", "legal effect", "significant effect", "contract denial", "service denial", "automated reject", "credit decision", "insurance pricing", "employment decision"]},
    "systematic_monitoring": {"number": 3, "description": "Systematic monitoring", "keywords": ["monitoring", "surveillance", "tracking", "observation", "cctv", "employee monitoring", "internet monitoring", "gps tracking", "email monitoring", "keystroke logging", "screen monitoring"]},
    "sensitive_data": {"number": 4, "description": "Sensitive data or data of a highly personal nature", "keywords": ["health", "genetic", "biometric", "racial", "ethnic", "political", "religious", "trade union", "sexual", "criminal", "financial", "location data", "communication content", "browsing history", "children", "minor", "vulnerable"]},
    "large_scale": {"number": 5, "description": "Data processed on a large scale", "keywords": ["large scale", "millions", "thousands", "nationwide", "country-wide", "regional", "all customers", "all employees", "all users", "population", "extensive", "mass processing", "bulk"]},
    "matching_combining": {"number": 6, "description": "Matching or combining datasets", "keywords": ["matching", "combining", "merging", "cross-referenc", "data fusion", "data linking", "dataset combination", "enrichment", "augmenting", "multiple sources", "third-party data", "data broker"]},
    "vulnerable_subjects": {"number": 7, "description": "Data concerning vulnerable data subjects", "keywords": ["children", "minor", "elderly", "patient", "mentally ill", "employee", "asylum seeker", "refugee", "student", "disabled", "vulnerable", "power imbalance", "dependent"]},
    "innovative_technology": {"number": 8, "description": "Innovative use or applying new technological or organisational solutions", "keywords": ["ai", "artificial intelligence", "machine learning", "deep learning", "blockchain", "iot", "smart device", "fingerprint", "facial recognition", "voice recognition", "neural network", "generative ai", "llm", "novel", "innovative", "new technology", "emerging technology"]},
    "preventing_right_or_service": {"number": 9, "description": "Processing preventing exercise of a right or use of service/contract", "keywords": ["prevent access", "deny service", "block", "restrict access", "gatekeeping", "eligibility check", "mandatory processing", "no opt-out", "compulsory", "required processing", "prerequisite"]},
}


def generate_template() -> Dict[str, Any]:
    """Generate a blank processing activity template."""
    return {"activity_name": "", "description": "", "purpose": "", "legal_basis": "",
            "data_categories": [], "data_subjects": [], "recipients": [],
            "retention_period": "", "international_transfers": False, "transfer_destinations": [],
            "automated_decision_making": False, "special_category_data": False,
            "large_scale": False, "systematic_monitoring": False,
            "innovative_technology": False, "vulnerable_data_subjects": False, "notes": ""}


def check_keywords(text: str, keywords: List[str]) -> Tuple[bool, List[str]]:
    """Check if any keywords match in the text. Returns (matched, matching_keywords)."""
    text_lower = text.lower()
    matched: List[str] = []
    for kw in keywords:
        if kw.lower() in text_lower:
            matched.append(kw)
    return len(matched) > 0, matched


def build_activity_text(data: Dict[str, Any]) -> str:
    """Build searchable text from structured input."""
    parts: List[str] = []
    for key in ["activity_name", "description", "purpose", "notes"]:
        val = data.get(key, "")
        if val:
            parts.append(str(val))

    for key in ["data_categories", "data_subjects", "recipients", "transfer_destinations"]:
        val = data.get(key, [])
        if isinstance(val, list):
            parts.extend(str(v) for v in val)

    # Add explicit flags as text
    flag_map = {
        "automated_decision_making": "automated decision making with legal effect",
        "special_category_data": "special category sensitive data health biometric",
        "large_scale": "large scale processing nationwide millions",
        "systematic_monitoring": "systematic monitoring surveillance tracking",
        "innovative_technology": "innovative technology AI machine learning",
        "vulnerable_data_subjects": "vulnerable data subjects children employees patients",
    }
    for flag, text in flag_map.items():
        if data.get(flag, False):
            parts.append(text)

    return " ".join(parts)


def assess_art35_triggers(text: str) -> List[Dict[str, Any]]:
    """Check Art. 35(3) mandatory triggers."""
    triggered: List[Dict[str, Any]] = []
    for trigger_id, trigger in ART35_TRIGGERS.items():
        matched, keywords = check_keywords(text, trigger["keywords"])
        if matched:
            triggered.append({
                "id": trigger_id,
                "article": trigger["article"],
                "description": trigger["description"],
                "matched_keywords": keywords,
            })
    return triggered


def assess_edpb_criteria(text: str) -> List[Dict[str, Any]]:
    """Check EDPB 9 criteria and return matched criteria."""
    matched_criteria: List[Dict[str, Any]] = []
    for criterion_id, criterion in EDPB_CRITERIA.items():
        matched, keywords = check_keywords(text, criterion["keywords"])
        if matched:
            matched_criteria.append({
                "id": criterion_id,
                "number": criterion["number"],
                "description": criterion["description"],
                "matched_keywords": keywords,
            })
    return matched_criteria


def determine_verdict(
    art35_triggers: List[Dict[str, Any]],
    edpb_matches: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """Determine DPIA verdict. Returns (verdict, reasoning)."""
    # Art. 35(3) mandatory triggers
    if art35_triggers:
        trigger_names = [t["article"] for t in art35_triggers]
        return (
            "REQUIRED",
            f"Art. 35(3) mandatory trigger(s) matched: {', '.join(trigger_names)}. "
            f"DPIA is legally required before processing begins.",
        )

    # Two-criterion presumption (WP 248 rev.01)
    edpb_count = len(edpb_matches)
    if edpb_count >= 2:
        criteria_nums = [str(m["number"]) for m in edpb_matches]
        return (
            "REQUIRED",
            f"{edpb_count} of 9 EDPB criteria met (criteria {', '.join(criteria_nums)}). "
            f"Two-criterion presumption applies per WP 248 rev.01. "
            f"DPIA is presumptively required. Controller may rebut with documented justification.",
        )

    # Single criterion — recommended
    if edpb_count == 1:
        return (
            "RECOMMENDED",
            f"1 of 9 EDPB criteria met (criterion {edpb_matches[0]['number']}). "
            f"Two-criterion presumption not triggered, but DPIA is recommended as good practice. "
            f"Document rationale if not conducting DPIA.",
        )

    # No matches
    return (
        "NOT_REQUIRED",
        "No Art. 35(3) triggers matched and no EDPB criteria met. "
        "DPIA is not required based on the information provided. "
        "Document this assessment. Re-evaluate if processing scope changes.",
    )


def format_human(
    verdict: str,
    reasoning: str,
    art35_triggers: List[Dict[str, Any]],
    edpb_matches: List[Dict[str, Any]],
) -> str:
    """Format results for human-readable output."""
    lines: List[str] = [
        "=" * 65,
        "DPIA THRESHOLD ASSESSMENT",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 65,
        "",
        f"VERDICT: {verdict}",
        "",
        f"Reasoning: {reasoning}",
        "",
    ]

    if art35_triggers:
        lines.append("ART. 35(3) MANDATORY TRIGGERS MATCHED:")
        lines.append("-" * 45)
        for t in art35_triggers:
            lines.append(f"  [{t['article']}] {t['description']}")
            lines.append(f"    Matched indicators: {', '.join(t['matched_keywords'][:5])}")
        lines.append("")

    lines.append(f"EDPB CRITERIA ASSESSMENT ({len(edpb_matches)} of 9 met):")
    lines.append("-" * 45)

    all_criteria_ids = sorted(EDPB_CRITERIA.keys(), key=lambda k: EDPB_CRITERIA[k]["number"])
    matched_ids = {m["id"] for m in edpb_matches}

    for cid in all_criteria_ids:
        criterion = EDPB_CRITERIA[cid]
        status = "MET" if cid in matched_ids else "---"
        match_info = ""
        if cid in matched_ids:
            match = next(m for m in edpb_matches if m["id"] == cid)
            match_info = f" (indicators: {', '.join(match['matched_keywords'][:3])})"
        lines.append(f"  [{status}] {criterion['number']}. {criterion['description']}{match_info}")

    lines.append("")

    two_crit = len(edpb_matches) >= 2
    lines.append(f"Two-criterion presumption: {'APPLIES' if two_crit else 'Does not apply'}")
    lines.append("")

    # Recommendations
    lines.append("NEXT STEPS:")
    lines.append("-" * 45)
    if verdict == "REQUIRED":
        lines.append("  1. Conduct full DPIA before processing begins (Art. 35(1))")
        lines.append("  2. Document processing description, necessity, proportionality")
        lines.append("  3. Identify and assess risks from data subject perspective")
        lines.append("  4. Apply mitigations and calculate residual risk")
        lines.append("  5. Consult DPO (Art. 35(2))")
        lines.append("  6. If residual risk high, consider Art. 36 prior consultation with SA")
    elif verdict == "RECOMMENDED":
        lines.append("  1. Consider conducting DPIA as best practice")
        lines.append("  2. Document rationale if not conducting DPIA")
        lines.append("  3. Monitor for changes that could trigger additional criteria")
    else:
        lines.append("  1. Document this threshold assessment")
        lines.append("  2. Re-evaluate if processing scope or nature changes")
        lines.append("  3. Check national SA blacklists for jurisdiction-specific requirements")

    lines.append("")
    lines.append("=" * 65)
    return "\n".join(lines)


def format_json(
    activity_text: str,
    verdict: str,
    reasoning: str,
    art35_triggers: List[Dict[str, Any]],
    edpb_matches: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format results as JSON."""
    return {
        "assessment_date": datetime.now().isoformat(),
        "verdict": verdict,
        "reasoning": reasoning,
        "art35_triggers": art35_triggers,
        "edpb_criteria": {
            "total_met": len(edpb_matches),
            "two_criterion_presumption": len(edpb_matches) >= 2,
            "matched": edpb_matches,
        },
        "activity_summary": activity_text[:200] if activity_text else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DPIA Threshold Checker — Art. 35(3) triggers and EDPB criteria"
    )
    parser.add_argument("--activity", type=str, help="Processing activity description text")
    parser.add_argument("--input", type=str, help="JSON file with processing activity details")
    parser.add_argument("--template", action="store_true", help="Generate blank input template")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if args.template:
        print(json.dumps(generate_template(), indent=2))
        return

    # Get activity text
    activity_text: str = ""
    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(path, "r") as f:
                data = json.load(f)
            activity_text = build_activity_text(data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.activity:
        activity_text = args.activity
    else:
        parser.error("Provide --activity, --input, or --template")

    if not activity_text.strip():
        print("Error: Activity description is empty", file=sys.stderr)
        sys.exit(1)

    # Run assessment
    art35_triggers = assess_art35_triggers(activity_text)
    edpb_matches = assess_edpb_criteria(activity_text)
    verdict, reasoning = determine_verdict(art35_triggers, edpb_matches)

    # Output
    if args.json:
        result = format_json(activity_text, verdict, reasoning, art35_triggers, edpb_matches)
        print(json.dumps(result, indent=2))
    else:
        print(format_human(verdict, reasoning, art35_triggers, edpb_matches))


if __name__ == "__main__":
    main()
