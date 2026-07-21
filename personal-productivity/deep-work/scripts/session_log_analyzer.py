#!/usr/bin/env python3
"""Analyse a deep-work session log for volume, quality, and trend.

Reads logged focus sessions and reports weekly deep-work volume, session-length
distribution, interruption rate, plan-vs-actual drift, single-artefact
adherence, and whether the practice is improving or decaying. Deterministic: no
clock reads, no network, no randomness.

Usage:
    python3 session_log_analyzer.py --input assets/sample_sessions.json
    python3 session_log_analyzer.py --input sessions.json --weekly-target 600 --format json
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

MIN_VIABLE_BLOCK_MIN = 90
# Above roughly 4 hours a day, session quality collapses for most people.
DAILY_CEILING_MIN = 240
DEFAULT_WEEKLY_TARGET_MIN = 600
# More than one interruption per hour means the block was never really protected.
INTERRUPTION_RATE_CEILING = 1.0


def load_sessions(path: Path) -> List[Dict[str, Any]]:
    """Load session records from a JSON list or an object with a 'sessions' key."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "sessions" not in data:
            raise ValueError(
                f"{path.name} is a JSON object with no 'sessions' key "
                f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a session log")
        sessions = data["sessions"]
    else:
        sessions = data
    if not isinstance(sessions, list):
        raise ValueError("session log must be a JSON list or an object with a 'sessions' list")
    if not sessions:
        raise ValueError("session log is empty — nothing to analyse")
    return sessions


def iso_week(date_str: str) -> str:
    """Return the ISO year-week label for a YYYY-MM-DD date."""
    try:
        parsed = datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"bad date {date_str!r} — expected YYYY-MM-DD")
    year, week, _ = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def normalise(session: Dict[str, Any]) -> Dict[str, Any]:
    """Validate one session record and fill in derived fields."""
    for field in ("date", "actual_min"):
        if field not in session:
            raise KeyError(f"session missing required field {field!r}: {session}")
    actual = int(session["actual_min"])
    if actual < 0:
        raise ValueError(f"actual_min cannot be negative: {session}")
    planned = int(session.get("planned_min", actual))
    interruptions = int(session.get("interruptions", 0))
    return {
        "date": str(session["date"])[:10],
        "week": iso_week(session["date"]),
        "planned_min": planned,
        "actual_min": actual,
        "interruptions": interruptions,
        "artefacts": session.get("artefacts", [session["artefact"]] if session.get("artefact") else []),
        "focus_rating": session.get("focus_rating"),
        "viable": actual >= MIN_VIABLE_BLOCK_MIN,
        "completion": round(actual / planned, 2) if planned else 1.0,
        "interruptions_per_hour": round(interruptions / (actual / 60), 2) if actual >= 15 else None,
    }


def weekly_rollup(sessions: List[Dict[str, Any]], target: int) -> List[Dict[str, Any]]:
    """Aggregate sessions into weekly totals against the volume target."""
    weeks: Dict[str, List[Dict[str, Any]]] = {}
    for session in sessions:
        weeks.setdefault(session["week"], []).append(session)
    rollup: List[Dict[str, Any]] = []
    for week in sorted(weeks):
        group = weeks[week]
        total = sum(s["actual_min"] for s in group)
        rollup.append({
            "week": week,
            "sessions": len(group),
            "total_min": total,
            "viable_sessions": sum(1 for s in group if s["viable"]),
            "median_session_min": int(statistics.median(s["actual_min"] for s in group)),
            "interruptions": sum(s["interruptions"] for s in group),
            "pct_of_target": round(total / target, 2) if target else 0.0,
            "days_active": len({s["date"] for s in group}),
        })
    return rollup


def trend(weeks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare the first and second half of the period to detect drift."""
    if len(weeks) < 2:
        return {"direction": "insufficient-data", "change_pct": None,
                "note": "Need at least 2 weeks of sessions to detect a trend."}
    midpoint = len(weeks) // 2
    early = statistics.mean(w["total_min"] for w in weeks[:midpoint])
    late = statistics.mean(w["total_min"] for w in weeks[midpoint:])
    change = (late - early) / early if early else 0.0
    if change > 0.10:
        direction, note = "improving", "Weekly volume is rising; hold the current defence tactics."
    elif change < -0.10:
        direction, note = "decaying", "Volume is falling — check what started encroaching on the blocks."
    else:
        direction, note = "stable", "Volume is holding steady week to week."
    return {"direction": direction, "change_pct": round(change, 3),
            "early_mean_min": round(early), "late_mean_min": round(late), "note": note}


def diagnose(sessions: List[Dict[str, Any]], weeks: List[Dict[str, Any]], target: int) -> List[str]:
    """Name the specific practice failures visible in the log."""
    findings: List[str] = []
    total = len(sessions)
    short = sum(1 for s in sessions if not s["viable"])
    if short / total > 0.4:
        findings.append(
            f"{short}/{total} sessions are under {MIN_VIABLE_BLOCK_MIN} min — "
            "warmup eats most of a short block; consolidate rather than adding sessions.")

    rates = [s["interruptions_per_hour"] for s in sessions if s["interruptions_per_hour"] is not None]
    if rates and statistics.mean(rates) > INTERRUPTION_RATE_CEILING:
        findings.append(
            f"Mean {statistics.mean(rates):.1f} interruptions/hour exceeds {INTERRUPTION_RATE_CEILING} — "
            "the blocks are scheduled but not defended.")

    drift = [s["completion"] for s in sessions if s["completion"] < 1.0]
    if len(drift) / total > 0.5:
        findings.append(
            f"{len(drift)}/{total} sessions ran short of plan — either the plan is optimistic "
            "or blocks are being cut into by adjacent commitments.")

    multi = sum(1 for s in sessions if len(s["artefacts"]) > 1)
    if multi / total > 0.3:
        findings.append(
            f"{multi}/{total} sessions touched more than one artefact — the single-artefact rule "
            "is the cheapest quality lever available; each extra artefact re-pays warmup.")

    over = [w for w in weeks if w["total_min"] / max(w["days_active"], 1) > DAILY_CEILING_MIN]
    if over:
        findings.append(
            f"{len(over)} week(s) averaged over {DAILY_CEILING_MIN} min/day of deep work — "
            "sustainable for a sprint, not a quarter; expect quality decay.")

    below = [w for w in weeks if w["pct_of_target"] < 0.7]
    if below:
        findings.append(
            f"{len(below)}/{len(weeks)} weeks fell below 70% of the {target}-min target.")
    if not findings:
        findings.append("No structural failures detected — volume, block length, and defence all hold.")
    return findings


def analyse(raw: List[Dict[str, Any]], target: int) -> Dict[str, Any]:
    """Produce the full session-log report."""
    sessions = [normalise(s) for s in raw]
    weeks = weekly_rollup(sessions, target)
    total = sum(s["actual_min"] for s in sessions)
    return {
        "sessions": len(sessions),
        "weeks": len(weeks),
        "total_min": total,
        "mean_session_min": round(statistics.mean(s["actual_min"] for s in sessions)),
        "median_session_min": int(statistics.median(s["actual_min"] for s in sessions)),
        "viable_share": round(sum(1 for s in sessions if s["viable"]) / len(sessions), 2),
        "weekly_target_min": target,
        "weekly": weeks,
        "trend": trend(weeks),
        "findings": diagnose(sessions, weeks, target),
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the session report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Deep-work sessions — {report['sessions']} sessions over {report['weeks']} weeks")
    print(f"Total {report['total_min']} min ({report['total_min'] / 60:.1f} h) | "
          f"median session {report['median_session_min']} min | "
          f"{report['viable_share']:.0%} at or above {MIN_VIABLE_BLOCK_MIN} min")
    print("-" * 66)
    print(f"{'week':<12}{'sess':>6}{'total':>8}{'median':>8}{'intr':>6}{'vs target':>11}")
    for week in report["weekly"]:
        print(f"{week['week']:<12}{week['sessions']:>6}{week['total_min']:>7}m"
              f"{week['median_session_min']:>7}m{week['interruptions']:>6}{week['pct_of_target']:>10.0%}")
    tr = report["trend"]
    change = f"{tr['change_pct']:+.0%}" if tr["change_pct"] is not None else "n/a"
    print(f"\nTrend: {tr['direction'].upper()} ({change}) — {tr['note']}")
    print("\nFindings:")
    for finding in report["findings"]:
        print(f"  - {finding}")


def main() -> None:
    """Parse arguments, analyse the session log, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Analyse a deep-work session log for volume, quality, and trend.",
    )
    parser.add_argument("--input", required=True, help="Path to the JSON session log")
    parser.add_argument("--weekly-target", type=int, default=DEFAULT_WEEKLY_TARGET_MIN, help=f"Weekly deep-work target in minutes (default: {DEFAULT_WEEKLY_TARGET_MIN})")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"session log not found: {path}")
        if args.weekly_target <= 0:
            raise ValueError("--weekly-target must be positive")
        output(analyse(load_sessions(path), args.weekly_target), args.format)
    except (OSError, ValueError, KeyError, TypeError, statistics.StatisticsError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
