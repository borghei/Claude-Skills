#!/usr/bin/env python3
"""
Code Churn Analyzer

Identifies file hotspots, calculates churn rates, detects code oscillation,
maps churn to directories/modules, and flags potential refactoring candidates.

Usage:
    python code_churn_analyzer.py --days 14
    python code_churn_analyzer.py --days 14 --top 20 --detect-oscillation
    python code_churn_analyzer.py --days 14 --path src/ --format json

Standard library only.
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


# --- Git Helpers ---

def run_git(args: list[str], repo: str = ".") -> str:
    cmd = ["git", "-C", repo] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def parse_datetime(iso_str: str) -> datetime:
    clean = iso_str.strip()
    if len(clean) > 19 and (clean[-3] == ":" and (clean[-6] == "+" or clean[-6] == "-")):
        clean = clean[:-3] + clean[-2:]
    try:
        return datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        try:
            return datetime.strptime(clean[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return datetime.now()


# --- Data Collection ---

def get_file_changes(since: str, until: str, repo: str = ".",
                     path_filter: str | None = None) -> list[dict]:
    """Get per-commit file-level change data."""
    log = run_git([
        "log", "--all", f"--since={since}", f"--until={until}",
        "--pretty=format:COMMIT|%H|%ae|%aI|%s", "--numstat", "--no-merges"
    ], repo)
    if not log:
        return []

    commits = []
    current = None

    for line in log.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("COMMIT|"):
            if current:
                commits.append(current)
            parts = line.split("|", 4)
            if len(parts) < 5:
                current = None
                continue
            current = {
                "hash": parts[1],
                "author": parts[2],
                "date": parts[3],
                "subject": parts[4],
                "files": [],
            }
        elif current and "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 3:
                filepath = parts[2]
                if path_filter and not filepath.startswith(path_filter):
                    continue
                try:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    removed = int(parts[1]) if parts[1] != "-" else 0
                except ValueError:
                    added = 0
                    removed = 0
                current["files"].append({
                    "path": filepath,
                    "added": added,
                    "removed": removed,
                })

    if current:
        commits.append(current)

    return commits


# --- Hotspot Analysis ---

def compute_hotspots(commits: list[dict], total_days: int, top_n: int = 15) -> list[dict]:
    """Compute file hotspots ranked by composite churn score."""
    file_data = defaultdict(lambda: {
        "changes": 0,
        "authors": set(),
        "total_added": 0,
        "total_removed": 0,
        "last_changed": None,
        "commit_dates": [],
    })

    for c in commits:
        commit_dt = parse_datetime(c["date"])
        for f in c.get("files", []):
            path = f["path"]
            fd = file_data[path]
            fd["changes"] += 1
            fd["authors"].add(c["author"])
            fd["total_added"] += f["added"]
            fd["total_removed"] += f["removed"]
            fd["commit_dates"].append(commit_dt)
            if fd["last_changed"] is None or commit_dt > fd["last_changed"]:
                fd["last_changed"] = commit_dt

    # Compute recency weight (more recent = higher weight)
    now = datetime.now()
    hotspots = []
    for path, fd in file_data.items():
        author_count = len(fd["authors"])
        changes = fd["changes"]

        # Recency: days since last change, mapped to 0-1
        if fd["last_changed"]:
            try:
                last = fd["last_changed"].replace(tzinfo=None)
                days_ago = (now - last).days
            except (TypeError, AttributeError):
                days_ago = total_days
        else:
            days_ago = total_days
        recency = max(0, 1 - (days_ago / max(total_days, 1)))

        # Composite score
        churn_score = round(changes * (1 + 0.3 * (author_count - 1)) * (0.5 + 0.5 * recency), 1)
        churn_rate = round(changes / max(total_days, 1), 2)

        hotspots.append({
            "file": path,
            "changes": changes,
            "authors": sorted(fd["authors"]),
            "author_count": author_count,
            "loc_added": fd["total_added"],
            "loc_removed": fd["total_removed"],
            "loc_churn": fd["total_added"] + fd["total_removed"],
            "churn_rate": churn_rate,
            "churn_score": churn_score,
        })

    hotspots.sort(key=lambda x: -x["churn_score"])
    return hotspots[:top_n]


# --- Directory Churn ---

def compute_directory_churn(commits: list[dict]) -> list[dict]:
    """Aggregate churn by top-level directory."""
    dir_data = defaultdict(lambda: {
        "changes": 0, "files": set(), "authors": set(),
        "loc_added": 0, "loc_removed": 0,
    })

    for c in commits:
        for f in c.get("files", []):
            path = f["path"]
            parts = path.split("/")
            directory = parts[0] if len(parts) > 1 else "."
            dd = dir_data[directory]
            dd["changes"] += 1
            dd["files"].add(path)
            dd["authors"].add(c["author"])
            dd["loc_added"] += f["added"]
            dd["loc_removed"] += f["removed"]

    result = []
    for directory, dd in dir_data.items():
        result.append({
            "directory": directory,
            "changes": dd["changes"],
            "unique_files": len(dd["files"]),
            "authors": sorted(dd["authors"]),
            "author_count": len(dd["authors"]),
            "loc_added": dd["loc_added"],
            "loc_removed": dd["loc_removed"],
        })

    result.sort(key=lambda x: -x["changes"])
    return result


# --- Oscillation Detection ---

def detect_oscillation(commits: list[dict], threshold: int = 3) -> list[dict]:
    """Detect files with add-remove oscillation patterns.

    Looks for files where lines are added then removed (or vice versa) in
    alternating commits, indicating unclear requirements or design churn.
    """
    # Track per-file add/remove patterns in chronological order
    file_patterns = defaultdict(list)

    # Sort commits by date
    sorted_commits = sorted(commits, key=lambda c: c["date"])

    for c in sorted_commits:
        for f in c.get("files", []):
            path = f["path"]
            added = f["added"]
            removed = f["removed"]
            if added > removed:
                file_patterns[path].append("add")
            elif removed > added:
                file_patterns[path].append("remove")
            else:
                file_patterns[path].append("neutral")

    oscillating = []
    for path, patterns in file_patterns.items():
        if len(patterns) < threshold:
            continue

        # Count direction changes
        changes = 0
        for i in range(1, len(patterns)):
            if patterns[i] != patterns[i - 1] and patterns[i] != "neutral" and patterns[i - 1] != "neutral":
                changes += 1

        if changes >= threshold - 1:
            oscillating.append({
                "file": path,
                "total_changes": len(patterns),
                "direction_changes": changes,
                "pattern": patterns,
                "oscillation_ratio": round(changes / max(len(patterns) - 1, 1), 2),
            })

    oscillating.sort(key=lambda x: -x["direction_changes"])
    return oscillating


# --- Code Health Indicators ---

def classify_commit_type(subject: str) -> str:
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


def is_test_file(path: str) -> bool:
    p = path.lower()
    test_indicators = ["test_", "_test.", ".test.", ".spec.", "_spec.", "__tests__/", "/test/", "/tests/", "/spec/"]
    return any(ind in p for ind in test_indicators)


def compute_health_indicators(commits: list[dict], hotspots: list[dict],
                              total_days: int) -> dict:
    """Compute aggregate code health indicators."""
    total_commits = len(commits)

    # Commit type counts
    type_counts = defaultdict(int)
    for c in commits:
        t = classify_commit_type(c["subject"])
        type_counts[t] += 1

    # Refactor frequency
    refactor_freq = round(type_counts.get("refactor", 0) / max(total_commits, 1), 2)

    # Test-to-production ratio
    test_changes = 0
    prod_changes = 0
    all_files = set()

    for c in commits:
        for f in c.get("files", []):
            all_files.add(f["path"])
            total_loc = f["added"] + f["removed"]
            if is_test_file(f["path"]):
                test_changes += total_loc
            else:
                prod_changes += total_loc

    test_ratio = round(test_changes / max(prod_changes, 1), 2)

    # Hotspot concentration
    total_file_changes = sum(1 for c in commits for _ in c.get("files", []))
    if hotspots and total_file_changes > 0:
        top_10_pct_count = max(1, len(all_files) // 10)
        top_changes = sum(h["changes"] for h in hotspots[:top_10_pct_count])
        hotspot_concentration = round(top_changes / total_file_changes, 2)
    else:
        hotspot_concentration = 0.0

    # Overall churn rate
    churn_rate = round(total_file_changes / max(total_days, 1) / max(len(all_files), 1), 2)

    return {
        "churn_rate": churn_rate,
        "hotspot_concentration": hotspot_concentration,
        "test_to_prod_ratio": test_ratio,
        "refactor_frequency": refactor_freq,
        "total_files_changed": len(all_files),
        "total_commits": total_commits,
        "commit_type_distribution": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
    }


# --- Refactoring Candidates ---

def identify_refactoring_candidates(hotspots: list[dict], health: dict) -> list[dict]:
    """Identify files that are strong candidates for refactoring."""
    candidates = []
    for h in hotspots:
        reasons = []

        if h["churn_rate"] > 0.5:
            reasons.append(f"high churn rate ({h['churn_rate']}/day)")
        if h["author_count"] >= 3:
            reasons.append(f"touched by {h['author_count']} authors (coordination overhead)")
        if h["loc_churn"] > 500:
            reasons.append(f"high LOC churn ({h['loc_churn']} lines)")
        if h["changes"] >= 8:
            reasons.append(f"changed {h['changes']} times (instability)")

        if len(reasons) >= 2:
            candidates.append({
                "file": h["file"],
                "churn_score": h["churn_score"],
                "reasons": reasons,
                "recommendation": "Consider splitting, refactoring, or stabilizing this file.",
            })

    return candidates


# --- Main Analysis ---

def analyze_churn(since: str, until: str, repo: str,
                  path_filter: str | None = None,
                  top_n: int = 15,
                  oscillation: bool = False) -> dict:
    """Run full churn analysis."""
    commits = get_file_changes(since, until, repo, path_filter)

    try:
        d_since = datetime.strptime(since, "%Y-%m-%d")
        d_until = datetime.strptime(until, "%Y-%m-%d")
        total_days = max((d_until - d_since).days, 1)
    except ValueError:
        total_days = 7

    hotspots = compute_hotspots(commits, total_days, top_n)
    dir_churn = compute_directory_churn(commits)
    health = compute_health_indicators(commits, hotspots, total_days)
    candidates = identify_refactoring_candidates(hotspots, health)

    result = {
        "period": {"since": since, "until": until, "days": total_days},
        "hotspots": hotspots,
        "directory_churn": dir_churn,
        "health_indicators": health,
        "refactoring_candidates": candidates,
    }

    if oscillation:
        osc = detect_oscillation(commits)
        result["oscillation"] = osc
        # Add oscillation score to health
        total_files = health["total_files_changed"]
        osc_pct = round(len(osc) / max(total_files, 1) * 100, 1)
        result["health_indicators"]["oscillation_pct"] = osc_pct

    return result


# --- Text Formatting ---

def bar_chart(value: float, max_value: float, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = min(round((value / max_value) * width), width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def status_indicator(value: float, good_max: float, warn_max: float) -> str:
    if value <= good_max:
        return "OK"
    elif value <= warn_max:
        return "WARN"
    else:
        return "HIGH"


def format_text(data: dict) -> str:
    p = data["period"]
    lines = [
        f"Code Churn Analysis ({p['since']} to {p['until']})",
        "=" * 65,
        "",
    ]

    # Health indicators
    h = data["health_indicators"]
    lines.append("Health Indicators")
    lines.append("-" * 40)
    lines.append(f"  Churn Rate:            {h['churn_rate']:<8} [{status_indicator(h['churn_rate'], 0.3, 0.5)}]")
    lines.append(f"  Hotspot Concentration: {h['hotspot_concentration']:<8} [{status_indicator(h['hotspot_concentration'], 0.3, 0.5)}]")
    lines.append(f"  Test-to-Prod Ratio:    {h['test_to_prod_ratio']:<8} [{'OK' if h['test_to_prod_ratio'] >= 0.3 else 'LOW'}]")
    lines.append(f"  Refactor Frequency:    {h['refactor_frequency']:<8} [{'OK' if 0.08 <= h['refactor_frequency'] <= 0.3 else 'CHECK'}]")
    if "oscillation_pct" in h:
        lines.append(f"  Oscillation:           {h['oscillation_pct']}%    [{status_indicator(h['oscillation_pct'], 3, 8)}]")
    lines.append(f"  Total Files Changed:   {h['total_files_changed']}")
    lines.append(f"  Total Commits:         {h['total_commits']}")
    lines.append("")

    # Hotspots
    hotspots = data["hotspots"]
    if hotspots:
        max_score = hotspots[0]["churn_score"] if hotspots else 1
        lines.append("File Hotspots (ranked by churn score)")
        lines.append("-" * 65)
        lines.append(f"  {'File':<40} {'Chg':>4} {'Auth':>4} {'Score':>6}")
        lines.append(f"  {'':->40} {'':->4} {'':->4} {'':->6}")
        for h in hotspots:
            name = h["file"]
            if len(name) > 38:
                name = "..." + name[-35:]
            chart = bar_chart(h["churn_score"], max_score, 10)
            lines.append(f"  {name:<40} {h['changes']:>4} {h['author_count']:>4} {h['churn_score']:>6} {chart}")
        lines.append("")

    # Directory churn
    dir_churn = data["directory_churn"]
    if dir_churn:
        lines.append("Directory Churn")
        lines.append("-" * 50)
        max_dc = dir_churn[0]["changes"] if dir_churn else 1
        for d in dir_churn[:10]:
            chart = bar_chart(d["changes"], max_dc, 15)
            lines.append(f"  {d['directory'] + '/':<25} {d['changes']:>5} changes  {d['unique_files']:>3} files  {chart}")
        lines.append("")

    # Refactoring candidates
    candidates = data.get("refactoring_candidates", [])
    if candidates:
        lines.append("Refactoring Candidates")
        lines.append("-" * 50)
        for c in candidates:
            lines.append(f"  {c['file']}")
            for r in c["reasons"]:
                lines.append(f"    - {r}")
            lines.append(f"    >> {c['recommendation']}")
            lines.append("")

    # Oscillation
    osc = data.get("oscillation", [])
    if osc:
        lines.append("Oscillating Files (add/remove churn)")
        lines.append("-" * 50)
        for o in osc[:10]:
            lines.append(f"  {o['file']}")
            lines.append(f"    Changes: {o['total_changes']}, Direction switches: {o['direction_changes']}, Ratio: {o['oscillation_ratio']}")
        lines.append("")

    return "\n".join(lines)


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Code Churn Analyzer — hotspots, oscillation, and refactoring candidates"
    )
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--since", type=str, default=None,
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, default=None,
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--top", type=int, default=15,
                        help="Number of top hotspots to show (default: 15)")
    parser.add_argument("--path", type=str, default=None,
                        help="Filter to files under this path prefix")
    parser.add_argument("--detect-oscillation", action="store_true",
                        help="Detect files with add/remove oscillation patterns")
    parser.add_argument("--repo", type=str, default=".",
                        help="Path to git repository")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.until:
        until_date = args.until
    else:
        until_date = datetime.now().strftime("%Y-%m-%d")

    if args.since:
        since_date = args.since
    else:
        d_until = datetime.strptime(until_date, "%Y-%m-%d")
        d_since = d_until - timedelta(days=args.days)
        since_date = d_since.strftime("%Y-%m-%d")

    check = run_git(["rev-parse", "--is-inside-work-tree"], args.repo)
    if check != "true":
        print(f"Error: '{args.repo}' is not a git repository.", file=sys.stderr)
        sys.exit(1)

    data = analyze_churn(
        since_date, until_date, args.repo,
        path_filter=args.path,
        top_n=args.top,
        oscillation=args.detect_oscillation,
    )

    if args.format == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(format_text(data))


if __name__ == "__main__":
    main()
