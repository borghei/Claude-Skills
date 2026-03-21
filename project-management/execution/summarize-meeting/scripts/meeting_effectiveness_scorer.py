#!/usr/bin/env python3
"""Meeting Effectiveness Scorer - Score meeting effectiveness from summary data.

Analyzes meeting summaries to score effectiveness based on decisions made,
action items generated, time efficiency, and follow-through.

Usage:
    python meeting_effectiveness_scorer.py --meetings meetings.json
    python meeting_effectiveness_scorer.py --meetings meetings.json --json
    python meeting_effectiveness_scorer.py --example
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def score_meeting(meeting: dict) -> dict:
    topic = meeting.get("topic", "Unknown")
    duration_min = meeting.get("duration_minutes", 60)
    participants = meeting.get("participants", [])
    decisions = meeting.get("decisions", [])
    action_items = meeting.get("action_items", [])
    agenda_items = meeting.get("agenda_items", 0)
    agenda_covered = meeting.get("agenda_items_covered", 0)

    score = 0
    max_score = 100
    checks = {}

    # Decisions made (25 points)
    if decisions:
        decision_score = min(25, len(decisions) * 8)
        checks["decisions"] = {"score": decision_score, "max": 25, "detail": f"{len(decisions)} decision(s) documented"}
    else:
        decision_score = 0
        checks["decisions"] = {"score": 0, "max": 25, "detail": "No decisions documented"}
    score += decision_score

    # Action items with owners and dates (25 points)
    owned_actions = sum(1 for a in action_items if a.get("owner"))
    dated_actions = sum(1 for a in action_items if a.get("due_date"))
    if action_items:
        ownership_pct = owned_actions / len(action_items)
        dated_pct = dated_actions / len(action_items)
        ai_score = int(min(25, len(action_items) * 5 * ((ownership_pct + dated_pct) / 2)))
        checks["action_items"] = {"score": ai_score, "max": 25, "detail": f"{len(action_items)} items ({owned_actions} owned, {dated_actions} dated)"}
    else:
        ai_score = 0
        checks["action_items"] = {"score": 0, "max": 25, "detail": "No action items"}
    score += ai_score

    # Time efficiency (20 points)
    if duration_min <= 30:
        time_score = 20
    elif duration_min <= 60:
        time_score = 15
    elif duration_min <= 90:
        time_score = 10
    else:
        time_score = 5
    # Bonus for output density
    outputs = len(decisions) + len(action_items)
    density = outputs / (duration_min / 30) if duration_min > 0 else 0
    if density >= 3:
        time_score = min(20, time_score + 5)
    checks["time_efficiency"] = {"score": time_score, "max": 20, "detail": f"{duration_min}min, {outputs} outputs, density: {density:.1f}/30min"}
    score += time_score

    # Agenda coverage (15 points)
    if agenda_items > 0:
        coverage = agenda_covered / agenda_items
        agenda_score = int(15 * coverage)
        checks["agenda_coverage"] = {"score": agenda_score, "max": 15, "detail": f"{agenda_covered}/{agenda_items} agenda items covered ({coverage*100:.0f}%)"}
    else:
        agenda_score = 8  # No agenda is a mild negative
        checks["agenda_coverage"] = {"score": agenda_score, "max": 15, "detail": "No agenda defined"}
    score += agenda_score

    # Participant efficiency (15 points)
    if len(participants) <= 5:
        part_score = 15
    elif len(participants) <= 8:
        part_score = 10
    elif len(participants) <= 12:
        part_score = 5
    else:
        part_score = 0
    checks["participants"] = {"score": part_score, "max": 15, "detail": f"{len(participants)} participants"}
    score += part_score

    if score >= 80:
        rating = "Highly Effective"
    elif score >= 60:
        rating = "Effective"
    elif score >= 40:
        rating = "Needs Improvement"
    else:
        rating = "Ineffective"

    return {
        "topic": topic,
        "date": meeting.get("date", "Unknown"),
        "score": score,
        "rating": rating,
        "duration_minutes": duration_min,
        "participant_count": len(participants),
        "decision_count": len(decisions),
        "action_item_count": len(action_items),
        "checks": checks,
    }


def analyze_meetings(data: dict) -> dict:
    meetings = data.get("meetings", [])
    results = [score_meeting(m) for m in meetings]
    scores = [r["score"] for r in results]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    total_time = sum(r["duration_minutes"] for r in results)
    total_decisions = sum(r["decision_count"] for r in results)
    total_actions = sum(r["action_item_count"] for r in results)

    recs = []
    low_scoring = [r for r in results if r["score"] < 50]
    if low_scoring:
        recs.append(f"{len(low_scoring)} meeting(s) scored below 50. Review if these meetings are needed or need restructuring.")
    no_decisions = [r for r in results if r["decision_count"] == 0]
    if no_decisions:
        recs.append(f"{len(no_decisions)} meeting(s) produced no decisions. Consider if the meeting purpose was clear.")
    long_meetings = [r for r in results if r["duration_minutes"] > 60]
    if long_meetings:
        recs.append(f"{len(long_meetings)} meeting(s) exceeded 60 minutes. Review agenda focus and consider splitting.")

    return {
        "total_meetings": len(results),
        "average_score": avg,
        "total_time_minutes": total_time,
        "total_decisions": total_decisions,
        "total_action_items": total_actions,
        "meetings": results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nMeeting Effectiveness Report")
    print(f"Meetings: {result['total_meetings']}  |  Avg Score: {result['average_score']:.0f}/100")
    print("=" * 65)
    print(f"Total Time: {result['total_time_minutes']}min  |  Decisions: {result['total_decisions']}  |  Action Items: {result['total_action_items']}")

    print(f"\nPer-Meeting Scores:")
    print(f"  {'Date':<12} {'Topic':<25} {'Score':>6} {'Rating':<18} {'Dec':>4} {'AI':>4} {'Min':>4}")
    print(f"  {'-'*12} {'-'*25} {'-'*6} {'-'*18} {'-'*4} {'-'*4} {'-'*4}")
    for m in sorted(result["meetings"], key=lambda x: x["score"]):
        topic = m["topic"][:23] + ".." if len(m["topic"]) > 25 else m["topic"]
        print(f"  {m['date']:<12} {topic:<25} {m['score']:>5}% {m['rating']:<18} {m['decision_count']:>4} {m['action_item_count']:>4} {m['duration_minutes']:>4}")

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
                "topic": "Sprint Planning",
                "duration_minutes": 60,
                "participants": ["Alice", "Bob", "Carol", "Dave"],
                "agenda_items": 4,
                "agenda_items_covered": 4,
                "decisions": [
                    {"decision": "Focus on onboarding flow this sprint", "rationale": "Highest impact item"},
                ],
                "action_items": [
                    {"action": "Create Jira tickets for onboarding epics", "owner": "Alice", "due_date": "2026-03-15"},
                    {"action": "Draft design spec", "owner": "Bob", "due_date": "2026-03-17"},
                ],
            },
            {
                "date": "2026-03-12",
                "topic": "Status Sync",
                "duration_minutes": 45,
                "participants": ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Henry"],
                "agenda_items": 0,
                "agenda_items_covered": 0,
                "decisions": [],
                "action_items": [{"action": "Look into the issue", "owner": "", "due_date": ""}],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Score meeting effectiveness.")
    parser.add_argument("--meetings", type=str, help="Path to meetings JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.meetings:
        parser.error("--meetings is required")

    data = load_data(args.meetings)
    result = analyze_meetings(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
