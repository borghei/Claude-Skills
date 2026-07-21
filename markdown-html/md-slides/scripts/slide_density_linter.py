#!/usr/bin/env python3
"""
Slide Density Linter — flag slides carrying more content than an audience can
absorb while a presenter is talking over them.

Checks word count, bullet count, words per bullet, heading length, table and
code size, image-only slides missing alt text, and slides with no speaker
notes. Exits non-zero when blocking findings exist, so it runs as a CI gate.

Thresholds default to the projected-deck profile and can be relaxed for decks
that will be read rather than presented (--profile read).

Usage:
    python3 slide_density_linter.py --input deck.md
    python3 slide_density_linter.py --input deck.md --profile read --format json
    python3 slide_density_linter.py --input deck.md --max-severity warning
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ULI_RE = re.compile(r"^\s*[-*]\s+(.*)$")
OLI_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
LAYOUT_RE = re.compile(r"^\[layout:\s*([a-z-]+)\]\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
NOTES_MARKER = "???"
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
# (warning threshold, error threshold) per profile.
PROFILES: Dict[str, Dict[str, Any]] = {
    "present": {"words": (50, 75), "bullets": (6, 8), "bullet_words": (12, 20),
                "heading_chars": (60, 90), "table_rows": (6, 9), "code_lines": (12, 20)},
    "read": {"words": (90, 130), "bullets": (8, 12), "bullet_words": (18, 28),
             "heading_chars": (70, 100), "table_rows": (9, 14), "code_lines": (18, 30)},
}
# Layouts intentionally exempt from the body-density rules.
LIGHT_LAYOUTS = {"title", "section", "quote", "image"}


def parse_slides(lines: List[str]) -> List[Dict[str, Any]]:
    """Split markdown into slide records with content, layout, and notes."""
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        lines = lines[end + 1:]
    slides: List[Dict[str, Any]] = []
    body: List[str] = []
    notes: List[str] = []
    layout, in_notes, in_code, start = "default", False, False, 1

    def flush(line_number: int) -> None:
        nonlocal layout, in_notes, start
        if any(l.strip() for l in body) or notes:
            slides.append({"line": start, "lines": list(body),
                           "notes": "\n".join(notes).strip(), "layout": layout})
            layout = "default"
        body.clear()
        notes.clear()
        in_notes = False
        start = line_number + 1

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if not in_code and stripped == "---":
            flush(number)
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
    flush(len(lines))
    return slides


def measure(slide: Dict[str, Any]) -> Dict[str, Any]:
    """Compute the density metrics for one slide."""
    words, bullets, bullet_words = 0, 0, []
    table_rows, code_lines, images = 0, 0, []
    heading, in_code = "", False
    for line in slide["lines"]:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            code_lines += 1
            continue
        if not stripped:
            continue
        head = HEADING_RE.match(stripped)
        if head and not heading:
            heading = head.group(2)
        images.extend(IMAGE_RE.findall(stripped))
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                table_rows += 1
            continue
        item = ULI_RE.match(stripped) or OLI_RE.match(stripped)
        if item:
            bullets += 1
            bullet_words.append(len(item.group(1).split()))
        words += len(re.sub(r"[#>*`\-]", " ", stripped).split())
    return {"words": words, "bullets": bullets,
            "max_bullet_words": max(bullet_words) if bullet_words else 0,
            "heading": heading, "heading_chars": len(heading),
            "table_rows": table_rows, "code_lines": code_lines, "images": images}


def check(value: int, bounds: tuple) -> str:
    """Classify a measured value against (warning, error) thresholds."""
    warn, err = bounds
    return "error" if value > err else ("warning" if value > warn else "")


def audit(slides: List[Dict[str, Any]], profile: str) -> List[Dict[str, Any]]:
    """Apply the density rules to every slide and return the findings."""
    limits = PROFILES[profile]
    out: List[Dict[str, Any]] = []

    def add(sev: str, code: str, index: int, line: int, message: str, fix: str) -> None:
        out.append({"severity": sev, "code": code, "slide": index, "line": line,
                    "message": message, "fix": fix})

    for index, slide in enumerate(slides, start=1):
        m = measure(slide)
        line, light = slide["line"], slide["layout"] in LIGHT_LAYOUTS
        if not light:
            sev = check(m["words"], limits["words"])
            if sev:
                add(sev, "DENSITY_WORDS", index, line,
                    f"{m['words']} words (limit {limits['words'][0]})",
                    "split into two slides, or move the detail into speaker notes")
            sev = check(m["bullets"], limits["bullets"])
            if sev:
                add(sev, "DENSITY_BULLETS", index, line,
                    f"{m['bullets']} bullets (limit {limits['bullets'][0]})",
                    "keep one idea per slide; a 9-bullet slide is two slides")
            sev = check(m["max_bullet_words"], limits["bullet_words"])
            if sev:
                add(sev, "BULLET_TOO_LONG", index, line,
                    f"longest bullet is {m['max_bullet_words']} words "
                    f"(limit {limits['bullet_words'][0]})",
                    "a bullet is a label, not a sentence; move the sentence to notes")
        sev = check(m["heading_chars"], limits["heading_chars"])
        if sev:
            add(sev, "HEADING_LONG", index, line,
                f"heading is {m['heading_chars']} characters",
                "headings wrap to two lines and eat the slide; shorten to a claim")
        sev = check(m["table_rows"], limits["table_rows"])
        if sev:
            add(sev, "TABLE_LARGE", index, line,
                f"table has {m['table_rows']} rows (limit {limits['table_rows'][0]})",
                "show the rows that carry the argument; put the full table in an appendix")
        sev = check(m["code_lines"], limits["code_lines"])
        if sev:
            add(sev, "CODE_LARGE", index, line,
                f"code block is {m['code_lines']} lines (limit {limits['code_lines'][0]})",
                "show the lines that matter; nobody reads 20 lines of projected code")
        for alt, _src in m["images"]:
            if len(alt.strip()) < 8:
                add("error", "IMAGE_ALT_MISSING", index, line,
                    f"image has empty or placeholder alt text: '{alt}'",
                    "describe what the image shows for non-sighted attendees")
        if not slide["notes"] and not light and m["words"] > 10:
            add("info", "NOTES_MISSING", index, line,
                "content slide has no speaker notes",
                "notes are where the sentences go once the bullets become labels")
        if not m["heading"] and not light:
            add("warning", "HEADING_MISSING", index, line,
                "content slide has no heading",
                "every content slide needs a heading; it is the slide's claim")
    return out


def output(findings: List[Dict[str, Any]], slides: List[Dict[str, Any]],
           profile: str, threshold: str, fmt: str) -> int:
    """Print findings and return the count at or above the gate threshold."""
    limit = SEVERITY_ORDER[threshold]
    blocking = [f for f in findings if SEVERITY_ORDER[f["severity"]] >= limit]
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    metrics = [measure(s) for s in slides]
    total_words = sum(m["words"] for m in metrics)
    stats = {"slides": len(slides), "total_words": total_words,
             "mean_words": round(total_words / len(slides), 1) if slides else 0,
             "densest_slide": (max(range(len(metrics)), key=lambda i: metrics[i]["words"]) + 1
                               if metrics else 0)}
    if fmt == "json":
        print(json.dumps({"gate": "fail" if blocking else "pass", "profile": profile,
                          "threshold": threshold, "stats": stats, "counts": counts,
                          "findings": findings}, indent=2))
        return len(blocking)
    print(f"Density lint ({profile} profile) - {stats['slides']} slides, "
          f"{stats['mean_words']} words/slide average\n")
    if not findings:
        print("  no findings - every slide is within the density budget")
    for sev in ("error", "warning", "info"):
        for f in [x for x in findings if x["severity"] == sev]:
            print(f"  [{sev.upper():<7}] slide {f['slide']:>2} (line {f['line']:>3})  "
                  f"{f['code']}: {f['message']}")
            print(f"                            fix: {f['fix']}")
    print(f"\n{counts['error']} error, {counts['warning']} warning, {counts['info']} info")
    print(f"GATE ({threshold}+): {'FAIL' if blocking else 'PASS'}")
    return len(blocking)


def main() -> None:
    """Parse arguments, lint the deck, and exit non-zero on blocking findings."""
    parser = argparse.ArgumentParser(
        description="Flag slides carrying more content than an audience can absorb.")
    parser.add_argument("--input", required=True, help="path to the markdown deck source")
    parser.add_argument("--profile", choices=["present", "read"], default="present",
                        help="density budget: projected deck (default) or read-alone deck")
    parser.add_argument("--max-severity", choices=["info", "warning", "error"],
                        default="error", dest="threshold",
                        help="lowest severity that fails the gate (default: error)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--no-gate", action="store_true",
                        help="always exit 0, even when findings block (report-only mode)")
    args = parser.parse_args()

    try:
        text = Path(args.input).read_text(encoding="utf-8")
        slides = parse_slides(text.replace("\r\n", "\n").split("\n"))
        if not slides:
            raise SystemExit("error: no slides found - separate slides with a '---' line")
        blocking = output(audit(slides, args.profile), slides,
                          args.profile, args.threshold, args.format)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: density lint failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)
    if blocking and not args.no_gate:
        sys.exit(2)  # 2 = gate failed (1 is reserved for tool errors)


if __name__ == "__main__":
    main()
