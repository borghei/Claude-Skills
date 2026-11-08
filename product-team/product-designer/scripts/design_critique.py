#!/usr/bin/env python3
"""
Design Critique Generator

Evaluates a UI design against Nielsen's 10 usability heuristics and three
accessibility groups, then turns a completed checklist into a critique report
with severity ratings, a compliance score and the issues to fix first.

The checklist wording and severity scale live in references/heuristics.json.
Uses ONLY Python standard library.

Usage:
    python design_critique.py --checklist
    python design_critique.py --checklist --format json > checklist.json
    python design_critique.py --answers answers.json
    python design_critique.py --answers answers.json --format json

Exit codes:
    0  checklist printed, or critique passes the gate (no Critical issue, grade C or better)
    1  critique fails the gate (any Critical issue, or grade D/F)
    2  bad input (missing or unreadable file, invalid JSON, bad severity, nothing answered)
"""

import argparse
import json
import os
import sys
from typing import Dict

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "heuristics.json")


class InputError(Exception):
    """Raised for input the critique cannot score; reported with exit code 2."""


def load_data() -> Dict:
    """Load heuristics, accessibility checks and the severity scale."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["severity_levels"] = {int(k): v for k, v in data["severity_levels"].items()}
    return data


DATA = load_data()
NIELSEN_HEURISTICS = DATA["heuristics"]
A11Y_HEURISTICS = DATA["accessibility"]
SEVERITY_LEVELS = DATA["severity_levels"]


def generate_checklist() -> Dict:
    """Generate empty checklist for evaluation."""
    checklist = {"heuristics": [], "accessibility": []}
    for key, source in (("heuristics", NIELSEN_HEURISTICS), ("accessibility", A11Y_HEURISTICS)):
        for h in source:
            checklist[key].append({
                "id": h["id"],
                "name": h["name"],
                "checkpoints": [
                    {"check": cp, "pass": None, "severity": None, "notes": ""}
                    for cp in h["checkpoints"]
                ],
            })
    return checklist


def _severity(cp: Dict, where: str) -> int:
    """Severity of a failed checkpoint; a blank severity counts as Minor (1)."""
    severity = cp.get("severity")
    if severity is None:
        return 1
    if isinstance(severity, bool) or not isinstance(severity, int) or severity not in SEVERITY_LEVELS:
        raise InputError(f"{where}: severity must be 0-3 or null, got {severity!r}")
    return severity


def analyze_answers(answers: Dict) -> Dict:
    """Analyze completed checklist and generate critique report.

    Checkpoints whose "pass" is still null are left out of the score and
    counted as unanswered, so a partial review is not graded as a failure.
    """
    if not isinstance(answers, dict):
        raise InputError("answers file must be a JSON object with 'heuristics' and/or 'accessibility'")
    issues = []
    passes = []
    total_checks = 0
    passed_checks = 0
    unanswered = 0

    for section_key in ["heuristics", "accessibility"]:
        section = answers.get(section_key, [])
        if not isinstance(section, list):
            raise InputError(f"'{section_key}' must be a list")
        for heuristic in section:
            if not isinstance(heuristic, dict) or "id" not in heuristic or "name" not in heuristic:
                raise InputError(f"every entry in '{section_key}' needs 'id', 'name' and 'checkpoints'")
            for cp in heuristic.get("checkpoints", []):
                if not isinstance(cp, dict) or "check" not in cp:
                    raise InputError(f"{heuristic['id']}: every checkpoint needs a 'check' text")
                if cp.get("pass") is None:
                    unanswered += 1
                    continue
                total_checks += 1
                if cp.get("pass") is True:
                    passed_checks += 1
                    passes.append({
                        "heuristic_id": heuristic["id"],
                        "heuristic_name": heuristic["name"],
                        "checkpoint": cp["check"],
                    })
                elif cp.get("pass") is False:
                    severity = _severity(cp, f"{heuristic['id']} '{cp['check']}'")
                    issues.append({
                        "heuristic_id": heuristic["id"],
                        "heuristic_name": heuristic["name"],
                        "checkpoint": cp["check"],
                        "severity": severity,
                        "severity_label": SEVERITY_LEVELS[severity]["label"],
                        "action": SEVERITY_LEVELS[severity]["action"],
                        "notes": cp.get("notes", ""),
                    })
                else:
                    raise InputError(f"{heuristic['id']} '{cp['check']}': pass must be true, false or null")

    if total_checks == 0:
        raise InputError("no answered checkpoints; set \"pass\" to true or false for each one you reviewed")

    # Sort issues by severity (highest first)
    issues.sort(key=lambda x: -x["severity"])

    compliance_score = round((passed_checks / total_checks) * 100, 1)

    severity_counts = {v["label"]: 0 for v in SEVERITY_LEVELS.values()}
    for issue in issues:
        severity_counts[issue["severity_label"]] = severity_counts.get(issue["severity_label"], 0) + 1

    # Overall grade: a Critical issue caps the grade at C whatever the score
    if compliance_score >= 90 and severity_counts.get("Critical", 0) == 0:
        grade = "A"
    elif compliance_score >= 80 and severity_counts.get("Critical", 0) == 0:
        grade = "B"
    elif compliance_score >= 65:
        grade = "C"
    elif compliance_score >= 50:
        grade = "D"
    else:
        grade = "F"

    summary = {
        "total_checks": total_checks,
        "passed": passed_checks,
        "failed": total_checks - passed_checks,
        "compliance_score": compliance_score,
        "grade": grade,
        "severity_distribution": severity_counts,
    }
    if unanswered:
        summary["unanswered"] = unanswered

    return {
        "summary": summary,
        "issues": issues,
        "strengths": passes[:5],
        "top_priorities": issues[:5],
    }


def gate_failed(report: Dict) -> bool:
    """True when the design should not ship as is: a Critical issue or grade D/F."""
    s = report["summary"]
    return s["severity_distribution"].get("Critical", 0) > 0 or s["grade"] in ("D", "F")


def format_checklist_output(checklist: Dict) -> str:
    """Format checklist as human-readable text for manual evaluation."""
    lines = []
    lines.append("=" * 60)
    lines.append("DESIGN CRITIQUE CHECKLIST")
    lines.append("=" * 60)
    lines.append("\nFill in pass (true/false), severity (0-3), and notes for each checkpoint.")
    lines.append("Save as JSON and run: python design_critique.py --answers answers.json\n")

    for section in ["heuristics", "accessibility"]:
        section_label = "NIELSEN'S 10 HEURISTICS" if section == "heuristics" else "ACCESSIBILITY"
        lines.append(f"\n  {section_label}")
        lines.append("  " + "-" * 50)

        for h in checklist[section]:
            lines.append(f"\n  [{h['id']}] {h['name']}")
            for cp in h["checkpoints"]:
                lines.append(f"    [ ] {cp['check']}")

    lines.append("\n\nSeverity scale: 0=Cosmetic, 1=Minor, 2=Major, 3=Critical")
    return "\n".join(lines)


def format_report_output(report: Dict) -> str:
    """Format critique report as human-readable text."""
    s = report["summary"]
    lines = []
    lines.append("=" * 60)
    lines.append("DESIGN CRITIQUE REPORT")
    lines.append("=" * 60)

    lines.append(f"\n  COMPLIANCE SCORE: {s['compliance_score']}%  (Grade: {s['grade']})")
    lines.append(f"  Checks: {s['passed']} passed / {s['failed']} failed / {s['total_checks']} total")
    if s.get("unanswered"):
        lines.append(f"  Unanswered: {s['unanswered']} (left out of the score)")

    lines.append("\n  SEVERITY DISTRIBUTION")
    for label, count in s["severity_distribution"].items():
        bar = "#" * (count * 3)
        lines.append(f"    {label:<12} {count:>3} {bar}")

    if report["top_priorities"]:
        lines.append("\n  TOP PRIORITIES (fix first)")
        lines.append("  " + "-" * 50)
        for i, issue in enumerate(report["top_priorities"], 1):
            lines.append(f"  {i}. [{issue['severity_label'].upper()}] {issue['checkpoint']}")
            lines.append(f"     Heuristic: {issue['heuristic_id']} - {issue['heuristic_name']}")
            lines.append(f"     Action: {issue['action']}")
            if issue["notes"]:
                lines.append(f"     Notes: {issue['notes']}")

    if report["strengths"]:
        lines.append("\n  STRENGTHS")
        lines.append("  " + "-" * 50)
        for strength in report["strengths"]:
            lines.append(f"    + {strength['checkpoint']}")

    if report["issues"]:
        lines.append(f"\n  ALL ISSUES ({len(report['issues'])} total)")
        lines.append("  " + "-" * 50)
        for issue in report["issues"]:
            lines.append(f"    [{issue['severity_label']:<9}] {issue['checkpoint']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate design critique based on usability heuristics and accessibility standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python design_critique.py --checklist
  python design_critique.py --checklist --format json > checklist.json
  python design_critique.py --answers completed_checklist.json
  python design_critique.py --answers completed_checklist.json --format json

Exit codes: 0 pass or checklist, 1 Critical issue or grade D/F, 2 bad input
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--checklist", action="store_true", help="Generate empty checklist for evaluation")
    group.add_argument("--answers", help="Path to completed checklist JSON file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Same as --format json")

    args = parser.parse_args()
    as_json = args.json or args.format == "json"

    if args.checklist:
        checklist = generate_checklist()
        print(json.dumps(checklist, indent=2) if as_json else format_checklist_output(checklist))
        return 0

    try:
        with open(args.answers, "r", encoding="utf-8") as f:
            answers = json.load(f)
        report = analyze_answers(answers)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2) if as_json else format_report_output(report))
    return 1 if gate_failed(report) else 0


if __name__ == "__main__":
    sys.exit(main())
