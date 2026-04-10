#!/usr/bin/env python3
"""
Data Subject Request (DSR) Tracker

Tracks DSR lifecycle across multiple privacy regulations with deadline calculation,
status management, and overdue alerts.

Usage:
    python dsr_tracker.py add --type access --regulation gdpr --subject "Jane Smith" --email "jane@example.com"
    python dsr_tracker.py list
    python dsr_tracker.py list --overdue
    python dsr_tracker.py update --id DSR-0001 --status verified
    python dsr_tracker.py dashboard
    python dsr_tracker.py dashboard --json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DATA_FILE = "dsr_requests.json"

REQUEST_TYPES = [
    "access", "deletion", "correction", "portability",
    "restriction", "objection", "automated_decision", "withdraw_consent",
]

VALID_STATUSES = ["received", "verified", "processing", "completed", "denied", "extended"]

REGULATION_DEADLINES: Dict[str, Dict] = {
    "gdpr": {
        "name": "GDPR",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 60,
        "ack_business_days": None,
        "max_total_days": 90,
    },
    "ccpa": {
        "name": "CCPA/CPRA",
        "initial_days": 45,
        "calendar_type": "calendar",
        "extension_days": 45,
        "ack_business_days": 10,
        "max_total_days": 90,
    },
    "lgpd": {
        "name": "LGPD",
        "initial_days": 15,
        "calendar_type": "calendar",
        "extension_days": 0,
        "ack_business_days": None,
        "max_total_days": 15,
    },
    "popia": {
        "name": "POPIA",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 0,
        "ack_business_days": None,
        "max_total_days": 30,
    },
    "pipeda": {
        "name": "PIPEDA",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 30,
        "ack_business_days": None,
        "max_total_days": 60,
    },
    "pdpa": {
        "name": "PDPA",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 0,
        "ack_business_days": None,
        "max_total_days": 30,
    },
    "privacy_act_au": {
        "name": "Privacy Act (AU)",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 30,
        "ack_business_days": None,
        "max_total_days": 60,
    },
    "pipl": {
        "name": "PIPL",
        "initial_days": 15,
        "calendar_type": "calendar",
        "extension_days": 15,
        "ack_business_days": None,
        "max_total_days": 30,
    },
    "uk_gdpr": {
        "name": "UK GDPR",
        "initial_days": 30,
        "calendar_type": "calendar",
        "extension_days": 60,
        "ack_business_days": None,
        "max_total_days": 90,
    },
}


def load_data(data_file: str) -> Dict:
    """Load DSR data from JSON file."""
    path = Path(data_file)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"requests": [], "next_id": 1}


def save_data(data: Dict, data_file: str) -> None:
    """Save DSR data to JSON file."""
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2, default=str)


def calculate_deadline(received_date: str, regulation: str, is_extended: bool = False) -> Dict:
    """Calculate deadline based on regulation and extension status."""
    reg = REGULATION_DEADLINES.get(regulation)
    if not reg:
        return {"error": f"Unknown regulation: {regulation}"}

    received = datetime.fromisoformat(received_date)
    initial_deadline = received + timedelta(days=reg["initial_days"])

    if is_extended and reg["extension_days"] > 0:
        final_deadline = received + timedelta(days=reg["max_total_days"])
    else:
        final_deadline = initial_deadline

    now = datetime.now()
    remaining = (final_deadline - now).days
    ack_deadline = None
    ack_remaining = None
    if reg["ack_business_days"]:
        # Approximate business days (skip weekends)
        bd = reg["ack_business_days"]
        ack_date = received
        added = 0
        while added < bd:
            ack_date += timedelta(days=1)
            if ack_date.weekday() < 5:
                added += 1
        ack_deadline = ack_date.isoformat()
        ack_remaining = (ack_date - now).days

    return {
        "initial_deadline": initial_deadline.isoformat(),
        "final_deadline": final_deadline.isoformat(),
        "days_remaining": remaining,
        "is_overdue": remaining < 0,
        "ack_deadline": ack_deadline,
        "ack_days_remaining": ack_remaining,
        "extension_available": not is_extended and reg["extension_days"] > 0,
        "extension_days": reg["extension_days"],
    }


def add_request(data: Dict, request_type: str, regulation: str,
                subject: str, email: str) -> Dict:
    """Add a new DSR to the tracker."""
    req_id = f"DSR-{data['next_id']:04d}"
    now = datetime.now().isoformat()

    deadline_info = calculate_deadline(now, regulation)

    request = {
        "id": req_id,
        "type": request_type,
        "regulation": regulation,
        "regulation_name": REGULATION_DEADLINES[regulation]["name"],
        "subject": subject,
        "email": email,
        "status": "received",
        "received_date": now,
        "initial_deadline": deadline_info["initial_deadline"],
        "final_deadline": deadline_info["final_deadline"],
        "ack_deadline": deadline_info.get("ack_deadline"),
        "is_extended": False,
        "status_history": [
            {"status": "received", "date": now, "note": "Request logged"}
        ],
    }

    data["requests"].append(request)
    data["next_id"] += 1
    return request


def update_status(data: Dict, req_id: str, new_status: str, note: str = "") -> Optional[Dict]:
    """Update the status of a DSR."""
    for req in data["requests"]:
        if req["id"] == req_id:
            old_status = req["status"]
            req["status"] = new_status
            now = datetime.now().isoformat()

            if new_status == "extended":
                req["is_extended"] = True
                deadline_info = calculate_deadline(req["received_date"], req["regulation"], True)
                req["final_deadline"] = deadline_info["final_deadline"]

            entry = {"status": new_status, "date": now, "note": note or f"Status changed from {old_status}"}
            req["status_history"].append(entry)
            return req
    return None


def list_requests(data: Dict, overdue_only: bool = False) -> List[Dict]:
    """List requests with current deadline status."""
    results = []
    for req in data["requests"]:
        if req["status"] in ("completed", "denied"):
            if overdue_only:
                continue
            results.append({**req, "days_remaining": None, "is_overdue": False})
            continue

        deadline_info = calculate_deadline(
            req["received_date"], req["regulation"], req.get("is_extended", False)
        )
        enriched = {
            **req,
            "days_remaining": deadline_info["days_remaining"],
            "is_overdue": deadline_info["is_overdue"],
            "ack_days_remaining": deadline_info.get("ack_days_remaining"),
            "extension_available": deadline_info.get("extension_available", False),
        }
        if overdue_only and not deadline_info["is_overdue"]:
            continue
        results.append(enriched)
    return results


def generate_dashboard(data: Dict) -> Dict:
    """Generate dashboard summary with alerts."""
    all_requests = list_requests(data)
    open_requests = [r for r in all_requests if r["status"] not in ("completed", "denied")]
    overdue = [r for r in open_requests if r.get("is_overdue")]
    urgent = [r for r in open_requests if not r.get("is_overdue") and r.get("days_remaining") is not None and r["days_remaining"] <= 7]
    completed = [r for r in all_requests if r["status"] == "completed"]
    denied = [r for r in all_requests if r["status"] == "denied"]

    by_regulation = {}
    for r in open_requests:
        reg = r.get("regulation_name", r.get("regulation", "unknown"))
        by_regulation.setdefault(reg, 0)
        by_regulation[reg] += 1

    by_type = {}
    for r in open_requests:
        by_type.setdefault(r["type"], 0)
        by_type[r["type"]] += 1

    return {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_requests": len(all_requests),
            "open": len(open_requests),
            "overdue": len(overdue),
            "urgent_within_7_days": len(urgent),
            "completed": len(completed),
            "denied": len(denied),
        },
        "by_regulation": by_regulation,
        "by_type": by_type,
        "overdue_requests": [
            {"id": r["id"], "type": r["type"], "regulation": r.get("regulation_name", ""),
             "subject": r["subject"], "days_overdue": abs(r["days_remaining"]),
             "status": r["status"]}
            for r in overdue
        ],
        "urgent_requests": [
            {"id": r["id"], "type": r["type"], "regulation": r.get("regulation_name", ""),
             "subject": r["subject"], "days_remaining": r["days_remaining"],
             "status": r["status"]}
            for r in urgent
        ],
    }


def format_dashboard_text(dashboard: Dict) -> str:
    """Format dashboard as human-readable text."""
    lines = []
    s = dashboard["summary"]
    lines.append("=" * 60)
    lines.append("DSR TRACKER DASHBOARD")
    lines.append(f"Generated: {dashboard['generated'][:16]}")
    lines.append("=" * 60)
    lines.append(f"\n  Total Requests:    {s['total_requests']}")
    lines.append(f"  Open:              {s['open']}")
    lines.append(f"  Overdue:           {s['overdue']}")
    lines.append(f"  Urgent (<=7 days): {s['urgent_within_7_days']}")
    lines.append(f"  Completed:         {s['completed']}")
    lines.append(f"  Denied:            {s['denied']}")

    if dashboard["by_regulation"]:
        lines.append("\n  Open by Regulation:")
        for reg, count in dashboard["by_regulation"].items():
            lines.append(f"    {reg}: {count}")

    if dashboard["overdue_requests"]:
        lines.append(f"\n{'!' * 60}")
        lines.append("  OVERDUE REQUESTS")
        lines.append(f"{'!' * 60}")
        for r in dashboard["overdue_requests"]:
            lines.append(f"  [{r['id']}] {r['type']} ({r['regulation']}) — {r['subject']}")
            lines.append(f"    {r['days_overdue']} days overdue | Status: {r['status']}")

    if dashboard["urgent_requests"]:
        lines.append(f"\n{'-' * 60}")
        lines.append("  URGENT REQUESTS (due within 7 days)")
        lines.append(f"{'-' * 60}")
        for r in dashboard["urgent_requests"]:
            lines.append(f"  [{r['id']}] {r['type']} ({r['regulation']}) — {r['subject']}")
            lines.append(f"    {r['days_remaining']} days remaining | Status: {r['status']}")

    if not dashboard["overdue_requests"] and not dashboard["urgent_requests"]:
        lines.append("\n  No overdue or urgent requests.")

    return "\n".join(lines)


def format_list_text(requests: List[Dict]) -> str:
    """Format request list as human-readable text."""
    if not requests:
        return "No requests found."
    lines = []
    lines.append(f"{'ID':<12} {'Type':<20} {'Regulation':<15} {'Subject':<20} {'Status':<12} {'Days Left':<10}")
    lines.append("-" * 89)
    for r in requests:
        days = r.get("days_remaining")
        days_str = str(days) if days is not None else "—"
        if r.get("is_overdue"):
            days_str = f"OVERDUE ({abs(days)}d)"
        reg_name = r.get("regulation_name", r.get("regulation", ""))
        lines.append(f"{r['id']:<12} {r['type']:<20} {reg_name:<15} {r['subject']:<20} {r['status']:<12} {days_str:<10}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Data Subject Request Lifecycle Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Shared arguments for all subcommands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parent_parser.add_argument("--data-file", default=DEFAULT_DATA_FILE, help="Path to data file")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new DSR", parents=[parent_parser])
    add_parser.add_argument("--type", required=True, choices=REQUEST_TYPES, help="Request type")
    add_parser.add_argument("--regulation", required=True, choices=list(REGULATION_DEADLINES.keys()), help="Applicable regulation")
    add_parser.add_argument("--subject", required=True, help="Data subject name")
    add_parser.add_argument("--email", required=True, help="Data subject email")

    # List command
    list_parser = subparsers.add_parser("list", help="List DSRs", parents=[parent_parser])
    list_parser.add_argument("--overdue", action="store_true", help="Show overdue only")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update DSR status", parents=[parent_parser])
    update_parser.add_argument("--id", required=True, help="Request ID (e.g., DSR-0001)")
    update_parser.add_argument("--status", required=True, choices=VALID_STATUSES, help="New status")
    update_parser.add_argument("--note", default="", help="Optional note")

    # Dashboard command
    subparsers.add_parser("dashboard", help="Show dashboard summary", parents=[parent_parser])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        data = load_data(args.data_file)

        if args.command == "add":
            request = add_request(data, args.type, args.regulation, args.subject, args.email)
            save_data(data, args.data_file)
            if args.json:
                print(json.dumps(request, indent=2, default=str))
            else:
                dl = request["initial_deadline"][:10]
                print(f"Created {request['id']}: {request['type']} ({request['regulation_name']})")
                print(f"  Subject: {request['subject']} <{request['email']}>")
                print(f"  Deadline: {dl}")
                if request.get("ack_deadline"):
                    print(f"  Acknowledgment deadline: {request['ack_deadline'][:10]}")

        elif args.command == "list":
            requests = list_requests(data, overdue_only=args.overdue)
            if args.json:
                print(json.dumps(requests, indent=2, default=str))
            else:
                print(format_list_text(requests))

        elif args.command == "update":
            result = update_status(data, args.id, args.status, args.note)
            if result is None:
                print(f"Error: Request {args.id} not found.", file=sys.stderr)
                sys.exit(1)
            save_data(data, args.data_file)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"Updated {result['id']}: status -> {result['status']}")
                if args.status == "extended":
                    print(f"  Extended deadline: {result['final_deadline'][:10]}")

        elif args.command == "dashboard":
            dashboard = generate_dashboard(data)
            if args.json:
                print(json.dumps(dashboard, indent=2, default=str))
            else:
                print(format_dashboard_text(dashboard))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
