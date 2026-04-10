#!/usr/bin/env python3
"""
NDA Checklist Generator

Generates a 10-point compliance checklist for an NDA, checking all
screening criteria with pass/fail status and notes.

Usage:
    python nda_checklist.py nda_draft.txt
    python nda_checklist.py nda_draft.txt --json
    python nda_checklist.py nda_draft.txt --output checklist.json --json
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple


# 10-point screening criteria with detection patterns
SCREENING_CRITERIA = [
    {
        "id": 1,
        "name": "Agreement Structure",
        "description": "Mutual vs. one-way; parties identified; purpose stated",
        "checks": [
            {
                "name": "parties_identified",
                "patterns": [
                    r"between\s+.{2,60}\s+(?:and|&)\s+.{2,60}",
                    r"(?:party|parties)\s+(?:hereto|to\s+this)",
                    r"(?:\"company\"|\"discloser\"|\"recipient\"|\"party\s+[ab]\")",
                ],
                "description": "Parties clearly identified",
            },
            {
                "name": "purpose_stated",
                "patterns": [
                    r"(?:purpose|reason|connection\s+with|in\s+relation\s+to|regarding)\s+(?:of|for)?\s*(?:this|the)\s+(?:agreement|nda|disclosure)",
                    r"(?:evaluat|explor|discuss|consider|assess|pursu)",
                    r"(?:business\s+(?:purpose|relationship|opportunity|transaction))",
                ],
                "description": "Purpose of disclosure stated",
            },
            {
                "name": "mutual_or_one_way",
                "patterns": [
                    r"mutual",
                    r"(?:each|both)\s+part(?:y|ies)",
                    r"(?:one[- ]?way|unilateral)",
                    r"(?:disclosing\s+party|receiving\s+party)",
                ],
                "description": "Direction of obligations clear (mutual or one-way)",
            },
        ],
    },
    {
        "id": 2,
        "name": "Definition of Confidential Information",
        "description": "Scope, specificity, marking requirements",
        "checks": [
            {
                "name": "definition_present",
                "patterns": [
                    r"(?:\"|')confidential\s+information(?:\"|')\s+(?:means|shall\s+mean|includes?|refers?\s+to)",
                    r"(?:definition|meaning)\s+of\s+confidential",
                    r"confidential\s+information\s+(?:is\s+defined|means)",
                ],
                "description": "Confidential information defined",
            },
            {
                "name": "marking_requirement",
                "patterns": [
                    r"mark(?:ed|ing)\s+(?:as\s+)?(?:\"|')?\s*confidential",
                    r"(?:labeled|designated|stamped)\s+(?:as\s+)?confidential",
                    r"(?:written|oral).*(?:confirm|identif|summariz).*(?:in\s+writing|\d+\s+(?:day|business))",
                ],
                "description": "Marking or identification requirement for confidential information",
            },
            {
                "name": "scope_bounded",
                "patterns": [
                    r"(?:relating\s+to|concerning|regarding|in\s+connection\s+with)\s+(?:the\s+)?(?:purpose|project|transaction|business)",
                    r"limited\s+to",
                    r"specifically\s+(?:identified|designated|marked)",
                ],
                "description": "Scope of confidential information is bounded",
            },
        ],
    },
    {
        "id": 3,
        "name": "Obligations",
        "description": "Standard of care, use restrictions, disclosure limits",
        "checks": [
            {
                "name": "standard_of_care",
                "patterns": [
                    r"reasonable\s+(?:care|efforts?|measures?|steps?|precautions?)",
                    r"same\s+(?:degree|standard|level)\s+of\s+(?:care|protection)",
                    r"protect.*(?:confidential|proprietary).*(?:reasonable|same\s+degree)",
                ],
                "description": "Standard of care for protecting confidential information",
            },
            {
                "name": "use_restriction",
                "patterns": [
                    r"(?:use|utilized?)\s+(?:solely|only|exclusively)\s+(?:for|in\s+connection)",
                    r"shall\s+not\s+(?:use|utilize)\s+(?:the\s+)?confidential.*(?:except|other\s+than)",
                    r"(?:restricted|limited)\s+(?:to\s+)?(?:the\s+)?(?:purpose|permitted\s+use)",
                ],
                "description": "Use restricted to stated purpose",
            },
            {
                "name": "disclosure_limits",
                "patterns": [
                    r"shall\s+not\s+(?:disclose|reveal|divulge|share)",
                    r"(?:restrict|limit)\s+(?:disclosure|access)\s+to",
                    r"need[- ]to[- ]know\s+basis",
                ],
                "description": "Disclosure limited to authorized persons",
            },
        ],
    },
    {
        "id": 4,
        "name": "Standard Carveouts",
        "description": "5 required: public knowledge, prior possession, independent development, third-party receipt, legal compulsion",
        "checks": [
            {
                "name": "public_knowledge",
                "patterns": [
                    r"public(?:ly)?\s+(?:known|available|domain)",
                    r"generally\s+(?:known|available)\s+to\s+the\s+public",
                ],
                "description": "Public knowledge carveout",
            },
            {
                "name": "prior_possession",
                "patterns": [
                    r"prior\s+(?:possession|knowledge|receipt)",
                    r"already\s+(?:known|possessed|in\s+possession)",
                ],
                "description": "Prior possession carveout",
            },
            {
                "name": "independent_development",
                "patterns": [
                    r"independent(?:ly)?\s+develop",
                    r"without\s+(?:use\s+of|reference\s+to)\s+(?:the\s+)?confidential",
                ],
                "description": "Independent development carveout",
            },
            {
                "name": "third_party_receipt",
                "patterns": [
                    r"(?:received|obtained)\s+from\s+a\s+third\s+party",
                    r"third[- ]party\s+(?:source|disclosure)",
                ],
                "description": "Third-party receipt carveout",
            },
            {
                "name": "legal_compulsion",
                "patterns": [
                    r"(?:required|compelled|ordered)\s+(?:by|under)\s+law",
                    r"court\s+order",
                    r"subpoena",
                    r"legal(?:ly)?\s+(?:required|compelled)",
                ],
                "description": "Legal compulsion carveout",
            },
        ],
    },
    {
        "id": 5,
        "name": "Permitted Disclosures",
        "description": "Representatives, advisors, affiliates with need-to-know",
        "checks": [
            {
                "name": "representatives",
                "patterns": [
                    r"(?:representatives?|employees?|officers?|directors?)",
                    r"(?:agents?|advisors?|counsel|accountants?|consultants?)",
                ],
                "description": "Disclosure to representatives permitted",
            },
            {
                "name": "need_to_know",
                "patterns": [
                    r"need[- ]to[- ]know",
                    r"(?:require|necessary)\s+(?:for\s+)?(?:the\s+)?(?:purpose|performance)",
                ],
                "description": "Need-to-know requirement for permitted recipients",
            },
            {
                "name": "affiliate_coverage",
                "patterns": [
                    r"affiliates?",
                    r"subsidi(?:ary|aries)",
                    r"(?:parent|related)\s+(?:compan|entit)",
                ],
                "description": "Affiliates covered in permitted disclosures",
            },
        ],
    },
    {
        "id": 6,
        "name": "Term & Duration",
        "description": "Reasonable term, survival period, obligations after expiry",
        "checks": [
            {
                "name": "term_defined",
                "patterns": [
                    r"term\s+(?:of\s+)?(?:this\s+)?(?:agreement\s+)?(?:shall\s+be|is)\s+\d",
                    r"\d+\s+(?:year|month)s?\s+(?:from|after|following)",
                    r"(?:effective|initial)\s+(?:date|period|term)",
                ],
                "description": "Agreement term is defined",
            },
            {
                "name": "survival_period",
                "patterns": [
                    r"surviv(?:e|al|ing).*(?:\d+\s+(?:year|month)|termination|expir)",
                    r"(?:obligations?|duties?)\s+(?:shall\s+)?(?:survive|continue)\s+(?:for\s+)?\d+",
                    r"(?:after|following)\s+(?:termination|expir).*\d+\s+(?:year|month)",
                ],
                "description": "Survival period for obligations after termination",
            },
        ],
    },
    {
        "id": 7,
        "name": "Return/Destruction",
        "description": "Obligation to return or destroy upon request or termination",
        "checks": [
            {
                "name": "return_or_destroy",
                "patterns": [
                    r"return\s+(?:or\s+)?destroy",
                    r"destroy\s+(?:or\s+)?return",
                    r"(?:return|destruction)\s+of\s+(?:all\s+)?(?:confidential\s+)?(?:information|materials|copies|documents)",
                ],
                "description": "Return or destruction obligation present",
            },
            {
                "name": "certification",
                "patterns": [
                    r"certif(?:y|ication)\s+(?:of\s+)?(?:destruction|compliance|return)",
                    r"(?:written|officer)\s+certif",
                ],
                "description": "Certification of destruction required",
            },
        ],
    },
    {
        "id": 8,
        "name": "Remedies",
        "description": "Injunctive relief, damages, indemnification scope",
        "checks": [
            {
                "name": "injunctive_relief",
                "patterns": [
                    r"injunctive\s+relief",
                    r"specific\s+performance",
                    r"equitable\s+(?:relief|remed)",
                    r"irreparable\s+(?:harm|injury|damage)",
                ],
                "description": "Injunctive relief available for breach",
            },
            {
                "name": "no_liquidated_damages",
                "patterns": [
                    r"liquidated\s+damages",
                    r"stipulated\s+damages",
                    r"penalty\s+(?:of|in\s+the\s+amount)",
                ],
                "description": "No liquidated damages (negative check)",
                "negative": True,
            },
        ],
    },
    {
        "id": 9,
        "name": "Problematic Provisions",
        "description": "Non-solicitation, non-compete, exclusivity, residuals, IP assignment, audit rights",
        "checks": [
            {
                "name": "no_non_solicitation",
                "patterns": [r"non[- ]?solicitation", r"shall\s+not\s+solicit"],
                "description": "No non-solicitation clause",
                "negative": True,
            },
            {
                "name": "no_non_compete",
                "patterns": [r"non[- ]?compete", r"competitive\s+activit", r"shall\s+not\s+compete"],
                "description": "No non-compete clause",
                "negative": True,
            },
            {
                "name": "no_exclusivity",
                "patterns": [r"exclusiv(?:e|ity)\s+(?:deal|negotiat|discuss|period|obligation)"],
                "description": "No exclusivity provision",
                "negative": True,
            },
            {
                "name": "no_ip_assignment",
                "patterns": [r"assign(?:s|ment)?\s+(?:all\s+)?(?:right|title)", r"work[- ]?for[- ]?hire"],
                "description": "No IP assignment clause",
                "negative": True,
            },
            {
                "name": "no_residuals",
                "patterns": [r"residual", r"unaided\s+(?:memory|recall)"],
                "description": "No residuals clause",
                "negative": True,
            },
        ],
    },
    {
        "id": 10,
        "name": "Governing Law",
        "description": "Jurisdiction, dispute resolution mechanism",
        "checks": [
            {
                "name": "governing_law",
                "patterns": [
                    r"govern(?:ed|ing)\s+(?:by\s+)?(?:the\s+)?laws?\s+of",
                    r"applicable\s+law",
                    r"choice\s+of\s+law",
                ],
                "description": "Governing law specified",
            },
            {
                "name": "dispute_resolution",
                "patterns": [
                    r"(?:dispute|controversy)\s+(?:resolution|settlement)",
                    r"arbitration",
                    r"jurisdiction\s+of\s+(?:the\s+)?courts?",
                    r"(?:venue|forum)\s+(?:for\s+)?(?:any\s+)?(?:dispute|action|proceeding)",
                ],
                "description": "Dispute resolution mechanism specified",
            },
        ],
    },
]


def read_nda(file_path: str) -> str:
    """Read NDA text from file."""
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()


def evaluate_criterion(text: str, criterion: Dict) -> Dict:
    """Evaluate a single screening criterion against NDA text."""
    text_lower = text.lower()
    checks_results = []
    all_pass = True
    critical_fail = False

    for check in criterion["checks"]:
        found = False
        for pattern in check["patterns"]:
            if re.search(pattern, text_lower):
                found = True
                break

        is_negative = check.get("negative", False)

        if is_negative:
            # For negative checks, finding the pattern means FAIL
            passed = not found
            if not passed:
                critical_fail = True
        else:
            # For positive checks, finding the pattern means PASS
            passed = found

        if not passed:
            all_pass = False

        checks_results.append({
            "name": check["name"],
            "description": check["description"],
            "passed": passed,
            "negative_check": is_negative,
        })

    # Determine overall status for this criterion
    if critical_fail:
        status = "FAIL"
    elif all_pass:
        status = "PASS"
    else:
        # Partial pass: at least one sub-check failed but no critical failures
        passed_count = sum(1 for c in checks_results if c["passed"])
        total_count = len(checks_results)
        if passed_count >= total_count / 2:
            status = "PARTIAL"
        else:
            status = "FAIL"

    # Generate notes
    notes_parts = []
    for cr in checks_results:
        if not cr["passed"]:
            if cr["negative_check"]:
                notes_parts.append(f"Detected: {cr['description'].replace('No ', '')}")
            else:
                notes_parts.append(f"Missing: {cr['description']}")

    notes = "; ".join(notes_parts) if notes_parts else "All checks passed"

    return {
        "id": criterion["id"],
        "name": criterion["name"],
        "description": criterion["description"],
        "status": status,
        "notes": notes,
        "checks": checks_results,
    }


def classify_from_checklist(results: List[Dict]) -> Tuple[str, int, int]:
    """Classify NDA based on checklist results."""
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    # Check for critical failures
    critical_criteria = [4, 9]  # Standard Carveouts and Problematic Provisions
    critical_fails = [r for r in results if r["id"] in critical_criteria and r["status"] == "FAIL"]

    if critical_fails or fail_count >= 3:
        return "RED", pass_count, total
    elif fail_count >= 1 or any(r["status"] == "PARTIAL" for r in results):
        return "YELLOW", pass_count, total
    else:
        return "GREEN", pass_count, total


def format_text_output(result: Dict) -> str:
    """Format checklist as human-readable text."""
    lines = []
    lines.append("NDA COMPLIANCE CHECKLIST")
    lines.append("=" * 50)
    lines.append(f"File: {result['file']}")
    lines.append(f"Overall: {result['classification']} ({result['pass_count']}/{result['total']} PASS)")
    lines.append("")

    # Header
    lines.append(f" {'#':>2}  {'Criterion':<32} {'Status':<8} Notes")
    lines.append(f" {'--':>2}  {'-' * 32} {'-' * 8} {'-' * 40}")

    for criterion in result["criteria"]:
        status_display = criterion["status"]
        lines.append(
            f" {criterion['id']:>2}  {criterion['name']:<32} {status_display:<8} {criterion['notes']}"
        )

    lines.append("")

    # Failed criteria details
    failed = [c for c in result["criteria"] if c["status"] in ("FAIL", "PARTIAL")]
    if failed:
        lines.append("DETAILS ON FAILED/PARTIAL CRITERIA")
        lines.append("-" * 40)
        for criterion in failed:
            lines.append(f"  [{criterion['status']}] #{criterion['id']} {criterion['name']}")
            for check in criterion["checks"]:
                if not check["passed"]:
                    prefix = "  [!]" if check.get("negative_check") else "  [-]"
                    lines.append(f"    {prefix} {check['description']}")
            lines.append("")

    return "\n".join(lines)


def generate_checklist(file_path: str) -> Dict:
    """Main checklist generation pipeline."""
    text = read_nda(file_path)
    results = []

    for criterion in SCREENING_CRITERIA:
        result = evaluate_criterion(text, criterion)
        results.append(result)

    classification, pass_count, total = classify_from_checklist(results)

    return {
        "file": os.path.basename(file_path),
        "classification": classification,
        "pass_count": pass_count,
        "total": total,
        "criteria": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a 10-point compliance checklist for an NDA."
    )
    parser.add_argument("nda_file", help="Path to NDA text file (.txt or .md)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output in JSON format")
    parser.add_argument("-o", "--output", help="Write output to file")

    args = parser.parse_args()
    result = generate_checklist(args.nda_file)

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
