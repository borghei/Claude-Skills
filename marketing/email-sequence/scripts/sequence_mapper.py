#!/usr/bin/env python3
"""
Email Sequence Mapper

Generates a visual sequence map with timing, branching logic,
and exit conditions from a sequence definition file.

Usage:
    python sequence_mapper.py sequence_def.json
    python sequence_mapper.py sequence_def.json --json
    python sequence_mapper.py --sample

Input JSON format:
{
    "name": "SaaS Welcome Onboarding",
    "trigger": "New signup",
    "goal": "Activate user",
    "emails": [
        {"position": 1, "day": 0, "subject": "Welcome", "purpose": "Set expectations"},
        {"position": 2, "day": 1, "subject": "Core feature", "purpose": "Drive activation"}
    ],
    "branches": [
        {"after_email": 2, "condition": "activated core feature", "action": "skip to email 4"}
    ],
    "exit_conditions": ["Converts to paid", "Unsubscribes"]
}
"""

import argparse
import json
import sys
from pathlib import Path

TIMING_BENCHMARKS = {
    "welcome": {"ideal_gap": [0, 1, 3, 5, 7, 10, 13], "max_days": 14},
    "nurture": {"ideal_gap": [0, 3, 7, 14, 21, 28], "max_days": 30},
    "trial_expiration": {"ideal_gap": [7, 3, 1, 0, -3], "max_days": 10},
    "re_engagement": {"ideal_gap": [0, 3, 7, 14], "max_days": 14},
}

SAMPLE = {
    "name": "SaaS Welcome Onboarding",
    "type": "welcome",
    "trigger": "New user signup",
    "goal": "Activate core feature within 14 days",
    "emails": [
        {"position": 1, "day": 0, "subject": "Welcome to [Product] -- start here", "purpose": "Set expectations, one CTA to activate"},
        {"position": 2, "day": 1, "subject": "The one feature that changes everything", "purpose": "Drive to core value action"},
        {"position": 3, "day": 3, "subject": "How [Company] got [Result] in [Timeframe]", "purpose": "Social proof, case study"},
        {"position": 4, "day": 5, "subject": "Quick question", "purpose": "Check engagement, offer help"},
        {"position": 5, "day": 7, "subject": "3 things you might have missed", "purpose": "Feature discovery"},
        {"position": 6, "day": 10, "subject": "Your trial is halfway done", "purpose": "Progress report, urgency"},
        {"position": 7, "day": 13, "subject": "Last day of your trial", "purpose": "Convert or lose access"},
    ],
    "branches": [
        {"after_email": 2, "condition": "User completed core action", "action": "Skip email 3, go to email 4"},
        {"after_email": 4, "condition": "No login for 5+ days", "action": "Switch to re-engagement variant"},
        {"after_email": 6, "condition": "Visited pricing page", "action": "Send pricing-focused email 7 variant"},
    ],
    "exit_conditions": ["Converts to paid", "Unsubscribes", "Requests removal"],
}


def analyze_sequence(data: dict) -> dict:
    emails = data.get("emails", [])
    branches = data.get("branches", [])
    exits = data.get("exit_conditions", [])
    seq_type = data.get("type", "welcome")

    result = {
        "name": data.get("name", "Unnamed"),
        "type": seq_type,
        "trigger": data.get("trigger", "Unknown"),
        "goal": data.get("goal", "Unknown"),
        "email_count": len(emails),
        "total_days": max((e.get("day", 0) for e in emails), default=0),
        "timing_analysis": [],
        "flow_map": [],
        "branch_count": len(branches),
        "exit_conditions": exits,
        "warnings": [],
        "suggestions": [],
    }

    # Timing analysis
    benchmark = TIMING_BENCHMARKS.get(seq_type, TIMING_BENCHMARKS["welcome"])
    days = [e.get("day", 0) for e in emails]
    gaps = [days[i+1] - days[i] for i in range(len(days)-1)]

    for i, email in enumerate(emails):
        entry = {
            "position": email.get("position", i+1),
            "day": email.get("day", 0),
            "subject": email.get("subject", ""),
            "purpose": email.get("purpose", ""),
        }
        if i < len(gaps):
            entry["gap_to_next"] = gaps[i]
        result["timing_analysis"].append(entry)

    # Flow map (ASCII visualization)
    for i, email in enumerate(emails):
        node = f"[Email {email.get('position', i+1)}] Day {email.get('day', 0)}: {email.get('subject', '')[:40]}"
        result["flow_map"].append(node)

        # Add branches after this email
        for branch in branches:
            if branch.get("after_email") == email.get("position", i+1):
                result["flow_map"].append(f"  IF {branch['condition']} -> {branch['action']}")

    # Warnings
    if len(emails) > 7:
        result["warnings"].append(f"Sequence has {len(emails)} emails. Consider trimming to 5-7 to reduce fatigue.")
    if len(emails) < 3:
        result["warnings"].append(f"Sequence has only {len(emails)} emails. Most conversions happen in follow-ups.")

    if any(g == 0 for g in gaps):
        result["warnings"].append("Some emails are sent on the same day. Ensure they have different triggers.")

    if any(g > 10 for g in gaps):
        result["warnings"].append("Long gaps (>10 days) between emails risk losing momentum.")

    if not branches:
        result["suggestions"].append("Add branching logic for different user behaviors (active vs. inactive).")

    if not exits:
        result["suggestions"].append("Define exit conditions (conversion, unsubscribe, sequence completion).")

    if len(exits) < 2:
        result["suggestions"].append("Add more exit conditions to prevent over-emailing converted users.")

    # Suppression check
    result["suggestions"].append("Set suppression rules to prevent overlap with other active sequences.")

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 65, "  EMAIL SEQUENCE MAPPER", "=" * 65]
    lines.append(f"\n  Name: {result['name']}")
    lines.append(f"  Type: {result['type']} | Emails: {result['email_count']} | Duration: {result['total_days']} days")
    lines.append(f"  Trigger: {result['trigger']}")
    lines.append(f"  Goal: {result['goal']}")

    lines.append(f"\n  Sequence Flow:")
    for node in result["flow_map"]:
        if node.startswith("  IF"):
            lines.append(f"    {node}")
        else:
            lines.append(f"    {node}")

    lines.append(f"\n  Timing:")
    for t in result["timing_analysis"]:
        gap = f" (+{t['gap_to_next']}d)" if "gap_to_next" in t else " (final)"
        lines.append(f"    Email {t['position']}: Day {t['day']}{gap} - {t['purpose']}")

    if result["exit_conditions"]:
        lines.append(f"\n  Exit Conditions:")
        for e in result["exit_conditions"]:
            lines.append(f"    - {e}")

    if result["warnings"]:
        lines.append(f"\n  Warnings:")
        for w in result["warnings"]:
            lines.append(f"    ! {w}")

    if result["suggestions"]:
        lines.append(f"\n  Suggestions:")
        for s in result["suggestions"]:
            lines.append(f"    > {s}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Map and analyze email sequences.")
    parser.add_argument("file", nargs="?", help="Sequence definition JSON file")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--sample", action="store_true", help="Run with sample data")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE
    elif args.file:
        try:
            data = json.loads(Path(args.file).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_sequence(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
