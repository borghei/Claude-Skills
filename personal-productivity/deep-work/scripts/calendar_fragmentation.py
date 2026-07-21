#!/usr/bin/env python3
"""Measure how badly a calendar fragments the working day, and propose a fix.

Reads a calendar export and reports, per day: the longest uninterrupted block,
the context-switch count, and the deep-work ratio against a target. For days
that miss the target it searches single-meeting moves and proposes the one that
buys back the most contiguous time. Deterministic: no clock reads, no network.

Usage:
    python3 calendar_fragmentation.py --input assets/sample_calendar.json
    python3 calendar_fragmentation.py --input cal.json --min-block 120 --target 0.5 --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# A block shorter than this cannot host real cognitive work: warmup alone eats 15-20 min.
MIN_VIABLE_BLOCK_MIN = 90
# Minutes of degraded output after an interruption before full re-immersion.
INTERRUPTION_RECOVERY_MIN = 23
DEFAULT_TARGET_RATIO = 0.40
DEFAULT_DAY_START = "09:00"
DEFAULT_DAY_END = "17:00"

Interval = Tuple[int, int]


def to_minutes(hhmm: str) -> int:
    """Convert an HH:MM string to minutes past midnight."""
    try:
        hours, minutes = hhmm.strip().split(":")
        total = int(hours) * 60 + int(minutes)
    except (ValueError, AttributeError):
        raise ValueError(f"bad time value {hhmm!r} — expected HH:MM")
    if not 0 <= total <= 24 * 60:
        raise ValueError(f"time out of range: {hhmm!r}")
    return total


def to_hhmm(minutes: int) -> str:
    """Convert minutes past midnight back to an HH:MM string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def load_events(path: Path) -> List[Dict[str, Any]]:
    """Load calendar events from a JSON list or an object with an 'events' key."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "events" not in data:
            raise ValueError(
                f"{path.name} is a JSON object with no 'events' key "
                f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a calendar export")
        events = data["events"]
    else:
        events = data
    if not isinstance(events, list):
        raise ValueError("calendar must be a JSON list or an object with an 'events' list")
    return events


def merge(intervals: List[Interval]) -> List[Interval]:
    """Merge overlapping or touching intervals into a minimal disjoint set."""
    if not intervals:
        return []
    merged = [intervals[0]]
    for start, end in sorted(intervals)[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def free_gaps(busy: List[Interval], window: Interval) -> List[Interval]:
    """Return the unbooked intervals inside the working window."""
    gaps: List[Interval] = []
    cursor = window[0]
    for start, end in merge(busy):
        start, end = max(start, window[0]), min(end, window[1])
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < window[1]:
        gaps.append((cursor, window[1]))
    return gaps


def score_day(busy: List[Interval], window: Interval, min_block: int) -> Dict[str, Any]:
    """Compute longest block, switch count, and deep-work ratio for one day."""
    gaps = free_gaps(busy, window)
    span = window[1] - window[0]
    deep = sum(e - s for s, e in gaps if e - s >= min_block)
    longest = max((e - s for s, e in gaps), default=0)
    meetings = len(merge(busy))
    return {
        "longest_block_min": longest,
        "deep_work_min": deep,
        "deep_work_ratio": round(deep / span, 3) if span else 0.0,
        "meeting_min": sum(min(e, window[1]) - max(s, window[0]) for s, e in merge(busy)),
        "meeting_count": meetings,
        "context_switches": meetings * 2,
        "recovery_cost_min": meetings * INTERRUPTION_RECOVERY_MIN,
        "viable_blocks": sum(1 for s, e in gaps if e - s >= min_block),
    }


def propose_move(
    events: List[Dict[str, Any]], window: Interval, min_block: int
) -> Optional[Dict[str, Any]]:
    """Find the single meeting move that most increases the longest free block."""
    movable = [e for e in events if not e.get("fixed")]
    if len(events) < 2 or not movable:
        return None
    busy = [(to_minutes(e["start"]), to_minutes(e["end"])) for e in events]
    base = max((e - s for s, e in free_gaps(busy, window)), default=0)
    best: Optional[Dict[str, Any]] = None

    for event in movable:
        start, end = to_minutes(event["start"]), to_minutes(event["end"])
        duration = end - start
        others = [(to_minutes(e["start"]), to_minutes(e["end"])) for e in events if e is not event]
        # Candidate slots: flush against the edge of any other meeting, or at either end of the day.
        candidates = {window[0], window[1] - duration}
        for other_start, other_end in others:
            candidates.add(other_end)
            candidates.add(other_start - duration)
        for slot in sorted(candidates):
            if slot < window[0] or slot + duration > window[1]:
                continue
            trial = others + [(slot, slot + duration)]
            if any(s < slot + duration and slot < e for s, e in others):
                continue
            longest = max((e - s for s, e in free_gaps(trial, window)), default=0)
            gain = longest - base
            if gain > 0 and (best is None or gain > best["gain_min"]):
                best = {
                    "move": event.get("title", "untitled"),
                    "from": f"{to_hhmm(start)}-{to_hhmm(end)}",
                    "to": f"{to_hhmm(slot)}-{to_hhmm(slot + duration)}",
                    "longest_block_before_min": base,
                    "longest_block_after_min": longest,
                    "gain_min": gain,
                    "clears_threshold": longest >= min_block,
                }
    return best


def analyse(
    events: List[Dict[str, Any]], window: Interval, min_block: int, target: float
) -> Dict[str, Any]:
    """Score every day in the export and attach a reschedule proposal where needed."""
    by_day: Dict[str, List[Dict[str, Any]]] = {}
    for event in events:
        for field in ("date", "start", "end"):
            if field not in event:
                raise KeyError(f"event missing required field {field!r}: {event}")
        by_day.setdefault(str(event["date"]), []).append(event)

    days: List[Dict[str, Any]] = []
    for date in sorted(by_day):
        day_events = by_day[date]
        busy = [(to_minutes(e["start"]), to_minutes(e["end"])) for e in day_events]
        stats = score_day(busy, window, min_block)
        stats["date"] = date
        stats["meets_target"] = stats["deep_work_ratio"] >= target
        stats["proposal"] = None if stats["meets_target"] else propose_move(day_events, window, min_block)
        days.append(stats)

    total_deep = sum(d["deep_work_min"] for d in days)
    span = (window[1] - window[0]) * len(days)
    return {
        "days_analysed": len(days),
        "min_block_min": min_block,
        "target_ratio": target,
        "overall_deep_work_ratio": round(total_deep / span, 3) if span else 0.0,
        "days_meeting_target": sum(1 for d in days if d["meets_target"]),
        "total_recovery_cost_min": sum(d["recovery_cost_min"] for d in days),
        "days": days,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the fragmentation report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Calendar fragmentation — {report['days_analysed']} days")
    print(f"Deep-work ratio {report['overall_deep_work_ratio']:.0%} vs target {report['target_ratio']:.0%}"
          f" | {report['days_meeting_target']}/{report['days_analysed']} days on target")
    print(f"Interruption recovery cost: {report['total_recovery_cost_min']} min "
          f"({report['total_recovery_cost_min'] / 60:.1f} h) across the period")
    print("-" * 68)
    print(f"{'date':<12}{'longest':>9}{'deep':>7}{'ratio':>8}{'mtgs':>6}{'switch':>8}  status")
    for day in report["days"]:
        status = "ok" if day["meets_target"] else "FRAGMENTED"
        print(f"{day['date']:<12}{day['longest_block_min']:>7} m{day['deep_work_min']:>6}"
              f"{day['deep_work_ratio']:>8.0%}{day['meeting_count']:>6}{day['context_switches']:>8}  {status}")
    print()
    for day in report["days"]:
        p = day["proposal"]
        if p:
            verdict = "clears the threshold" if p["clears_threshold"] else "still short of a viable block"
            print(f"{day['date']}: move \"{p['move']}\" {p['from']} -> {p['to']}")
            print(f"    longest block {p['longest_block_before_min']} -> {p['longest_block_after_min']} min "
                  f"(+{p['gain_min']}), {verdict}")
        elif not day["meets_target"]:
            print(f"{day['date']}: no single move helps — decline or delegate a meeting instead")


def main() -> None:
    """Parse arguments, analyse the calendar, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Analyse calendar fragmentation and propose a reschedule.",
    )
    parser.add_argument("--input", required=True, help="Path to the JSON calendar export")
    parser.add_argument("--day-start", default=DEFAULT_DAY_START, help=f"Working-window start HH:MM (default: {DEFAULT_DAY_START})")
    parser.add_argument("--day-end", default=DEFAULT_DAY_END, help=f"Working-window end HH:MM (default: {DEFAULT_DAY_END})")
    parser.add_argument("--min-block", type=int, default=MIN_VIABLE_BLOCK_MIN, help=f"Minutes for a viable deep-work block (default: {MIN_VIABLE_BLOCK_MIN})")
    parser.add_argument("--target", type=float, default=DEFAULT_TARGET_RATIO, help=f"Target deep-work ratio 0-1 (default: {DEFAULT_TARGET_RATIO})")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"calendar export not found: {path}")
        if not 0 < args.target <= 1:
            raise ValueError("--target must be between 0 and 1")
        window = (to_minutes(args.day_start), to_minutes(args.day_end))
        if window[1] <= window[0]:
            raise ValueError("--day-end must be after --day-start")
        output(analyse(load_events(path), window, args.min_block, args.target), args.format)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
