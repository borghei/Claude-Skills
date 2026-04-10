#!/usr/bin/env python3
"""
Contract Analyzer

Analyzes contract text files for clause types, identifies missing standard
clauses, and flags risk indicators with GREEN/YELLOW/RED severity.

Usage:
    python contract_analyzer.py contract.txt
    python contract_analyzer.py agreement.md --json
    python contract_analyzer.py contract.txt --output analysis.json --json
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


# Clause type definitions with detection patterns and risk indicators
CLAUSE_TYPES = {
    "limitation_of_liability": {
        "headings": [
            r"limitation\s+of\s+liability", r"liability\s+cap",
            r"damages?\s+cap", r"limit\s+of\s+liability",
            r"limitation\s+on\s+liability",
        ],
        "keywords": ["liability", "aggregate", "cap", "damages", "limitation"],
        "description": "Limitation of Liability",
    },
    "indemnification": {
        "headings": [
            r"indemnif", r"hold\s+harmless", r"defense\s+and\s+indemnity",
        ],
        "keywords": ["indemnify", "indemnification", "hold harmless", "defense"],
        "description": "Indemnification",
    },
    "intellectual_property": {
        "headings": [
            r"intellectual\s+property", r"\bip\s+rights", r"ownership\s+of\s+work",
            r"work\s+product", r"proprietary\s+rights",
        ],
        "keywords": ["intellectual property", "copyright", "patent", "trademark",
                      "work for hire", "work-for-hire", "license grant", "ip rights"],
        "description": "Intellectual Property",
    },
    "data_protection": {
        "headings": [
            r"data\s+protection", r"data\s+privacy", r"data\s+processing",
            r"personal\s+data", r"dpa\b",
        ],
        "keywords": ["data protection", "personal data", "data processing",
                      "sub-processor", "data breach", "gdpr", "ccpa", "dpa"],
        "description": "Data Protection",
    },
    "term_and_termination": {
        "headings": [
            r"term\s+and\s+termination", r"\btermination\b", r"\bterm\b.*agreement",
            r"duration\s+and\s+termination",
        ],
        "keywords": ["termination", "term", "renewal", "cure period", "expiration"],
        "description": "Term & Termination",
    },
    "governing_law": {
        "headings": [
            r"governing\s+law", r"applicable\s+law", r"jurisdiction",
            r"choice\s+of\s+law", r"dispute\s+resolution",
        ],
        "keywords": ["governing law", "jurisdiction", "arbitration", "venue",
                      "dispute resolution", "jury waiver"],
        "description": "Governing Law",
    },
    "representations_warranties": {
        "headings": [
            r"representations?\s+and\s+warrant", r"representations?",
            r"warranties", r"covenants?\s+and\s+warrant",
        ],
        "keywords": ["represents", "warrants", "warranty", "representation",
                      "as-is", "disclaimer"],
        "description": "Representations & Warranties",
    },
    "force_majeure": {
        "headings": [
            r"force\s+majeure", r"excused\s+performance", r"unforeseeable\s+events",
        ],
        "keywords": ["force majeure", "act of god", "pandemic", "natural disaster",
                      "unforeseeable"],
        "description": "Force Majeure",
    },
    "confidentiality": {
        "headings": [
            r"confidential", r"non-disclosure", r"nda\b", r"proprietary\s+information",
        ],
        "keywords": ["confidential", "non-disclosure", "proprietary information",
                      "trade secret"],
        "description": "Confidentiality",
    },
    "payment_terms": {
        "headings": [
            r"payment\s+terms", r"fees\s+and\s+payment", r"compensation",
            r"pricing", r"invoic",
        ],
        "keywords": ["payment", "invoice", "fees", "compensation", "net 30",
                      "net 60", "pricing"],
        "description": "Payment Terms",
    },
}

# Risk indicator patterns with severity and explanation
RISK_INDICATORS = [
    {
        "id": "uncapped_liability",
        "patterns": [
            r"liability\s+shall\s+not\s+be\s+limited",
            r"unlimited\s+liability",
            r"no\s+limit\s+on\s+liability",
            r"without\s+limitation\s+as\s+to\s+amount",
            r"liability\s+is\s+not\s+capped",
        ],
        "clause": "limitation_of_liability",
        "severity": "RED",
        "description": "Uncapped liability exposure",
    },
    {
        "id": "no_consequential_damages_exclusion",
        "patterns": [
            r"consequential\s+damages\s+shall\s+apply",
            r"including\s+consequential",
            r"special,?\s+incidental,?\s+and\s+consequential",
        ],
        "clause": "limitation_of_liability",
        "severity": "YELLOW",
        "description": "Consequential damages not excluded",
    },
    {
        "id": "unilateral_indemnification",
        "patterns": [
            r"(?:you|customer|client|buyer|licensee)\s+shall\s+indemnify",
            r"(?:you|customer|client)\s+agrees?\s+to\s+indemnify",
            r"sole\s+indemnification\s+obligation",
        ],
        "clause": "indemnification",
        "severity": "YELLOW",
        "description": "One-sided indemnification obligation",
    },
    {
        "id": "broad_ip_assignment",
        "patterns": [
            r"assigns?\s+all\s+(?:right|title|interest)",
            r"transfer\s+of\s+all\s+ip",
            r"work\s+(?:made\s+)?for\s+hire.*all\s+rights",
            r"irrevocable.*license.*(?:sublicens|transfer)",
        ],
        "clause": "intellectual_property",
        "severity": "RED",
        "description": "Broad IP assignment or transfer",
    },
    {
        "id": "perpetual_term",
        "patterns": [
            r"perpetual\s+(?:term|license|agreement)",
            r"no\s+expiration",
            r"in\s+perpetuity",
            r"shall\s+continue\s+indefinitely",
        ],
        "clause": "term_and_termination",
        "severity": "RED",
        "description": "Perpetual term with no termination path",
    },
    {
        "id": "auto_renewal_no_opt_out",
        "patterns": [
            r"automatically\s+renew(?:s|ed)?\s+(?:for|unless)",
            r"auto[- ]?renewal",
            r"evergreen\s+(?:clause|provision|term)",
        ],
        "clause": "term_and_termination",
        "severity": "YELLOW",
        "description": "Automatic renewal clause detected",
    },
    {
        "id": "no_cure_period",
        "patterns": [
            r"immediate\s+termination",
            r"terminat(?:e|ion)\s+without\s+(?:notice|cure)",
            r"no\s+(?:cure|remedy)\s+period",
        ],
        "clause": "term_and_termination",
        "severity": "YELLOW",
        "description": "Termination without cure period",
    },
    {
        "id": "unlimited_audit_rights",
        "patterns": [
            r"unlimited\s+audit",
            r"audit\s+at\s+any\s+time",
            r"unrestricted\s+(?:access|audit|inspection)",
        ],
        "clause": "data_protection",
        "severity": "YELLOW",
        "description": "Unlimited or unrestricted audit rights",
    },
    {
        "id": "no_data_breach_notification",
        "patterns": [
            r"no\s+(?:obligation|requirement)\s+to\s+notify",
            r"breach\s+notification\s+waived",
        ],
        "clause": "data_protection",
        "severity": "RED",
        "description": "No data breach notification obligation",
    },
    {
        "id": "unfavorable_jurisdiction",
        "patterns": [
            r"exclusive\s+jurisdiction.*(?:foreign|overseas)",
            r"laws?\s+of\s+(?:the\s+)?(?:people'?s?\s+republic|china|russia)",
        ],
        "clause": "governing_law",
        "severity": "YELLOW",
        "description": "Potentially unfavorable jurisdiction",
    },
    {
        "id": "jury_waiver",
        "patterns": [
            r"waiv(?:e|er)\s+(?:of\s+)?(?:right\s+to\s+)?(?:a\s+)?jury\s+trial",
            r"jury\s+trial\s+waiver",
        ],
        "clause": "governing_law",
        "severity": "YELLOW",
        "description": "Jury trial waiver present",
    },
    {
        "id": "as_is_no_warranty",
        "patterns": [
            r"as[- ]is\b.*(?:without|no)\s+warrant",
            r"disclaim(?:s|ed)?\s+all\s+warranties",
            r"no\s+representations?\s+or\s+warranties",
        ],
        "clause": "representations_warranties",
        "severity": "YELLOW",
        "description": "Full warranty disclaimer (as-is)",
    },
]

# Standard clauses expected in commercial contracts
STANDARD_CLAUSES = [
    "limitation_of_liability",
    "indemnification",
    "intellectual_property",
    "data_protection",
    "term_and_termination",
    "governing_law",
    "confidentiality",
]


def read_contract(file_path: str) -> str:
    """Read contract text from file."""
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()


def detect_clauses(text: str) -> List[Dict]:
    """Detect clause types in contract text by heading and keyword matching."""
    clauses_found: List[Dict] = []
    text_lower = text.lower()
    lines = text.split("\n")

    for clause_id, clause_def in CLAUSE_TYPES.items():
        # Check headings first (stronger signal)
        heading_match = False
        snippet = ""
        for i, line in enumerate(lines):
            for pattern in clause_def["headings"]:
                if re.search(pattern, line, re.IGNORECASE):
                    heading_match = True
                    # Capture surrounding context (up to 5 lines)
                    start = max(0, i)
                    end = min(len(lines), i + 6)
                    snippet = "\n".join(lines[start:end]).strip()
                    break
            if heading_match:
                break

        # Fallback to keyword density if no heading found
        keyword_count = 0
        if not heading_match:
            for kw in clause_def["keywords"]:
                keyword_count += len(re.findall(re.escape(kw), text_lower))

        if heading_match or keyword_count >= 2:
            clauses_found.append({
                "type": clause_id,
                "description": clause_def["description"],
                "detected_by": "heading" if heading_match else "keywords",
                "keyword_count": keyword_count,
                "text_snippet": snippet[:300] if snippet else "",
                "severity": "GREEN",
                "risk_flags": [],
                "notes": "",
            })

    return clauses_found


def assess_risks(text: str, clauses: List[Dict]) -> List[Dict]:
    """Assess risk indicators and update clause severities."""
    text_lower = text.lower()
    clause_map = {c["type"]: c for c in clauses}

    for indicator in RISK_INDICATORS:
        for pattern in indicator["patterns"]:
            match = re.search(pattern, text_lower)
            if match:
                clause_id = indicator["clause"]
                if clause_id in clause_map:
                    clause = clause_map[clause_id]
                    clause["risk_flags"].append(indicator["id"])
                    # Escalate severity: GREEN -> YELLOW -> RED
                    if indicator["severity"] == "RED":
                        clause["severity"] = "RED"
                    elif indicator["severity"] == "YELLOW" and clause["severity"] != "RED":
                        clause["severity"] = "YELLOW"
                    if clause["notes"]:
                        clause["notes"] += "; "
                    clause["notes"] += indicator["description"]
                else:
                    # Risk found but clause not detected -- add as standalone finding
                    clauses.append({
                        "type": clause_id,
                        "description": CLAUSE_TYPES.get(clause_id, {}).get(
                            "description", clause_id
                        ),
                        "detected_by": "risk_indicator",
                        "keyword_count": 0,
                        "text_snippet": "",
                        "severity": indicator["severity"],
                        "risk_flags": [indicator["id"]],
                        "notes": indicator["description"],
                    })
                    clause_map[clause_id] = clauses[-1]
                break  # One match per indicator is sufficient

    return clauses


def check_missing_clauses(clauses: List[Dict]) -> List[str]:
    """Check for standard clauses that are missing from the contract."""
    found_types = {c["type"] for c in clauses}
    return [c for c in STANDARD_CLAUSES if c not in found_types]


def compute_summary(clauses: List[Dict], missing: List[str]) -> Dict:
    """Compute risk summary and overall risk level."""
    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    for c in clauses:
        counts[c["severity"]] = counts.get(c["severity"], 0) + 1

    # Missing critical clauses escalate to YELLOW
    missing_critical = [m for m in missing if m in [
        "limitation_of_liability", "indemnification", "data_protection"
    ]]
    if missing_critical:
        counts["YELLOW"] += len(missing_critical)

    if counts["RED"] > 0:
        overall = "RED"
    elif counts["YELLOW"] > 0:
        overall = "YELLOW"
    else:
        overall = "GREEN"

    return {"RED": counts["RED"], "YELLOW": counts["YELLOW"],
            "GREEN": counts["GREEN"], "overall": overall}


def format_text_output(result: Dict) -> str:
    """Format analysis as human-readable text."""
    lines = []
    lines.append("CONTRACT ANALYSIS REPORT")
    lines.append("=" * 50)
    lines.append(f"File: {result['file']}")
    lines.append(f"Overall Risk: {result['overall_risk']}")
    lines.append(f"Clauses Found: {len(result['clauses_found'])}")
    lines.append(f"Missing Clauses: {len(result['missing_clauses'])}")
    lines.append("")

    # Risk summary
    rs = result["risk_summary"]
    lines.append(f"Risk Summary: RED={rs['RED']}  YELLOW={rs['YELLOW']}  GREEN={rs['GREEN']}")
    lines.append("")

    # Clauses by severity
    for severity in ["RED", "YELLOW", "GREEN"]:
        severity_clauses = [c for c in result["clauses_found"] if c["severity"] == severity]
        if severity_clauses:
            lines.append(f"--- {severity} ---")
            for c in severity_clauses:
                lines.append(f"  [{severity}] {c['description']} ({c['type']})")
                if c["risk_flags"]:
                    lines.append(f"         Flags: {', '.join(c['risk_flags'])}")
                if c["notes"]:
                    lines.append(f"         Notes: {c['notes']}")
                if c["text_snippet"]:
                    snippet = c["text_snippet"][:150].replace("\n", " ")
                    lines.append(f"         Snippet: {snippet}...")
            lines.append("")

    # Missing clauses
    if result["missing_clauses"]:
        lines.append("--- MISSING CLAUSES ---")
        for m in result["missing_clauses"]:
            desc = CLAUSE_TYPES.get(m, {}).get("description", m)
            lines.append(f"  [!] {desc} ({m})")
        lines.append("")

    return "\n".join(lines)


def analyze_contract(file_path: str) -> Dict:
    """Main analysis pipeline."""
    text = read_contract(file_path)
    clauses = detect_clauses(text)
    clauses = assess_risks(text, clauses)
    missing = check_missing_clauses(clauses)
    summary = compute_summary(clauses, missing)

    # Clean up internal fields for output
    for c in clauses:
        c.pop("keyword_count", None)
        c.pop("detected_by", None)

    return {
        "file": os.path.basename(file_path),
        "clauses_found": clauses,
        "missing_clauses": missing,
        "risk_summary": summary,
        "overall_risk": summary["overall"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze contract text for clause types, missing clauses, and risk indicators."
    )
    parser.add_argument("contract_file", help="Path to contract text file (.txt or .md)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output in JSON format")
    parser.add_argument("-o", "--output", help="Write output to file")

    args = parser.parse_args()
    result = analyze_contract(args.contract_file)

    if args.json_output:
        output = json.dumps(result, indent=2)
    else:
        output = format_text_output(result)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to {args.output}")
        except IOError as e:
            print(f"Error writing to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
