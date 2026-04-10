#!/usr/bin/env python3
"""
Legal Meeting Brief Generator

Generates structured meeting briefings with type-specific sections
for 8 legal meeting types.

Usage:
    python meeting_brief_generator.py --type deal-review --title "Series B Review" --date 2026-04-15
    python meeting_brief_generator.py --type board --title "Q1 Board" --date 2026-04-20 --json
    python meeting_brief_generator.py --type regulatory --title "FDA Meeting" --date 2026-05-01
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


MEETING_TYPES = [
    "deal-review", "board", "vendor", "team-sync",
    "client", "regulatory", "litigation", "cross-functional",
]

# Common sections for all meeting types
COMMON_SECTIONS: List[Dict[str, str]] = [
    {"title": "Meeting Details", "content": ""},
    {"title": "Participants", "content": ""},
    {"title": "Agenda / Expected Topics", "content": ""},
    {"title": "Background and Context", "content": "[Provide relevant background for this meeting.]"},
    {"title": "Key Documents", "content": "| Document | Version | Status | Location |\n|----------|---------|--------|----------|\n| [Document name] | [v#] | [Draft/Final] | [Link/path] |"},
    {"title": "Open Issues", "content": "| # | Issue | Status | Owner | Priority |\n|---|-------|--------|-------|----------|\n| 1 | [Issue description] | [Open/In Progress] | [Name] | [High/Medium/Low] |"},
    {"title": "Legal Considerations", "content": "[Key legal issues, risks, or compliance considerations for this meeting.]"},
    {"title": "Talking Points", "content": "1. **[Topic]** -- [Supporting context and key message]\n2. **[Topic]** -- [Supporting context and key message]"},
    {"title": "Questions to Raise", "content": "1. **[Question]** -- *Why this matters:* [Context for why this question is important]\n2. **[Question]** -- *Why this matters:* [Context]"},
    {"title": "Decisions Needed", "content": "| Decision | Options | Recommendation | Deadline |\n|----------|---------|----------------|----------|\n| [Decision needed] | [Option A / Option B] | [Recommended option with rationale] | [Date] |"},
    {"title": "Prior Meeting Follow-Up", "content": "| # | Action Item | Owner | Status | Due Date |\n|---|------------|-------|--------|----------|\n| 1 | [Action from prior meeting] | [Name] | [Status] | [Date] |"},
    {"title": "Preparation Gaps", "content": "| # | Gap | Impact | Action Needed |\n|---|-----|--------|---------------|\n| 1 | [Missing information or document] | [How it affects meeting] | [Steps to fill gap] |"},
]

# Type-specific additional sections
TYPE_SECTIONS: Dict[str, List[Dict[str, str]]] = {
    "deal-review": [
        {"title": "Deal Summary", "content": (
            "| Field | Detail |\n|-------|--------|\n"
            "| Parties | [Buyer/Seller/Investor] |\n"
            "| Structure | [Asset purchase/Stock purchase/Merger/Investment] |\n"
            "| Value | [$X million] |\n"
            "| Timeline | [Expected close date] |\n"
            "| Stage | [LOI/Due Diligence/Definitive Agreement/Closing] |"
        )},
        {"title": "Contract Status", "content": (
            "| Document | Version | Status | Open Issues |\n"
            "|----------|---------|--------|-------------|\n"
            "| [Agreement name] | [v#] | [Draft/Redline/Final] | [# open issues] |"
        )},
        {"title": "Approval Requirements", "content": (
            "| Approver | Authority Limit | Status |\n"
            "|----------|----------------|--------|\n"
            "| [Name/Role] | [$X] | [Pending/Approved] |"
        )},
        {"title": "Counterparty Dynamics", "content": "[Negotiation position, prior dealings, leverage points, known concerns.]"},
        {"title": "Red Lines / Non-Negotiables", "content": "1. [Non-negotiable term and rationale]\n2. [Non-negotiable term and rationale]"},
    ],
    "board": [
        {"title": "Legal Department Update", "content": (
            "| Metric | Current | Prior Quarter | Trend |\n"
            "|--------|---------|---------------|-------|\n"
            "| Open matters | [#] | [#] | [Up/Down/Flat] |\n"
            "| Budget utilization | [$X / $Y] | [$X / $Y] | [%] |\n"
            "| Outside counsel spend | [$X] | [$X] | [%] |"
        )},
        {"title": "Risk Highlights", "content": (
            "| # | Risk | Likelihood | Impact | Mitigation |\n"
            "|---|------|-----------|--------|------------|\n"
            "| 1 | [Risk description] | [H/M/L] | [H/M/L] | [Mitigation plan] |"
        )},
        {"title": "Regulatory Update", "content": "[Recent regulatory changes affecting the organization and compliance status.]"},
        {"title": "Pending Board Approvals", "content": (
            "| # | Item | Type | Recommendation | Deadline |\n"
            "|---|------|------|----------------|----------|\n"
            "| 1 | [Approval item] | [Contract/Policy/Transaction] | [Approve/Reject/Defer] | [Date] |"
        )},
        {"title": "Litigation Summary", "content": (
            "| Matter | Type | Status | Exposure | Reserve |\n"
            "|--------|------|--------|----------|--------|\n"
            "| [Matter name] | [Type] | [Active/Settled/Closed] | [$X] | [$X] |"
        )},
    ],
    "vendor": [
        {"title": "Vendor Profile", "content": (
            "| Field | Detail |\n|-------|--------|\n"
            "| Vendor | [Name] |\n"
            "| Category | [SaaS/Professional Services/Hardware/etc.] |\n"
            "| Contract value | [$X/year] |\n"
            "| Contract expiry | [Date] |\n"
            "| Relationship owner | [Name] |"
        )},
        {"title": "Contract History", "content": "[Prior contracts, amendments, renewals, and their outcomes.]"},
        {"title": "Open Issues with Vendor", "content": (
            "| # | Issue | Severity | Owner | Status |\n"
            "|---|-------|----------|-------|--------|\n"
            "| 1 | [Issue] | [Critical/High/Medium/Low] | [Name] | [Status] |"
        )},
        {"title": "Negotiation Strategy", "content": "[Key objectives, fallback positions, and BATNA for this vendor discussion.]"},
    ],
    "team-sync": [
        {"title": "Workload Overview", "content": (
            "| Team Member | Active Matters | Capacity | Blockers |\n"
            "|-------------|---------------|----------|----------|\n"
            "| [Name] | [#] | [Available/At Capacity/Overloaded] | [Blockers if any] |"
        )},
        {"title": "Upcoming Deadlines", "content": (
            "| Deadline | Matter | Owner | Status |\n"
            "|----------|--------|-------|--------|\n"
            "| [Date] | [Matter] | [Name] | [On Track/At Risk/Overdue] |"
        )},
        {"title": "Resource Needs", "content": "[Additional resources, outside counsel, tools, or budget needed.]"},
    ],
    "client": [
        {"title": "Client/Customer Profile", "content": (
            "| Field | Detail |\n|-------|--------|\n"
            "| Client | [Name] |\n"
            "| Relationship manager | [Name] |\n"
            "| Contract value | [$X] |\n"
            "| Tenure | [X years] |"
        )},
        {"title": "Open Matters", "content": (
            "| # | Matter | Type | Status | Owner |\n"
            "|---|--------|------|--------|-------|\n"
            "| 1 | [Matter] | [Type] | [Status] | [Name] |"
        )},
        {"title": "Risk Areas", "content": "[Known risks, sensitivities, or compliance concerns related to this client.]"},
    ],
    "regulatory": [
        {"title": "Regulatory Body Context", "content": (
            "| Field | Detail |\n|-------|--------|\n"
            "| Agency | [Name] |\n"
            "| Jurisdiction | [Federal/State/International] |\n"
            "| Key contacts | [Names/Titles] |\n"
            "| Enforcement priorities | [Current focus areas] |"
        )},
        {"title": "Enforcement Patterns", "content": "[Recent enforcement actions in the sector; relevant precedent.]"},
        {"title": "Matter History", "content": "[Prior interactions, submissions, correspondence with this regulator.]"},
        {"title": "Privilege Considerations", "content": (
            "**What IS privileged (do not share):**\n"
            "- [Internal legal analysis and strategy]\n"
            "- [Attorney-client communications]\n\n"
            "**What can be shared:**\n"
            "- [Factual information requested]\n"
            "- [Required disclosures]"
        )},
        {"title": "Compliance Posture", "content": "[Current compliance status; remediation progress; open findings.]"},
    ],
    "litigation": [
        {"title": "Case Summary", "content": (
            "| Field | Detail |\n|-------|--------|\n"
            "| Case | [Name v. Name] |\n"
            "| Court/Forum | [Court name] |\n"
            "| Case number | [#] |\n"
            "| Filed | [Date] |\n"
            "| Claims | [Summary of claims] |"
        )},
        {"title": "Procedural Posture", "content": "[Current stage: pleadings, discovery, motions, trial, appeal.]"},
        {"title": "Upcoming Deadlines", "content": (
            "| Deadline | Event | Owner | Status |\n"
            "|----------|-------|-------|--------|\n"
            "| [Date] | [Filing/Hearing/Deposition] | [Name] | [Status] |"
        )},
        {"title": "Settlement Status", "content": "[Current settlement discussions, offers, counteroffers, and assessment.]"},
        {"title": "Exposure Assessment", "content": (
            "| Scenario | Likelihood | Financial Impact |\n"
            "|----------|-----------|------------------|\n"
            "| Best case | [%] | [$X] |\n"
            "| Most likely | [%] | [$X] |\n"
            "| Worst case | [%] | [$X] |"
        )},
    ],
    "cross-functional": [
        {"title": "Stakeholder Map", "content": (
            "| Stakeholder | Department | Interest | Influence |\n"
            "|------------|-----------|---------|----------|\n"
            "| [Name] | [Dept] | [What they care about] | [High/Medium/Low] |"
        )},
        {"title": "Competing Priorities", "content": "[Known conflicts between departments or teams that may surface.]"},
        {"title": "Decision Framework", "content": "[How decisions will be made: consensus, escalation, RACI matrix.]"},
    ],
}


def build_meeting_details(title: str, date: str, meeting_type: str) -> str:
    """Build the meeting details section."""
    return (
        f"| Field | Detail |\n|-------|--------|\n"
        f"| Title | {title} |\n"
        f"| Type | {meeting_type.replace('-', ' ').title()} |\n"
        f"| Date | {date} |\n"
        f"| Time | [INSERT TIME] |\n"
        f"| Location | [INSERT LOCATION / VIDEO LINK] |\n"
        f"| Duration | [INSERT DURATION] |\n"
        f"| Prepared by | [INSERT NAME] |\n"
        f"| Prepared on | {datetime.now().strftime('%Y-%m-%d')} |"
    )


def build_participants_section(participants: List[Dict[str, str]]) -> str:
    """Build the participants table."""
    lines = ["| Name | Organization | Role | Key Interests |",
             "|------|-------------|------|---------------|"]
    if participants:
        for p in participants:
            name = p.get("name", "[Name]")
            org = p.get("org", "[Org]")
            role = p.get("role", "[Role]")
            interests = p.get("interests", "[Key interests/concerns]")
            lines.append(f"| {name} | {org} | {role} | {interests} |")
    else:
        lines.append("| [Name] | [Organization] | [Role] | [Key interests] |")
    return "\n".join(lines)


def build_agenda_section(agenda_items: List[str]) -> str:
    """Build the agenda section."""
    if not agenda_items:
        return "1. [Agenda item 1]\n2. [Agenda item 2]\n3. [Agenda item 3]"
    lines = []
    for i, item in enumerate(agenda_items, 1):
        lines.append(f"{i}. {item.strip()}")
    return "\n".join(lines)


def generate_briefing(args: argparse.Namespace) -> Dict[str, Any]:
    """Generate the meeting briefing."""
    meeting_type = args.type
    title = args.title
    date = args.date

    # Parse participants
    participants: List[Dict[str, str]] = []
    if args.participants:
        try:
            participants = json.loads(args.participants)
        except json.JSONDecodeError:
            participants = [{"name": p.strip()} for p in args.participants.split(",")]

    # Parse agenda
    agenda_items: List[str] = []
    if args.agenda:
        agenda_items = [a.strip() for a in args.agenda.split(",")]

    # Build sections
    all_sections = []
    for section in COMMON_SECTIONS:
        s = dict(section)
        if s["title"] == "Meeting Details":
            s["content"] = build_meeting_details(title, date, meeting_type)
        elif s["title"] == "Participants":
            s["content"] = build_participants_section(participants)
        elif s["title"] == "Agenda / Expected Topics":
            s["content"] = build_agenda_section(agenda_items)
        all_sections.append(s)

    # Insert type-specific sections after "Legal Considerations"
    type_specific = TYPE_SECTIONS.get(meeting_type, [])
    legal_idx = next((i for i, s in enumerate(all_sections)
                      if s["title"] == "Legal Considerations"), len(all_sections))
    for i, ts in enumerate(type_specific):
        all_sections.insert(legal_idx + 1 + i, dict(ts))

    # Generate markdown
    md_lines = [f"# Meeting Briefing: {title}", ""]
    md_lines.append(f"**Type:** {meeting_type.replace('-', ' ').title()}")
    md_lines.append(f"**Date:** {date}")
    md_lines.append(f"**Prepared:** {datetime.now().strftime('%Y-%m-%d')}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # TOC
    md_lines.append("## Table of Contents")
    md_lines.append("")
    for i, section in enumerate(all_sections, 1):
        anchor = section["title"].lower().replace(" ", "-").replace("/", "").replace("(", "").replace(")", "")
        md_lines.append(f"{i}. [{section['title']}](#{anchor})")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Sections
    for i, section in enumerate(all_sections, 1):
        md_lines.append(f"## {i}. {section['title']}")
        md_lines.append("")
        md_lines.append(section["content"])
        md_lines.append("")

    md_lines.append("---")
    md_lines.append(f"*Briefing generated on {datetime.now().strftime('%Y-%m-%d')} "
                    f"for {title}. Review and customize before distribution.*")

    briefing_text = "\n".join(md_lines)

    return {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "meeting_type": meeting_type,
        "title": title,
        "date": date,
        "participants_count": len(participants),
        "agenda_items_count": len(agenda_items),
        "total_sections": len(all_sections),
        "type_specific_sections": len(type_specific),
        "section_titles": [s["title"] for s in all_sections],
        "briefing_text": briefing_text,
    }


def format_text(result: Dict[str, Any]) -> str:
    """Return the briefing markdown text."""
    return result["briefing_text"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate structured meeting briefings for legal meetings."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--type", required=True, choices=MEETING_TYPES,
                        help="Meeting type")
    parser.add_argument("--title", required=True, help="Meeting title")
    parser.add_argument("--date", required=True,
                        help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--participants", default=None,
                        help='JSON array: [{"name","org","role","interests"}]')
    parser.add_argument("--agenda", default=None,
                        help="Comma-separated agenda items")
    parser.add_argument("--output", default=None,
                        help="Write briefing to file instead of stdout")

    args = parser.parse_args()

    try:
        result = generate_briefing(args)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result["briefing_text"])
            print(f"Briefing written to {args.output} ({result['total_sections']} sections)")
        elif args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
