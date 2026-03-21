#!/usr/bin/env python3
"""Paywall Trigger Auditor - Audit paywall trigger configuration for timing and compliance issues.

Reads a JSON file of trigger rules and user event data, then flags misconfigured
triggers, missing cooldowns, dark-pattern risks, and coverage gaps.

Usage:
    python paywall_trigger_auditor.py triggers.json
    python paywall_trigger_auditor.py triggers.json --format json
"""

import argparse
import json
import sys
from typing import Any


# Best-practice thresholds
BEST_PRACTICES = {
    "max_paywalls_per_session": 1,
    "min_cooldown_days_after_dismiss": 3,
    "max_paywalls_per_month": 3,
    "min_seconds_before_trigger": 5,
    "require_escape_hatch": True,
    "require_value_first": True,
}

DARK_PATTERN_KEYWORDS = [
    "no, i don't want",
    "no thanks, i prefer",
    "i don't need",
    "i hate saving",
    "i'll pay full price",
]

REQUIRED_TRIGGER_FIELDS = ["id", "type", "timing"]
VALID_TRIGGER_TYPES = [
    "feature_gate", "usage_limit", "trial_expiration",
    "time_based", "milestone_based", "team_based",
]


def validate_trigger(trigger: dict, index: int) -> list[dict]:
    """Validate a single trigger rule against best practices."""
    issues = []
    trigger_id = trigger.get("id", f"trigger_{index}")

    # Check required fields
    for field in REQUIRED_TRIGGER_FIELDS:
        if field not in trigger:
            issues.append({
                "trigger_id": trigger_id,
                "severity": "error",
                "issue": f"Missing required field: {field}",
                "recommendation": f"Add '{field}' to trigger configuration",
            })

    # Check trigger type
    trigger_type = trigger.get("type", "")
    if trigger_type and trigger_type not in VALID_TRIGGER_TYPES:
        issues.append({
            "trigger_id": trigger_id,
            "severity": "warning",
            "issue": f"Unknown trigger type: {trigger_type}",
            "recommendation": f"Use one of: {', '.join(VALID_TRIGGER_TYPES)}",
        })

    # Check cooldown
    cooldown_days = trigger.get("cooldown_days", 0)
    if cooldown_days < BEST_PRACTICES["min_cooldown_days_after_dismiss"]:
        issues.append({
            "trigger_id": trigger_id,
            "severity": "warning",
            "issue": f"Cooldown too short: {cooldown_days} days (minimum: {BEST_PRACTICES['min_cooldown_days_after_dismiss']})",
            "recommendation": "Increase cooldown to at least 3 days after dismissal to avoid user annoyance",
        })

    # Check frequency cap
    max_per_month = trigger.get("max_per_month")
    if max_per_month is not None and max_per_month > BEST_PRACTICES["max_paywalls_per_month"]:
        issues.append({
            "trigger_id": trigger_id,
            "severity": "warning",
            "issue": f"Monthly frequency cap too high: {max_per_month} (recommended max: {BEST_PRACTICES['max_paywalls_per_month']})",
            "recommendation": "Cap at 3 paywalls per month to prevent churn from annoyance",
        })

    # Check escape hatch
    if not trigger.get("has_escape_hatch", True):
        issues.append({
            "trigger_id": trigger_id,
            "severity": "error",
            "issue": "No escape hatch (close/dismiss option) configured",
            "recommendation": "Always provide a clear 'Not now' or close button -- hiding it is a dark pattern",
        })

    # Check value-first principle
    if trigger.get("fires_before_activation", False):
        issues.append({
            "trigger_id": trigger_id,
            "severity": "error",
            "issue": "Trigger fires before user activation (aha moment)",
            "recommendation": "Delay trigger until after user has experienced core value -- this is the #1 paywall CRO rule",
        })

    # Check for interruption during tasks
    if trigger.get("fires_during_active_task", False):
        issues.append({
            "trigger_id": trigger_id,
            "severity": "warning",
            "issue": "Trigger fires during active user task",
            "recommendation": "Never interrupt users mid-workflow -- wait for natural pause points",
        })

    # Check dark pattern copy
    decline_text = trigger.get("decline_text", "").lower()
    for pattern in DARK_PATTERN_KEYWORDS:
        if pattern in decline_text:
            issues.append({
                "trigger_id": trigger_id,
                "severity": "error",
                "issue": f"Dark pattern detected in decline text: '{trigger.get('decline_text')}'",
                "recommendation": "Use neutral decline text: 'Maybe later', 'Not now', 'No thanks'",
            })
            break

    # Check sessions per paywall
    max_per_session = trigger.get("max_per_session", 1)
    if max_per_session > BEST_PRACTICES["max_paywalls_per_session"]:
        issues.append({
            "trigger_id": trigger_id,
            "severity": "warning",
            "issue": f"Multiple paywalls per session allowed: {max_per_session}",
            "recommendation": "Limit to 1 paywall per session to maintain trust",
        })

    return issues


def calculate_coverage(triggers: list[dict]) -> dict:
    """Calculate trigger coverage across trigger types."""
    covered_types = set()
    for trigger in triggers:
        t = trigger.get("type", "")
        if t in VALID_TRIGGER_TYPES:
            covered_types.add(t)

    missing_types = set(VALID_TRIGGER_TYPES) - covered_types
    coverage_pct = (len(covered_types) / len(VALID_TRIGGER_TYPES)) * 100 if VALID_TRIGGER_TYPES else 0

    return {
        "covered_types": sorted(covered_types),
        "missing_types": sorted(missing_types),
        "coverage_pct": round(coverage_pct, 1),
        "total_triggers": len(triggers),
    }


def audit_triggers(data: dict) -> dict:
    """Run full audit on trigger configuration."""
    triggers = data.get("triggers", [])

    all_issues = []
    for i, trigger in enumerate(triggers):
        issues = validate_trigger(trigger, i)
        all_issues.extend(issues)

    # Count by severity
    error_count = sum(1 for i in all_issues if i["severity"] == "error")
    warning_count = sum(1 for i in all_issues if i["severity"] == "warning")

    coverage = calculate_coverage(triggers)

    # Overall health rating
    if error_count == 0 and warning_count <= 2:
        health = "Healthy"
    elif error_count <= 2 and warning_count <= 5:
        health = "Needs Attention"
    else:
        health = "Critical"

    return {
        "summary": {
            "total_triggers": len(triggers),
            "total_issues": len(all_issues),
            "errors": error_count,
            "warnings": warning_count,
            "health_rating": health,
        },
        "coverage": coverage,
        "issues": all_issues,
        "best_practices": BEST_PRACTICES,
    }


def format_text(result: dict) -> str:
    """Format audit results as human-readable text."""
    lines = []
    summary = result["summary"]

    lines.append("=" * 60)
    lines.append("PAYWALL TRIGGER AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Health Rating: {summary['health_rating']}")
    lines.append(f"Total Triggers: {summary['total_triggers']}")
    lines.append(f"Total Issues: {summary['total_issues']} ({summary['errors']} errors, {summary['warnings']} warnings)")
    lines.append("")

    # Coverage
    cov = result["coverage"]
    lines.append("-" * 40)
    lines.append("TRIGGER COVERAGE")
    lines.append("-" * 40)
    lines.append(f"Coverage: {cov['coverage_pct']}% of trigger types")
    lines.append(f"Covered: {', '.join(cov['covered_types']) if cov['covered_types'] else 'None'}")
    if cov["missing_types"]:
        lines.append(f"Missing: {', '.join(cov['missing_types'])}")
    lines.append("")

    # Issues
    if result["issues"]:
        lines.append("-" * 40)
        lines.append("ISSUES FOUND")
        lines.append("-" * 40)
        for issue in result["issues"]:
            severity_marker = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
            lines.append(f"\n{severity_marker} {issue['trigger_id']}")
            lines.append(f"  Issue: {issue['issue']}")
            lines.append(f"  Fix: {issue['recommendation']}")
    else:
        lines.append("No issues found. Trigger configuration follows best practices.")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit paywall trigger configuration for timing, frequency, and compliance issues."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with trigger rules",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = audit_triggers(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
