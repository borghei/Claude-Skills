#!/usr/bin/env python3
"""Popup Strategy Auditor - Audit popup configurations for compliance and best practices.

Checks popup inventory for frequency conflicts, targeting gaps, mobile safety,
compliance issues (GDPR, CAN-SPAM), and dark pattern risks.

Usage:
    python popup_strategy_auditor.py popups.json
    python popup_strategy_auditor.py popups.json --format json
"""

import argparse
import json
import sys
from typing import Any


MOBILE_SAFE_FORMATS = ["bottom_bar", "top_bar", "slide_in", "inline_expansion"]
MOBILE_UNSAFE_FORMATS = ["full_screen_overlay"]

VALID_FORMATS = [
    "center_modal", "slide_in", "top_bar", "bottom_bar",
    "full_screen_overlay", "inline_expansion", "exit_intent_modal",
]

VALID_TRIGGERS = [
    "exit_intent", "time_delay", "scroll_depth", "page_count",
    "click_trigger", "inactivity", "entry",
]

COMPLIANCE_REQUIREMENTS = {
    "gdpr": ["consent_checkbox", "privacy_link", "data_purpose"],
    "ccpa": ["do_not_sell_link", "privacy_policy"],
    "can_spam": ["unsubscribe_mechanism", "physical_address"],
}

SHAME_PHRASES = [
    "no, i don't want to",
    "no thanks, i prefer",
    "i don't need",
    "i hate saving",
]


def audit_single_popup(popup: dict, index: int) -> list[dict]:
    """Audit a single popup configuration."""
    issues = []
    popup_id = popup.get("id", f"popup_{index}")

    # Format validation
    fmt = popup.get("format", "")
    if fmt and fmt not in VALID_FORMATS:
        issues.append({
            "popup_id": popup_id,
            "category": "configuration",
            "severity": "warning",
            "issue": f"Unknown format: {fmt}",
            "fix": f"Use one of: {', '.join(VALID_FORMATS)}",
        })

    # Mobile safety
    if fmt in MOBILE_UNSAFE_FORMATS and popup.get("show_on_mobile", True):
        issues.append({
            "popup_id": popup_id,
            "category": "mobile",
            "severity": "error",
            "issue": f"Format '{fmt}' is not mobile-safe and will trigger Google penalty",
            "fix": "Set show_on_mobile to false or switch to a mobile-safe format (slide_in, bottom_bar)",
        })

    # Trigger validation
    trigger = popup.get("trigger", "")
    if trigger == "exit_intent" and popup.get("show_on_mobile", True):
        issues.append({
            "popup_id": popup_id,
            "category": "mobile",
            "severity": "warning",
            "issue": "Exit intent trigger does not work on mobile devices",
            "fix": "Add mobile-specific trigger (scroll_up, inactivity) or disable popup on mobile",
        })

    # Time delay check
    if trigger == "time_delay":
        delay = popup.get("delay_seconds", 0)
        if delay < 10:
            issues.append({
                "popup_id": popup_id,
                "category": "timing",
                "severity": "warning",
                "issue": f"Time delay of {delay}s is too aggressive (< 10s)",
                "fix": "Set delay to 15-30 seconds for optimal balance",
            })

    # Frequency caps
    max_per_session = popup.get("max_per_session")
    if max_per_session is not None and max_per_session > 1:
        issues.append({
            "popup_id": popup_id,
            "category": "frequency",
            "severity": "warning",
            "issue": f"Allows {max_per_session} impressions per session (should be max 1)",
            "fix": "Limit to 1 popup impression per session",
        })

    cooldown = popup.get("cooldown_days", 0)
    if cooldown < 3:
        issues.append({
            "popup_id": popup_id,
            "category": "frequency",
            "severity": "warning",
            "issue": f"Cooldown of {cooldown} days is too short after dismissal",
            "fix": "Set cooldown to minimum 7 days after dismissal",
        })

    # Exclusion rules
    if not popup.get("exclude_converted_users", False):
        issues.append({
            "popup_id": popup_id,
            "category": "targeting",
            "severity": "error",
            "issue": "Not excluding users who already converted",
            "fix": "Always suppress popup for users who have already subscribed/purchased/signed up",
        })

    if not popup.get("exclude_checkout_flow", False):
        issues.append({
            "popup_id": popup_id,
            "category": "targeting",
            "severity": "error",
            "issue": "Popup may appear during checkout flow",
            "fix": "Exclude checkout and payment pages from popup targeting",
        })

    # Decline text dark pattern check
    decline_text = popup.get("decline_text", "").lower()
    for phrase in SHAME_PHRASES:
        if phrase in decline_text:
            issues.append({
                "popup_id": popup_id,
                "category": "dark_pattern",
                "severity": "error",
                "issue": f"Shame language in decline text: '{popup.get('decline_text')}'",
                "fix": "Use neutral text: 'No thanks', 'Maybe later', 'Not now'",
            })
            break

    # Close button
    if popup.get("close_button_visible") is False:
        issues.append({
            "popup_id": popup_id,
            "category": "dark_pattern",
            "severity": "error",
            "issue": "Close button is hidden",
            "fix": "Close button must be clearly visible with minimum 44x44px touch target on mobile",
        })

    # Compliance checks
    if popup.get("captures_email", False):
        compliance_regions = popup.get("target_regions", [])
        for region, requirements in COMPLIANCE_REQUIREMENTS.items():
            if not compliance_regions or region in compliance_regions:
                compliance_features = popup.get("compliance", {})
                for req in requirements:
                    if not compliance_features.get(req, False):
                        issues.append({
                            "popup_id": popup_id,
                            "category": "compliance",
                            "severity": "error",
                            "issue": f"Missing {region.upper()} requirement: {req.replace('_', ' ')}",
                            "fix": f"Add {req.replace('_', ' ')} to comply with {region.upper()} regulations",
                        })

    return issues


def check_conflicts(popups: list[dict]) -> list[dict]:
    """Check for conflicts between multiple popups."""
    issues = []

    # Check for overlapping triggers on same pages
    page_popups: dict[str, list] = {}
    for popup in popups:
        for page in popup.get("target_pages", ["all"]):
            page_popups.setdefault(page, []).append(popup)

    for page, page_popup_list in page_popups.items():
        if len(page_popup_list) > 2:
            popup_ids = [p.get("id", "unknown") for p in page_popup_list]
            issues.append({
                "popup_id": "system",
                "category": "conflict",
                "severity": "warning",
                "issue": f"Page '{page}' has {len(page_popup_list)} popups configured: {', '.join(popup_ids)}",
                "fix": "Implement priority queue -- max 1 marketing popup per session after legal popups",
            })

    # Check for missing cookie consent priority
    has_cookie_consent = any(p.get("type") == "cookie_consent" for p in popups)
    has_marketing = any(p.get("type") != "cookie_consent" for p in popups)
    if has_marketing and not has_cookie_consent:
        issues.append({
            "popup_id": "system",
            "category": "compliance",
            "severity": "warning",
            "issue": "Marketing popups configured but no cookie consent popup found",
            "fix": "Add cookie consent popup with highest priority if targeting EU/UK users",
        })

    return issues


def audit_popups(data: dict) -> dict:
    """Run full popup audit."""
    popups = data.get("popups", [])

    all_issues = []
    for i, popup in enumerate(popups):
        all_issues.extend(audit_single_popup(popup, i))

    all_issues.extend(check_conflicts(popups))

    error_count = sum(1 for i in all_issues if i["severity"] == "error")
    warning_count = sum(1 for i in all_issues if i["severity"] == "warning")

    # Category summary
    categories = {}
    for issue in all_issues:
        cat = issue["category"]
        categories.setdefault(cat, {"errors": 0, "warnings": 0})
        categories[cat]["errors" if issue["severity"] == "error" else "warnings"] += 1

    if error_count == 0 and warning_count <= 2:
        health = "Healthy"
    elif error_count <= 3:
        health = "Needs Attention"
    else:
        health = "Critical"

    return {
        "summary": {
            "total_popups": len(popups),
            "total_issues": len(all_issues),
            "errors": error_count,
            "warnings": warning_count,
            "health_rating": health,
        },
        "category_summary": categories,
        "issues": all_issues,
    }


def format_text(result: dict) -> str:
    """Format audit results as human-readable text."""
    lines = []
    summary = result["summary"]

    lines.append("=" * 60)
    lines.append("POPUP STRATEGY AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Health Rating: {summary['health_rating']}")
    lines.append(f"Total Popups: {summary['total_popups']}")
    lines.append(f"Issues: {summary['total_issues']} ({summary['errors']} errors, {summary['warnings']} warnings)")
    lines.append("")

    if result["category_summary"]:
        lines.append("-" * 40)
        lines.append("ISSUES BY CATEGORY")
        lines.append("-" * 40)
        for cat, counts in sorted(result["category_summary"].items()):
            lines.append(f"  {cat}: {counts['errors']} errors, {counts['warnings']} warnings")
        lines.append("")

    if result["issues"]:
        lines.append("-" * 40)
        lines.append("DETAILED ISSUES")
        lines.append("-" * 40)
        for issue in result["issues"]:
            severity = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
            lines.append(f"\n{severity} [{issue['category']}] {issue['popup_id']}")
            lines.append(f"  Issue: {issue['issue']}")
            lines.append(f"  Fix: {issue['fix']}")
    else:
        lines.append("No issues found.")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit popup configurations for compliance, frequency, and best practices."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with popup inventory",
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

    result = audit_popups(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
