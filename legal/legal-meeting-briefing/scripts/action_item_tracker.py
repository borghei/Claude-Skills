#!/usr/bin/env python3
"""
Legal Meeting Action Item Tracker

Manages action items from legal meetings with CRUD operations,
priority levels, ownership, and status dashboard.

Usage:
    python action_item_tracker.py add --title "Draft NDA" --owner "Jane" --priority high --deadline 2026-04-20
    python action_item_tracker.py list --filter-status open --filter-priority high
    python action_item_tracker.py complete --id 3
    python action_item_tracker.py dashboard --json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


STORAGE_FILE = "action_items.json"
VALID_STATUSES = ["open", "in-progress", "complete"]
VALID_PRIORITIES = ["high", "medium", "low"]


def load_items(filepath: str) -> List[Dict[str, Any]]:
    """Load action items from storage file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_items(items: List[Dict[str, Any]], filepath: str) -> None:
    """Save action items to storage file."""
    with open(filepath, "w") as f:
        json.dump(items, f, indent=2)


def next_id(items: List[Dict[str, Any]]) -> int:
    """Get next available ID."""
    if not items:
        return 1
    return max(item.get("id", 0) for item in items) + 1


def is_overdue(deadline: str) -> bool:
    """Check if a deadline has passed."""
    try:
        dl = datetime.strptime(deadline, "%Y-%m-%d")
        return dl.date() < datetime.now().date()
    except (ValueError, TypeError):
        return False


def get_effective_status(item: Dict[str, Any]) -> str:
    """Get effective status (marks as overdue if deadline passed and not complete)."""
    if item["status"] == "complete":
        return "complete"
    if is_overdue(item.get("deadline", "")):
        return "overdue"
    return item["status"]


def add_item(args: argparse.Namespace, filepath: str) -> Dict[str, Any]:
    """Add a new action item."""
    items = load_items(filepath)
    new_id = next_id(items)

    item: Dict[str, Any] = {
        "id": new_id,
        "title": args.title,
        "owner": args.owner,
        "priority": args.priority,
        "deadline": args.deadline,
        "status": "open",
        "meeting": getattr(args, "meeting", None) or "",
        "notes": getattr(args, "notes", None) or "",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed_date": None,
    }

    items.append(item)
    save_items(items, filepath)

    return {"action": "add", "item": item, "total_items": len(items)}


def list_items(args: argparse.Namespace, filepath: str) -> Dict[str, Any]:
    """List action items with optional filters."""
    items = load_items(filepath)

    filter_status = getattr(args, "filter_status", "all") or "all"
    filter_priority = getattr(args, "filter_priority", "all") or "all"
    filter_owner = getattr(args, "filter_owner", None)

    filtered = []
    for item in items:
        eff_status = get_effective_status(item)

        # Status filter
        if filter_status != "all":
            if filter_status == "overdue":
                if eff_status != "overdue":
                    continue
            elif filter_status == "open":
                if eff_status not in ("open", "overdue"):
                    continue
            elif eff_status != filter_status and item["status"] != filter_status:
                continue

        # Priority filter
        if filter_priority != "all" and item["priority"] != filter_priority:
            continue

        # Owner filter
        if filter_owner and item["owner"].lower() != filter_owner.lower():
            continue

        item_copy = dict(item)
        item_copy["effective_status"] = eff_status
        filtered.append(item_copy)

    return {
        "action": "list",
        "filters": {
            "status": filter_status,
            "priority": filter_priority,
            "owner": filter_owner,
        },
        "count": len(filtered),
        "items": filtered,
    }


def update_item(args: argparse.Namespace, filepath: str) -> Dict[str, Any]:
    """Update an existing action item."""
    items = load_items(filepath)
    item_id = args.id

    for item in items:
        if item["id"] == item_id:
            if hasattr(args, "status") and args.status:
                item["status"] = args.status
            if hasattr(args, "priority") and args.priority:
                item["priority"] = args.priority
            if hasattr(args, "deadline") and args.deadline:
                item["deadline"] = args.deadline
            if hasattr(args, "notes") and args.notes:
                item["notes"] = args.notes
            item["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            save_items(items, filepath)
            return {"action": "update", "item": item}

    return {"action": "update", "error": True, "message": f"Item ID {item_id} not found"}


def complete_item(args: argparse.Namespace, filepath: str) -> Dict[str, Any]:
    """Mark an action item as complete."""
    items = load_items(filepath)
    item_id = args.id

    for item in items:
        if item["id"] == item_id:
            item["status"] = "complete"
            item["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            item["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            save_items(items, filepath)
            return {"action": "complete", "item": item}

    return {"action": "complete", "error": True, "message": f"Item ID {item_id} not found"}


def generate_dashboard(args: argparse.Namespace, filepath: str) -> Dict[str, Any]:
    """Generate action item summary dashboard."""
    items = load_items(filepath)

    total = len(items)
    open_count = 0
    in_progress_count = 0
    complete_count = 0
    overdue_count = 0
    high_open = 0
    medium_open = 0
    low_open = 0

    by_owner: Dict[str, Dict[str, int]] = {}
    by_meeting: Dict[str, int] = {}

    for item in items:
        eff_status = get_effective_status(item)

        if eff_status == "complete":
            complete_count += 1
        elif eff_status == "overdue":
            overdue_count += 1
            open_count += 1
        elif eff_status == "in-progress":
            in_progress_count += 1
        else:
            open_count += 1

        if item["status"] != "complete":
            if item["priority"] == "high":
                high_open += 1
            elif item["priority"] == "medium":
                medium_open += 1
            else:
                low_open += 1

        owner = item.get("owner", "Unassigned")
        if owner not in by_owner:
            by_owner[owner] = {"open": 0, "in_progress": 0, "complete": 0, "overdue": 0}
        if eff_status == "complete":
            by_owner[owner]["complete"] += 1
        elif eff_status == "overdue":
            by_owner[owner]["overdue"] += 1
        elif eff_status == "in-progress":
            by_owner[owner]["in_progress"] += 1
        else:
            by_owner[owner]["open"] += 1

        meeting = item.get("meeting", "No Meeting")
        if meeting:
            by_meeting[meeting] = by_meeting.get(meeting, 0) + 1

    completion_rate = round((complete_count / total) * 100, 1) if total > 0 else 0.0

    # Overdue items detail
    overdue_items = []
    for item in items:
        if get_effective_status(item) == "overdue":
            overdue_items.append({
                "id": item["id"],
                "title": item["title"],
                "owner": item["owner"],
                "deadline": item["deadline"],
                "priority": item["priority"],
            })

    return {
        "action": "dashboard",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "total": total,
            "open": open_count,
            "in_progress": in_progress_count,
            "complete": complete_count,
            "overdue": overdue_count,
            "completion_rate_pct": completion_rate,
        },
        "by_priority": {
            "high_open": high_open,
            "medium_open": medium_open,
            "low_open": low_open,
        },
        "by_owner": by_owner,
        "by_meeting": by_meeting,
        "overdue_items": overdue_items,
    }


def format_text_add(result: Dict[str, Any]) -> str:
    """Format add result."""
    item = result["item"]
    return (f"Action item #{item['id']} added.\n"
            f"  Title:    {item['title']}\n"
            f"  Owner:    {item['owner']}\n"
            f"  Priority: {item['priority']}\n"
            f"  Deadline: {item['deadline']}\n"
            f"  Meeting:  {item['meeting'] or 'N/A'}\n"
            f"Total items: {result['total_items']}")


def format_text_list(result: Dict[str, Any]) -> str:
    """Format list result."""
    lines = [f"Action Items ({result['count']} found)", "=" * 70]
    filters = result["filters"]
    lines.append(f"Filters: status={filters['status']}, priority={filters['priority']}, "
                 f"owner={filters['owner'] or 'all'}")
    lines.append("")

    if not result["items"]:
        lines.append("No items match the specified filters.")
        return "\n".join(lines)

    lines.append(f"{'ID':<5} {'Priority':<10} {'Status':<14} {'Owner':<15} {'Deadline':<12} {'Title'}")
    lines.append("-" * 70)
    for item in result["items"]:
        eff = item.get("effective_status", item["status"])
        status_str = f"{'** ' if eff == 'overdue' else ''}{eff.upper()}"
        lines.append(f"{item['id']:<5} {item['priority']:<10} {status_str:<14} "
                     f"{item['owner']:<15} {item['deadline']:<12} {item['title']}")

    return "\n".join(lines)


def format_text_update(result: Dict[str, Any]) -> str:
    """Format update result."""
    if result.get("error"):
        return f"Error: {result['message']}"
    item = result["item"]
    return f"Action item #{item['id']} updated. Status: {item['status']}, Priority: {item['priority']}"


def format_text_complete(result: Dict[str, Any]) -> str:
    """Format complete result."""
    if result.get("error"):
        return f"Error: {result['message']}"
    item = result["item"]
    return f"Action item #{item['id']} marked complete. ({item['title']})"


def format_text_dashboard(result: Dict[str, Any]) -> str:
    """Format dashboard result."""
    s = result["summary"]
    p = result["by_priority"]
    lines = ["=" * 70, "ACTION ITEM DASHBOARD", "=" * 70]
    lines.append(f"Generated: {result['generated']}")
    lines.append("")
    lines.append(f"Total Items:      {s['total']}")
    lines.append(f"Open:             {s['open']}")
    lines.append(f"In Progress:      {s['in_progress']}")
    lines.append(f"Complete:         {s['complete']}")
    lines.append(f"Overdue:          {s['overdue']}")
    lines.append(f"Completion Rate:  {s['completion_rate_pct']}%")
    lines.append("")
    lines.append("BY PRIORITY (Open):")
    lines.append(f"  High:   {p['high_open']}")
    lines.append(f"  Medium: {p['medium_open']}")
    lines.append(f"  Low:    {p['low_open']}")

    if result.get("by_owner"):
        lines.append("")
        lines.append("BY OWNER:")
        lines.append(f"{'Owner':<20} {'Open':<8} {'In Prog':<8} {'Done':<8} {'Overdue':<8}")
        lines.append("-" * 52)
        for owner, counts in result["by_owner"].items():
            lines.append(f"{owner:<20} {counts['open']:<8} {counts['in_progress']:<8} "
                         f"{counts['complete']:<8} {counts['overdue']:<8}")

    if result.get("overdue_items"):
        lines.append("")
        lines.append("OVERDUE ITEMS (Requires Escalation):")
        for item in result["overdue_items"]:
            lines.append(f"  #{item['id']} [{item['priority'].upper()}] {item['title']} "
                         f"(Owner: {item['owner']}, Due: {item['deadline']})")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


FORMAT_FUNCS = {
    "add": format_text_add,
    "list": format_text_list,
    "update": format_text_update,
    "complete": format_text_complete,
    "dashboard": format_text_dashboard,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage action items from legal meetings."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--storage", default=STORAGE_FILE,
                        help=f"Storage file path (default: {STORAGE_FILE})")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new action item")
    add_parser.add_argument("--title", required=True, help="Action item description")
    add_parser.add_argument("--owner", required=True, help="Responsible person")
    add_parser.add_argument("--priority", required=True, choices=VALID_PRIORITIES)
    add_parser.add_argument("--deadline", required=True, help="Due date YYYY-MM-DD")
    add_parser.add_argument("--meeting", default="", help="Source meeting name")
    add_parser.add_argument("--notes", default="", help="Additional notes")

    # List command
    list_parser = subparsers.add_parser("list", help="List action items")
    list_parser.add_argument("--filter-status",
                             choices=["open", "in-progress", "complete", "overdue", "all"],
                             default="all")
    list_parser.add_argument("--filter-priority",
                             choices=["high", "medium", "low", "all"],
                             default="all")
    list_parser.add_argument("--filter-owner", default=None)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an action item")
    update_parser.add_argument("--id", required=True, type=int)
    update_parser.add_argument("--status", choices=VALID_STATUSES)
    update_parser.add_argument("--priority", choices=VALID_PRIORITIES)
    update_parser.add_argument("--deadline")
    update_parser.add_argument("--notes")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark item complete")
    complete_parser.add_argument("--id", required=True, type=int)

    # Dashboard command
    subparsers.add_parser("dashboard", help="Show summary dashboard")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    filepath = args.storage
    commands = {
        "add": add_item,
        "list": list_items,
        "update": update_item,
        "complete": complete_item,
        "dashboard": generate_dashboard,
    }

    try:
        handler = commands[args.command]
        result = handler(args, filepath)

        if result.get("error"):
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            formatter = FORMAT_FUNCS.get(args.command, lambda r: json.dumps(r, indent=2))
            print(formatter(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
