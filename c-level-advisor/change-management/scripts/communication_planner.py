#!/usr/bin/env python3
"""
Change Communication Planner - Generate sequenced communication plans.

Creates audience-sequenced communication plans with templates, channel
recommendations, and timing for organizational changes.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


CHANGE_COMM_TEMPLATES = {
    "process": {
        "phases": [
            {"timing": "T-2 weeks", "audience": "Leadership team", "channel": "In-person meeting", "content_type": "Full context briefing"},
            {"timing": "T-1 week", "audience": "Team leads", "channel": "Small group meeting", "content_type": "Heads-up with their role in rollout"},
            {"timing": "T-0 (Go-live)", "audience": "All affected employees", "channel": "Email + all-hands", "content_type": "Announcement with FAQ"},
            {"timing": "T+1 week", "audience": "All affected employees", "channel": "FAQ document + Slack", "content_type": "FAQ published, Q&A channel open"},
            {"timing": "T+4 weeks", "audience": "All affected employees", "channel": "Team meeting", "content_type": "Adoption check + public wins"},
            {"timing": "T+8 weeks", "audience": "All employees", "channel": "Email", "content_type": "Old system deprecated notice"},
        ],
    },
    "org": {
        "phases": [
            {"timing": "T-1 week", "audience": "Most affected individuals", "channel": "1:1 with manager", "content_type": "Personal impact conversation"},
            {"timing": "T-0", "audience": "All affected employees", "channel": "Synchronous meeting (in-person preferred)", "content_type": "WHY announcement with Q&A"},
            {"timing": "T+1 day", "audience": "Directly affected", "channel": "Manager 1:1s", "content_type": "Individual impact and support"},
            {"timing": "T+1 week", "audience": "All employees", "channel": "Written FAQ", "content_type": "Honest FAQ with what you CAN share"},
            {"timing": "T+2-4 weeks", "audience": "New structure", "channel": "Team meetings", "content_type": "New structure operating"},
            {"timing": "T+2 months", "audience": "All affected", "channel": "Retrospective", "content_type": "First retrospective"},
            {"timing": "T+3-6 months", "audience": "All", "channel": "HR check-ins", "content_type": "Regular health check-ins"},
        ],
    },
    "strategy": {
        "phases": [
            {"timing": "T-2 weeks", "audience": "Leadership team", "channel": "Off-site/meeting", "content_type": "Full alignment (everyone on same page)"},
            {"timing": "T-0", "audience": "All employees", "channel": "All-hands (employees BEFORE press)", "content_type": "Internal announcement"},
            {"timing": "T+1 week", "audience": "Each team", "channel": "Team-level meetings", "content_type": "'What does this mean for us' conversations"},
            {"timing": "T+2 weeks", "audience": "All employees", "channel": "CEO update", "content_type": "Resource reallocation announced"},
            {"timing": "T+1 month", "audience": "All employees", "channel": "Company update", "content_type": "First milestone of new direction visible"},
            {"timing": "T+ ongoing", "audience": "All employees", "channel": "Regular updates", "content_type": "Progress on new direction"},
        ],
    },
    "culture": {
        "phases": [
            {"timing": "T-8 weeks", "audience": "Representative sample", "channel": "Workshops", "content_type": "Input gathering on culture change"},
            {"timing": "T-4 weeks", "audience": "Leadership team", "channel": "Workshop", "content_type": "Define observable behaviors"},
            {"timing": "T-0", "audience": "All employees", "channel": "Story-based all-hands", "content_type": "Story-based announcement"},
            {"timing": "T+2 weeks", "audience": "All employees", "channel": "Written + examples", "content_type": "Behavioral anchors published"},
            {"timing": "T+1 month", "audience": "Leadership team", "channel": "Visible modeling", "content_type": "Leaders visibly model new behavior"},
            {"timing": "T+next review", "audience": "All employees", "channel": "Performance system", "content_type": "Behaviors in performance reviews"},
            {"timing": "T+ ongoing", "audience": "All employees", "channel": "Recognition", "content_type": "Public recognition of new behaviors"},
        ],
    },
}

MESSAGE_TEMPLATE = """
COMMUNICATION: {title}

1. WHAT IS CHANGING
   {what_changing}

2. WHY IT IS CHANGING
   {why_changing}

3. WHAT THIS MEANS FOR YOU
   {impact}

4. WHAT IS NOT CHANGING
   {not_changing}

5. TIMELINE
   {timeline}

6. HOW TO ASK QUESTIONS
   {questions_channel}

7. WHAT HAPPENS NEXT
   {next_step}
"""


def generate_plan(data: dict) -> dict:
    """Generate a change communication plan."""
    change_type = data.get("change_type", "process")
    change_name = data.get("change_name", "Change Initiative")
    go_live_date_str = data.get("go_live_date", "")
    message_inputs = data.get("message", {})

    try:
        go_live = datetime.strptime(go_live_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        go_live = datetime.now() + timedelta(weeks=2)

    template = CHANGE_COMM_TEMPLATES.get(change_type, CHANGE_COMM_TEMPLATES["process"])

    results = {
        "timestamp": datetime.now().isoformat(),
        "change_name": change_name,
        "change_type": change_type,
        "go_live_date": go_live.strftime("%Y-%m-%d"),
        "communication_phases": [],
        "message_draft": "",
        "anti_patterns": [
            "Do NOT announce on Friday afternoon - people stew over the weekend",
            "Do NOT say 'this is final, questions are not welcome' - creates underground resistance",
            "Do NOT skip the FAQ - concerns go unaddressed",
            "Do NOT let leaders be exempt from the change - destroys credibility",
            "Do NOT communicate via email only for org changes - requires synchronous delivery",
        ],
        "quality_checklist": [
            {"check": "Specific dates included (not 'soon')", "status": False},
            {"check": "Named person for questions", "status": False},
            {"check": "What is NOT changing explicitly stated", "status": False},
            {"check": "FAQ prepared", "status": False},
            {"check": "Leadership aligned before announcement", "status": False},
            {"check": "Affected individuals told before general announcement", "status": False},
            {"check": "Follow-up cadence defined", "status": False},
        ],
        "recommendations": [],
    }

    # Build phases with actual dates
    for phase in template["phases"]:
        timing_str = phase["timing"]
        # Parse timing to compute date
        if timing_str.startswith("T-"):
            parts = timing_str.replace("T-", "").strip()
            if "week" in parts:
                weeks = int(parts.split()[0])
                phase_date = go_live - timedelta(weeks=weeks)
            elif "day" in parts:
                days = int(parts.split()[0])
                phase_date = go_live - timedelta(days=days)
            else:
                phase_date = go_live
        elif timing_str.startswith("T+"):
            parts = timing_str.replace("T+", "").strip()
            if "week" in parts:
                weeks = int(parts.split()[0])
                phase_date = go_live + timedelta(weeks=weeks)
            elif "day" in parts:
                days = int(parts.split()[0])
                phase_date = go_live + timedelta(days=days)
            elif "month" in parts:
                months = int(parts.split()[0])
                phase_date = go_live + timedelta(weeks=months * 4)
            else:
                phase_date = go_live + timedelta(weeks=4)
        else:
            phase_date = go_live

        results["communication_phases"].append({
            "timing": timing_str,
            "date": phase_date.strftime("%Y-%m-%d"),
            "audience": phase["audience"],
            "channel": phase["channel"],
            "content_type": phase["content_type"],
            "is_past_due": datetime.now() > phase_date,
        })

    # Generate message draft
    results["message_draft"] = MESSAGE_TEMPLATE.format(
        title=change_name,
        what_changing=message_inputs.get("what_changing", "[What is changing - 1-2 sentences, direct]"),
        why_changing=message_inputs.get("why_changing", "[The business reason - be honest]"),
        impact=message_inputs.get("impact", "[Practical impact on the audience]"),
        not_changing=message_inputs.get("not_changing", "[Stability anchor - what stays the same]"),
        timeline=message_inputs.get("timeline", "[Specific dates for key milestones]"),
        questions_channel=message_inputs.get("questions_channel", "[Channel, named person, office hours schedule]"),
        next_step=message_inputs.get("next_step", "[The very first concrete step]"),
    ).strip()

    # Recommendations
    past_due = [p for p in results["communication_phases"] if p["is_past_due"]]
    if past_due:
        results["recommendations"].append(f"{len(past_due)} communication phase(s) past due. Catch up immediately.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    lines = [
        "=" * 65,
        "CHANGE COMMUNICATION PLAN",
        "=" * 65,
        f"Change: {results['change_name']}",
        f"Type: {results['change_type'].title()}  |  Go-Live: {results['go_live_date']}",
        "",
        "COMMUNICATION SEQUENCE:",
        f"{'Timing':<14} {'Date':<12} {'Audience':<25} {'Channel':<22}",
        "-" * 65,
    ]

    for p in results["communication_phases"]:
        flag = " [PAST DUE]" if p["is_past_due"] else ""
        lines.append(f"{p['timing']:<14} {p['date']:<12} {p['audience']:<25} {p['channel']:<22}{flag}")
        lines.append(f"{'':>14} Content: {p['content_type']}")

    lines.extend(["", "MESSAGE TEMPLATE:", "-" * 40, results["message_draft"], "-" * 40])

    lines.extend(["", "ANTI-PATTERNS TO AVOID:"])
    for ap in results["anti_patterns"]:
        lines.append(f"  [X] {ap}")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 65])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate change communication plan")
    parser.add_argument("--input", "-i", help="JSON file with communication data")
    parser.add_argument("--type", choices=["process", "org", "strategy", "culture"], default="process", help="Change type")
    parser.add_argument("--name", help="Change name")
    parser.add_argument("--date", help="Go-live date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "change_type": args.type,
            "change_name": args.name or "New CRM Rollout",
            "go_live_date": args.date or (datetime.now() + timedelta(weeks=3)).strftime("%Y-%m-%d"),
        }

    results = generate_plan(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
