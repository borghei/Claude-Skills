#!/usr/bin/env python3
"""
NDA Screener

Scans NDA text for red flags, missing carveouts, and problematic provisions.
Outputs GREEN/YELLOW/RED classification with reasoning.

Usage:
    python nda_screener.py nda_draft.txt
    python nda_screener.py incoming_nda.md --json
    python nda_screener.py nda_draft.txt --output screening.json --json
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple


# Standard carveouts that should be present in every NDA
STANDARD_CARVEOUTS = {
    "public_knowledge": {
        "patterns": [
            r"public(?:ly)?\s+(?:known|available|domain)",
            r"generally\s+(?:known|available)\s+to\s+the\s+public",
            r"becomes?\s+public(?:ly)?\s+(?:known|available)",
            r"part\s+of\s+the\s+public\s+domain",
            r"public\s+knowledge",
        ],
        "description": "Information that is or becomes publicly available",
    },
    "prior_possession": {
        "patterns": [
            r"prior\s+(?:possession|knowledge|receipt)",
            r"already\s+(?:known|possessed|in\s+possession)",
            r"(?:known|possessed)\s+(?:by|to)\s+the\s+receiving",
            r"in\s+(?:its|the)\s+possession\s+prior",
            r"previously\s+known",
        ],
        "description": "Information already known to the receiving party before disclosure",
    },
    "independent_development": {
        "patterns": [
            r"independent(?:ly)?\s+develop",
            r"developed\s+independent(?:ly)?",
            r"without\s+(?:use\s+of|reference\s+to|reliance\s+on)\s+(?:the\s+)?confidential",
            r"independent\s+creation",
        ],
        "description": "Information independently developed without use of confidential information",
    },
    "third_party_receipt": {
        "patterns": [
            r"(?:received|obtained)\s+from\s+a\s+third\s+party",
            r"third[- ]party\s+(?:source|disclosure|receipt)",
            r"lawfully\s+(?:received|obtained|acquired)\s+from",
            r"rightfully\s+(?:received|obtained)\s+from",
        ],
        "description": "Information received from a third party without confidentiality obligation",
    },
    "legal_compulsion": {
        "patterns": [
            r"(?:required|compelled|ordered)\s+(?:by|under|pursuant\s+to)\s+law",
            r"legal(?:ly)?\s+(?:required|compelled|obligated)",
            r"court\s+order",
            r"subpoena",
            r"government(?:al)?\s+(?:request|order|requirement)",
            r"judicial\s+(?:order|process|proceeding)",
            r"regulatory\s+(?:requirement|authority|request)",
        ],
        "description": "Disclosure required by law, court order, or governmental authority",
    },
}

# Problematic provisions to flag
RED_FLAG_PROVISIONS = [
    {
        "id": "non_solicitation",
        "patterns": [
            r"non[- ]?solicitation",
            r"shall\s+not\s+solicit",
            r"refrain\s+from\s+soliciting",
            r"not\s+(?:directly\s+or\s+indirectly\s+)?solicit",
        ],
        "severity": "RED",
        "description": "Non-solicitation clause restricting hiring or business solicitation",
        "recommendation": "Remove non-solicitation clause; it is not standard in NDAs",
    },
    {
        "id": "non_compete",
        "patterns": [
            r"non[- ]?compete",
            r"shall\s+not\s+compete",
            r"competitive\s+activit",
            r"not\s+engage\s+in\s+(?:any\s+)?(?:business|activit)",
            r"refrain\s+from\s+compet",
        ],
        "severity": "RED",
        "description": "Non-compete clause restricting business activities",
        "recommendation": "Remove non-compete clause; unacceptable in a standard NDA",
    },
    {
        "id": "exclusivity",
        "patterns": [
            r"exclusive(?:ly)?\s+(?:deal|negotiate|discuss|engage)",
            r"exclusivity\s+(?:period|obligation|provision)",
            r"shall\s+not\s+(?:discuss|negotiate|engage)\s+with\s+(?:any\s+)?(?:other|third)",
        ],
        "severity": "RED",
        "description": "Exclusivity provision limiting engagement with other parties",
        "recommendation": "Remove exclusivity clause; inappropriate for an NDA",
    },
    {
        "id": "residuals",
        "patterns": [
            r"residual(?:s)?\s+(?:clause|knowledge|information|rights)",
            r"unaided\s+(?:memory|recall|recollection)",
            r"retained\s+in\s+(?:the\s+)?(?:unaided\s+)?memor",
            r"general\s+(?:knowledge|skills|experience)\s+retained",
        ],
        "severity": "YELLOW",
        "description": "Residuals clause allowing use of ideas retained in memory",
        "recommendation": "Remove or narrowly scope residuals clause to exclude trade secrets",
    },
    {
        "id": "ip_assignment",
        "patterns": [
            r"assign(?:s|ment)?\s+(?:all\s+)?(?:right|title|interest)\s+in",
            r"(?:intellectual\s+property|ip)\s+(?:rights?\s+)?(?:shall\s+)?(?:be\s+)?(?:owned\s+by|vest\s+in|transfer)",
            r"work[- ]?(?:for[- ]?hire|made\s+for\s+hire)",
            r"hereby\s+assign",
        ],
        "severity": "RED",
        "description": "IP assignment or work-for-hire clause in an NDA",
        "recommendation": "Remove IP assignment; NDAs should not transfer IP rights",
    },
    {
        "id": "ip_license_grant",
        "patterns": [
            r"grant(?:s)?\s+(?:a\s+)?(?:non-exclusive|exclusive|perpetual|irrevocable)\s+license",
            r"license\s+to\s+use.*confidential\s+information",
            r"right\s+to\s+(?:use|exploit|commercialize)",
        ],
        "severity": "RED",
        "description": "License grant over confidential information",
        "recommendation": "Remove license grant; NDA should protect information, not license it",
    },
    {
        "id": "liquidated_damages",
        "patterns": [
            r"liquidated\s+damages",
            r"stipulated\s+damages",
            r"pre[- ]?determined\s+damages",
            r"penalty\s+(?:of|in\s+the\s+amount)",
            r"\$[\d,]+\s+(?:per|for\s+each)\s+(?:breach|violation)",
        ],
        "severity": "RED",
        "description": "Liquidated damages or penalty provision for breach",
        "recommendation": "Remove liquidated damages; standard remedies are sufficient for NDAs",
    },
    {
        "id": "unlimited_audit",
        "patterns": [
            r"(?:unlimited|unrestricted)\s+(?:audit|inspection|access)",
            r"audit\s+(?:at\s+any\s+time|without\s+(?:notice|limitation))",
            r"right\s+to\s+inspect.*(?:premises|records|systems)",
        ],
        "severity": "YELLOW",
        "description": "Audit rights allowing inspection of premises or systems",
        "recommendation": "Remove or limit audit rights; excessive for standard NDAs",
    },
    {
        "id": "perpetual_obligations",
        "patterns": [
            r"perpetual(?:ly)?\s+(?:confidential|obligat)",
            r"obligations?\s+(?:shall\s+)?(?:survive|continue)\s+(?:in\s+)?perpetuit",
            r"indefinite(?:ly)?\s+(?:period|term|duration|obligat)",
            r"no\s+expiration\s+(?:of\s+)?(?:confidentiality|obligations)",
            r"forever\s+(?:remain|be\s+kept|maintain)",
        ],
        "severity": "YELLOW",
        "description": "Perpetual or indefinite confidentiality obligations",
        "recommendation": "Limit obligations to 3-5 years from disclosure or termination",
    },
    {
        "id": "overbroad_definition",
        "patterns": [
            r"all\s+information\s+(?:of\s+any\s+(?:kind|nature|type)|whatsoever|disclosed)",
            r"any\s+(?:and\s+all\s+)?information\s+(?:relating\s+to|concerning|regarding)\s+(?:the\s+)?(?:disclos|party)",
            r"without\s+limitation.*(?:oral|written|visual|electronic|any\s+(?:form|medium))",
        ],
        "severity": "YELLOW",
        "description": "Overbroad definition of confidential information",
        "recommendation": "Narrow definition to information marked confidential or reasonably understood to be confidential",
    },
    {
        "id": "one_sided_obligations",
        "patterns": [
            r"(?:only|solely)\s+(?:the\s+)?(?:receiving|recipient)\s+(?:party\s+)?(?:shall|agrees?|is\s+obligated)",
            r"(?:disclos(?:ing|er)|provider)\s+(?:party\s+)?(?:shall\s+have\s+no|is\s+not\s+(?:subject|bound))",
        ],
        "severity": "YELLOW",
        "description": "One-sided obligations (only binding on receiving party)",
        "recommendation": "Request mutual obligations or ensure one-way structure is appropriate for the relationship",
    },
]

# Structure detection patterns
STRUCTURE_PATTERNS = {
    "mutual": [
        r"mutual\s+(?:non[- ]?disclosure|nda|confidentiality)",
        r"each\s+party\s+(?:may\s+)?disclos",
        r"(?:both|each)\s+parties?\s+(?:shall|agree)",
        r"disclosing\s+party.*receiving\s+party",
    ],
    "one_way": [
        r"(?:one[- ]?way|unilateral)\s+(?:non[- ]?disclosure|nda|confidentiality)",
        r"(?:the\s+)?(?:company|discloser)\s+(?:may\s+)?disclose.*(?:the\s+)?(?:recipient|receiver)\s+(?:shall|agrees?)",
    ],
    "return_destruction": [
        r"return\s+(?:or\s+)?destroy",
        r"destroy\s+(?:or\s+)?return",
        r"(?:return|destruction)\s+of\s+(?:confidential\s+)?(?:information|materials)",
        r"certif(?:y|ication)\s+of\s+destruction",
    ],
    "injunctive_relief": [
        r"injunctive\s+relief",
        r"specific\s+performance",
        r"equitable\s+relief",
        r"irreparable\s+(?:harm|injury|damage)",
    ],
    "term_defined": [
        r"(?:initial\s+)?term\s+(?:of\s+)?(?:this\s+)?(?:agreement\s+)?(?:shall\s+be|is)\s+\d",
        r"\d+\s+(?:year|month|day)s?\s+(?:from|after|following)",
        r"effective\s+(?:date|period).*(?:terminat|expir)",
    ],
    "governing_law": [
        r"govern(?:ed|ing)\s+(?:by\s+)?(?:the\s+)?laws?\s+of",
        r"(?:state|commonwealth)\s+of\s+\w+",
        r"jurisdiction\s+of\s+(?:the\s+)?courts?",
    ],
    "permitted_disclosures": [
        r"permitted\s+disclos",
        r"(?:representatives?|advisors?|agents?|employees?|officers?|directors?)\s+(?:who\s+)?(?:have\s+a\s+)?need[- ]to[- ]know",
        r"disclose\s+to\s+(?:its\s+)?(?:representatives?|advisors?|counsel|accountants?)",
    ],
}


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


def check_carveouts(text: str) -> Dict[str, bool]:
    """Check which standard carveouts are present."""
    text_lower = text.lower()
    results = {}
    for carveout_id, carveout_def in STANDARD_CARVEOUTS.items():
        found = False
        for pattern in carveout_def["patterns"]:
            if re.search(pattern, text_lower):
                found = True
                break
        results[carveout_id] = found
    return results


def detect_red_flags(text: str) -> List[Dict]:
    """Detect problematic provisions in NDA text."""
    text_lower = text.lower()
    flags: List[Dict] = []

    for provision in RED_FLAG_PROVISIONS:
        for pattern in provision["patterns"]:
            match = re.search(pattern, text_lower)
            if match:
                # Extract context around the match
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text[start:end].strip().replace("\n", " ")

                flags.append({
                    "id": provision["id"],
                    "severity": provision["severity"],
                    "description": provision["description"],
                    "recommendation": provision["recommendation"],
                    "context": context[:200],
                })
                break  # One match per provision

    return flags


def detect_structure(text: str) -> Dict[str, bool]:
    """Detect structural elements of the NDA."""
    text_lower = text.lower()
    results = {}
    for element, patterns in STRUCTURE_PATTERNS.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found = True
                break
        results[element] = found
    return results


def classify_nda(carveouts: Dict[str, bool], red_flags: List[Dict],
                 structure: Dict[str, bool]) -> Tuple[str, str]:
    """Classify NDA as GREEN/YELLOW/RED with reasoning."""
    reasons: List[str] = []

    # Count issues
    missing_carveouts = [k for k, v in carveouts.items() if not v]
    red_severity_flags = [f for f in red_flags if f["severity"] == "RED"]
    yellow_severity_flags = [f for f in red_flags if f["severity"] == "YELLOW"]

    # RED classification triggers
    if len(missing_carveouts) >= 3:
        reasons.append(f"{len(missing_carveouts)} missing standard carveouts")
    if red_severity_flags:
        flag_names = [f["id"] for f in red_severity_flags]
        reasons.append(f"Critical provisions: {', '.join(flag_names)}")

    if len(missing_carveouts) >= 3 or red_severity_flags:
        summary = "; ".join(reasons) + ". Do not sign without senior counsel review."
        return "RED", summary

    # YELLOW classification triggers
    if missing_carveouts:
        carveout_names = [STANDARD_CARVEOUTS[k]["description"] for k in missing_carveouts]
        reasons.append(f"Missing carveout(s): {'; '.join(carveout_names)}")
    if yellow_severity_flags:
        flag_names = [f["description"] for f in yellow_severity_flags]
        reasons.append(f"Minor concerns: {'; '.join(flag_names)}")
    if not structure.get("mutual") and not structure.get("one_way"):
        reasons.append("Agreement structure unclear (mutual vs. one-way)")
    if not structure.get("return_destruction"):
        reasons.append("No return/destruction obligation detected")
    if not structure.get("term_defined"):
        reasons.append("No defined term or duration detected")

    if reasons:
        summary = "; ".join(reasons) + ". Route to counsel for review."
        return "YELLOW", summary

    # GREEN classification
    summary = "All standard carveouts present; no problematic provisions detected. Standard approval."
    return "GREEN", summary


def format_text_output(result: Dict) -> str:
    """Format screening results as human-readable text."""
    lines = []
    lines.append("NDA SCREENING REPORT")
    lines.append("=" * 50)
    lines.append(f"File: {result['file']}")
    lines.append(f"Classification: {result['classification']}")
    lines.append(f"Summary: {result['summary']}")
    lines.append("")

    # Carveouts
    lines.append("STANDARD CARVEOUTS")
    lines.append("-" * 30)
    for carveout_id, present in result["carveouts"].items():
        status = "PRESENT" if present else "MISSING"
        desc = STANDARD_CARVEOUTS[carveout_id]["description"]
        marker = "  [+]" if present else "  [!]"
        lines.append(f"{marker} {desc}: {status}")
    lines.append("")

    # Structure
    lines.append("STRUCTURE")
    lines.append("-" * 30)
    for element, detected in result["structure"].items():
        status = "Yes" if detected else "No"
        lines.append(f"  {element.replace('_', ' ').title()}: {status}")
    lines.append("")

    # Red flags
    if result["red_flags"]:
        lines.append("RED FLAGS")
        lines.append("-" * 30)
        for flag in result["red_flags"]:
            lines.append(f"  [{flag['severity']}] {flag['description']}")
            lines.append(f"         Recommendation: {flag['recommendation']}")
            if flag.get("context"):
                lines.append(f"         Context: ...{flag['context']}...")
        lines.append("")
    else:
        lines.append("RED FLAGS: None detected")
        lines.append("")

    return "\n".join(lines)


def screen_nda(file_path: str) -> Dict:
    """Main screening pipeline."""
    text = read_nda(file_path)
    carveouts = check_carveouts(text)
    red_flags = detect_red_flags(text)
    structure = detect_structure(text)
    classification, summary = classify_nda(carveouts, red_flags, structure)

    return {
        "file": os.path.basename(file_path),
        "classification": classification,
        "summary": summary,
        "carveouts": carveouts,
        "red_flags": red_flags,
        "structure": structure,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Screen NDA text for red flags and classify as GREEN/YELLOW/RED."
    )
    parser.add_argument("nda_file", help="Path to NDA text file (.txt or .md)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output in JSON format")
    parser.add_argument("-o", "--output", help="Write output to file")

    args = parser.parse_args()
    result = screen_nda(args.nda_file)

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
