#!/usr/bin/env python3
"""
Meeting Pulse Designer - Design and validate company meeting rhythms.

Generates meeting cadence recommendations, validates meeting load,
identifies redundancies, and produces L10 agenda templates.
"""

import argparse
import json
import sys
from datetime import datetime


RECOMMENDED_PULSE = {
    "daily_standup": {"frequency": "Daily", "duration_min": 15, "who": "Each team", "purpose": "Blockers only", "required": True},
    "l10_leadership": {"frequency": "Weekly", "duration_min": 90, "who": "Leadership team", "purpose": "Scorecard + IDS", "required": True},
    "department_review": {"frequency": "Monthly", "duration_min": 60, "who": "Dept + leadership", "purpose": "Deep dive", "required": True},
    "quarterly_planning": {"frequency": "Quarterly", "duration_min": 480, "who": "Leadership", "purpose": "Set rocks, review strategy", "required": True},
    "annual_planning": {"frequency": "Annual", "duration_min": 960, "who": "Leadership", "purpose": "1-year + 3-year vision", "required": True},
    "all_hands": {"frequency": "Monthly", "duration_min": 60, "who": "All employees", "purpose": "Company update + Q&A", "required": False},
    "one_on_ones": {"frequency": "Weekly", "duration_min": 30, "who": "Manager + report", "purpose": "Coaching + blockers", "required": True},
}

L10_AGENDA = [
    {"segment": "Good news", "duration_min": 5, "activity": "Personal + business wins"},
    {"segment": "Scorecard review", "duration_min": 5, "activity": "Flag red items only"},
    {"segment": "Rock review", "duration_min": 5, "activity": "On/off track for each rock"},
    {"segment": "Customer/employee headlines", "duration_min": 5, "activity": "Notable events"},
    {"segment": "Issues list (IDS)", "duration_min": 60, "activity": "Identify, Discuss, Solve"},
    {"segment": "To-dos review", "duration_min": 5, "activity": "Last week done or not?"},
    {"segment": "Conclude", "duration_min": 5, "activity": "Rate 1-10, improve next time"},
]


def design_pulse(data: dict) -> dict:
    """Design and validate meeting pulse."""
    current_meetings = data.get("current_meetings", [])
    team_size = data.get("team_size", 20)
    leadership_count = data.get("leadership_team_size", 6)

    results = {
        "timestamp": datetime.now().isoformat(),
        "team_size": team_size,
        "recommended_pulse": [],
        "current_analysis": [],
        "l10_agenda": L10_AGENDA,
        "meeting_load": {},
        "redundancies": [],
        "gaps": [],
        "recommendations": [],
    }

    # Recommended pulse
    for meeting_id, config in RECOMMENDED_PULSE.items():
        results["recommended_pulse"].append({
            "meeting": meeting_id.replace("_", " ").title(),
            "frequency": config["frequency"],
            "duration": f"{config['duration_min']} min",
            "who": config["who"],
            "purpose": config["purpose"],
            "required": config["required"],
        })

    # Analyze current meetings
    total_weekly_hours = 0
    meeting_purposes = set()

    for meeting in current_meetings:
        name = meeting.get("name", "")
        freq = meeting.get("frequency", "weekly")
        duration = meeting.get("duration_min", 60)
        attendees = meeting.get("attendees", 0)
        purpose = meeting.get("purpose", "")
        has_agenda = meeting.get("has_agenda", False)
        produces_decisions = meeting.get("produces_decisions", False)

        # Weekly equivalent hours
        freq_multiplier = {"daily": 5, "weekly": 1, "biweekly": 0.5, "monthly": 0.25, "quarterly": 0.02}
        weekly_hours = (duration / 60) * freq_multiplier.get(freq, 1) * attendees

        meeting_purposes.add(purpose.lower())

        analysis = {
            "name": name,
            "frequency": freq,
            "duration_min": duration,
            "attendees": attendees,
            "weekly_person_hours": round(weekly_hours, 1),
            "has_agenda": has_agenda,
            "produces_decisions": produces_decisions,
            "purpose": purpose,
            "issues": [],
        }

        if not has_agenda:
            analysis["issues"].append("No agenda - meetings without agendas waste time")
        if not produces_decisions and duration > 30:
            analysis["issues"].append("No decisions produced - consider if this meeting is needed")
        if duration > 90 and freq in ["daily", "weekly"]:
            analysis["issues"].append("Over 90 min for recurring meeting - energy drops after 90")

        results["current_analysis"].append(analysis)
        total_weekly_hours += weekly_hours

    # Meeting load
    hours_per_person = total_weekly_hours / team_size if team_size > 0 else 0
    results["meeting_load"] = {
        "total_weekly_person_hours": round(total_weekly_hours, 1),
        "avg_hours_per_person": round(hours_per_person, 1),
        "meeting_pct_of_week": round(hours_per_person / 40 * 100, 1),
        "assessment": "Healthy" if hours_per_person <= 8 else "Heavy" if hours_per_person <= 15 else "Excessive",
    }

    # Find redundancies
    purpose_groups = {}
    for meeting in current_meetings:
        p = meeting.get("purpose", "").lower()
        if p not in purpose_groups:
            purpose_groups[p] = []
        purpose_groups[p].append(meeting.get("name", ""))
    for purpose, meetings in purpose_groups.items():
        if len(meetings) > 1 and purpose:
            results["redundancies"].append({
                "purpose": purpose,
                "meetings": meetings,
                "recommendation": "Consolidate into one meeting or differentiate purposes",
            })

    # Find gaps
    essential = {"scorecard": False, "ids": False, "rocks": False, "standup": False, "planning": False}
    for meeting in current_meetings:
        purpose = meeting.get("purpose", "").lower()
        if "scorecard" in purpose or "metrics" in purpose:
            essential["scorecard"] = True
        if "ids" in purpose or "issues" in purpose or "problem" in purpose:
            essential["ids"] = True
        if "rock" in purpose or "quarterly" in purpose:
            essential["rocks"] = True
        if "standup" in purpose or "daily" in purpose:
            essential["standup"] = True
        if "planning" in purpose or "strategy" in purpose:
            essential["planning"] = True

    for meeting_type, present in essential.items():
        if not present:
            results["gaps"].append({
                "missing": meeting_type,
                "impact": f"No {meeting_type} meeting detected. This is a core OS component.",
            })

    # Recommendations
    if results["meeting_load"]["assessment"] == "Excessive":
        results["recommendations"].append("Meeting load is excessive. Audit and cut meetings that don't produce decisions.")
    if results["redundancies"]:
        results["recommendations"].append(f"{len(results['redundancies'])} redundant meeting group(s). Consolidate.")
    if results["gaps"]:
        results["recommendations"].append(f"{len(results['gaps'])} missing meeting type(s). Implement to complete your OS.")
    no_agenda = [m for m in results["current_analysis"] if not m["has_agenda"]]
    if no_agenda:
        results["recommendations"].append(f"{len(no_agenda)} meeting(s) without agendas. Add agendas or cancel.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    ml = results["meeting_load"]
    lines = [
        "=" * 65,
        "MEETING PULSE DESIGN",
        "=" * 65,
        f"Team Size: {results['team_size']}  |  Meeting Load: {ml['avg_hours_per_person']:.1f} hrs/person/week ({ml['assessment']})",
        "",
        "RECOMMENDED PULSE:",
        f"{'Meeting':<25} {'Freq':<12} {'Duration':<10} {'Who':<18}",
        "-" * 65,
    ]

    for m in results["recommended_pulse"]:
        req = "*" if m["required"] else " "
        lines.append(f"{req}{m['meeting']:<24} {m['frequency']:<12} {m['duration']:<10} {m['who']:<18}")

    if results["current_analysis"]:
        lines.extend(["", "CURRENT MEETINGS:"])
        for m in results["current_analysis"]:
            issues_flag = " [!]" if m["issues"] else ""
            lines.append(f"  {m['name']:<25} {m['frequency']:<10} {m['duration_min']:>3}min {m['weekly_person_hours']:>5.1f}hrs/wk{issues_flag}")
            for issue in m["issues"]:
                lines.append(f"    -> {issue}")

    if results["gaps"]:
        lines.extend(["", "GAPS:"])
        for g in results["gaps"]:
            lines.append(f"  [!] Missing: {g['missing']} - {g['impact']}")

    if results["redundancies"]:
        lines.extend(["", "REDUNDANCIES:"])
        for r in results["redundancies"]:
            lines.append(f"  [!] '{r['purpose']}' covered by: {', '.join(r['meetings'])}")

    lines.extend(["", "L10 MEETING AGENDA (90 min):"])
    for segment in L10_AGENDA:
        lines.append(f"  {segment['duration_min']:>2} min | {segment['segment']:<30} | {segment['activity']}")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "* = required for effective OS", "=" * 65])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Design and validate meeting pulse")
    parser.add_argument("--input", "-i", help="JSON file with meeting data")
    parser.add_argument("--team-size", type=int, default=35, help="Company team size")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "team_size": args.team_size,
            "leadership_team_size": 6,
            "current_meetings": [
                {"name": "Engineering standup", "frequency": "daily", "duration_min": 15, "attendees": 12, "purpose": "daily standup", "has_agenda": True, "produces_decisions": False},
                {"name": "Leadership sync", "frequency": "weekly", "duration_min": 60, "attendees": 6, "purpose": "scorecard and updates", "has_agenda": True, "produces_decisions": True},
                {"name": "Product review", "frequency": "weekly", "duration_min": 60, "attendees": 8, "purpose": "product updates", "has_agenda": True, "produces_decisions": True},
                {"name": "Sales pipeline", "frequency": "weekly", "duration_min": 45, "attendees": 5, "purpose": "pipeline review", "has_agenda": False, "produces_decisions": False},
                {"name": "All hands", "frequency": "monthly", "duration_min": 60, "attendees": 35, "purpose": "company update", "has_agenda": True, "produces_decisions": False},
                {"name": "Status update", "frequency": "weekly", "duration_min": 30, "attendees": 6, "purpose": "scorecard and updates", "has_agenda": False, "produces_decisions": False},
            ],
        }

    results = design_pulse(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
