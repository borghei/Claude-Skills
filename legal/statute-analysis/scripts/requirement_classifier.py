#!/usr/bin/env python3
"""
Requirement Classifier

Takes statutory requirements (from text or JSON) and classifies each by type,
implementation team, enforcement mechanism, and penalty type. Generates an
implementation matrix for compliance planning.

Usage:
    python requirement_classifier.py --input requirements.json
    python requirement_classifier.py --text "Controllers must provide a privacy notice..."
    python requirement_classifier.py --input requirements.json --json
    python requirement_classifier.py --input requirements.json --output matrix.json

Input JSON schema (list of requirements):
[
    {"id": "R-001", "text": "The controller shall provide..."},
    {"id": "R-002", "text": "Data subjects have the right to..."}
]

Or plain text with one requirement per line.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


# Requirement type classification patterns
TYPE_PATTERNS: List[Tuple[str, List[str], str]] = [
    ("disclosure", [
        r"\bprovide\s+(?:information|notice|notification|disclosure)",
        r"\binform\b", r"\bnotif(?:y|ication)\b", r"\btransparenc(?:y|t)\b",
        r"\bprivacy\s+(?:notice|policy)\b", r"\bdisclose\b",
        r"\bmake\s+available\b", r"\bpubli(?:sh|c)\b",
    ], "Information must be provided to someone"),
    ("operational", [
        r"\bimplement\b", r"\bestablish\b", r"\bmaintain\b",
        r"\bprocess(?:es|ing)?\b", r"\bprocedure\b", r"\bpolic(?:y|ies)\b",
        r"\brecord[- ]?keep", r"\blog(?:ging|s)?\b", r"\baudit\b",
        r"\breview\b", r"\bmonitor\b", r"\bensure\b",
    ], "Process or procedure must exist"),
    ("technical", [
        r"\bencrypt(?:ion)?\b", r"\baccess\s+control", r"\bpseudonymis",
        r"\btechnical\s+measure", r"\bsecurit(?:y|ies)\b", r"\bfirewall\b",
        r"\bauthenticat(?:e|ion)\b", r"\bbackup\b", r"\bdata\s+(?:integrity|protection)",
        r"\bcybersecurity\b", r"\bsafeguard\b",
    ], "System capability or safeguard required"),
    ("ui_design", [
        r"\bconsent\s+(?:mechanism|form|button|dialog)", r"\bopt[- ](?:in|out)\b",
        r"\buser\s+interface\b", r"\bcookie\s+(?:banner|notice)\b",
        r"\bpreference\s+(?:center|setting)", r"\btoggle\b",
        r"\bcheckbox\b", r"\bvisual(?:ly)?\s+(?:display|present|prominent)",
    ], "User interface must include specific elements"),
    ("organizational", [
        r"\bappoint\b", r"\bdesignat(?:e|ion)\b", r"\bofficer\b",
        r"\bboard\b", r"\bgovernance\b", r"\bcommittee\b",
        r"\bresponsib(?:le|ility)\b", r"\baccountab(?:le|ility)\b",
        r"\brole\b", r"\btraining\b", r"\bawareness\b",
    ], "Governance structure or role required"),
    ("documentation", [
        r"\bdocument(?:ation|ed)?\b", r"\brecord\b", r"\bimpact\s+assessment\b",
        r"\brisk\s+assessment\b", r"\bdata\s+protection\s+impact",
        r"\bwritten\b", r"\breport\b", r"\bregist(?:er|ration)\b",
    ], "Written records must be maintained"),
    ("reporting", [
        r"\breport\s+to\b", r"\bnotif(?:y|ication)\s+(?:to\s+)?(?:the\s+)?(?:authority|supervisor|regulator)",
        r"\bsubmit\b", r"\bfile\s+(?:with|to)\b", r"\bannual\s+report\b",
        r"\bbreach\s+notification\b", r"\bincident\s+report",
    ], "Information must be submitted to authority"),
]

# Implementation team patterns
TEAM_PATTERNS: List[Tuple[str, List[str]]] = [
    ("legal", [
        r"\blegal\b", r"\bcompliance\b", r"\bcontract", r"\bliabilit",
        r"\bdisclaimer\b", r"\bterms\b", r"\blawful\b", r"\blegal\s+basis",
    ]),
    ("engineering", [
        r"\btechnical\b", r"\bsystem\b", r"\bimplement\b", r"\bencrypt",
        r"\baccess\s+control", r"\bapi\b", r"\bsoftware\b", r"\barchitect",
        r"\binfrastructure\b", r"\bautomated\b",
    ]),
    ("product", [
        r"\buser\s+(?:interface|experience)\b", r"\bdesign\b", r"\bfeature\b",
        r"\bconsent\b", r"\bopt[- ](?:in|out)\b", r"\bpreference\b",
        r"\bdashboard\b", r"\bsetting\b",
    ]),
    ("compliance", [
        r"\baudit\b", r"\bmonitor\b", r"\bassess\b", r"\breview\b",
        r"\bpolic(?:y|ies)\b", r"\bprocedure\b", r"\brecord\b",
        r"\brisk\b", r"\bgovernance\b",
    ]),
    ("security", [
        r"\bsecurit(?:y|ies)\b", r"\bcybersecurity\b", r"\bbreach\b",
        r"\bincident\b", r"\bthreat\b", r"\bvulnerabilit", r"\bpenetration",
    ]),
    ("hr", [
        r"\btraining\b", r"\bawareness\b", r"\bstaff\b", r"\bpersonnel\b",
        r"\bemployee\b", r"\bhir(?:e|ing)\b", r"\brole\b",
    ]),
    ("management", [
        r"\bboard\b", r"\bsenior\s+management\b", r"\bgovernance\b",
        r"\bappoint\b", r"\boversight\b", r"\baccountab",
    ]),
]

# Enforcement mechanism patterns
ENFORCEMENT_PATTERNS: Dict[str, List[str]] = {
    "administrative_fine": [
        r"\bfine\b", r"\bpenalt(?:y|ies)\b", r"\badministrative\s+(?:fine|sanction)",
        r"\bmonetary\b", r"\b(?:EUR|USD|\$|€)\s*\d",
    ],
    "criminal": [
        r"\bcriminal\b", r"\bimprisonment\b", r"\boffence\b", r"\boffense\b",
        r"\bprosecuti", r"\bfelony\b", r"\bmisdemeanor\b",
    ],
    "civil_liability": [
        r"\bliab(?:le|ility)\b", r"\bdamages\b", r"\bcompensati",
        r"\bcivil\b", r"\bclaim\b", r"\bright\s+of\s+action\b",
    ],
    "injunction": [
        r"\binjuncti", r"\bcease\b", r"\bsuspend\b", r"\bprohibit\b",
        r"\brestraining\s+order\b", r"\bban\b",
    ],
    "license_revocation": [
        r"\brevok(?:e|ation)\b", r"\bsuspend\b", r"\bwithdr(?:aw|awal)\b",
        r"\blicen(?:s|c)e\b", r"\bauthori[sz]ation\b",
    ],
    "audit_investigation": [
        r"\baudit\b", r"\binvestigat\b", r"\binspect\b", r"\bexamin",
    ],
}

# Priority keywords
PRIORITY_KEYWORDS: Dict[str, List[str]] = {
    "critical": [r"\bimmediately\b", r"\bwithout delay\b", r"\bprohibit\b", r"\bban\b"],
    "high": [r"\bshall\b", r"\bmust\b", r"\brequired\b", r"\bmandatory\b"],
    "medium": [r"\bshould\b", r"\bexpected\b", r"\brecommend\b"],
    "low": [r"\bmay\b", r"\boptional\b", r"\bconsider\b"],
}


def classify_type(text: str) -> Tuple[str, str, float]:
    """Classify requirement type. Returns (type, description, confidence)."""
    text_lower = text.lower()
    scores: Dict[str, int] = {}
    desc_map: Dict[str, str] = {}
    for type_name, patterns, description in TYPE_PATTERNS:
        score = 0
        for p in patterns:
            if re.search(p, text_lower):
                score += 1
        if score > 0:
            scores[type_name] = score
            desc_map[type_name] = description
    if not scores:
        return "general", "General requirement", 0.3
    best = max(scores, key=scores.get)
    confidence = min(scores[best] / 3.0, 1.0)
    return best, desc_map[best], round(confidence, 2)


def classify_team(text: str) -> List[str]:
    """Identify implementation teams."""
    text_lower = text.lower()
    teams = []
    for team_name, patterns in TEAM_PATTERNS:
        for p in patterns:
            if re.search(p, text_lower):
                teams.append(team_name)
                break
    return teams if teams else ["compliance"]


def classify_enforcement(text: str) -> List[str]:
    """Identify enforcement mechanisms."""
    text_lower = text.lower()
    mechanisms = []
    for mechanism, patterns in ENFORCEMENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                mechanisms.append(mechanism)
                break
    return mechanisms if mechanisms else ["unspecified"]


def classify_priority(text: str) -> str:
    """Determine requirement priority."""
    text_lower = text.lower()
    for priority, patterns in PRIORITY_KEYWORDS.items():
        for p in patterns:
            if re.search(p, text_lower):
                return priority
    return "medium"


def extract_deadline_indicators(text: str) -> Optional[str]:
    """Extract deadline-related language."""
    patterns = [
        r"within\s+\d+\s+(?:days?|months?|years?|hours?)",
        r"no\s+later\s+than\s+[\w\s,]+",
        r"by\s+\d{1,2}\s+\w+\s+\d{4}",
        r"before\s+[\w\s,]+\d{4}",
        r"(?:immediately|without\s+(?:undue\s+)?delay)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group().strip()
    return None


def classify_requirement(req_id: str, text: str) -> Dict[str, Any]:
    """Classify a single requirement."""
    req_type, type_desc, confidence = classify_type(text)
    teams = classify_team(text)
    enforcement = classify_enforcement(text)
    priority = classify_priority(text)
    deadline = extract_deadline_indicators(text)

    return {
        "id": req_id,
        "text": text.strip(),
        "classification": {
            "type": req_type,
            "type_description": type_desc,
            "confidence": confidence,
        },
        "implementation": {
            "teams": teams,
            "primary_team": teams[0] if teams else "compliance",
        },
        "enforcement": {
            "mechanisms": enforcement,
        },
        "priority": priority,
        "deadline_indicator": deadline,
    }


def parse_input(text: str) -> List[Dict[str, str]]:
    """Parse input as JSON list or plain text (one requirement per line)."""
    text = text.strip()
    if text.startswith("["):
        try:
            data = json.loads(text)
            if isinstance(data, list):
                result = []
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        req_id = item.get("id", f"R-{i+1:03d}")
                        req_text = item.get("text", str(item))
                    else:
                        req_id = f"R-{i+1:03d}"
                        req_text = str(item)
                    result.append({"id": req_id, "text": req_text})
                return result
        except json.JSONDecodeError:
            pass
    # Plain text: one requirement per line
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return [{"id": f"R-{i+1:03d}", "text": line} for i, line in enumerate(lines)]


def compute_matrix_summary(classified: List[Dict]) -> Dict[str, Any]:
    """Compute summary statistics for the implementation matrix."""
    type_counts: Dict[str, int] = {}
    team_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    enforcement_counts: Dict[str, int] = {}

    for req in classified:
        t = req["classification"]["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
        for team in req["implementation"]["teams"]:
            team_counts[team] = team_counts.get(team, 0) + 1
        p = req["priority"]
        priority_counts[p] = priority_counts.get(p, 0) + 1
        for e in req["enforcement"]["mechanisms"]:
            enforcement_counts[e] = enforcement_counts.get(e, 0) + 1

    return {
        "total_requirements": len(classified),
        "by_type": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
        "by_team": dict(sorted(team_counts.items(), key=lambda x: -x[1])),
        "by_priority": dict(sorted(priority_counts.items(), key=lambda x: -x[1])),
        "by_enforcement": dict(sorted(enforcement_counts.items(), key=lambda x: -x[1])),
    }


def format_human_report(classified: List[Dict], summary: Dict) -> str:
    """Format results as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("REQUIREMENT CLASSIFICATION MATRIX")
    lines.append("=" * 72)

    lines.append(f"\nTotal requirements: {summary['total_requirements']}")

    lines.append("\n--- BY TYPE ---")
    for t, c in summary["by_type"].items():
        lines.append(f"  {t:20s} {c:4d}")

    lines.append("\n--- BY TEAM ---")
    for t, c in summary["by_team"].items():
        lines.append(f"  {t:20s} {c:4d}")

    lines.append("\n--- BY PRIORITY ---")
    for p, c in summary["by_priority"].items():
        lines.append(f"  {p:20s} {c:4d}")

    lines.append("\n--- REQUIREMENTS ---")
    for req in classified:
        lines.append(f"\n  [{req['id']}] ({req['priority'].upper()})")
        lines.append(f"    Text:         {req['text'][:150]}")
        lines.append(f"    Type:         {req['classification']['type']} ({req['classification']['confidence']:.0%})")
        lines.append(f"    Teams:        {', '.join(req['implementation']['teams'])}")
        lines.append(f"    Enforcement:  {', '.join(req['enforcement']['mechanisms'])}")
        if req["deadline_indicator"]:
            lines.append(f"    Deadline:     {req['deadline_indicator']}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify statutory requirements by type, team, enforcement, and priority."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to requirements file (JSON or text)")
    parser.add_argument("--text", "-t", type=str, help="Inline requirement text")
    parser.add_argument("--output", "-o", type=str, help="Path to save output (JSON)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    if not args.input and not args.text:
        parser.print_help()
        sys.exit(1)

    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = args.text

        if not raw or not raw.strip():
            print("Error: Empty input.", file=sys.stderr)
            sys.exit(1)

        requirements = parse_input(raw)
        classified = [classify_requirement(r["id"], r["text"]) for r in requirements]
        summary = compute_matrix_summary(classified)

        result = {
            "summary": summary,
            "requirements": classified,
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Matrix saved to {args.output}")
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(classified, summary))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
