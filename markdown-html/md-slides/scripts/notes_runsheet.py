#!/usr/bin/env python3
"""
Notes Runsheet — extract speaker notes from a markdown deck and build a timed
runsheet: per-slide duration estimates, cumulative timings, and a comparison
against the intended talk length.

Timing is derived from spoken word count at a configurable rate, plus a fixed
per-slide transition allowance. Slides with no notes are estimated from their
on-slide content instead, and flagged.

Usage:
    python3 notes_runsheet.py --input deck.md --target-minutes 15
    python3 notes_runsheet.py --input deck.md --wpm 120 --format json
    python3 notes_runsheet.py --input deck.md --format markdown
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LAYOUT_RE = re.compile(r"^\[layout:\s*([a-z-]+)\]\s*$")
NOTES_MARKER = "???"
# Seconds of dead air per slide change: click, look up, re-orient the room.
TRANSITION_SECONDS = 4.0
# Speaking rates in words per minute, measured across presentation styles.
RATE_GUIDANCE = {
    "deliberate": 110, "conversational": 130, "brisk": 150, "rushed": 170,
}


def parse_slides(lines: List[str]) -> List[Dict[str, Any]]:
    """Split markdown into slide records with heading, content, and notes."""
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        lines = lines[end + 1:]
    slides: List[Dict[str, Any]] = []
    body: List[str] = []
    notes: List[str] = []
    layout, in_notes, in_code = "default", False, False

    def flush() -> None:
        nonlocal layout, in_notes
        if any(l.strip() for l in body) or notes:
            heading = next((HEADING_RE.match(l.strip()).group(2)
                            for l in body if HEADING_RE.match(l.strip())), "")
            content = " ".join(l.strip() for l in body
                               if l.strip() and not HEADING_RE.match(l.strip()))
            slides.append({"heading": heading, "content": content, "layout": layout,
                           "notes": "\n".join(notes).strip()})
            layout = "default"
        body.clear()
        notes.clear()
        in_notes = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if not in_code and stripped == "---":
            flush()
            continue
        if not in_code and stripped == NOTES_MARKER:
            in_notes = True
            continue
        if in_notes:
            notes.append(line)
            continue
        match = LAYOUT_RE.match(stripped)
        if match and not in_code:
            layout = match.group(1)
            continue
        body.append(line)
    flush()
    return slides


def word_count(text: str) -> int:
    """Count spoken words, ignoring markdown punctuation and table pipes."""
    cleaned = re.sub(r"[|#>*`_\-]", " ", text)
    return len([w for w in cleaned.split() if any(c.isalnum() for c in w)])


def estimate(slides: List[Dict[str, Any]], wpm: int) -> List[Dict[str, Any]]:
    """Estimate a duration for every slide and accumulate a running clock."""
    rows: List[Dict[str, Any]] = []
    elapsed = 0.0
    for index, slide in enumerate(slides, start=1):
        note_words = word_count(slide["notes"])
        if note_words:
            words, source = note_words, "notes"
        else:
            # No notes: assume the presenter speaks roughly twice the words on
            # the slide, with a floor so a bare section divider is not zero.
            words, source = max(word_count(slide["content"]) * 2, 15), "estimated"
        seconds = (words / wpm) * 60 + TRANSITION_SECONDS
        elapsed += seconds
        rows.append({
            "slide": index,
            "heading": slide["heading"] or f"({slide['layout']} slide)",
            "layout": slide["layout"],
            "words": words,
            "source": source,
            "seconds": round(seconds, 1),
            "cumulative_seconds": round(elapsed, 1),
        })
    return rows


def clock(seconds: float) -> str:
    """Format seconds as m:ss."""
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def analyze(rows: List[Dict[str, Any]], target_minutes: float) -> Dict[str, Any]:
    """Summarize the runsheet against the intended talk length."""
    total = rows[-1]["cumulative_seconds"] if rows else 0.0
    target = target_minutes * 60
    longest = max(rows, key=lambda r: r["seconds"]) if rows else None
    return {
        "slides": len(rows),
        "total_seconds": round(total, 1),
        "total_clock": clock(total),
        "target_seconds": target,
        "target_clock": clock(target),
        "delta_seconds": round(total - target, 1),
        "over_target": total > target,
        "mean_seconds": round(total / len(rows), 1) if rows else 0,
        "without_notes": sum(1 for r in rows if r["source"] == "estimated"),
        "longest_slide": longest["slide"] if longest else 0,
        "longest_seconds": longest["seconds"] if longest else 0,
    }


def output(rows: List[Dict[str, Any]], summary: Dict[str, Any], wpm: int, fmt: str) -> None:
    """Print the runsheet in the requested format."""
    if fmt == "json":
        print(json.dumps({"wpm": wpm, "summary": summary, "runsheet": rows}, indent=2))
        return
    if fmt == "markdown":
        print(f"# Runsheet\n\nEstimated at {wpm} wpm plus "
              f"{TRANSITION_SECONDS:.0f}s per transition.\n")
        print("| # | Slide | Words | Source | Duration | Cumulative |")
        print("|---|-------|-------|--------|----------|------------|")
        for r in rows:
            print(f"| {r['slide']} | {r['heading']} | {r['words']} | {r['source']} "
                  f"| {clock(r['seconds'])} | {clock(r['cumulative_seconds'])} |")
        print(f"\n**Total: {summary['total_clock']}** against a target of "
              f"{summary['target_clock']}.")
        return
    print(f"Runsheet - {summary['slides']} slides at {wpm} wpm\n")
    print(f"  {'#':>2}  {'slide':<34} {'words':>5}  {'dur':>5}  {'cum':>5}")
    for r in rows:
        flag = " *" if r["source"] == "estimated" else "  "
        print(f"  {r['slide']:>2}  {r['heading'][:34]:<34} {r['words']:>5}  "
              f"{clock(r['seconds']):>5}  {clock(r['cumulative_seconds']):>5}{flag}")
    print(f"\n  * duration estimated from slide content - no speaker notes "
          f"({summary['without_notes']} slides)")
    print(f"\n  total    : {summary['total_clock']}")
    print(f"  target   : {summary['target_clock']}")
    if summary["over_target"]:
        print(f"  OVER by  : {clock(abs(summary['delta_seconds']))} - "
              f"cut content, do not speak faster")
    else:
        print(f"  under by : {clock(abs(summary['delta_seconds']))}")
    print(f"  longest  : slide {summary['longest_slide']} "
          f"({clock(summary['longest_seconds'])})")


def main() -> None:
    """Parse arguments, build the runsheet, and report."""
    parser = argparse.ArgumentParser(
        description="Extract speaker notes into a timed presentation runsheet.",
        epilog="Speaking rates: " + ", ".join(f"{k}={v}wpm" for k, v in RATE_GUIDANCE.items()))
    parser.add_argument("--input", required=True, help="path to the markdown deck source")
    parser.add_argument("--wpm", type=int, default=130,
                        help="speaking rate in words per minute (default: 130)")
    parser.add_argument("--target-minutes", type=float, default=15.0,
                        help="intended talk length in minutes (default: 15)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()

    if args.wpm < 60 or args.wpm > 250:
        print("error: --wpm must be between 60 and 250 to produce a usable estimate",
              file=sys.stderr)
        sys.exit(1)
    try:
        text = Path(args.input).read_text(encoding="utf-8")
        slides = parse_slides(text.replace("\r\n", "\n").split("\n"))
        if not slides:
            raise SystemExit("error: no slides found - separate slides with a '---' line")
        rows = estimate(slides, args.wpm)
        output(rows, analyze(rows, args.target_minutes), args.wpm, args.format)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: runsheet generation failed ({type(exc).__name__}: {exc})",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
