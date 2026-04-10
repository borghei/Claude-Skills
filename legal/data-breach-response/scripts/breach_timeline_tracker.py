#!/usr/bin/env python3
"""
Breach Timeline Tracker

Tracks data breach response timeline from T0 (moment of awareness).
Records events, calculates time remaining for regulatory deadlines,
and generates status dashboards.

Usage:
    python breach_timeline_tracker.py init --breach-id "BR-2026-001" --t0 "2026-04-10T08:00:00" --description "Unauthorized access"
    python breach_timeline_tracker.py event --timeline breach.json --action "Containment team activated" --category containment
    python breach_timeline_tracker.py status --timeline breach.json
    python breach_timeline_tracker.py deadlines --timeline breach.json --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


DEADLINE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "gdpr_72h_sa": {"label": "GDPR Art. 33 — SA Notification", "hours": 72, "description": "Notify SA of personal data breach"},
    "nis2_24h_ew": {"label": "NIS2 Art. 23 — Early Warning", "hours": 24, "description": "Submit early warning to CSIRT"},
    "nis2_72h": {"label": "NIS2 Art. 23 — Full Notification", "hours": 72, "description": "Full incident notification to CSIRT"},
    "pci_24h": {"label": "PCI DSS — Card Brand Notification", "hours": 24, "description": "Notify card brands"},
    "dpa_24h": {"label": "DPA Contractual — 24h Processor", "hours": 24, "description": "Processor notifies controller (24h)"},
    "dpa_48h": {"label": "DPA Contractual — 48h Processor", "hours": 48, "description": "Processor notifies controller (48h)"},
}
VALID_CATEGORIES: List[str] = ["detection", "containment", "assessment", "notification", "remediation", "communication", "documentation", "other"]
RESPONSE_CHECKLIST: List[Dict[str, str]] = [
    {"id": "C1", "action": "Breach detected and confirmed", "cat": "detection"},
    {"id": "C2", "action": "Incident response team activated", "cat": "containment"},
    {"id": "C3", "action": "Containment measures applied", "cat": "containment"},
    {"id": "C4", "action": "Scope and impact assessed", "cat": "assessment"},
    {"id": "C5", "action": "Severity score calculated", "cat": "assessment"},
    {"id": "C6", "action": "Notification obligations determined", "cat": "assessment"},
    {"id": "C7", "action": "Legal counsel engaged", "cat": "assessment"},
    {"id": "C8", "action": "SA notified (if required)", "cat": "notification"},
    {"id": "C9", "action": "Data subjects notified (if required)", "cat": "notification"},
    {"id": "C10", "action": "Root cause analysis completed", "cat": "remediation"},
    {"id": "C11", "action": "Remediation implemented", "cat": "remediation"},
    {"id": "C12", "action": "Breach register updated", "cat": "documentation"},
    {"id": "C13", "action": "Post-incident review conducted", "cat": "documentation"},
    {"id": "C14", "action": "Lessons learned documented", "cat": "documentation"},
]


def load_timeline(filepath: str) -> Dict[str, Any]:
    """Load timeline from file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: Timeline file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def save_timeline(filepath: str, timeline: Dict[str, Any]) -> None:
    """Save timeline to file."""
    timeline["last_updated"] = datetime.now().isoformat()
    with open(filepath, "w") as f:
        json.dump(timeline, f, indent=2)


def calculate_deadlines(t0_str: str) -> Dict[str, Dict[str, Any]]:
    """Calculate all deadline statuses from T0."""
    try:
        t0 = datetime.fromisoformat(t0_str)
    except ValueError:
        return {}

    now = datetime.now()
    result: Dict[str, Dict[str, Any]] = {}

    for dl_id, dl_def in DEADLINE_DEFINITIONS.items():
        deadline_time = t0 + timedelta(hours=dl_def["hours"])
        remaining = deadline_time - now
        remaining_hours = remaining.total_seconds() / 3600

        if remaining_hours <= 0:
            status = "EXPIRED"
        elif remaining_hours <= 6:
            status = "CRITICAL"
        elif remaining_hours <= 12:
            status = "URGENT"
        elif remaining_hours <= 24:
            status = "WARNING"
        else:
            status = "OK"

        result[dl_id] = {
            "label": dl_def["label"],
            "description": dl_def["description"],
            "deadline": deadline_time.isoformat(),
            "remaining_hours": round(remaining_hours, 1),
            "status": status,
            "expired": remaining_hours <= 0,
        }

    return result


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new breach timeline."""
    try:
        t0 = datetime.fromisoformat(args.t0)
    except ValueError:
        print(f"Error: Invalid T0 format '{args.t0}'. Use ISO: YYYY-MM-DDTHH:MM:SS", file=sys.stderr)
        sys.exit(1)

    timeline: Dict[str, Any] = {
        "breach_id": args.breach_id,
        "description": args.description,
        "t0": args.t0,
        "status": "active",
        "severity_score": None,
        "severity_verdict": None,
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "events": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "Breach timeline initialized",
                "category": "detection",
                "hours_from_t0": round((datetime.now() - t0).total_seconds() / 3600, 1),
            }
        ],
        "completed_actions": [],
        "notifications_sent": [],
    }

    output = args.output or f"breach_{args.breach_id.lower().replace('-', '_')}.json"
    save_timeline(output, timeline)
    print(f"Breach timeline initialized: {output}")
    print(f"  Breach ID: {args.breach_id}")
    print(f"  T0: {args.t0}")
    print(f"  Description: {args.description}")

    # Show immediate deadlines
    deadlines = calculate_deadlines(args.t0)
    urgent = [dl for dl in deadlines.values() if dl["status"] in ("CRITICAL", "URGENT", "EXPIRED")]
    if urgent:
        print("\n  URGENT DEADLINES:")
        for dl in urgent:
            print(f"    [{dl['status']}] {dl['label']}: {dl['remaining_hours']}h remaining")


def cmd_event(args: argparse.Namespace) -> None:
    """Record an event in the timeline."""
    if args.category not in VALID_CATEGORIES:
        print(f"Error: Invalid category '{args.category}'", file=sys.stderr)
        print(f"Valid: {', '.join(VALID_CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    timeline = load_timeline(args.timeline)

    try:
        t0 = datetime.fromisoformat(timeline["t0"])
    except (ValueError, KeyError):
        t0 = datetime.now()

    now = datetime.now()
    hours_from_t0 = round((now - t0).total_seconds() / 3600, 1)

    event: Dict[str, Any] = {
        "timestamp": now.isoformat(),
        "action": args.action,
        "category": args.category,
        "hours_from_t0": hours_from_t0,
    }

    timeline["events"].append(event)

    # Auto-complete matching checklist items
    for item in RESPONSE_CHECKLIST:
        if item["cat"] == args.category and item["id"] not in timeline.get("completed_actions", []):
            action_lower = args.action.lower()
            item_lower = item["action"].lower()
            # Simple keyword match
            keywords = item_lower.split()
            matches = sum(1 for kw in keywords if kw in action_lower)
            if matches >= len(keywords) * 0.4:
                timeline.setdefault("completed_actions", []).append(item["id"])

    save_timeline(args.timeline, timeline)

    if args.json:
        print(json.dumps(event, indent=2))
    else:
        print(f"Event recorded at T0+{hours_from_t0}h: {args.action}")


def cmd_status(args: argparse.Namespace) -> None:
    """Display status dashboard."""
    timeline = load_timeline(args.timeline)
    events = timeline.get("events", [])
    t0_str = timeline.get("t0", "")

    try:
        t0 = datetime.fromisoformat(t0_str)
        elapsed_hours = round((datetime.now() - t0).total_seconds() / 3600, 1)
    except ValueError:
        elapsed_hours = 0

    deadlines = calculate_deadlines(t0_str)
    completed = set(timeline.get("completed_actions", []))

    if args.json:
        result = {
            "breach_id": timeline.get("breach_id", "Unknown"),
            "status": timeline.get("status", "active"),
            "t0": t0_str,
            "elapsed_hours": elapsed_hours,
            "severity_score": timeline.get("severity_score"),
            "severity_verdict": timeline.get("severity_verdict"),
            "events_count": len(events),
            "completed_actions": list(completed),
            "pending_actions": [c["id"] for c in RESPONSE_CHECKLIST if c["id"] not in completed],
            "deadlines": deadlines,
        }
        print(json.dumps(result, indent=2))
        return

    lines: List[str] = ["=" * 60, "BREACH RESPONSE STATUS DASHBOARD", "=" * 60, ""]
    lines.append(f"  Breach: {timeline.get('breach_id', 'Unknown')} | Status: {timeline.get('status', 'active').upper()} | Elapsed: {elapsed_hours}h")
    lines.append(f"  T0: {t0_str} | Severity: {timeline.get('severity_verdict', 'N/A')}\n")
    lines.append("DEADLINES:")
    for dl in deadlines.values():
        icon = {"EXPIRED": "!!!", "CRITICAL": "!!!", "URGENT": ">>>", "WARNING": " > "}.get(dl["status"], "   ")
        lines.append(f"  {icon} {dl['label']}: {dl['remaining_hours']}h [{dl['status']}]")
    lines.append("\nCHECKLIST:")
    for item in RESPONSE_CHECKLIST:
        done = "[X]" if item["id"] in completed else "[ ]"
        lines.append(f"  {done} {item['id']}: {item['action']}")
    lines.append(f"  Progress: {len(completed)}/{len(RESPONSE_CHECKLIST)}\n")
    lines.append("RECENT EVENTS:")
    for evt in list(reversed(events))[:10]:
        lines.append(f"  T0+{evt.get('hours_from_t0', 0)}h [{evt.get('category', 'other')}] {evt.get('action', '')}")
    lines.append("=" * 60)
    print("\n".join(lines))


def cmd_deadlines(args: argparse.Namespace) -> None:
    """Check and display deadline status."""
    timeline = load_timeline(args.timeline)
    t0_str = timeline.get("t0", "")
    deadlines = calculate_deadlines(t0_str)

    if args.json:
        print(json.dumps({
            "breach_id": timeline.get("breach_id", "Unknown"),
            "t0": t0_str,
            "deadlines": deadlines,
        }, indent=2))
        return

    print(f"Breach: {timeline.get('breach_id', 'Unknown')}")
    print(f"T0: {t0_str}")
    print()

    for dl in sorted(deadlines.values(), key=lambda x: x["remaining_hours"]):
        icon = "!!!" if dl["expired"] else ">>>" if dl["status"] in ("CRITICAL", "URGENT") else "   "
        print(f"  {icon} {dl['label']}: {dl['remaining_hours']}h [{dl['status']}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Breach Timeline Tracker")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("init")
    p.add_argument("--breach-id", required=True); p.add_argument("--t0", required=True)
    p.add_argument("--description", required=True); p.add_argument("--output", type=str)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("event")
    p.add_argument("--timeline", required=True); p.add_argument("--action", required=True)
    p.add_argument("--category", required=True); p.add_argument("--json", action="store_true")
    for name in ["status", "deadlines"]:
        p = sub.add_parser(name)
        p.add_argument("--timeline", required=True); p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.command:
        parser.print_help(); sys.exit(1)
    cmds = {"init": cmd_init, "event": cmd_event, "status": cmd_status, "deadlines": cmd_deadlines}
    try:
        cmds[args.command](args)
    except KeyError:
        parser.print_help(); sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
