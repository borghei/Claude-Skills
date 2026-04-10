#!/usr/bin/env python3
"""
NDA Clause Reviewer

Performs deep clause-by-clause NDA analysis from Recipient or Discloser
perspective. Generates structured issue log with redlines, fallbacks,
rationale, owners, and deadlines.

Usage:
    python nda_clause_reviewer.py nda_draft.txt
    python nda_clause_reviewer.py nda_draft.txt --perspective discloser
    python nda_clause_reviewer.py nda_draft.txt --json --output issues.json
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


# Issue templates organized by clause area
# Each issue has: detection patterns, risk ratings per perspective, redlines
ISSUE_DEFINITIONS = [
    {
        "id": "overbroad_definition",
        "clause": "Definition of Confidential Information",
        "patterns": [
            r"all\s+information\s+(?:of\s+any\s+(?:kind|nature|type)|whatsoever)",
            r"any\s+(?:and\s+all\s+)?information.*(?:relating|concerning|regarding)",
            r"without\s+limitation.*(?:oral|written|visual|electronic|any\s+(?:form|medium))",
        ],
        "issue": "Overbroad definition with no clear boundaries",
        "risk": {"recipient": "H", "discloser": "L"},
        "preferred": "Narrow definition to information specifically marked or designated as Confidential, with 10-day written confirmation for oral disclosures",
        "fallback": "Add marking requirement for written information; 10-day confirmation window for oral disclosures",
        "rationale": {
            "recipient": "Overbroad definition traps all shared information as confidential, restricting normal business operations",
            "discloser": "Broad definition maximizes protection scope; minor concern",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "no_marking_requirement",
        "clause": "Definition of Confidential Information",
        "patterns": [
            # Negative: detect ABSENCE of marking requirement
            # We check for presence of marking; if not found, this fires
        ],
        "positive_patterns": [
            r"mark(?:ed|ing)\s+(?:as\s+)?(?:\"|')?\s*confidential",
            r"(?:labeled|designated|stamped)\s+(?:as\s+)?confidential",
            r"(?:written|oral).*(?:confirm|identif|summariz).*(?:in\s+writing|\d+\s+(?:day|business))",
        ],
        "negative_check": True,
        "issue": "No marking or identification requirement for confidential information",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Add: Information must be marked 'Confidential' when written; oral disclosures confirmed in writing within 10 business days",
        "fallback": "Add: Information reasonably understood to be confidential given the nature and circumstances of disclosure",
        "rationale": {
            "recipient": "Without marking, all information exchanged could be treated as confidential, creating uncertainty",
            "discloser": "No marking requirement means all information is protected without effort; generally favorable",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "missing_public_knowledge",
        "clause": "Standard Carveouts",
        "patterns": [],
        "positive_patterns": [
            r"public(?:ly)?\s+(?:known|available|domain)",
            r"generally\s+(?:known|available)\s+to\s+the\s+public",
        ],
        "negative_check": True,
        "issue": "Missing public knowledge carveout",
        "risk": {"recipient": "H", "discloser": "M"},
        "preferred": "Add: Information that is or becomes publicly available through no fault of the receiving party",
        "fallback": "Add: Information that is part of the public domain at the time of disclosure or thereafter",
        "rationale": {
            "recipient": "Without this carveout, information that becomes public may still be treated as confidential",
            "discloser": "Standard carveout; absence may raise concerns about enforceability",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "missing_prior_possession",
        "clause": "Standard Carveouts",
        "patterns": [],
        "positive_patterns": [
            r"prior\s+(?:possession|knowledge|receipt)",
            r"already\s+(?:known|possessed|in\s+possession)",
        ],
        "negative_check": True,
        "issue": "Missing prior possession carveout",
        "risk": {"recipient": "H", "discloser": "M"},
        "preferred": "Add: Information already in the receiving party's possession prior to disclosure, as documented by written records",
        "fallback": "Add: Information known to the receiving party prior to disclosure",
        "rationale": {
            "recipient": "Without this, pre-existing knowledge becomes subject to NDA restrictions",
            "discloser": "Standard carveout; documentary evidence requirement protects discloser interests",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "missing_independent_development",
        "clause": "Standard Carveouts",
        "patterns": [],
        "positive_patterns": [
            r"independent(?:ly)?\s+develop",
            r"without\s+(?:use\s+of|reference\s+to)\s+(?:the\s+)?confidential",
        ],
        "negative_check": True,
        "issue": "Missing independent development carveout",
        "risk": {"recipient": "H", "discloser": "M"},
        "preferred": "Add: Information independently developed by the receiving party without use of or reference to Confidential Information",
        "fallback": "Add: Information independently developed as demonstrated by documentary evidence created prior to or independent of any disclosure",
        "rationale": {
            "recipient": "Missing carveout blocks internal R&D; can create contamination claims against entire engineering teams",
            "discloser": "Standard carveout; documentary evidence requirement is acceptable protection",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "missing_third_party_receipt",
        "clause": "Standard Carveouts",
        "patterns": [],
        "positive_patterns": [
            r"(?:received|obtained)\s+from\s+a\s+third\s+party",
            r"third[- ]party\s+(?:source|disclosure|receipt)",
        ],
        "negative_check": True,
        "issue": "Missing third-party receipt carveout",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Add: Information received from a third party not under a confidentiality obligation to the disclosing party",
        "fallback": "Add: Information lawfully obtained from a third party who had the right to disclose it",
        "rationale": {
            "recipient": "Without this, information legitimately received from other sources becomes restricted",
            "discloser": "Standard carveout; low risk to discloser",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "missing_legal_compulsion",
        "clause": "Standard Carveouts",
        "patterns": [],
        "positive_patterns": [
            r"(?:required|compelled|ordered)\s+(?:by|under)\s+law",
            r"court\s+order",
            r"subpoena",
            r"legal(?:ly)?\s+(?:required|compelled)",
        ],
        "negative_check": True,
        "issue": "Missing legal compulsion carveout",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Add: Disclosure required by law, court order, or governmental authority, with prompt notice to disclosing party prior to disclosure",
        "fallback": "Add: Disclosure compelled by legal process, with notice to the extent permitted by law",
        "rationale": {
            "recipient": "Without this, compliance with legal obligations could technically breach the NDA",
            "discloser": "Standard carveout; notice requirement protects discloser's ability to seek protective order",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "non_compete",
        "clause": "Problematic Provisions",
        "patterns": [
            r"non[- ]?compete",
            r"shall\s+not\s+compete",
            r"competitive\s+activit",
            r"refrain\s+from\s+compet",
        ],
        "issue": "Non-compete clause restricting business activities",
        "risk": {"recipient": "H", "discloser": "H"},
        "preferred": "Delete entire non-compete provision; inappropriate for an NDA",
        "fallback": "If counterparty insists, require separate non-compete agreement with independent consideration and limited scope/duration",
        "rationale": {
            "recipient": "Non-compete in NDA restricts business operations without appropriate consideration",
            "discloser": "Non-compete enforceability varies by jurisdiction; separate agreement is more defensible",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "non_solicitation",
        "clause": "Problematic Provisions",
        "patterns": [
            r"non[- ]?solicitation",
            r"shall\s+not\s+solicit",
            r"refrain\s+from\s+soliciting",
        ],
        "issue": "Non-solicitation clause restricting hiring or business solicitation",
        "risk": {"recipient": "H", "discloser": "M"},
        "preferred": "Delete non-solicitation provision entirely",
        "fallback": "Limit to direct solicitation of specific named individuals for 12 months; exclude general advertising and unsolicited inquiries",
        "rationale": {
            "recipient": "Non-solicitation in NDA limits talent acquisition and business development without appropriate context",
            "discloser": "May be appropriate in M&A context; otherwise excessive for standard NDA",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "ip_assignment",
        "clause": "Problematic Provisions",
        "patterns": [
            r"assign(?:s|ment)?\s+(?:all\s+)?(?:right|title|interest)",
            r"work[- ]?(?:for[- ]?hire|made\s+for\s+hire)",
            r"hereby\s+assign",
        ],
        "issue": "IP assignment or work-for-hire clause in NDA",
        "risk": {"recipient": "H", "discloser": "H"},
        "preferred": "Delete IP assignment provision; NDA should protect information, not transfer IP rights",
        "fallback": "If IP transfer needed, negotiate in a separate services or development agreement with appropriate scope and consideration",
        "rationale": {
            "recipient": "IP assignment in NDA transfers rights without appropriate scope or consideration",
            "discloser": "IP assignment in NDA is overbroad and may be unenforceable; use separate IP agreement",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "broad_residuals",
        "clause": "Residuals",
        "patterns": [
            r"residual(?:s)?\s+(?:clause|knowledge|information|rights)",
            r"unaided\s+(?:memory|recall|recollection)",
            r"retained\s+in\s+(?:the\s+)?(?:unaided\s+)?memor",
            r"general\s+(?:knowledge|skills|experience)\s+retained",
        ],
        "issue": "Broad residuals clause allowing use of ideas retained in memory",
        "risk": {"recipient": "L", "discloser": "H"},
        "preferred": {
            "recipient": "Accept if narrowly scoped to exclude trade secrets and specific data",
            "discloser": "Delete residuals clause entirely; it undermines NDA protection",
        },
        "fallback": {
            "recipient": "Accept with requirement that retention was not intentional",
            "discloser": "Narrow to general concepts only, excluding trade secrets, algorithms, and specific data points",
        },
        "rationale": {
            "recipient": "Residuals clause protects freedom to operate after NDA engagement",
            "discloser": "Broad residuals clause effectively creates a carveout that swallows the NDA",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "ip_license_grant",
        "clause": "Problematic Provisions",
        "patterns": [
            r"grant(?:s)?\s+(?:a\s+)?(?:non-exclusive|exclusive|perpetual|irrevocable)\s+license",
            r"license\s+to\s+use.*confidential",
            r"right\s+to\s+(?:use|exploit|commercialize)",
        ],
        "issue": "License grant over confidential information",
        "risk": {"recipient": "H", "discloser": "H"},
        "preferred": "Delete license grant; NDA protects information, it does not license it",
        "fallback": "If license needed, negotiate in separate agreement with appropriate scope and terms",
        "rationale": {
            "recipient": "License grant in NDA creates confusion about permitted use vs. confidentiality obligations",
            "discloser": "License grant undermines the protective purpose of the NDA",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "liquidated_damages",
        "clause": "Remedies",
        "patterns": [
            r"liquidated\s+damages",
            r"stipulated\s+damages",
            r"penalty\s+(?:of|in\s+the\s+amount)",
            r"\$[\d,]+\s+(?:per|for\s+each)\s+(?:breach|violation)",
        ],
        "issue": "Liquidated damages or penalty clause for breach",
        "risk": {"recipient": "H", "discloser": "M"},
        "preferred": "Delete liquidated damages; standard NDA remedies (injunctive relief + actual damages) are sufficient",
        "fallback": "If counterparty insists, require that amount is a reasonable pre-estimate of loss and cap at a defined amount",
        "rationale": {
            "recipient": "Liquidated damages transform NDA from protective agreement into penalty contract",
            "discloser": "Liquidated damages may be unenforceable if deemed a penalty; actual damages are more reliable",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "perpetual_obligations",
        "clause": "Term & Duration",
        "patterns": [
            r"perpetual(?:ly)?\s+(?:confidential|obligat)",
            r"obligations?\s+(?:shall\s+)?(?:survive|continue)\s+(?:in\s+)?perpetuit",
            r"indefinite(?:ly)?\s+(?:period|term|duration|obligat)",
            r"forever\s+(?:remain|be\s+kept|maintain)",
        ],
        "issue": "Perpetual or indefinite confidentiality obligations",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Limit obligations to 3 years from date of disclosure or termination of agreement",
        "fallback": "Accept 5-year survival period; perpetual only for information meeting the legal definition of trade secret",
        "rationale": {
            "recipient": "Perpetual obligations create indefinite legal burden with no exit and unclear long-term compliance",
            "discloser": "Longer obligations provide more protection; perpetual may be appropriate for trade secrets",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "indemnification",
        "clause": "Remedies",
        "patterns": [
            r"indemnif(?:y|ication)",
            r"hold\s+harmless",
            r"defend\s+and\s+indemnif",
        ],
        "issue": "Indemnification clause in NDA",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Remove indemnification; standard NDA remedies are sufficient",
        "fallback": "If retained, make mutual and subject to a reasonable cap",
        "rationale": {
            "recipient": "Indemnification in NDA creates additional financial exposure beyond standard breach remedies",
            "discloser": "Indemnification adds protection but may complicate negotiation unnecessarily",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "audit_rights",
        "clause": "Problematic Provisions",
        "patterns": [
            r"(?:unlimited|unrestricted)\s+(?:audit|inspection|access)",
            r"audit\s+(?:at\s+any\s+time|without\s+(?:notice|limitation))",
            r"right\s+to\s+inspect.*(?:premises|records|systems)",
            r"audit\s+(?:right|provision|clause)",
        ],
        "issue": "Audit rights allowing inspection of premises, records, or systems",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Remove audit rights; excessive for standard NDA",
        "fallback": "Limit to annual audit with 30 days notice, during business hours, at auditing party's expense",
        "rationale": {
            "recipient": "Audit rights create operational burden and security concerns for receiving party",
            "discloser": "Audit rights provide verification but may be impractical and damage relationship",
        },
        "owner": "legal",
        "deadline": "pre-signing",
    },
    {
        "id": "one_sided_obligations",
        "clause": "Party Obligations",
        "patterns": [
            r"(?:only|solely)\s+(?:the\s+)?(?:receiving|recipient)\s+(?:party\s+)?(?:shall|agrees?)",
            r"(?:disclos(?:ing|er)|provider)\s+(?:party\s+)?(?:shall\s+have\s+no|is\s+not\s+(?:subject|bound))",
        ],
        "issue": "One-sided obligations in purportedly mutual NDA",
        "risk": {"recipient": "M", "discloser": "L"},
        "preferred": "Make obligations mutual if agreement is structured as mutual NDA",
        "fallback": "Accept one-way obligations if agreement is accurately labeled as unilateral; ensure structure matches title",
        "rationale": {
            "recipient": "One-sided obligations in a 'mutual' NDA create imbalanced risk allocation",
            "discloser": "One-sided obligations are appropriate for unilateral NDAs; ensure labeling matches structure",
        },
        "owner": "legal",
        "deadline": "pre-signing",
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


def get_value(field, perspective: str) -> str:
    """Get perspective-specific value from a field that may be a string or dict."""
    if isinstance(field, dict):
        return field.get(perspective, field.get("recipient", str(field)))
    return str(field)


def detect_issues(text: str, perspective: str) -> List[Dict]:
    """Detect all issues in NDA text from the given perspective."""
    text_lower = text.lower()
    issues: List[Dict] = []
    issue_counter = 0

    for issue_def in ISSUE_DEFINITIONS:
        triggered = False

        if issue_def.get("negative_check"):
            # Negative check: issue triggers when positive_patterns are NOT found
            found = False
            for pattern in issue_def.get("positive_patterns", []):
                if re.search(pattern, text_lower):
                    found = True
                    break
            triggered = not found
        else:
            # Positive check: issue triggers when patterns ARE found
            for pattern in issue_def.get("patterns", []):
                if re.search(pattern, text_lower):
                    triggered = True
                    break

        if triggered:
            issue_counter += 1
            risk = issue_def["risk"]
            risk_rating = risk.get(perspective, risk.get("recipient", "M"))

            issues.append({
                "id": issue_counter,
                "issue_key": issue_def["id"],
                "clause": issue_def["clause"],
                "issue": issue_def["issue"],
                "risk": risk_rating,
                "preferred_redline": get_value(issue_def["preferred"], perspective),
                "fallback": get_value(issue_def["fallback"], perspective),
                "rationale": get_value(issue_def["rationale"], perspective),
                "owner": issue_def["owner"],
                "deadline": issue_def["deadline"],
            })

    # Sort by risk: H first, then M, then L
    risk_order = {"H": 0, "M": 1, "L": 2}
    issues.sort(key=lambda i: (risk_order.get(i["risk"], 1), i["id"]))

    # Re-number after sort
    for idx, issue in enumerate(issues, 1):
        issue["id"] = idx

    return issues


def compute_summary(issues: List[Dict]) -> Dict:
    """Compute issue summary counts."""
    counts = {"H": 0, "M": 0, "L": 0}
    for issue in issues:
        counts[issue["risk"]] = counts.get(issue["risk"], 0) + 1
    return {
        "total_issues": len(issues),
        "high": counts["H"],
        "medium": counts["M"],
        "low": counts["L"],
    }


def format_text_output(result: Dict) -> str:
    """Format issue log as human-readable text."""
    lines = []
    lines.append("NDA CLAUSE REVIEW -- ISSUE LOG")
    lines.append("=" * 55)
    lines.append(f"File: {result['file']}")
    lines.append(f"Perspective: {result['perspective'].title()}")
    s = result["summary"]
    lines.append(f"Issues Found: {s['total_issues']} (H:{s['high']} M:{s['medium']} L:{s['low']})")
    lines.append("")

    if not result["issues"]:
        lines.append("No issues detected. NDA appears well-drafted from this perspective.")
        return "\n".join(lines)

    for issue in result["issues"]:
        lines.append(
            f" {issue['id']:>2}  [{issue['risk']}]  {issue['clause']}"
        )
        lines.append(f"        Issue: {issue['issue']}")
        lines.append(f"        Preferred: {issue['preferred_redline']}")
        lines.append(f"        Fallback:  {issue['fallback']}")
        lines.append(f"        Rationale: {issue['rationale']}")
        lines.append(f"        Owner: {issue['owner']} | Deadline: {issue['deadline']}")
        lines.append("")

    # Executive summary
    lines.append("-" * 55)
    lines.append("EXECUTIVE SUMMARY")
    lines.append("")
    if s["high"] > 0:
        lines.append(f"  {s['high']} HIGH-risk issue(s) must be resolved before signing.")
    if s["medium"] > 0:
        lines.append(f"  {s['medium']} MEDIUM-risk issue(s) should be addressed in negotiation.")
    if s["low"] > 0:
        lines.append(f"  {s['low']} LOW-risk issue(s) are nice-to-have improvements.")
    lines.append("")

    if s["high"] > 0:
        lines.append("  RECOMMENDATION: Do not sign until all HIGH-risk issues are resolved.")
    elif s["medium"] > 0:
        lines.append("  RECOMMENDATION: Negotiate MEDIUM-risk items; sign with documented risk acceptance if needed.")
    else:
        lines.append("  RECOMMENDATION: LOW-risk issues only. Acceptable to sign with minor improvements.")

    return "\n".join(lines)


def review_nda(file_path: str, perspective: str) -> Dict:
    """Main review pipeline."""
    text = read_nda(file_path)
    issues = detect_issues(text, perspective)
    summary = compute_summary(issues)

    return {
        "file": os.path.basename(file_path),
        "perspective": perspective,
        "issues": issues,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Deep clause-by-clause NDA review with issue log, redlines, and fallbacks."
    )
    parser.add_argument("nda_file", help="Path to NDA text file (.txt or .md)")
    parser.add_argument("-p", "--perspective", choices=["recipient", "discloser"],
                        default="recipient",
                        help="Review perspective: recipient (default) or discloser")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output in JSON format")
    parser.add_argument("-o", "--output", help="Write output to file")

    args = parser.parse_args()
    result = review_nda(args.nda_file, args.perspective)

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
