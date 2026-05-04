#!/usr/bin/env python3
"""
Meeting Prep Briefer — generate a one-page briefing from a structured JSON input.

Usage:
    python meeting_prep_briefer.py meeting_input.json
    python meeting_prep_briefer.py meeting_input.json --json
"""

import argparse
import json
import sys
from pathlib import Path


def render_briefing(model):
    title = model.get("meeting_title", "Untitled Meeting")
    when = model.get("when", "")
    duration = model.get("duration_minutes", "")
    attendees = model.get("attendees", [])
    your_role = model.get("your_role", "")
    primary_goal = model.get("primary_goal", "")
    decisions_sought = model.get("decisions_sought", [])
    questions_to_ask = model.get("questions_to_ask", [])
    talking_points = model.get("talking_points", [])
    counter_arguments_to_anticipate = model.get("counter_arguments_to_anticipate", [])
    context = model.get("context", "")
    last_meeting_notes = model.get("last_meeting_notes", "")
    metrics_to_reference = model.get("metrics_to_reference", [])
    supporting_links = model.get("supporting_links", [])
    success_definition = model.get("success_definition", "")
    fallback_position = model.get("fallback_position", "")

    lines = []
    lines.append(f"# Briefing: {title}")
    lines.append("")
    if when or duration:
        meta = []
        if when:
            meta.append(f"**When:** {when}")
        if duration:
            meta.append(f"**Duration:** {duration} min")
        lines.append("  ·  ".join(meta))
        lines.append("")

    if your_role:
        lines.append(f"**Your role:** {your_role}")
        lines.append("")

    if primary_goal:
        lines.append("## Primary goal")
        lines.append(f"{primary_goal}")
        lines.append("")

    if attendees:
        lines.append("## Attendees")
        for a in attendees:
            if isinstance(a, dict):
                name = a.get("name", "")
                role = a.get("role", "")
                position = a.get("position_on_topic", "")
                line = f"- **{name}**" + (f" — {role}" if role else "")
                if position:
                    line += f" · _Position: {position}_"
                lines.append(line)
            else:
                lines.append(f"- {a}")
        lines.append("")

    if decisions_sought:
        lines.append("## Decisions needed")
        for d in decisions_sought:
            lines.append(f"- {d}")
        lines.append("")

    if questions_to_ask:
        lines.append("## Questions to ask")
        for q in questions_to_ask:
            lines.append(f"- {q}")
        lines.append("")

    if talking_points:
        lines.append("## Talking points")
        for tp in talking_points:
            lines.append(f"- {tp}")
        lines.append("")

    if counter_arguments_to_anticipate:
        lines.append("## Counter-arguments to anticipate")
        for ca in counter_arguments_to_anticipate:
            if isinstance(ca, dict):
                lines.append(f"- **They might say:** {ca.get('argument', '')}")
                lines.append(f"  - **Response:** {ca.get('response', '')}")
            else:
                lines.append(f"- {ca}")
        lines.append("")

    if metrics_to_reference:
        lines.append("## Metrics to reference")
        for m in metrics_to_reference:
            if isinstance(m, dict):
                lines.append(f"- **{m.get('name', '')}:** {m.get('value', '')}")
            else:
                lines.append(f"- {m}")
        lines.append("")

    if context:
        lines.append("## Context")
        lines.append(context)
        lines.append("")

    if last_meeting_notes:
        lines.append("## From last meeting")
        lines.append(last_meeting_notes)
        lines.append("")

    if supporting_links:
        lines.append("## Supporting links")
        for link in supporting_links:
            if isinstance(link, dict):
                lines.append(f"- [{link.get('title', '')}]({link.get('url', '')})")
            else:
                lines.append(f"- {link}")
        lines.append("")

    if success_definition or fallback_position:
        lines.append("## Outcomes")
        if success_definition:
            lines.append(f"**Success looks like:** {success_definition}")
        if fallback_position:
            lines.append(f"**Fallback position:** {fallback_position}")
        lines.append("")

    return "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(description="Generate a one-page meeting briefing from a JSON input.")
    parser.add_argument("input", help="Path to meeting_input.json")
    parser.add_argument("--json", action="store_true", help="Output the parsed input as JSON instead of markdown briefing")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(model, indent=2))
    else:
        print(render_briefing(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
