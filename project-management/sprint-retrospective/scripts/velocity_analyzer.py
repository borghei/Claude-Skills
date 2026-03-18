#!/usr/bin/env python3
"""
Sprint Velocity Analyzer

Analyzes git history to compute sprint velocity metrics including throughput,
cycle time, session detection, commit type breakdown, and hourly distribution.
Supports multiple time windows and trend comparison against previous periods.

Usage:
    python velocity_analyzer.py --days 14
    python velocity_analyzer.py --since 2026-03-04 --until 2026-03-18
    python velocity_analyzer.py --days 14 --compare-previous --format json

Standard library only. Uses subprocess for git commands.
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


# --- Git Data Collection ---

def run_git(args: list[str], repo: str = ".") -> str:
    """Run a git command and return stdout."""
    cmd = ["git", "-C", repo] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_commits(since: str, until: str, repo: str = ".") -> list[dict]:
    """Retrieve commits within a date range."""
    fmt = "%H|%ae|%aI|%s"
    log = run_git([
        "log", "--all", f"--since={since}", f"--until={until}",
        f"--pretty=format:{fmt}", "--no-merges"
    ], repo)
    if not log:
        return []
    commits = []
    for line in log.split("\n"):
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commits.append({
            "hash": parts[0],
            "author": parts[1],
            "date": parts[2],
            "subject": parts[3],
        })
    return commits


def get_merge_commits(since: str, until: str, repo: str = ".") -> list[dict]:
    """Retrieve merge commits (proxy for PRs merged)."""
    fmt = "%H|%ae|%aI|%s"
    log = run_git([
        "log", "--all", f"--since={since}", f"--until={until}",
        f"--pretty=format:{fmt}", "--merges"
    ], repo)
    if not log:
        return []
    merges = []
    for line in log.split("\n"):
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        merges.append({
            "hash": parts[0],
            "author": parts[1],
            "date": parts[2],
            "subject": parts[3],
        })
    return merges


def get_loc_stats(since: str, until: str, repo: str = ".") -> dict:
    """Get lines of code added/removed in the period."""
    log = run_git([
        "log", "--all", f"--since={since}", f"--until={until}",
        "--pretty=format:", "--numstat", "--no-merges"
    ], repo)
    added = 0
    removed = 0
    if not log:
        return {"added": 0, "removed": 0, "net": 0}
    for line in log.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            a = int(parts[0])
            r = int(parts[1])
            added += a
            removed += r
        except ValueError:
            continue  # binary files show '-'
    return {"added": added, "removed": removed, "net": added - removed}


def get_pr_loc_stats(merges: list[dict], repo: str = ".") -> list[int]:
    """Get LOC per merge commit (PR size proxy)."""
    sizes = []
    for m in merges:
        stat = run_git(["diff", "--shortstat", f"{m['hash']}^..{m['hash']}"], repo)
        if not stat:
            continue
        total = 0
        for part in stat.split(","):
            part = part.strip()
            if "insertion" in part:
                try:
                    total += int(part.split()[0])
                except ValueError:
                    pass
            elif "deletion" in part:
                try:
                    total += int(part.split()[0])
                except ValueError:
                    pass
        if total > 0:
            sizes.append(total)
    return sizes


# --- Parsing & Classification ---

def parse_datetime(iso_str: str) -> datetime:
    """Parse ISO 8601 datetime string robustly.

    Handles formats: 2026-03-18T12:00:00+05:30, 2026-03-18T12:00:00+0530,
    2026-03-18T12:00:00Z, 2026-03-18T12:00:00
    """
    clean = iso_str.strip()
    # Handle 'Z' suffix (UTC)
    if clean.endswith("Z"):
        clean = clean[:-1] + "+0000"
    # Remove colon in timezone offset for Python < 3.11 compat
    # Match patterns like +05:30 or -05:30 at end of string
    tz_match = re.search(r'([+-]\d{2}):(\d{2})$', clean)
    if tz_match:
        clean = clean[:tz_match.start()] + tz_match.group(1) + tz_match.group(2)
    try:
        return datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass
    # Try without timezone
    try:
        return datetime.strptime(clean[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    # Last resort: try common date-only format
    try:
        return datetime.strptime(clean[:10], "%Y-%m-%d")
    except ValueError:
        return datetime.now()


def classify_commit_type(subject: str) -> str:
    """Classify commit by conventional commit type."""
    s = subject.lower().strip()
    prefixes = [
        ("feat", "feat"), ("fix", "fix"), ("docs", "docs"),
        ("refactor", "refactor"), ("test", "test"), ("chore", "chore"),
        ("style", "style"), ("perf", "perf"), ("ci", "ci"),
        ("build", "build"), ("revert", "revert"),
    ]
    for prefix, label in prefixes:
        if s.startswith(prefix + ":") or s.startswith(prefix + "("):
            return label
    return "other"


# --- Session Detection ---

def detect_sessions(commits: list[dict], gap_minutes: int = 45) -> dict:
    """Detect work sessions per author using gap threshold."""
    by_author = defaultdict(list)
    for c in commits:
        dt = parse_datetime(c["date"])
        by_author[c["author"]].append(dt)

    sessions = {"deep_work": 0, "focused": 0, "micro": 0}
    all_sessions = []
    gap = timedelta(minutes=gap_minutes)

    for author, times in by_author.items():
        times.sort()
        if not times:
            continue
        session_start = times[0]
        session_end = times[0]

        for i in range(1, len(times)):
            if times[i] - session_end > gap:
                # Close previous session
                duration = (session_end - session_start).total_seconds() / 60
                all_sessions.append({
                    "author": author,
                    "start": session_start,
                    "end": session_end,
                    "duration_min": duration,
                })
                session_start = times[i]
                session_end = times[i]
            else:
                session_end = times[i]

        # Close final session
        duration = (session_end - session_start).total_seconds() / 60
        all_sessions.append({
            "author": author,
            "start": session_start,
            "end": session_end,
            "duration_min": duration,
        })

    for s in all_sessions:
        d = s["duration_min"]
        if d > 50:
            sessions["deep_work"] += 1
        elif d >= 20:
            sessions["focused"] += 1
        else:
            sessions["micro"] += 1

    return {
        "deep_work": sessions["deep_work"],
        "focused": sessions["focused"],
        "micro": sessions["micro"],
        "total": len(all_sessions),
        "details": [
            {
                "author": s["author"],
                "start": s["start"].isoformat(),
                "end": s["end"].isoformat(),
                "duration_min": round(s["duration_min"], 1),
                "type": "deep_work" if s["duration_min"] > 50 else ("focused" if s["duration_min"] >= 20 else "micro"),
            }
            for s in all_sessions
        ],
    }


# --- Hourly Distribution ---

def hourly_distribution(commits: list[dict]) -> dict[int, int]:
    """Count commits by hour of day."""
    hours = defaultdict(int)
    for c in commits:
        dt = parse_datetime(c["date"])
        hours[dt.hour] += 1
    return dict(sorted(hours.items()))


# --- Cycle Time Estimation ---

def estimate_cycle_time(merges: list[dict], commits: list[dict], repo: str = ".") -> float:
    """Estimate average cycle time (hours) from branch commits to merge."""
    if not merges:
        return 0.0
    cycle_times = []
    commit_dates = {c["hash"]: parse_datetime(c["date"]) for c in commits}

    for m in merges:
        merge_dt = parse_datetime(m["date"])
        # Get commits in the merge
        parents = run_git(["log", "--pretty=format:%H|%aI", f"{m['hash']}^..{m['hash']}", "--no-merges"], repo)
        if not parents:
            continue
        earliest = merge_dt
        for line in parents.split("\n"):
            parts = line.split("|", 1)
            if len(parts) < 2:
                continue
            cdt = parse_datetime(parts[1])
            if cdt < earliest:
                earliest = cdt
        if earliest < merge_dt:
            hours = (merge_dt - earliest).total_seconds() / 3600
            if hours > 0:
                cycle_times.append(hours)

    if not cycle_times:
        return 0.0
    return sum(cycle_times) / len(cycle_times)


# --- Main Analysis ---

def analyze_period(since: str, until: str, repo: str, gap_minutes: int) -> dict:
    """Run full velocity analysis for a time period."""
    commits = get_commits(since, until, repo)
    merges = get_merge_commits(since, until, repo)
    loc = get_loc_stats(since, until, repo)
    pr_sizes = get_pr_loc_stats(merges, repo)

    # Parse date range for day count
    try:
        d_since = datetime.strptime(since, "%Y-%m-%d")
        d_until = datetime.strptime(until, "%Y-%m-%d")
        days = max((d_until - d_since).days, 1)
    except ValueError:
        days = 7

    # Commit type breakdown
    type_counts = defaultdict(int)
    for c in commits:
        t = classify_commit_type(c["subject"])
        type_counts[t] += 1

    # Sessions
    sessions = detect_sessions(commits, gap_minutes)

    # Hourly
    hourly = hourly_distribution(commits)

    # Cycle time
    cycle_time = estimate_cycle_time(merges, commits, repo)

    # PR metrics
    avg_pr_size = int(round(sum(pr_sizes) / len(pr_sizes))) if pr_sizes else 0
    throughput = round(len(commits) / days, 1) if days > 0 else 0
    deploy_freq = round(len(merges) / days, 1) if days > 0 else 0

    # Unique authors
    authors = list(set(c["author"] for c in commits))

    return {
        "period": {"since": since, "until": until, "days": days},
        "total_commits": len(commits),
        "total_merges": len(merges),
        "loc": loc,
        "avg_pr_size_loc": int(avg_pr_size),
        "throughput_per_day": throughput,
        "cycle_time_hours": round(cycle_time, 1),
        "deploy_frequency_per_day": deploy_freq,
        "commit_types": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
        "hourly_distribution": hourly,
        "sessions": {
            "deep_work": sessions["deep_work"],
            "focused": sessions["focused"],
            "micro": sessions["micro"],
            "total": sessions["total"],
        },
        "unique_authors": authors,
        "author_count": len(authors),
    }


# --- Comparison ---

def compute_delta(current: float, previous: float) -> str:
    """Compute percentage delta with direction indicator."""
    if previous == 0:
        return "N/A"
    pct = ((current - previous) / previous) * 100
    arrow = "+" if pct >= 0 else ""
    return f"{arrow}{pct:.0f}%"


def compare_periods(current: dict, previous: dict) -> dict:
    """Compare two period analyses and produce deltas."""
    deltas = {}
    compare_keys = [
        ("total_commits", "Commits"),
        ("total_merges", "PRs Merged"),
        ("throughput_per_day", "Throughput"),
        ("cycle_time_hours", "Cycle Time"),
        ("deploy_frequency_per_day", "Deploy Frequency"),
        ("avg_pr_size_loc", "Avg PR Size"),
    ]
    for key, label in compare_keys:
        cur = current.get(key, 0)
        prev = previous.get(key, 0)
        deltas[label] = {
            "current": cur,
            "previous": prev,
            "delta": compute_delta(cur, prev),
        }
    # LOC comparison
    deltas["LOC Net"] = {
        "current": current.get("loc", {}).get("net", 0),
        "previous": previous.get("loc", {}).get("net", 0),
        "delta": compute_delta(
            current.get("loc", {}).get("net", 0),
            previous.get("loc", {}).get("net", 0)
        ),
    }
    return deltas


# --- Text Formatting ---

def bar_chart(value: int, max_value: int, width: int = 20) -> str:
    """Create a simple text bar chart."""
    if max_value == 0:
        return " " * width
    filled = round((value / max_value) * width)
    filled = min(filled, width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def format_text(data: dict, comparison: dict | None = None) -> str:
    """Format velocity data as human-readable text."""
    p = data["period"]
    lines = [
        f"Sprint Velocity Report ({p['since']} to {p['until']})",
        "=" * 55,
        "",
    ]

    # Summary metrics
    if comparison:
        lines.append(f"{'Metric':<25} {'Current':>10} {'Previous':>10} {'Delta':>10}")
        lines.append("-" * 55)
        for label, vals in comparison.items():
            cur = vals["current"]
            prev = vals["previous"]
            delta = vals["delta"]
            lines.append(f"{label:<25} {str(cur):>10} {str(prev):>10} {delta:>10}")
    else:
        lines.append(f"  Throughput:       {data['throughput_per_day']} commits/day")
        lines.append(f"  LOC Net:          {data['loc']['net']:+,} lines (added: {data['loc']['added']:,}, removed: {data['loc']['removed']:,})")
        lines.append(f"  PRs Merged:       {data['total_merges']}")
        lines.append(f"  Avg PR Size:      {data['avg_pr_size_loc']} LOC")
        lines.append(f"  Cycle Time:       {data['cycle_time_hours']} hours")
        lines.append(f"  Deploy Frequency: {data['deploy_frequency_per_day']}/day")
        lines.append(f"  Unique Authors:   {data['author_count']}")

    # Commit types
    lines.extend(["", "Commit Types:", "-" * 40])
    ct = data.get("commit_types", {})
    max_ct = max(ct.values()) if ct else 1
    total_ct = sum(ct.values()) if ct else 1
    for ctype, count in sorted(ct.items(), key=lambda x: -x[1]):
        pct = round(count / total_ct * 100) if total_ct else 0
        lines.append(f"  {ctype:<12} {bar_chart(count, max_ct)}  {pct:>3}%  ({count})")

    # Hourly distribution
    lines.extend(["", "Hourly Activity:", "-" * 40])
    hourly = data.get("hourly_distribution", {})
    max_h = max(hourly.values()) if hourly else 1
    for hour in range(24):
        count = hourly.get(hour, 0)
        if count > 0:
            lines.append(f"  {hour:02d}:00  {bar_chart(count, max_h, 30)}  {count}")

    # Sessions
    s = data.get("sessions", {})
    total_s = s.get("total", 0) or 1
    lines.extend(["", "Work Sessions:", "-" * 40])
    lines.append(f"  Deep Work (>50min): {s.get('deep_work', 0):>4}  ({round(s.get('deep_work', 0)/total_s*100)}%)")
    lines.append(f"  Focused (20-50min): {s.get('focused', 0):>4}  ({round(s.get('focused', 0)/total_s*100)}%)")
    lines.append(f"  Micro (<20min):     {s.get('micro', 0):>4}  ({round(s.get('micro', 0)/total_s*100)}%)")
    lines.append(f"  Total Sessions:     {s.get('total', 0):>4}")

    return "\n".join(lines)


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sprint Velocity Analyzer — analyze git history for velocity metrics"
    )
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--since", type=str, default=None,
                        help="Start date (YYYY-MM-DD), overrides --days")
    parser.add_argument("--until", type=str, default=None,
                        help="End date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--compare-previous", action="store_true",
                        help="Compare against the previous period of equal length")
    parser.add_argument("--gap-minutes", type=int, default=45,
                        help="Session gap threshold in minutes (default: 45)")
    parser.add_argument("--repo", type=str, default=".",
                        help="Path to git repository (default: current directory)")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine date range
    if args.until:
        until_date = args.until
    else:
        until_date = datetime.now().strftime("%Y-%m-%d")

    if args.since:
        since_date = args.since
        try:
            d_since = datetime.strptime(since_date, "%Y-%m-%d")
            d_until = datetime.strptime(until_date, "%Y-%m-%d")
            days = (d_until - d_since).days
        except ValueError:
            days = args.days
    else:
        days = args.days
        d_until = datetime.strptime(until_date, "%Y-%m-%d")
        d_since = d_until - timedelta(days=days)
        since_date = d_since.strftime("%Y-%m-%d")

    # Validate repo
    check = run_git(["rev-parse", "--is-inside-work-tree"], args.repo)
    if check != "true":
        print(f"Error: '{args.repo}' is not a git repository.", file=sys.stderr)
        sys.exit(1)

    # Analyze current period
    current = analyze_period(since_date, until_date, args.repo, args.gap_minutes)

    # Optionally analyze previous period
    comparison = None
    previous = None
    if args.compare_previous:
        prev_until = since_date
        prev_since = (d_since - timedelta(days=days)).strftime("%Y-%m-%d")
        previous = analyze_period(prev_since, prev_until, args.repo, args.gap_minutes)
        comparison = compare_periods(current, previous)

    # Output
    if args.format == "json":
        output = {"current": current}
        if comparison:
            output["previous"] = previous
            output["comparison"] = comparison
        print(json.dumps(output, indent=2, default=str))
    else:
        print(format_text(current, comparison))


if __name__ == "__main__":
    main()
