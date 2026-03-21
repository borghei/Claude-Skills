#!/usr/bin/env python3
"""
Competitor Data Tracker

Track and manage centralized competitor data files with staleness
detection, completeness scoring, and update reminders.

Usage:
    python competitor_data_tracker.py competitor_profiles/
    python competitor_data_tracker.py competitor_profiles/ --json
    python competitor_data_tracker.py competitor_profiles/ --stale-days 60
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta


REQUIRED_FIELDS = [
    "name", "website", "positioning", "pricing", "features",
    "strengths", "weaknesses", "best_for", "not_ideal_for",
]

RECOMMENDED_FIELDS = [
    "common_complaints", "migration_notes", "last_verified",
    "target_audience", "primary_differentiator",
]


def track_profiles(directory: str, stale_days: int) -> dict:
    """Track competitor profile completeness and staleness."""
    if not os.path.isdir(directory):
        return {"error": f"Directory not found: {directory}"}

    profiles = []
    json_files = [f for f in os.listdir(directory) if f.endswith(".json")]

    if not json_files:
        return {"error": f"No JSON files found in {directory}"}

    today = datetime.now()
    stale_threshold = today - timedelta(days=stale_days)

    for filename in sorted(json_files):
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            profiles.append({
                "file": filename,
                "status": "ERROR",
                "error": str(e),
            })
            continue

        name = data.get("name", filename.replace(".json", ""))
        last_verified = data.get("last_verified", "")

        # Staleness check
        is_stale = True
        days_since_update = None
        if last_verified:
            try:
                verified_date = datetime.strptime(last_verified, "%Y-%m-%d")
                days_since_update = (today - verified_date).days
                is_stale = verified_date < stale_threshold
            except ValueError:
                pass

        # Completeness check
        present_required = [f for f in REQUIRED_FIELDS if data.get(f)]
        missing_required = [f for f in REQUIRED_FIELDS if not data.get(f)]
        present_recommended = [f for f in RECOMMENDED_FIELDS if data.get(f)]
        missing_recommended = [f for f in RECOMMENDED_FIELDS if not data.get(f)]

        total_fields = len(REQUIRED_FIELDS) + len(RECOMMENDED_FIELDS)
        filled_fields = len(present_required) + len(present_recommended)
        completeness = round((filled_fields / total_fields) * 100, 1)

        # Status
        if missing_required:
            status = "INCOMPLETE"
        elif is_stale:
            status = "STALE"
        else:
            status = "OK"

        profiles.append({
            "file": filename,
            "competitor": name,
            "status": status,
            "completeness_pct": completeness,
            "last_verified": last_verified or "never",
            "days_since_update": days_since_update,
            "is_stale": is_stale,
            "missing_required": missing_required,
            "missing_recommended": missing_recommended,
        })

    # Summary
    ok_count = sum(1 for p in profiles if p.get("status") == "OK")
    stale_count = sum(1 for p in profiles if p.get("status") == "STALE")
    incomplete_count = sum(1 for p in profiles if p.get("status") == "INCOMPLETE")
    error_count = sum(1 for p in profiles if p.get("status") == "ERROR")

    avg_completeness = (sum(p.get("completeness_pct", 0) for p in profiles if "completeness_pct" in p) /
                        max(1, len([p for p in profiles if "completeness_pct" in p])))

    # Action items
    actions = []
    for p in profiles:
        if p.get("status") == "INCOMPLETE":
            actions.append({
                "priority": "HIGH",
                "competitor": p.get("competitor", p["file"]),
                "action": f"Complete missing required fields: {', '.join(p.get('missing_required', []))}",
            })
        elif p.get("status") == "STALE":
            days = p.get("days_since_update", "unknown")
            actions.append({
                "priority": "MEDIUM",
                "competitor": p.get("competitor", p["file"]),
                "action": f"Data is {days} days old. Verify pricing, features, and positioning.",
            })

    actions.sort(key=lambda x: 0 if x["priority"] == "HIGH" else 1)

    return {
        "directory": directory,
        "stale_threshold_days": stale_days,
        "summary": {
            "total_profiles": len(profiles),
            "ok": ok_count,
            "stale": stale_count,
            "incomplete": incomplete_count,
            "errors": error_count,
            "average_completeness_pct": round(avg_completeness, 1),
        },
        "profiles": profiles,
        "action_items": actions,
    }


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("COMPETITOR DATA TRACKER")
    lines.append("=" * 60)

    s = result["summary"]
    lines.append(f"\nDirectory: {result['directory']}")
    lines.append(f"Stale Threshold: {result['stale_threshold_days']} days")
    lines.append(f"Total Profiles: {s['total_profiles']}")
    lines.append(f"Status: OK={s['ok']}, Stale={s['stale']}, Incomplete={s['incomplete']}, Errors={s['errors']}")
    lines.append(f"Avg Completeness: {s['average_completeness_pct']}%")

    lines.append(f"\n--- Profile Details ---")
    lines.append(f"{'Competitor':<20} {'Status':<12} {'Complete':>9} {'Last Verified':>14} {'Days':>6}")
    for p in result["profiles"]:
        comp = p.get("competitor", p["file"])[:20]
        status = p.get("status", "?")
        complete = f"{p.get('completeness_pct', 0):.0f}%"
        verified = p.get("last_verified", "never")
        days = str(p.get("days_since_update", "-"))
        lines.append(f"{comp:<20} {status:<12} {complete:>9} {verified:>14} {days:>6}")

    if result["action_items"]:
        lines.append(f"\n--- Action Items ---")
        for a in result["action_items"]:
            lines.append(f"[{a['priority']}] {a['competitor']}: {a['action']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track competitor data file completeness and staleness."
    )
    parser.add_argument("directory", help="Directory containing competitor profile JSON files")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--stale-days", type=int, default=90,
                        help="Days before data is considered stale (default: 90)")

    args = parser.parse_args()

    result = track_profiles(args.directory, args.stale_days)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
