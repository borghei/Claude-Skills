#!/usr/bin/env python3
"""
Contract Clause Checker

Validate a contract document against required clauses for a given
jurisdiction and engagement type. Identifies missing clauses, incomplete
sections, and jurisdiction-specific compliance gaps.

Usage:
    python contract_clause_checker.py contract.json --jurisdiction us-delaware
    python contract_clause_checker.py contract.json --jurisdiction eu --json
"""

import argparse
import json
import sys


REQUIRED_CLAUSES = {
    "fixed-price": [
        {"clause": "parties", "label": "Parties and legal names", "all_jurisdictions": True},
        {"clause": "scope_of_work", "label": "Scope of Work / Deliverables", "all_jurisdictions": True},
        {"clause": "acceptance_criteria", "label": "Acceptance criteria with sign-off process", "all_jurisdictions": True},
        {"clause": "payment_terms", "label": "Payment terms and schedule", "all_jurisdictions": True},
        {"clause": "ip_assignment", "label": "Intellectual property assignment", "all_jurisdictions": True},
        {"clause": "pre_existing_ip", "label": "Pre-existing IP carve-out", "all_jurisdictions": True},
        {"clause": "confidentiality", "label": "Confidentiality / NDA clause", "all_jurisdictions": True},
        {"clause": "liability_cap", "label": "Liability limitation", "all_jurisdictions": True},
        {"clause": "termination", "label": "Termination for cause and convenience", "all_jurisdictions": True},
        {"clause": "change_order", "label": "Change order process", "all_jurisdictions": True},
        {"clause": "governing_law", "label": "Governing law and dispute resolution", "all_jurisdictions": True},
        {"clause": "force_majeure", "label": "Force majeure", "all_jurisdictions": True},
        {"clause": "warranties", "label": "Warranties and representations", "all_jurisdictions": True},
    ],
    "hourly": [
        {"clause": "parties", "label": "Parties and legal names", "all_jurisdictions": True},
        {"clause": "scope_of_work", "label": "Scope of Work / Services description", "all_jurisdictions": True},
        {"clause": "rate_schedule", "label": "Rate schedule and invoicing terms", "all_jurisdictions": True},
        {"clause": "time_tracking", "label": "Time tracking requirements", "all_jurisdictions": True},
        {"clause": "payment_terms", "label": "Payment terms (net-30 etc.)", "all_jurisdictions": True},
        {"clause": "ip_assignment", "label": "IP assignment", "all_jurisdictions": True},
        {"clause": "confidentiality", "label": "Confidentiality", "all_jurisdictions": True},
        {"clause": "liability_cap", "label": "Liability limitation", "all_jurisdictions": True},
        {"clause": "termination", "label": "Termination with notice period", "all_jurisdictions": True},
        {"clause": "governing_law", "label": "Governing law", "all_jurisdictions": True},
    ],
    "retainer": [
        {"clause": "parties", "label": "Parties and legal names", "all_jurisdictions": True},
        {"clause": "services_description", "label": "Services description", "all_jurisdictions": True},
        {"clause": "retainer_amount", "label": "Monthly retainer amount", "all_jurisdictions": True},
        {"clause": "hours_included", "label": "Hours included and overflow rate", "all_jurisdictions": True},
        {"clause": "payment_terms", "label": "Payment terms (prepaid monthly)", "all_jurisdictions": True},
        {"clause": "sla", "label": "Response time SLAs", "all_jurisdictions": True},
        {"clause": "ip_assignment", "label": "IP assignment", "all_jurisdictions": True},
        {"clause": "confidentiality", "label": "Confidentiality", "all_jurisdictions": True},
        {"clause": "termination", "label": "Termination with notice period", "all_jurisdictions": True},
        {"clause": "governing_law", "label": "Governing law", "all_jurisdictions": True},
    ],
    "nda": [
        {"clause": "parties", "label": "Parties and legal names", "all_jurisdictions": True},
        {"clause": "definition", "label": "Definition of confidential information", "all_jurisdictions": True},
        {"clause": "obligations", "label": "Obligations of receiving party", "all_jurisdictions": True},
        {"clause": "exceptions", "label": "Exceptions to confidentiality", "all_jurisdictions": True},
        {"clause": "term", "label": "Term and duration", "all_jurisdictions": True},
        {"clause": "return_destruction", "label": "Return or destruction of materials", "all_jurisdictions": True},
        {"clause": "governing_law", "label": "Governing law", "all_jurisdictions": True},
    ],
    "msa": [
        {"clause": "parties", "label": "Parties and legal names", "all_jurisdictions": True},
        {"clause": "master_terms", "label": "Master terms and conditions", "all_jurisdictions": True},
        {"clause": "sow_framework", "label": "SOW attachment framework", "all_jurisdictions": True},
        {"clause": "payment_terms", "label": "General payment terms", "all_jurisdictions": True},
        {"clause": "ip_assignment", "label": "IP assignment (default for all SOWs)", "all_jurisdictions": True},
        {"clause": "confidentiality", "label": "Confidentiality", "all_jurisdictions": True},
        {"clause": "liability_cap", "label": "Liability limitation", "all_jurisdictions": True},
        {"clause": "termination", "label": "Termination of master and individual SOWs", "all_jurisdictions": True},
        {"clause": "governing_law", "label": "Governing law", "all_jurisdictions": True},
        {"clause": "amendments", "label": "Amendment process (written only)", "all_jurisdictions": True},
    ],
}

JURISDICTION_EXTRAS = {
    "eu": [
        {"clause": "dpa", "label": "GDPR Data Processing Addendum (Art. 28)", "condition": "personal_data"},
        {"clause": "right_to_withdraw", "label": "Right to withdraw (14-day, B2C only)", "condition": "b2c"},
        {"clause": "ip_deed", "label": "Separate IP assignment deed", "condition": "always"},
    ],
    "dach": [
        {"clause": "dpa", "label": "DSGVO Data Processing Addendum", "condition": "personal_data"},
        {"clause": "nutzungsrechte", "label": "Explicit Nutzungsrechte (usage rights) transfer", "condition": "always"},
        {"clause": "schriftformklausel", "label": "Schriftformklausel (written form clause)", "condition": "always"},
        {"clause": "kuendigungsfristen", "label": "Statutory notice periods (Kuendigungsfristen)", "condition": "always"},
        {"clause": "moral_rights", "label": "Acknowledgment of Urheberpersoernlichkeitsrecht (cannot be transferred)", "condition": "always"},
    ],
    "uk": [
        {"clause": "uk_gdpr", "label": "UK GDPR compliance for data processing", "condition": "personal_data"},
        {"clause": "cdpa", "label": "CDPA 1988 IP provisions", "condition": "always"},
    ],
    "us-delaware": [
        {"clause": "work_for_hire", "label": "Work-for-hire declaration (Copyright Act 101)", "condition": "always"},
        {"clause": "esign_compliance", "label": "ESIGN Act / UETA compliance for e-signatures", "condition": "always"},
    ],
}


def check_contract(data: dict, jurisdiction: str, contract_type: str) -> dict:
    """Check contract against required clauses."""
    clauses_present = data.get("clauses", {})
    metadata = data.get("metadata", {})
    involves_personal_data = metadata.get("personal_data", False)
    is_b2c = metadata.get("b2c", False)

    # Check base clauses
    base_required = REQUIRED_CLAUSES.get(contract_type, REQUIRED_CLAUSES["fixed-price"])
    results = []
    passed = 0

    for req in base_required:
        present = bool(clauses_present.get(req["clause"]))
        if present:
            passed += 1
        results.append({
            "clause": req["clause"],
            "label": req["label"],
            "present": present,
            "required": True,
            "source": "base",
        })

    # Check jurisdiction extras
    extras = JURISDICTION_EXTRAS.get(jurisdiction, [])
    for extra in extras:
        applicable = True
        if extra["condition"] == "personal_data" and not involves_personal_data:
            applicable = False
        if extra["condition"] == "b2c" and not is_b2c:
            applicable = False

        if applicable:
            present = bool(clauses_present.get(extra["clause"]))
            if present:
                passed += 1
            results.append({
                "clause": extra["clause"],
                "label": extra["label"],
                "present": present,
                "required": True,
                "source": f"jurisdiction:{jurisdiction}",
            })

    # Check for unfilled placeholders
    placeholder_warnings = []
    for key, value in clauses_present.items():
        if isinstance(value, str) and "[" in value and "]" in value:
            placeholder_warnings.append({
                "clause": key,
                "warning": f"Contains unfilled placeholder: {value[:80]}",
            })

    total_required = len(results)
    missing = [r for r in results if not r["present"]]
    compliance_pct = (passed / total_required * 100) if total_required > 0 else 0

    if compliance_pct >= 95:
        status = "COMPLIANT"
    elif compliance_pct >= 75:
        status = "NEEDS_REVIEW"
    else:
        status = "NON_COMPLIANT"

    return {
        "contract_type": contract_type,
        "jurisdiction": jurisdiction,
        "status": status,
        "compliance_pct": round(compliance_pct, 1),
        "clauses_checked": total_required,
        "clauses_present": passed,
        "clauses_missing": len(missing),
        "results": results,
        "missing_clauses": missing,
        "placeholder_warnings": placeholder_warnings,
        "recommendations": _generate_recommendations(missing, jurisdiction, placeholder_warnings),
    }


def _generate_recommendations(missing: list, jurisdiction: str, placeholders: list) -> list:
    """Generate recommendations."""
    recs = []
    for m in missing:
        recs.append({
            "priority": "HIGH",
            "action": f"Add missing clause: {m['label']}",
            "source": m["source"],
        })
    if placeholders:
        recs.append({
            "priority": "CRITICAL",
            "action": f"{len(placeholders)} unfilled placeholder(s) found. Fill all [BRACKETED] values before sending.",
            "source": "validation",
        })
    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"CONTRACT CLAUSE CHECKER")
    lines.append("=" * 60)

    lines.append(f"\nType: {result['contract_type']}")
    lines.append(f"Jurisdiction: {result['jurisdiction']}")
    lines.append(f"Status: {result['status']}")
    lines.append(f"Compliance: {result['compliance_pct']}% ({result['clauses_present']}/{result['clauses_checked']})")

    lines.append(f"\n--- Clause Checklist ---")
    for r in result["results"]:
        status = "[OK]  " if r["present"] else "[MISS]"
        lines.append(f"  {status} {r['label']}")

    if result["placeholder_warnings"]:
        lines.append(f"\n--- Placeholder Warnings ---")
        for pw in result["placeholder_warnings"]:
            lines.append(f"  [WARN] {pw['clause']}: {pw['warning']}")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['action']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate contract against required clauses for jurisdiction and type."
    )
    parser.add_argument("input_file", help="JSON file with contract clauses and metadata")
    parser.add_argument("--jurisdiction", choices=["us-delaware", "eu", "uk", "dach"],
                        default="us-delaware", help="Jurisdiction (default: us-delaware)")
    parser.add_argument("--type", choices=["fixed-price", "hourly", "retainer", "nda", "msa"],
                        default="fixed-price", help="Contract type (default: fixed-price)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = check_contract(data, args.jurisdiction, args.type)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
