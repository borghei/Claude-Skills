#!/usr/bin/env python3
"""
Risk Categorizer CLI Tool

Categorizes and analyzes pre-mortem risks as Tigers (real risks),
Paper Tigers (unlikely/low-impact), and Elephants (unspoken concerns).
Generates action plans for launch-blocking tigers and flags elephants
that may need investigation.

Usage:
    python3 risk_categorizer.py input.json [--format json|text]
    python3 risk_categorizer.py --demo [--format json|text]

Input JSON format:
    {
        "risks": [
            {
                "description": "Authentication service has had 3 outages in the last month",
                "category": "tiger",
                "evidence": "Incident reports from last 30 days",
                "urgency": "launch_blocking"
            }
        ]
    }

Categories: tiger, paper_tiger, elephant
Urgency (tigers only): launch_blocking, fast_follow, track

Requires: Python 3.7+ (standard library only)
"""

import argparse
import json
import sys
from typing import Any

VALID_CATEGORIES = {"tiger", "paper_tiger", "elephant"}
VALID_URGENCIES = {"launch_blocking", "fast_follow", "track"}

URGENCY_LABELS = {
    "launch_blocking": "Launch-Blocking",
    "fast_follow": "Fast-Follow",
    "track": "Track",
}

URGENCY_ORDER = {
    "launch_blocking": 0,
    "fast_follow": 1,
    "track": 2,
}

# Keywords that suggest an elephant might actually be a tiger
ESCALATION_KEYWORDS = [
    "deadline", "timeline", "budget", "runway", "turnover", "quit",
    "leaving", "burnout", "overwork", "no plan", "unclear", "nobody",
    "no owner", "ignored", "blocked", "security", "compliance", "legal",
    "data loss", "outage", "downtime", "single point of failure",
]


def validate_risk(risk: dict[str, Any], index: int) -> list[str]:
    """Validate a single risk entry. Returns list of error messages."""
    errors = []

    if not risk.get("description"):
        errors.append(f"Risk {index}: missing 'description'")

    category = risk.get("category", "").lower()
    if category not in VALID_CATEGORIES:
        errors.append(
            f"Risk {index}: invalid category '{category}'. "
            f"Valid: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    if not risk.get("evidence"):
        errors.append(f"Risk {index}: missing 'evidence'")

    if category == "tiger":
        urgency = risk.get("urgency", "").lower()
        if urgency not in VALID_URGENCIES:
            errors.append(
                f"Risk {index}: tigers require 'urgency'. "
                f"Valid: {', '.join(sorted(VALID_URGENCIES))}"
            )

    return errors


def check_elephant_escalation(description: str, evidence: str) -> dict[str, Any]:
    """Check if an elephant might actually be a tiger based on keywords."""
    combined = (description + " " + evidence).lower()
    matched = [kw for kw in ESCALATION_KEYWORDS if kw in combined]
    needs_investigation = len(matched) > 0
    return {
        "needs_investigation": needs_investigation,
        "matched_keywords": matched,
        "recommendation": (
            "This elephant contains signals that suggest it may be a real risk (tiger). "
            "Investigate further before dismissing."
            if needs_investigation
            else "No escalation signals detected."
        ),
    }


def process_risks(risks: list[dict[str, Any]]) -> dict[str, Any]:
    """Process all risks and return categorized analysis."""
    tigers = []
    paper_tigers = []
    elephants = []

    for risk in risks:
        category = risk["category"].lower()
        entry = {
            "description": risk["description"],
            "evidence": risk.get("evidence", ""),
            "category": category,
        }

        if category == "tiger":
            urgency = risk.get("urgency", "track").lower()
            entry["urgency"] = urgency
            entry["urgency_label"] = URGENCY_LABELS.get(urgency, urgency)
            tigers.append(entry)
        elif category == "paper_tiger":
            paper_tigers.append(entry)
        elif category == "elephant":
            escalation = check_elephant_escalation(
                risk["description"], risk.get("evidence", "")
            )
            entry["escalation_check"] = escalation
            elephants.append(entry)

    # Sort tigers by urgency
    tigers.sort(key=lambda x: URGENCY_ORDER.get(x.get("urgency", "track"), 99))

    # Build summary
    tiger_by_urgency = {"launch_blocking": 0, "fast_follow": 0, "track": 0}
    for t in tigers:
        urg = t.get("urgency", "track")
        tiger_by_urgency[urg] = tiger_by_urgency.get(urg, 0) + 1

    elephants_needing_investigation = sum(
        1 for e in elephants if e["escalation_check"]["needs_investigation"]
    )

    return {
        "total_risks": len(risks),
        "summary": {
            "tigers": len(tigers),
            "tiger_urgency": {
                "launch_blocking": tiger_by_urgency["launch_blocking"],
                "fast_follow": tiger_by_urgency["fast_follow"],
                "track": tiger_by_urgency["track"],
            },
            "paper_tigers": len(paper_tigers),
            "elephants": len(elephants),
            "elephants_needing_investigation": elephants_needing_investigation,
        },
        "tigers": tigers,
        "paper_tigers": paper_tigers,
        "elephants": elephants,
    }


def format_text(results: dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("PRE-MORTEM RISK ANALYSIS")
    lines.append("=" * 70)

    s = results["summary"]
    lines.append("")
    lines.append(f"Total risks identified: {results['total_risks']}")
    lines.append("")
    lines.append("Distribution:")
    lines.append(f"  Tigers:        {s['tigers']}")
    lines.append(f"    Launch-Blocking: {s['tiger_urgency']['launch_blocking']}")
    lines.append(f"    Fast-Follow:     {s['tiger_urgency']['fast_follow']}")
    lines.append(f"    Track:           {s['tiger_urgency']['track']}")
    lines.append(f"  Paper Tigers:  {s['paper_tigers']}")
    lines.append(f"  Elephants:     {s['elephants']}")
    if s["elephants_needing_investigation"] > 0:
        lines.append(
            f"    ** {s['elephants_needing_investigation']} elephant(s) flagged for investigation **"
        )

    # Launch-Blocking Tigers
    launch_blocking = [t for t in results["tigers"] if t.get("urgency") == "launch_blocking"]
    if launch_blocking:
        lines.append("")
        lines.append("=" * 70)
        lines.append("LAUNCH-BLOCKING TIGERS (must resolve before launch)")
        lines.append("=" * 70)
        for i, t in enumerate(launch_blocking, 1):
            lines.append("")
            lines.append(f"  {i}. {t['description']}")
            lines.append(f"     Evidence:   {t['evidence']}")
            lines.append(f"     Action:     Assign owner, define mitigation, set decision date")

    # Fast-Follow Tigers
    fast_follow = [t for t in results["tigers"] if t.get("urgency") == "fast_follow"]
    if fast_follow:
        lines.append("")
        lines.append("-" * 70)
        lines.append("FAST-FOLLOW TIGERS (address within 2 weeks post-launch)")
        lines.append("-" * 70)
        for i, t in enumerate(fast_follow, 1):
            lines.append("")
            lines.append(f"  {i}. {t['description']}")
            lines.append(f"     Evidence: {t['evidence']}")

    # Track Tigers
    track = [t for t in results["tigers"] if t.get("urgency") == "track"]
    if track:
        lines.append("")
        lines.append("-" * 70)
        lines.append("TRACK TIGERS (monitor, act if escalated)")
        lines.append("-" * 70)
        for i, t in enumerate(track, 1):
            lines.append("")
            lines.append(f"  {i}. {t['description']}")
            lines.append(f"     Evidence: {t['evidence']}")

    # Paper Tigers
    if results["paper_tigers"]:
        lines.append("")
        lines.append("-" * 70)
        lines.append("PAPER TIGERS (unlikely or low impact)")
        lines.append("-" * 70)
        for i, p in enumerate(results["paper_tigers"], 1):
            lines.append("")
            lines.append(f"  {i}. {p['description']}")
            lines.append(f"     Evidence: {p['evidence']}")

    # Elephants
    if results["elephants"]:
        lines.append("")
        lines.append("-" * 70)
        lines.append("ELEPHANTS (unspoken concerns)")
        lines.append("-" * 70)
        for i, e in enumerate(results["elephants"], 1):
            flag = " ** INVESTIGATE **" if e["escalation_check"]["needs_investigation"] else ""
            lines.append("")
            lines.append(f"  {i}. {e['description']}{flag}")
            lines.append(f"     Evidence:  {e['evidence']}")
            if e["escalation_check"]["needs_investigation"]:
                keywords = ", ".join(e["escalation_check"]["matched_keywords"])
                lines.append(f"     Signals:   {keywords}")
                lines.append(f"     Action:    {e['escalation_check']['recommendation']}")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def get_demo_data() -> dict[str, Any]:
    """Return sample input data for demonstration."""
    return {
        "risks": [
            {
                "description": "Authentication service has had 3 outages in the last month; a launch-day outage is plausible",
                "category": "tiger",
                "evidence": "3 incident reports in the last 30 days (P1-level severity)",
                "urgency": "launch_blocking",
            },
            {
                "description": "CSV export does not handle unicode characters correctly",
                "category": "tiger",
                "evidence": "QA found the bug last week; affects ~15% of accounts with non-ASCII data",
                "urgency": "fast_follow",
            },
            {
                "description": "No automated monitoring alerts for the new data pipeline",
                "category": "tiger",
                "evidence": "Pipeline deployed 2 weeks ago; only manual log checks exist currently",
                "urgency": "track",
            },
            {
                "description": "A major competitor might copy our feature within weeks",
                "category": "paper_tiger",
                "evidence": "Competitor's last release was 9 months ago; their team is focused on a different market segment",
            },
            {
                "description": "Users might not discover the new analytics dashboard",
                "category": "paper_tiger",
                "evidence": "Dashboard is the new default landing page; usability test showed 100% discovery rate",
            },
            {
                "description": "The PM who originally championed this feature has left the company; nobody has re-validated requirements with current customers",
                "category": "elephant",
                "evidence": "PM departed 6 weeks ago; no customer interviews since then; team has been building to the original spec",
            },
            {
                "description": "The team is experiencing burnout after 3 consecutive crunch sprints; quality may be declining",
                "category": "elephant",
                "evidence": "Two engineers mentioned burnout in 1-on-1s; PR review thoroughness has visibly dropped",
            },
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Risk Categorizer: classify and analyze pre-mortem risks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 risk_categorizer.py --demo
  python3 risk_categorizer.py --demo --format json
  python3 risk_categorizer.py risks.json
  python3 risk_categorizer.py risks.json --format json

Categories: tiger, paper_tiger, elephant
Urgency (tigers only): launch_blocking, fast_follow, track
        """,
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to JSON file with risks (omit if using --demo)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in sample data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input_file:
        try:
            with open(args.input_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    risks = data.get("risks", [])
    if not risks:
        print("Error: No risks found in input data.", file=sys.stderr)
        sys.exit(1)

    # Validate
    all_errors = []
    for i, risk in enumerate(risks, 1):
        errors = validate_risk(risk, i)
        all_errors.extend(errors)

    if all_errors:
        print("Validation errors:", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    results = process_risks(risks)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
