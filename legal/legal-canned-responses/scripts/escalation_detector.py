#!/usr/bin/env python3
"""
Legal Escalation Detector

Analyzes inquiry text for escalation triggers using keyword and pattern
matching against universal and category-specific trigger definitions.

Usage:
    python escalation_detector.py --text "We received a subpoena from the DOJ"
    python escalation_detector.py --text "vendor threatening litigation" --category vendor --json
    python escalation_detector.py --text "reporter asking about data breach" --category privacy
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# Universal escalation triggers (always checked)
UNIVERSAL_TRIGGERS: List[Dict[str, Any]] = [
    {
        "id": "UT-001",
        "name": "Potential or Active Litigation",
        "patterns": [
            r"\blitigation\b", r"\blawsuit\b", r"\bsue\b", r"\bsuing\b",
            r"\bfiled\s+(a\s+)?complaint\b", r"\bcourt\s+order\b", r"\binjunction\b",
            r"\blegal\s+action\b", r"\bclass\s+action\b", r"\blitigate\b",
        ],
        "severity": "HIGH",
        "routing": "General Counsel",
        "reason": "Legal exposure requires immediate counsel assessment",
    },
    {
        "id": "UT-002",
        "name": "Regulatory Investigation",
        "patterns": [
            r"\bregulatory\s+investigation\b", r"\bregulator\b", r"\benforcement\s+action\b",
            r"\bcompliance\s+investigation\b", r"\baudit\s+by\s+\w+\s+authority\b",
            r"\bregulatory\s+inquiry\b", r"\bsanction\b",
        ],
        "severity": "HIGH",
        "routing": "General Counsel / Regulatory Affairs",
        "reason": "Regulatory response requires strategic legal approach",
    },
    {
        "id": "UT-003",
        "name": "Government or Law Enforcement",
        "patterns": [
            r"\bgovernment\s+inquiry\b", r"\blaw\s+enforcement\b", r"\bfbi\b",
            r"\bdoj\b", r"\bdepartment\s+of\s+justice\b", r"\bsec\b(?!\s*tion)",
            r"\bftc\b", r"\bfda\b", r"\bpolice\b", r"\bprosecutor\b",
            r"\bgrand\s+jury\b", r"\bsubpoena\b", r"\bwarrant\b",
            r"\bcivil\s+investigative\s+demand\b",
        ],
        "severity": "CRITICAL",
        "routing": "General Counsel (Immediate)",
        "reason": "Constitutional and procedural rights at stake",
    },
    {
        "id": "UT-004",
        "name": "Binding Legal Commitment",
        "patterns": [
            r"\bbinding\s+(legal\s+)?commitment\b", r"\bsign\s+(the\s+)?agreement\b",
            r"\bexecute\s+(the\s+)?contract\b", r"\bguarantee\b", r"\bindemnif",
            r"\bwaiver\b", r"\brelease\s+of\s+(all\s+)?claims\b",
        ],
        "severity": "HIGH",
        "routing": "Contracts / General Counsel",
        "reason": "Cannot create legal obligations without counsel review",
    },
    {
        "id": "UT-005",
        "name": "Criminal Liability",
        "patterns": [
            r"\bcriminal\b", r"\bfraud\b", r"\bbribery\b", r"\bcorruption\b",
            r"\bembezzlement\b", r"\bmoney\s+laundering\b", r"\bwhistleblow",
            r"\bcriminal\s+liability\b", r"\bcriminal\s+investigation\b",
        ],
        "severity": "CRITICAL",
        "routing": "General Counsel (Immediate)",
        "reason": "Requires immediate counsel involvement for defense strategy",
    },
    {
        "id": "UT-006",
        "name": "Media Attention",
        "patterns": [
            r"\bmedia\b", r"\bpress\b", r"\breporter\b", r"\bjournalist\b",
            r"\bnewspaper\b", r"\bnews\b.*\barticle\b", r"\bwall\s+street\s+journal\b",
            r"\bnew\s+york\s+times\b", r"\bbloomberg\b", r"\breuters\b",
            r"\bpublic\s+statement\b", r"\bpress\s+release\b",
        ],
        "severity": "HIGH",
        "routing": "General Counsel + Communications",
        "reason": "Reputational risk requires coordinated legal-comms response",
    },
    {
        "id": "UT-007",
        "name": "Unprecedented Situation",
        "patterns": [
            r"\bfirst\s+time\b", r"\bnever\s+(before|seen|encountered)\b",
            r"\bunprecedented\b", r"\bno\s+precedent\b", r"\bnovel\s+(issue|situation|question)\b",
            r"\buncharted\b",
        ],
        "severity": "MEDIUM",
        "routing": "Senior Counsel",
        "reason": "No template exists; bespoke legal analysis needed",
    },
    {
        "id": "UT-008",
        "name": "Multi-Jurisdictional Conflict",
        "patterns": [
            r"\bmulti.?jurisdictional\b", r"\bcross.?border\b", r"\binternational\s+dispute\b",
            r"\bconflict\s+of\s+laws\b", r"\bforeign\s+(government|authority|court)\b",
            r"\bjurisdiction\s+conflict\b", r"\bextraterritorial\b",
        ],
        "severity": "HIGH",
        "routing": "International / General Counsel",
        "reason": "Cross-border legal complexity requires expert analysis",
    },
]

# Category-specific triggers
CATEGORY_TRIGGERS: Dict[str, List[Dict[str, Any]]] = {
    "dsr": [
        {
            "id": "DSR-001", "name": "Minor Data Subject",
            "patterns": [r"\bminor\b", r"\bchild\b", r"\bunder\s+\d+\b", r"\bparent\b.*\bconsent\b"],
            "severity": "HIGH", "routing": "Privacy Counsel",
            "reason": "Children's data requires special protections and counsel review",
        },
        {
            "id": "DSR-002", "name": "Litigation Hold Conflict",
            "patterns": [r"\blitigation\s+hold\b", r"\blegal\s+hold\b", r"\bpreserv"],
            "severity": "HIGH", "routing": "Litigation + Privacy Counsel",
            "reason": "DSR may conflict with preservation obligations",
        },
        {
            "id": "DSR-003", "name": "HR/Employment Matter",
            "patterns": [r"\bemployee\b.*\b(file|record)\b", r"\bhr\b", r"\bhuman\s+resources\b",
                         r"\btermination\b", r"\bdisciplinary\b"],
            "severity": "MEDIUM", "routing": "Employment Counsel + Privacy",
            "reason": "Employment-related DSRs need special handling",
        },
        {
            "id": "DSR-004", "name": "Special Category Data",
            "patterns": [r"\bhealth\b", r"\bmedical\b", r"\bbiometric\b", r"\bgenetic\b",
                         r"\bracial\b", r"\bethnic\b", r"\bsexual\b", r"\breligio",
                         r"\bpolitical\b", r"\btrade\s+union\b"],
            "severity": "HIGH", "routing": "Privacy Counsel",
            "reason": "Special category data requires elevated protections",
        },
    ],
    "discovery": [
        {
            "id": "DIS-001", "name": "Criminal Liability in Discovery",
            "patterns": [r"\bcriminal\b", r"\bfraud\b", r"\bdestruction\s+of\s+evidence\b",
                         r"\bspoliation\b"],
            "severity": "CRITICAL", "routing": "General Counsel (Immediate)",
            "reason": "Criminal exposure requires immediate counsel involvement",
        },
        {
            "id": "DIS-002", "name": "Unclear Hold Scope",
            "patterns": [r"\bunclear\s+scope\b", r"\bwhat\s+(documents|data)\b",
                         r"\bhow\s+far\s+back\b", r"\bscope\s+question\b"],
            "severity": "HIGH", "routing": "Litigation Counsel",
            "reason": "Hold scope ambiguity risks under/over-preservation",
        },
        {
            "id": "DIS-003", "name": "Deletion Conflict",
            "patterns": [r"\balready\s+deleted\b", r"\bpurged\b", r"\bdestroyed\b",
                         r"\bauto.?delete\b", r"\bretention\s+polic"],
            "severity": "CRITICAL", "routing": "Litigation Counsel (Immediate)",
            "reason": "Potential spoliation requires immediate counsel attention",
        },
    ],
    "vendor": [
        {
            "id": "VEN-001", "name": "Vendor Dispute/Threat",
            "patterns": [r"\bthreatening\b", r"\bdispute\b", r"\bbreach\s+of\s+contract\b",
                         r"\bterminate\b.*\bagreement\b", r"\bpenalt"],
            "severity": "HIGH", "routing": "Contracts / General Counsel",
            "reason": "Vendor disputes may escalate to litigation",
        },
    ],
    "nda": [
        {
            "id": "NDA-001", "name": "Competitor NDA",
            "patterns": [r"\bcompetitor\b", r"\bcompeting\b", r"\brival\b"],
            "severity": "HIGH", "routing": "General Counsel + Business",
            "reason": "Competitor NDAs require strategic review of scope and terms",
        },
        {
            "id": "NDA-002", "name": "Government/Military",
            "patterns": [r"\bgovernment\b", r"\bmilitary\b", r"\bdefense\b", r"\bclassified\b",
                         r"\bsecurity\s+clearance\b"],
            "severity": "HIGH", "routing": "Government Contracts Counsel",
            "reason": "Government NDAs have special requirements and restrictions",
        },
    ],
    "subpoena": [
        {
            "id": "SUB-001", "name": "Always Escalate Subpoena",
            "patterns": [r".*"],  # Always matches
            "severity": "CRITICAL", "routing": "General Counsel (Immediate)",
            "reason": "ALL subpoena/legal process matters require counsel review",
        },
    ],
    "privacy": [
        {
            "id": "PRI-001", "name": "Data Breach",
            "patterns": [r"\bbreach\b", r"\bleak\b", r"\bunauthorized\s+access\b",
                         r"\bdata\s+incident\b", r"\bcompromised\b"],
            "severity": "CRITICAL", "routing": "Privacy Counsel + CISO",
            "reason": "Data breaches have mandatory notification timelines",
        },
    ],
    "insurance": [
        {
            "id": "INS-001", "name": "Coverage Dispute",
            "patterns": [r"\bden(y|ied|ial)\b", r"\bcoverage\s+dispute\b",
                         r"\breservation\s+of\s+rights\b", r"\bbad\s+faith\b"],
            "severity": "HIGH", "routing": "Insurance / General Counsel",
            "reason": "Coverage disputes require legal strategy assessment",
        },
    ],
}


def check_triggers(text: str, triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check text against a list of triggers. Returns matched triggers."""
    matched = []
    text_lower = text.lower()

    for trigger in triggers:
        for pattern in trigger["patterns"]:
            if re.search(pattern, text_lower):
                matched.append({
                    "id": trigger["id"],
                    "name": trigger["name"],
                    "severity": trigger["severity"],
                    "routing": trigger["routing"],
                    "reason": trigger["reason"],
                    "matched_pattern": pattern,
                })
                break  # One match per trigger is enough

    return matched


def detect_escalation(text: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Run escalation detection on inquiry text."""
    universal_matches = check_triggers(text, UNIVERSAL_TRIGGERS)

    category_matches = []
    if category and category in CATEGORY_TRIGGERS:
        category_matches = check_triggers(text, CATEGORY_TRIGGERS[category])

    all_matches = universal_matches + category_matches
    should_escalate = len(all_matches) > 0

    # Determine highest severity
    severity_order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
    max_severity = "NONE"
    if all_matches:
        max_severity = max(all_matches, key=lambda m: severity_order.get(m["severity"], 0))["severity"]

    # Collect unique routing recommendations
    routing = list(set(m["routing"] for m in all_matches))

    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "input_text": text[:200] + ("..." if len(text) > 200 else ""),
        "category": category,
        "escalate": should_escalate,
        "max_severity": max_severity,
        "trigger_count": len(all_matches),
        "universal_triggers": len(universal_matches),
        "category_triggers": len(category_matches),
        "recommended_routing": routing,
        "matched_triggers": all_matches,
        "action": _build_action(should_escalate, max_severity, routing),
    }


def _build_action(escalate: bool, severity: str, routing: List[str]) -> str:
    """Build recommended action string."""
    if not escalate:
        return "No escalation needed. Proceed with standard template response."

    if severity == "CRITICAL":
        return (f"IMMEDIATE ESCALATION REQUIRED. Route to: {', '.join(routing)}. "
                "Do not send any templated response. Contact counsel immediately.")
    elif severity == "HIGH":
        return (f"ESCALATION REQUIRED. Route to: {', '.join(routing)}. "
                "Mark any draft response 'FOR COUNSEL REVIEW ONLY'.")
    else:
        return (f"ESCALATION RECOMMENDED. Route to: {', '.join(routing)}. "
                "Seek counsel guidance before proceeding with response.")


def format_text(result: Dict[str, Any]) -> str:
    """Format escalation result as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("ESCALATION ANALYSIS")
    lines.append("=" * 70)
    lines.append(f"Date:     {result['analysis_date']}")
    lines.append(f"Category: {result['category'] or 'All (universal only)'}")
    lines.append(f"Input:    {result['input_text']}")
    lines.append("")

    if result["escalate"]:
        lines.append(">>> ESCALATION REQUIRED <<<")
    else:
        lines.append("No escalation triggers detected.")

    lines.append("")
    lines.append(f"Severity:   {result['max_severity']}")
    lines.append(f"Triggers:   {result['trigger_count']} "
                 f"({result['universal_triggers']} universal, "
                 f"{result['category_triggers']} category-specific)")
    lines.append("")
    lines.append(f"ACTION: {result['action']}")

    if result.get("recommended_routing"):
        lines.append("")
        lines.append("RECOMMENDED ROUTING:")
        for route in result["recommended_routing"]:
            lines.append(f"  -> {route}")

    if result.get("matched_triggers"):
        lines.append("")
        lines.append("-" * 70)
        lines.append("MATCHED TRIGGERS:")
        lines.append("-" * 70)
        for trigger in result["matched_triggers"]:
            lines.append(f"  [{trigger['severity']}] {trigger['id']}: {trigger['name']}")
            lines.append(f"           {trigger['reason']}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze inquiry text for legal escalation triggers."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--text", required=True,
                        help="Inquiry text to analyze for escalation triggers")
    parser.add_argument("--category", default=None,
                        choices=["dsr", "discovery", "privacy", "vendor",
                                 "nda", "subpoena", "insurance"],
                        help="Optional category for category-specific triggers")

    args = parser.parse_args()

    try:
        result = detect_escalation(args.text, args.category)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
