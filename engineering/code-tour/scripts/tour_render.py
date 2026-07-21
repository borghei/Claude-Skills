#!/usr/bin/env python3
"""Render a tour definition into a readable onboarding document.

Emits markdown with ordered stops, orientation, per-stop why-notes, and a coverage
audit that flags stops whose notes only restate what the code does.

Usage:
  python3 tour_render.py --input assets/sample_tour.json
  python3 tour_render.py --input assets/sample_tour.json --format json
  python3 tour_render.py --input assets/sample_tour.json --audit-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

WHAT_ONLY_RE = re.compile(
    r"^(?:this|the)\s+(?:file|function|class|module|method)\s+(?:is|does|contains|handles|"
    r"defines|implements|returns|calls|creates|sets)\b", re.IGNORECASE)
WHY_MARKERS = ("because", "so that", "rather than", "instead of", "reason", "why",
               "historically", "originally", "trade-off", "tradeoff", "we chose",
               "avoids", "prevents", "otherwise", "beware", "surprising", "counter-intuitive")
MIN_NOTE_WORDS = 20


def load_tour(path: str) -> Dict[str, Any]:
    """Load and validate a tour definition file."""
    try:
        tour = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: tour file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: tour file is not valid JSON ({path}): {exc}")
    stops = tour.get("stops") if isinstance(tour, dict) else None
    if not isinstance(stops, list) or not stops:
        raise SystemExit("error: tour must be an object with a non-empty 'stops' list")
    return tour


def audit_note(note: str) -> Dict[str, Any]:
    """Score one stop's note on whether it explains why rather than restating what."""
    words = len(note.split())
    issues: List[str] = []
    if words < MIN_NOTE_WORDS:
        issues.append(f"note is {words} words — too thin to carry the reasoning")
    if WHAT_ONLY_RE.match(note.strip()):
        issues.append("opens by restating what the code does; the reader can see that")
    if not any(marker in note.lower() for marker in WHY_MARKERS):
        issues.append("no causal language — nothing here explains why it is this way")
    return {"words": words, "issues": issues, "passes": not issues}


def audit_tour(tour: Dict[str, Any]) -> Dict[str, Any]:
    """Audit every stop's note and summarize the tour's explanatory quality."""
    rows: List[Dict[str, Any]] = []
    for index, stop in enumerate(tour["stops"], start=1):
        note = str(stop.get("note", ""))
        result = audit_note(note)
        rows.append({
            "stop": stop.get("stop", index),
            "title": stop.get("title", stop.get("path", "untitled")),
            "path": stop.get("path", ""),
            **result,
        })
    passing = sum(1 for row in rows if row["passes"])
    return {
        "total_stops": len(rows),
        "passing_stops": passing,
        "why_ratio": round(passing / len(rows), 2) if rows else 0.0,
        "stops": rows,
    }


def render_markdown(tour: Dict[str, Any], audit: Dict[str, Any]) -> str:
    """Render the tour as a markdown onboarding document."""
    lines: List[str] = [
        f"# {tour.get('title', 'Code Tour')}",
        "",
        f"**Repository:** `{tour.get('repo', '.')}`  ",
        f"**Audience:** {tour.get('audience', 'new engineer')}  ",
        f"**Estimated time:** {tour.get('duration_minutes', 45)} minutes  ",
        f"**Stops:** {len(tour['stops'])}",
        "",
    ]
    if tour.get("orientation"):
        lines += ["## Before you start", "", str(tour["orientation"]), ""]
    if tour.get("prerequisites"):
        lines += ["**Prerequisites:**", ""]
        lines += [f"- {item}" for item in tour["prerequisites"]]
        lines.append("")

    lines += ["## Stops", ""]
    for index, stop in enumerate(tour["stops"], start=1):
        number = stop.get("stop", index)
        anchor = f"::{stop['anchor']}" if stop.get("anchor") else ""
        location = f"`{stop.get('path', '')}{anchor}`"
        if stop.get("line"):
            location += f" (line {stop['line']})"
        lines += [
            f"### {number}. {stop.get('title', stop.get('path', 'Stop'))}",
            "",
            f"**Where:** {location}",
            "",
        ]
        if stop.get("read_first"):
            lines += [f"**Read first:** {stop['read_first']}", ""]
        lines += [str(stop.get("note", "_No note written for this stop._")), ""]
        if stop.get("question"):
            lines += [f"**Before moving on:** {stop['question']}", ""]
        if stop.get("gotcha"):
            lines += [f"> **Gotcha:** {stop['gotcha']}", ""]

    if tour.get("after"):
        lines += ["## After the tour", "", str(tour["after"]), ""]
    lines += [
        "## Tour maintenance",
        "",
        f"This tour has {audit['total_stops']} stops with a why-ratio of "
        f"{audit['why_ratio']:.0%}. Validate anchors before each use:",
        "",
        "```bash",
        "python3 scripts/tour_validate.py --tour <this tour>.json --repo <repo>",
        "```",
        "",
    ]
    return "\n".join(lines)


def output(tour: Dict[str, Any], audit: Dict[str, Any], fmt: str, audit_only: bool) -> None:
    """Print the rendered tour or the audit, as text or JSON."""
    if fmt == "json":
        payload = audit if audit_only else {"tour": tour, "audit": audit}
        print(json.dumps(payload, indent=2))
        return
    if not audit_only:
        print(render_markdown(tour, audit))
        return
    print(f"{audit['total_stops']} stops, {audit['passing_stops']} explain why "
          f"(why-ratio {audit['why_ratio']:.0%})\n")
    for row in audit["stops"]:
        if row["passes"]:
            print(f"  ok    stop {row['stop']}: {row['title']} ({row['words']} words)")
            continue
        print(f"  weak  stop {row['stop']}: {row['title']}")
        for issue in row["issues"]:
            print(f"          - {issue}")


def main() -> None:
    """Parse arguments, render or audit the tour, and exit non-zero below the why-ratio floor."""
    parser = argparse.ArgumentParser(description="Render a code tour into an onboarding document.")
    parser.add_argument("--input", required=True, help="tour definition JSON")
    parser.add_argument("--audit-only", action="store_true",
                        help="print the why-not-what audit instead of the document")
    parser.add_argument("--min-why-ratio", type=float, default=0.0,
                        help="minimum share of stops that must explain why (default: 0.0)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        tour = load_tour(args.input)
        audit = audit_tour(tour)
        output(tour, audit, args.format, args.audit_only)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not render tour: {exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(1 if audit["why_ratio"] < args.min_why_ratio else 0)


if __name__ == "__main__":
    main()
