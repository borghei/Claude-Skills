#!/usr/bin/env python3
"""
Decision Tracker - Track executive decisions with lifecycle management.

Manages decisions through states (Proposed > Approved > Active > Completed/Superseded/Expired).
Scans for overdue action items, stale decisions, and generates status summaries.

Usage:
    python decision_tracker.py --input decisions.json
    python decision_tracker.py --input decisions.json --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def parse_date(date_str):
    """Parse date string to datetime."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def check_overdue_actions(decision, today):
    """Check for overdue action items in a decision."""
    overdue = []
    for action in decision.get("action_items", []):
        if action.get("completed", False):
            continue
        due_date = parse_date(action.get("due_date"))
        if due_date and due_date < today:
            days_overdue = (today - due_date).days
            overdue.append({
                "action": action.get("description", "Unknown"),
                "owner": action.get("owner", "Unassigned"),
                "due_date": action.get("due_date"),
                "days_overdue": days_overdue,
                "decision_title": decision.get("title", "Unknown"),
                "decision_date": decision.get("date", "Unknown"),
            })
    return overdue


def check_stale_decisions(decision, today, stale_days=90):
    """Check if a decision is stale (no update in stale_days)."""
    status = decision.get("status", "active")
    if status in ("completed", "superseded", "expired"):
        return None

    last_update = parse_date(decision.get("last_updated", decision.get("date")))
    if not last_update:
        return None

    age = (today - last_update).days
    if age > stale_days:
        return {
            "title": decision.get("title", "Unknown"),
            "date": decision.get("date", "Unknown"),
            "days_since_update": age,
            "status": status,
        }
    return None


def check_review_overdue(decision, today):
    """Check if review date has passed."""
    review_date = parse_date(decision.get("review_date"))
    if not review_date:
        return None
    if review_date < today and decision.get("status") not in ("completed", "superseded", "expired"):
        return {
            "title": decision.get("title", "Unknown"),
            "review_date": decision.get("review_date"),
            "days_overdue": (today - review_date).days,
        }
    return None


def detect_conflicts(decisions):
    """Detect potential conflicts between active decisions."""
    conflicts = []
    active = [d for d in decisions if d.get("status") in ("approved", "active")]

    for i, d1 in enumerate(active):
        tags1 = set(d1.get("tags", []))
        for d2 in active[i + 1:]:
            tags2 = set(d2.get("tags", []))
            overlap = tags1 & tags2
            if overlap and len(overlap) >= 2:
                conflicts.append({
                    "decision_1": {"title": d1.get("title"), "date": d1.get("date")},
                    "decision_2": {"title": d2.get("title"), "date": d2.get("date")},
                    "overlapping_tags": list(overlap),
                    "type": "potential_topic_conflict",
                })

    return conflicts


def analyze_decisions(data):
    """Run full decision tracking analysis."""
    decisions = data.get("decisions", [])
    today = datetime.now()
    analysis_date = data.get("analysis_date")
    if analysis_date:
        today = parse_date(analysis_date) or today

    results = {
        "timestamp": datetime.now().isoformat(),
        "analysis_date": today.strftime("%Y-%m-%d"),
        "total_decisions": len(decisions),
        "status_distribution": {},
        "overdue_actions": [],
        "stale_decisions": [],
        "review_overdue": [],
        "conflicts": [],
        "owner_distribution": {},
        "recent_decisions": [],
        "summary": {},
        "recommendations": [],
    }

    # Status distribution
    status_counts = {}
    owner_counts = {}
    total_actions = 0
    completed_actions = 0
    all_overdue = []

    for decision in decisions:
        status = decision.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

        owner = decision.get("owner", "Unassigned")
        owner_counts[owner] = owner_counts.get(owner, 0) + 1

        # Check overdue actions
        overdue = check_overdue_actions(decision, today)
        all_overdue.extend(overdue)

        # Count actions
        for action in decision.get("action_items", []):
            total_actions += 1
            if action.get("completed", False):
                completed_actions += 1

        # Check stale
        stale = check_stale_decisions(decision, today)
        if stale:
            results["stale_decisions"].append(stale)

        # Check review
        review = check_review_overdue(decision, today)
        if review:
            results["review_overdue"].append(review)

    results["status_distribution"] = status_counts
    results["owner_distribution"] = owner_counts
    results["overdue_actions"] = sorted(all_overdue, key=lambda x: x["days_overdue"], reverse=True)

    # Conflicts
    results["conflicts"] = detect_conflicts(decisions)

    # Recent decisions (last 10)
    sorted_decisions = sorted(decisions, key=lambda x: x.get("date", ""), reverse=True)
    results["recent_decisions"] = [
        {
            "title": d.get("title", "Unknown"),
            "date": d.get("date", "Unknown"),
            "status": d.get("status", "unknown"),
            "owner": d.get("owner", "Unassigned"),
            "confidence": d.get("confidence", "unknown"),
        }
        for d in sorted_decisions[:10]
    ]

    # Summary
    action_completion_rate = round((completed_actions / max(total_actions, 1)) * 100, 1)
    active_decisions = status_counts.get("active", 0) + status_counts.get("approved", 0)

    results["summary"] = {
        "active_decisions": active_decisions,
        "completed_decisions": status_counts.get("completed", 0),
        "total_action_items": total_actions,
        "completed_action_items": completed_actions,
        "action_completion_rate": action_completion_rate,
        "overdue_action_count": len(all_overdue),
        "stale_decision_count": len(results["stale_decisions"]),
        "review_overdue_count": len(results["review_overdue"]),
        "conflict_count": len(results["conflicts"]),
    }

    # Recommendations
    recs = results["recommendations"]
    if all_overdue:
        critical_overdue = [a for a in all_overdue if a["days_overdue"] > 14]
        if critical_overdue:
            recs.append(f"CRITICAL: {len(critical_overdue)} action items overdue by 14+ days -- escalate to founder")
        else:
            recs.append(f"{len(all_overdue)} action items overdue -- review in next session")

    if results["stale_decisions"]:
        recs.append(f"{len(results['stale_decisions'])} decisions stale (>90 days without update) -- schedule review")

    if results["review_overdue"]:
        recs.append(f"{len(results['review_overdue'])} decisions past review date -- prompt founder for check-in")

    if results["conflicts"]:
        recs.append(f"{len(results['conflicts'])} potential decision conflicts detected -- resolve before logging new decisions")

    # Owner concentration
    if owner_counts:
        max_owner = max(owner_counts, key=owner_counts.get)
        max_count = owner_counts[max_owner]
        if max_count > len(decisions) * 0.5 and len(decisions) > 5:
            recs.append(f"Owner concentration: {max_owner} owns {max_count}/{len(decisions)} decisions -- consider distributing")

    if action_completion_rate < 60:
        recs.append(f"Action completion rate at {action_completion_rate}% -- accountability or capacity issue")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "DECISION TRACKING REPORT",
        "=" * 60,
        f"Analysis Date: {results['analysis_date']}",
        f"Total Decisions: {results['total_decisions']}",
        "",
        "SUMMARY",
        f"  Active Decisions: {results['summary']['active_decisions']}",
        f"  Completed: {results['summary']['completed_decisions']}",
        f"  Action Items: {results['summary']['completed_action_items']}/{results['summary']['total_action_items']} "
        f"({results['summary']['action_completion_rate']}% complete)",
        f"  Overdue Actions: {results['summary']['overdue_action_count']}",
        f"  Stale Decisions: {results['summary']['stale_decision_count']}",
        f"  Reviews Overdue: {results['summary']['review_overdue_count']}",
        f"  Conflicts: {results['summary']['conflict_count']}",
    ]

    if results["overdue_actions"]:
        lines.append("")
        lines.append("OVERDUE ACTION ITEMS")
        for a in results["overdue_actions"][:10]:
            lines.append(f"  [{a['days_overdue']}d overdue] {a['action']}")
            lines.append(f"    Owner: {a['owner']} | Due: {a['due_date']} | Decision: {a['decision_title']}")

    if results["stale_decisions"]:
        lines.append("")
        lines.append("STALE DECISIONS (>90 days)")
        for s in results["stale_decisions"]:
            lines.append(f"  {s['title']} -- {s['days_since_update']} days since update (status: {s['status']})")

    if results["review_overdue"]:
        lines.append("")
        lines.append("REVIEWS OVERDUE")
        for r in results["review_overdue"]:
            lines.append(f"  {r['title']} -- review was due {r['review_date']} ({r['days_overdue']} days ago)")

    if results["conflicts"]:
        lines.append("")
        lines.append("POTENTIAL CONFLICTS")
        for c in results["conflicts"]:
            lines.append(f"  {c['decision_1']['title']} vs {c['decision_2']['title']}")
            lines.append(f"    Overlapping tags: {', '.join(c['overlapping_tags'])}")

    lines.append("")
    lines.append("RECENT DECISIONS")
    for d in results["recent_decisions"]:
        lines.append(f"  {d['date']}: {d['title']} ({d['status']}) -- Owner: {d['owner']}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track executive decisions with lifecycle management")
    parser.add_argument("--input", required=True, help="Path to JSON decisions file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_decisions(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
