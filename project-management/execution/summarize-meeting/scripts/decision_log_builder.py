#!/usr/bin/env python3
"""Decision Log Builder - Build and query a decision log from meeting data.

Aggregates decisions across meetings and provides search, timeline,
and decision audit capabilities.

Usage:
    python decision_log_builder.py --meetings meetings.json
    python decision_log_builder.py --meetings meetings.json --search "launch"
    python decision_log_builder.py --meetings meetings.json --json
    python decision_log_builder.py --example
"""

import argparse
import json
import re
import sys
from datetime import datetime


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def build_log(data: dict, search: str = None) -> dict:
    meetings = data.get("meetings", [])

    decisions = []
    for meeting in meetings:
        date = meeting.get("date", "Unknown")
        topic = meeting.get("topic", "Unknown")
        participants = meeting.get("participants", [])

        for dec in meeting.get("decisions", []):
            decision = {
                "id": f"DEC-{date.replace('-', '')}-{len(decisions)+1:03d}",
                "date": date,
                "meeting_topic": topic,
                "decision": dec.get("decision", ""),
                "rationale": dec.get("rationale", ""),
                "decided_by": dec.get("decided_by", "Unknown"),
                "participants": participants,
                "category": dec.get("category", "General"),
                "impact": dec.get("impact", "Medium"),
                "reversible": dec.get("reversible", True),
            }
            decisions.append(decision)

    # Sort by date (most recent first)
    decisions.sort(key=lambda x: x["date"], reverse=True)

    # Apply search filter
    if search:
        pattern = re.compile(search, re.IGNORECASE)
        decisions = [d for d in decisions if pattern.search(d["decision"]) or pattern.search(d.get("rationale", ""))]

    # Category distribution
    categories = {}
    for d in decisions:
        cat = d["category"]
        categories[cat] = categories.get(cat, 0) + 1

    # Impact distribution
    impact_counts = {"High": 0, "Medium": 0, "Low": 0}
    for d in decisions:
        impact_counts[d["impact"]] = impact_counts.get(d["impact"], 0) + 1

    # Quality checks
    missing_rationale = [d for d in decisions if not d.get("rationale")]
    high_impact_reversible = [d for d in decisions if d["impact"] == "High" and d.get("reversible", True)]

    recs = []
    if missing_rationale:
        recs.append(f"{len(missing_rationale)} decision(s) without documented rationale. Future teams need to understand 'why'.")
    if high_impact_reversible:
        recs.append(f"{len(high_impact_reversible)} high-impact decision(s) marked as reversible. Verify this is correct and document rollback plans.")

    return {
        "total_decisions": len(decisions),
        "search_query": search,
        "categories": categories,
        "impact_distribution": impact_counts,
        "decisions": decisions,
        "quality": {
            "missing_rationale": len(missing_rationale),
            "decisions_with_rationale_pct": round((len(decisions) - len(missing_rationale)) / len(decisions) * 100, 1) if decisions else 0,
        },
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nDecision Log")
    if result["search_query"]:
        print(f"Search: '{result['search_query']}'")
    print(f"Total Decisions: {result['total_decisions']}")
    print("=" * 65)

    imp = result["impact_distribution"]
    print(f"Impact: High={imp.get('High',0)} | Medium={imp.get('Medium',0)} | Low={imp.get('Low',0)}")
    print(f"Rationale Coverage: {result['quality']['decisions_with_rationale_pct']:.0f}%")

    print(f"\nDecisions:")
    for d in result["decisions"]:
        rev = " [reversible]" if d.get("reversible") else " [irreversible]"
        print(f"\n  {d['id']} ({d['date']})")
        print(f"    Decision: {d['decision']}")
        if d["rationale"]:
            print(f"    Rationale: {d['rationale'][:80]}")
        print(f"    Decided by: {d['decided_by']}  |  Impact: {d['impact']}{rev}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "meetings": [
            {
                "date": "2026-03-14",
                "topic": "Architecture Review",
                "participants": ["Alice", "Bob", "Carol"],
                "decisions": [
                    {"decision": "Use PostgreSQL for analytics service", "rationale": "80% relational queries based on pattern analysis", "decided_by": "Engineering leads", "category": "Technical", "impact": "High", "reversible": False},
                    {"decision": "Adopt trunk-based development", "rationale": "Reduce merge conflicts and improve CI speed", "decided_by": "Alice", "category": "Process", "impact": "Medium", "reversible": True},
                ],
            },
            {
                "date": "2026-03-07",
                "topic": "Sprint Planning",
                "participants": ["Alice", "Dave"],
                "decisions": [
                    {"decision": "Launch date set for April 15", "rationale": "Allows 2 full sprints for QA after feature freeze", "decided_by": "Steering committee", "category": "Schedule", "impact": "High", "reversible": True},
                ],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Build and query a decision log.")
    parser.add_argument("--meetings", type=str, help="Path to meetings JSON file")
    parser.add_argument("--search", type=str, help="Search decisions by keyword")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.meetings:
        parser.error("--meetings is required")

    data = load_data(args.meetings)
    result = build_log(data, args.search)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
