#!/usr/bin/env python3
"""
Weekly Review Synthesizer — produce a structured weekly review markdown
from a JSON input.

Usage:
    python weekly_review_synthesizer.py input.json
    python weekly_review_synthesizer.py input.json --json
"""

import argparse
import json
import sys
from pathlib import Path


def render(model):
    week_of = model.get("week_of", "[YYYY-MM-DD]")
    energy = model.get("energy_level_1_to_10", "")

    wins = model.get("wins", [])
    learnings = model.get("learnings", [])
    blockers = model.get("blockers_or_risks", [])
    okr_progress = model.get("okr_progress", [])
    next_week_priorities = model.get("next_week_priorities", [])
    open_loops = model.get("open_loops_to_close", [])
    declines = model.get("things_to_decline", [])
    journal = model.get("journal_note", "")

    lines = []
    lines.append(f"# Weekly Review — week of {week_of}")
    if energy:
        lines.append(f"_Energy this week (1-10): {energy}_")
    lines.append("")

    if wins:
        lines.append(f"## Wins ({len(wins)})")
        for w in wins:
            lines.append(f"- {w}")
        lines.append("")

    if learnings:
        lines.append(f"## Learnings ({len(learnings)})")
        for l in learnings:
            lines.append(f"- {l}")
        lines.append("")

    if blockers:
        lines.append(f"## Blockers / risks for next week ({len(blockers)})")
        for b in blockers:
            if isinstance(b, dict):
                lines.append(f"- **{b.get('item', '')}** — owner: {b.get('owner', 'self')}; mitigation: {b.get('mitigation', 'TBD')}")
            else:
                lines.append(f"- {b}")
        lines.append("")

    if okr_progress:
        lines.append(f"## OKR / goal progress")
        for o in okr_progress:
            if isinstance(o, dict):
                key = o.get("objective", "")
                kr = o.get("key_result", "")
                progress = o.get("progress", "")
                status = o.get("status", "")
                lines.append(f"- **{key}** — KR: {kr} → progress: {progress}{f' ({status})' if status else ''}")
            else:
                lines.append(f"- {o}")
        lines.append("")

    if next_week_priorities:
        lines.append(f"## Next-week priorities ({len(next_week_priorities)})")
        for i, p in enumerate(next_week_priorities, 1):
            lines.append(f"{i}. {p}")
        lines.append("")

    if open_loops:
        lines.append(f"## Open loops to close")
        for ol in open_loops:
            lines.append(f"- {ol}")
        lines.append("")

    if declines:
        lines.append(f"## Things to actively decline")
        for d in declines:
            lines.append(f"- {d}")
        lines.append("")

    if journal:
        lines.append(f"## Journal note")
        lines.append(journal)
        lines.append("")

    # Self-coach section
    lines.append("## Self-coach prompts (answer briefly)")
    lines.append("- What did I avoid this week that I shouldn't have?")
    lines.append("- What am I telling myself I'm too busy for that I'm actually just avoiding?")
    lines.append("- What would I do differently if I started this week over?")
    lines.append("- What is the single most important thing for next week?")
    lines.append("")

    return "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(description="Synthesize a structured weekly review.")
    parser.add_argument("input", help="Path to weekly_review_input.json")
    parser.add_argument("--json", action="store_true", help="Echo the input as JSON instead of rendering markdown")
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
        print(render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
