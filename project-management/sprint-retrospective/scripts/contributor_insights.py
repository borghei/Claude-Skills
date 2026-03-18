#!/usr/bin/env python3
"""
Contributor Insights Analyzer

Per-contributor breakdown of commits, LOC, work patterns, specialization
detection, session analysis, and collaboration metrics from git history.

Usage:
    python contributor_insights.py --days 14
    python contributor_insights.py --days 14 --author "jane@example.com"
    python contributor_insights.py --days 14 --collaboration --format json

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

def get_commits_with_files(since: str, until: str, repo: str = ".") -> list[dict]:
    """Get commits with file-level numstat data."""
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
                try:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    removed = int(parts[1]) if parts[1] != "-" else 0
                except ValueError:
                    added = 0
                    removed = 0
                current["files"].append({
                    "path": parts[2],
                    "added": added,
                    "removed": removed,
                })

    if current:
        commits.append(current)

    return commits


def get_coauthor_info(since: str, until: str, repo: str = ".") -> list[dict]:
    """Get commits with co-author trailers."""
    log = run_git([
        "log", "--all", f"--since={since}", f"--until={until}",
        "--pretty=format:%H|%ae|%b", "--no-merges"
    ], repo)
    if not log:
        return []

    coauthored = []
    for line in log.split("\n"):
        if "Co-authored-by" in line or "Co-Authored-By" in line:
            parts = line.split("|", 2)
            if len(parts) >= 3:
                coauthored.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "body": parts[2],
                })
    return coauthored


# --- Specialization Detection ---

SPECIALIZATION_PATTERNS = {
    "frontend": {
        "extensions": {".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".sass", ".less", ".html"},
        "paths": {"src/ui", "src/components", "src/pages", "frontend/", "client/", "web/"},
    },
    "backend": {
        "extensions": {".py", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".scala", ".kt"},
        "paths": {"src/api", "src/server", "backend/", "server/", "api/"},
    },
    "infrastructure": {
        "extensions": {".yml", ".yaml", ".tf", ".hcl", ".toml"},
        "paths": {"terraform/", "k8s/", "kubernetes/", ".github/", "infra/", "deploy/", "ci/"},
        "filenames": {"Dockerfile", "docker-compose.yml", "Makefile", "Jenkinsfile"},
    },
    "documentation": {
        "extensions": {".md", ".rst", ".txt", ".adoc"},
        "paths": {"docs/", "documentation/", "wiki/"},
    },
    "tests": {
        "extensions": set(),
        "paths": {"test/", "tests/", "__tests__/", "spec/", "e2e/"},
        "patterns": {"test_", "_test.", ".test.", ".spec.", "_spec."},
    },
    "data": {
        "extensions": {".sql", ".json", ".csv", ".parquet"},
        "paths": {"migrations/", "data/", "seeds/", "fixtures/"},
    },
}


def detect_specialization(filepath: str) -> str:
    """Classify a file path into a specialization category."""
    fp_lower = filepath.lower()
    filename = filepath.split("/")[-1]

    # Check tests first (pattern-based, overrides extension)
    test_pats = SPECIALIZATION_PATTERNS["tests"]
    for p in test_pats.get("paths", set()):
        if p in fp_lower:
            return "tests"
    for pat in test_pats.get("patterns", set()):
        if pat in fp_lower:
            return "tests"

    # Check other categories
    for category, rules in SPECIALIZATION_PATTERNS.items():
        if category == "tests":
            continue
        # Check filenames
        for fn in rules.get("filenames", set()):
            if filename == fn:
                return category
        # Check paths
        for path in rules.get("paths", set()):
            if path in fp_lower:
                return category
        # Check extensions
        for ext in rules.get("extensions", set()):
            if fp_lower.endswith(ext):
                return category

    return "other"


# --- Session Detection ---

def detect_sessions(timestamps: list[datetime], gap_minutes: int = 45) -> dict:
    """Detect work sessions from sorted timestamps."""
    if not timestamps:
        return {"deep_work": 0, "focused": 0, "micro": 0, "total": 0, "details": []}

    timestamps.sort()
    gap = timedelta(minutes=gap_minutes)
    sessions = []
    start = timestamps[0]
    end = timestamps[0]

    for i in range(1, len(timestamps)):
        if timestamps[i] - end > gap:
            sessions.append((start, end))
            start = timestamps[i]
            end = timestamps[i]
        else:
            end = timestamps[i]
    sessions.append((start, end))

    result = {"deep_work": 0, "focused": 0, "micro": 0, "total": len(sessions), "details": []}
    for s, e in sessions:
        dur = (e - s).total_seconds() / 60
        if dur > 50:
            stype = "deep_work"
        elif dur >= 20:
            stype = "focused"
        else:
            stype = "micro"
        result[stype] += 1
        result["details"].append({
            "start": s.isoformat(),
            "end": e.isoformat(),
            "duration_min": round(dur, 1),
            "type": stype,
        })

    return result


# --- Consistency Score ---

def compute_consistency(commit_dates: list[datetime], total_days: int) -> float:
    """Compute consistency score (0-1). Higher = more evenly distributed commits across days."""
    if not commit_dates or total_days <= 0:
        return 0.0

    day_counts = defaultdict(int)
    for dt in commit_dates:
        day_key = dt.strftime("%Y-%m-%d")
        day_counts[day_key] += 1

    active_days = len(day_counts)
    if total_days <= 1:
        return 1.0 if active_days > 0 else 0.0

    # Ratio of active days to total days, weighted by evenness
    coverage = active_days / total_days
    if active_days <= 1:
        return coverage * 0.5

    # Coefficient of variation of daily commit counts (lower = more even)
    counts = list(day_counts.values())
    mean_c = sum(counts) / len(counts)
    variance = sum((c - mean_c) ** 2 for c in counts) / len(counts)
    std_c = variance ** 0.5
    cv = std_c / mean_c if mean_c > 0 else 0

    evenness = max(0, 1 - cv)  # CV of 0 = perfectly even
    return round(coverage * 0.6 + evenness * 0.4, 2)


# --- Collaboration Metrics ---

def compute_collaboration(commits: list[dict]) -> dict:
    """Compute collaboration metrics from commit data."""
    # Files touched by each author
    author_files = defaultdict(set)
    # Directories touched by each author
    author_dirs = defaultdict(set)
    # All files and their authors
    file_authors = defaultdict(set)

    for c in commits:
        author = c["author"]
        for f in c.get("files", []):
            path = f["path"]
            author_files[author].add(path)
            file_authors[path].add(author)
            parts = path.split("/")
            if len(parts) > 1:
                directory = "/".join(parts[:-1])
                author_dirs[author].add(directory)

    # Knowledge silos: files touched by only 1 person
    total_files = len(file_authors)
    single_owner = sum(1 for authors in file_authors.values() if len(authors) == 1)
    silo_pct = round(single_owner / total_files * 100, 1) if total_files > 0 else 0

    # Cross-directory work per author
    cross_dir = {}
    for author, dirs in author_dirs.items():
        cross_dir[author] = len(dirs)

    # Bus factor per directory
    dir_authors = defaultdict(set)
    for path, authors in file_authors.items():
        parts = path.split("/")
        if len(parts) > 1:
            directory = "/".join(parts[:-1])
            dir_authors[directory].update(authors)

    bus_factor_risks = []
    for directory, authors in dir_authors.items():
        if len(authors) == 1:
            bus_factor_risks.append({
                "directory": directory,
                "sole_author": list(authors)[0],
            })

    return {
        "total_files_touched": total_files,
        "single_owner_files": single_owner,
        "single_owner_pct": silo_pct,
        "bus_factor_risks": bus_factor_risks[:20],  # Top 20
        "author_directory_spread": cross_dir,
    }


# --- Main Analysis ---

def analyze_contributors(since: str, until: str, repo: str,
                         author_filter: str | None = None,
                         collaboration: bool = False,
                         gap_minutes: int = 45) -> dict:
    """Run full contributor analysis."""
    commits = get_commits_with_files(since, until, repo)

    try:
        d_since = datetime.strptime(since, "%Y-%m-%d")
        d_until = datetime.strptime(until, "%Y-%m-%d")
        total_days = max((d_until - d_since).days, 1)
    except ValueError:
        total_days = 7

    # Group by author
    by_author = defaultdict(list)
    for c in commits:
        by_author[c["author"]].append(c)

    if author_filter:
        filtered = {}
        for author, clist in by_author.items():
            if author_filter.lower() in author.lower():
                filtered[author] = clist
        by_author = filtered

    contributors = []
    for author, author_commits in sorted(by_author.items(), key=lambda x: -len(x[1])):
        loc_added = 0
        loc_removed = 0
        files_touched = set()
        hourly = defaultdict(int)
        spec_counts = defaultdict(int)
        timestamps = []

        for c in author_commits:
            dt = parse_datetime(c["date"])
            timestamps.append(dt)
            hourly[dt.hour] += 1
            for f in c.get("files", []):
                loc_added += f["added"]
                loc_removed += f["removed"]
                files_touched.add(f["path"])
                cat = detect_specialization(f["path"])
                spec_counts[cat] += 1

        # Specialization percentages
        total_spec = sum(spec_counts.values()) or 1
        specialization = {
            k: round(v / total_spec, 2)
            for k, v in sorted(spec_counts.items(), key=lambda x: -x[1])
        }

        # Peak hours (top 4)
        sorted_hours = sorted(hourly.items(), key=lambda x: -x[1])
        peak_hours = [h for h, _ in sorted_hours[:4]]

        # Sessions
        sessions = detect_sessions(timestamps, gap_minutes)

        # Consistency
        consistency = compute_consistency(timestamps, total_days)

        # Focus areas (top directories)
        dir_counts = defaultdict(int)
        for f_path in files_touched:
            parts = f_path.split("/")
            if len(parts) > 1:
                dir_counts[parts[0]] += 1
            else:
                dir_counts["."] += 1
        top_dirs = sorted(dir_counts.items(), key=lambda x: -x[1])[:5]

        contributors.append({
            "author": author,
            "commits": len(author_commits),
            "loc_added": loc_added,
            "loc_removed": loc_removed,
            "loc_net": loc_added - loc_removed,
            "files_touched": len(files_touched),
            "peak_hours": peak_hours,
            "hourly_distribution": dict(sorted(hourly.items())),
            "specialization": specialization,
            "sessions": {
                "deep_work": sessions["deep_work"],
                "focused": sessions["focused"],
                "micro": sessions["micro"],
                "total": sessions["total"],
            },
            "consistency_score": consistency,
            "top_directories": [{"dir": d, "files": c} for d, c in top_dirs],
        })

    result = {
        "period": {"since": since, "until": until, "days": total_days},
        "contributor_count": len(contributors),
        "contributors": contributors,
    }

    if collaboration:
        result["collaboration"] = compute_collaboration(commits)

    return result


# --- Text Formatting ---

def bar_chart(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = min(round((value / max_value) * width), width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def format_text(data: dict) -> str:
    p = data["period"]
    lines = [
        f"Contributor Insights ({p['since']} to {p['until']})",
        "=" * 60,
        f"Contributors: {data['contributor_count']}",
        "",
    ]

    for c in data["contributors"]:
        lines.append("-" * 60)
        lines.append(f"Contributor: {c['author']}")
        lines.append(f"  Commits: {c['commits']} | LOC: +{c['loc_added']:,} / -{c['loc_removed']:,} (net: {c['loc_net']:+,}) | Files: {c['files_touched']}")

        # Sessions
        s = c["sessions"]
        total_s = s["total"] or 1
        lines.append(f"  Sessions: {s['total']} (deep: {s['deep_work']}, focused: {s['focused']}, micro: {s['micro']})")

        # Peak hours
        if c["peak_hours"]:
            hours_str = ", ".join(f"{h}:00" for h in c["peak_hours"])
            lines.append(f"  Peak Hours: {hours_str}")

        # Specialization
        if c["specialization"]:
            specs = [f"{k} ({v:.0%})" for k, v in list(c["specialization"].items())[:4]]
            lines.append(f"  Specialization: {', '.join(specs)}")

        # Top directories
        if c["top_directories"]:
            dirs = [f"{d['dir']}/ ({d['files']})" for d in c["top_directories"][:3]]
            lines.append(f"  Top Directories: {', '.join(dirs)}")

        # Consistency
        lines.append(f"  Consistency: {c['consistency_score']:.2f}")

        # Hourly heatmap
        hourly = c.get("hourly_distribution", {})
        if hourly:
            max_h = max(hourly.values()) if hourly else 1
            lines.append("  Hourly Activity:")
            for hour in range(24):
                count = hourly.get(hour, 0)
                if count > 0:
                    lines.append(f"    {hour:02d}:00  {bar_chart(count, max_h, 15)}  {count}")

        lines.append("")

    # Collaboration section
    collab = data.get("collaboration")
    if collab:
        lines.append("=" * 60)
        lines.append("Collaboration Metrics")
        lines.append("-" * 40)
        lines.append(f"  Total Files Touched: {collab['total_files_touched']}")
        lines.append(f"  Single-Owner Files: {collab['single_owner_files']} ({collab['single_owner_pct']}%)")

        if collab["bus_factor_risks"]:
            lines.append(f"  Bus Factor Risks ({len(collab['bus_factor_risks'])} directories):")
            for risk in collab["bus_factor_risks"][:10]:
                lines.append(f"    {risk['directory']}/ — sole author: {risk['sole_author']}")

    return "\n".join(lines)


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Contributor Insights — per-person analysis from git history"
    )
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--since", type=str, default=None,
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, default=None,
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--author", type=str, default=None,
                        help="Filter to a specific author (partial match)")
    parser.add_argument("--collaboration", action="store_true",
                        help="Include collaboration and bus factor metrics")
    parser.add_argument("--gap-minutes", type=int, default=45,
                        help="Session gap threshold in minutes (default: 45)")
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

    data = analyze_contributors(
        since_date, until_date, args.repo,
        author_filter=args.author,
        collaboration=args.collaboration,
        gap_minutes=args.gap_minutes,
    )

    if args.format == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(format_text(data))


if __name__ == "__main__":
    main()
