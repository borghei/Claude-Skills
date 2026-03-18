#!/usr/bin/env python3
"""
Retrospective Report Generator

Takes velocity, contributor, and churn analysis data (as JSON files) and
generates a comprehensive markdown retrospective report with executive
summary, velocity dashboard, contributor spotlights, code health section,
sprint comparison, and action item tracking.

Usage:
    python retro_report_generator.py \\
        --velocity velocity.json \\
        --contributors contributors.json \\
        --churn churn.json \\
        --sprint-name "Sprint 23"

    python retro_report_generator.py \\
        -v velocity.json -c contributors.json -u churn.json \\
        --previous-retro retro_sprint_22.md \\
        --previous-velocity velocity_prev.json \\
        -s "Sprint 23" -o retro_sprint_23.md

Standard library only.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any


# --- Data Loading ---

def load_json(path: str) -> dict:
    """Load a JSON file and return the parsed data."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
        return {}


def load_text(path: str) -> str:
    """Load a text file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


# --- Previous Retro Parsing ---

def extract_action_items(retro_text: str) -> list[dict]:
    """Extract action items from a previous retrospective markdown file."""
    items = []
    for line in retro_text.split("\n"):
        line = line.strip()
        # Match markdown checkboxes: - [ ] or - [x]
        match = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line)
        if match:
            checked = match.group(1).lower() == "x"
            text = match.group(2).strip()
            # Try to extract owner and due date
            owner = ""
            due = ""
            owner_match = re.search(r"Owner:\s*(\S+)", text)
            if owner_match:
                owner = owner_match.group(1)
            due_match = re.search(r"Due:\s*(\S+)", text)
            if due_match:
                due = due_match.group(1)
            # Clean text
            clean_text = re.sub(r"\s*[-—]\s*Owner:.*$", "", text).strip()
            clean_text = re.sub(r"\s*[-—]\s*Due:.*$", "", clean_text).strip()

            items.append({
                "text": clean_text,
                "done": checked,
                "owner": owner,
                "due": due,
            })
    return items


# --- Bar Charts ---

def text_bar(value: int, max_value: int, width: int = 20) -> str:
    """Generate a unicode bar chart segment."""
    if max_value == 0:
        return " " * width
    filled = min(round((value / max_value) * width), width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def md_bar(value: int, max_value: int, width: int = 15) -> str:
    """Generate a markdown-friendly bar using block chars."""
    if max_value == 0:
        return ""
    filled = min(round((value / max_value) * width), width)
    return "`" + "\u2588" * filled + "\u2591" * (width - filled) + "`"


# --- Delta Formatting ---

def fmt_delta(current: float, previous: float) -> str:
    """Format a delta between two values."""
    if previous == 0:
        return "N/A"
    pct = ((current - previous) / abs(previous)) * 100
    if pct > 0:
        return f"+{pct:.0f}%"
    elif pct < 0:
        return f"{pct:.0f}%"
    return "0%"


def delta_emoji(current: float, previous: float, higher_is_better: bool = True) -> str:
    """Return a direction indicator (no emoji, text-based)."""
    if previous == 0:
        return ""
    diff = current - previous
    if abs(diff) < 0.01:
        return "(stable)"
    if higher_is_better:
        return "(up)" if diff > 0 else "(down)"
    else:
        return "(down - good)" if diff < 0 else "(up - check)"


# --- Report Sections ---

def generate_header(sprint_name: str, velocity: dict) -> str:
    """Generate report header."""
    # Extract period from velocity data
    v = velocity.get("current", velocity)
    period = v.get("period", {})
    since = period.get("since", "unknown")
    until = period.get("until", "unknown")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""# Sprint Retrospective — {sprint_name}

**Period:** {since} to {until}
**Generated:** {now}
**Tool:** sprint-retrospective v2.0.0

---
"""


def generate_tweetable_summary(velocity: dict, churn: dict) -> str:
    """Generate a one-line tweetable summary of the sprint."""
    v = velocity.get("current", velocity)
    total_commits = v.get("total_commits", 0)
    loc_net = v.get("loc", {}).get("net", 0)
    prs = v.get("total_merges", 0)

    # Find dominant commit type
    types = v.get("commit_types", {})
    dominant = max(types.items(), key=lambda x: x[1])[0] if types else "mixed"

    # Churn health
    health = churn.get("health_indicators", {})
    test_ratio = health.get("test_to_prod_ratio", 0)

    parts = [f"{total_commits} commits"]
    if loc_net != 0:
        parts.append(f"{loc_net:+,} LOC")
    if prs > 0:
        parts.append(f"{prs} PRs merged")

    flavor = ""
    if dominant == "feat":
        flavor = "feature-heavy sprint"
    elif dominant == "fix":
        flavor = "bug-fix focused sprint"
    elif dominant == "docs":
        flavor = "documentation-heavy sprint"
    elif dominant == "refactor":
        flavor = "refactoring sprint"
    else:
        flavor = "balanced sprint"

    if test_ratio < 0.1:
        flavor += " with low test coverage"

    summary = f"> {', '.join(parts)} — {flavor}."
    return summary + "\n"


def generate_executive_summary(velocity: dict, contributors: dict, churn: dict) -> str:
    """Generate an executive summary from the data."""
    v = velocity.get("current", velocity)
    c_data = contributors
    ch = churn

    lines = ["## Executive Summary", ""]

    # Key metrics
    total_commits = v.get("total_commits", 0)
    throughput = v.get("throughput_per_day", 0)
    prs = v.get("total_merges", 0)
    loc_net = v.get("loc", {}).get("net", 0)
    authors = v.get("author_count", 0)
    cycle_time = v.get("cycle_time_hours", 0)

    lines.append(f"This sprint delivered **{total_commits} commits** across **{authors} contributors**, "
                 f"merging **{prs} PRs** with a net change of **{loc_net:+,} lines**. "
                 f"Throughput was **{throughput} commits/day** with an average cycle time of **{cycle_time} hours**.")
    lines.append("")

    # Sessions summary
    sessions = v.get("sessions", {})
    total_sessions = sessions.get("total", 0) or 1
    deep_pct = round(sessions.get("deep_work", 0) / total_sessions * 100)
    lines.append(f"Work pattern analysis: **{deep_pct}% deep work sessions**, "
                 f"{sessions.get('focused', 0)} focused sessions, "
                 f"{sessions.get('micro', 0)} micro sessions.")
    lines.append("")

    # Code health summary
    health = ch.get("health_indicators", {})
    churn_rate = health.get("churn_rate", 0)
    test_ratio = health.get("test_to_prod_ratio", 0)
    refactor_freq = health.get("refactor_frequency", 0)

    health_notes = []
    if churn_rate > 0.5:
        health_notes.append("elevated churn rate")
    if test_ratio < 0.3:
        health_notes.append("low test-to-production ratio")
    if refactor_freq < 0.08:
        health_notes.append("low refactoring activity")
    if refactor_freq > 0.3:
        health_notes.append("high refactoring activity")

    if health_notes:
        lines.append(f"**Attention areas:** {', '.join(health_notes)}.")
    else:
        lines.append("**Code health indicators are within healthy ranges.**")
    lines.append("")

    # Comparison if available
    comparison = velocity.get("comparison")
    if comparison:
        lines.append("### Sprint-over-Sprint Comparison")
        lines.append("")
        lines.append("| Metric | Current | Previous | Delta |")
        lines.append("|--------|---------|----------|-------|")
        for label, vals in comparison.items():
            lines.append(f"| {label} | {vals['current']} | {vals['previous']} | {vals['delta']} |")
        lines.append("")

    return "\n".join(lines)


def generate_velocity_dashboard(velocity: dict) -> str:
    """Generate velocity metrics dashboard."""
    v = velocity.get("current", velocity)

    lines = ["## Velocity Dashboard", ""]

    # Core metrics table
    loc = v.get("loc", {})
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Commits | {v.get('total_commits', 0)} |")
    lines.append(f"| LOC Added | +{loc.get('added', 0):,} |")
    lines.append(f"| LOC Removed | -{loc.get('removed', 0):,} |")
    lines.append(f"| LOC Net | {loc.get('net', 0):+,} |")
    lines.append(f"| PRs Merged | {v.get('total_merges', 0)} |")
    lines.append(f"| Avg PR Size | {v.get('avg_pr_size_loc', 0)} LOC |")
    lines.append(f"| Throughput | {v.get('throughput_per_day', 0)} commits/day |")
    lines.append(f"| Cycle Time | {v.get('cycle_time_hours', 0)} hours |")
    lines.append(f"| Deploy Frequency | {v.get('deploy_frequency_per_day', 0)}/day |")
    lines.append(f"| Unique Authors | {v.get('author_count', 0)} |")
    lines.append("")

    # Commit type breakdown
    ct = v.get("commit_types", {})
    if ct:
        total_ct = sum(ct.values()) or 1
        max_ct = max(ct.values()) if ct else 1
        lines.append("### Commit Type Distribution")
        lines.append("")
        lines.append("```")
        for ctype, count in sorted(ct.items(), key=lambda x: -x[1]):
            pct = round(count / total_ct * 100)
            bar = text_bar(count, max_ct, 20)
            lines.append(f"  {ctype:<12} {bar}  {pct:>3}%  ({count})")
        lines.append("```")
        lines.append("")

    # Hourly distribution
    hourly = v.get("hourly_distribution", {})
    if hourly:
        # Convert string keys to int if needed
        hourly_int = {int(k): v for k, v in hourly.items()}
        max_h = max(hourly_int.values()) if hourly_int else 1
        lines.append("### Hourly Activity")
        lines.append("")
        lines.append("```")
        for hour in range(24):
            count = hourly_int.get(hour, 0)
            if count > 0:
                bar = text_bar(count, max_h, 25)
                lines.append(f"  {hour:02d}:00  {bar}  {count}")
        lines.append("```")
        lines.append("")

    # Session breakdown
    s = v.get("sessions", {})
    if s:
        total_s = s.get("total", 0) or 1
        lines.append("### Work Sessions")
        lines.append("")
        lines.append("| Session Type | Count | Percentage |")
        lines.append("|-------------|-------|------------|")
        lines.append(f"| Deep Work (>50min) | {s.get('deep_work', 0)} | {round(s.get('deep_work', 0)/total_s*100)}% |")
        lines.append(f"| Focused (20-50min) | {s.get('focused', 0)} | {round(s.get('focused', 0)/total_s*100)}% |")
        lines.append(f"| Micro (<20min) | {s.get('micro', 0)} | {round(s.get('micro', 0)/total_s*100)}% |")
        lines.append(f"| **Total** | **{s.get('total', 0)}** | **100%** |")
        lines.append("")

    return "\n".join(lines)


def generate_contributor_spotlights(contributors: dict) -> str:
    """Generate per-contributor spotlight sections."""
    lines = ["## Contributor Spotlights", ""]

    contribs = contributors.get("contributors", [])
    if not contribs:
        lines.append("No contributor data available.")
        return "\n".join(lines)

    for c in contribs:
        lines.append(f"### {c['author']}")
        lines.append("")
        lines.append(f"- **Commits:** {c['commits']} | **LOC:** +{c['loc_added']:,} / -{c['loc_removed']:,} (net: {c.get('loc_net', c['loc_added'] - c['loc_removed']):+,}) | **Files:** {c['files_touched']}")

        # Sessions
        s = c.get("sessions", {})
        if s:
            lines.append(f"- **Sessions:** {s.get('total', 0)} (deep: {s.get('deep_work', 0)}, focused: {s.get('focused', 0)}, micro: {s.get('micro', 0)})")

        # Peak hours
        ph = c.get("peak_hours", [])
        if ph:
            hours_str = ", ".join(f"{h}:00" for h in ph)
            lines.append(f"- **Peak Hours:** {hours_str}")

        # Specialization
        spec = c.get("specialization", {})
        if spec:
            specs = [f"{k} ({v:.0%})" for k, v in list(spec.items())[:4]]
            lines.append(f"- **Specialization:** {', '.join(specs)}")

        # Top directories
        dirs = c.get("top_directories", [])
        if dirs:
            dir_str = ", ".join(f"`{d['dir']}/` ({d['files']})" for d in dirs[:3])
            lines.append(f"- **Top Directories:** {dir_str}")

        # Consistency
        lines.append(f"- **Consistency Score:** {c.get('consistency_score', 0):.2f}")
        lines.append("")

    # Collaboration
    collab = contributors.get("collaboration")
    if collab:
        lines.append("### Collaboration Metrics")
        lines.append("")
        lines.append(f"- **Total Files Touched:** {collab['total_files_touched']}")
        lines.append(f"- **Single-Owner Files:** {collab['single_owner_files']} ({collab['single_owner_pct']}%)")

        risks = collab.get("bus_factor_risks", [])
        if risks:
            lines.append(f"- **Bus Factor Risks:** {len(risks)} directories with single owner")
            lines.append("")
            lines.append("| Directory | Sole Author |")
            lines.append("|-----------|-------------|")
            for r in risks[:10]:
                lines.append(f"| `{r['directory']}/` | {r['sole_author']} |")
            lines.append("")

    return "\n".join(lines)


def generate_code_health(churn: dict) -> str:
    """Generate code health section from churn data."""
    lines = ["## Code Health", ""]

    health = churn.get("health_indicators", {})
    if health:
        lines.append("### Health Indicators")
        lines.append("")
        lines.append("| Indicator | Value | Status |")
        lines.append("|-----------|-------|--------|")

        cr = health.get("churn_rate", 0)
        cr_status = "OK" if cr <= 0.3 else ("WARN" if cr <= 0.5 else "HIGH")
        lines.append(f"| Churn Rate | {cr} | {cr_status} |")

        hc = health.get("hotspot_concentration", 0)
        hc_status = "OK" if hc <= 0.3 else ("WARN" if hc <= 0.5 else "HIGH")
        lines.append(f"| Hotspot Concentration | {hc} | {hc_status} |")

        tr = health.get("test_to_prod_ratio", 0)
        tr_status = "OK" if tr >= 0.3 else "LOW"
        lines.append(f"| Test-to-Prod Ratio | {tr} | {tr_status} |")

        rf = health.get("refactor_frequency", 0)
        rf_status = "OK" if 0.08 <= rf <= 0.3 else "CHECK"
        lines.append(f"| Refactor Frequency | {rf} | {rf_status} |")

        if "oscillation_pct" in health:
            op = health["oscillation_pct"]
            op_status = "OK" if op <= 3 else ("WARN" if op <= 8 else "HIGH")
            lines.append(f"| Oscillation | {op}% | {op_status} |")

        lines.append("")

    # Hotspots table
    hotspots = churn.get("hotspots", [])
    if hotspots:
        lines.append("### File Hotspots")
        lines.append("")
        lines.append("| Rank | File | Changes | Authors | Churn Score |")
        lines.append("|------|------|---------|---------|-------------|")
        for i, h in enumerate(hotspots[:15], 1):
            name = h["file"]
            if len(name) > 45:
                name = "..." + name[-42:]
            lines.append(f"| {i} | `{name}` | {h['changes']} | {h['author_count']} | {h['churn_score']} |")
        lines.append("")

    # Directory churn
    dir_churn = churn.get("directory_churn", [])
    if dir_churn:
        lines.append("### Directory Activity")
        lines.append("")
        lines.append("| Directory | Changes | Files | Authors |")
        lines.append("|-----------|---------|-------|---------|")
        for d in dir_churn[:10]:
            lines.append(f"| `{d['directory']}/` | {d['changes']} | {d['unique_files']} | {d['author_count']} |")
        lines.append("")

    # Refactoring candidates
    candidates = churn.get("refactoring_candidates", [])
    if candidates:
        lines.append("### Refactoring Candidates")
        lines.append("")
        for c in candidates:
            lines.append(f"**`{c['file']}`** (score: {c['churn_score']})")
            for r in c["reasons"]:
                lines.append(f"- {r}")
            lines.append(f"- *{c['recommendation']}*")
            lines.append("")

    # Oscillation
    osc = churn.get("oscillation", [])
    if osc:
        lines.append("### Oscillating Files")
        lines.append("")
        lines.append("Files with repeated add/remove cycles, indicating possible requirement churn:")
        lines.append("")
        lines.append("| File | Changes | Direction Switches | Oscillation Ratio |")
        lines.append("|------|---------|-------------------|-------------------|")
        for o in osc[:10]:
            lines.append(f"| `{o['file']}` | {o['total_changes']} | {o['direction_changes']} | {o['oscillation_ratio']} |")
        lines.append("")

    return "\n".join(lines)


def generate_previous_items_section(items: list[dict]) -> str:
    """Generate section tracking previous action items."""
    if not items:
        return ""

    lines = ["## Previous Action Items", ""]

    done_count = sum(1 for i in items if i["done"])
    total = len(items)
    completion = round(done_count / total * 100) if total > 0 else 0

    lines.append(f"**Completion Rate:** {done_count}/{total} ({completion}%)")
    lines.append("")

    for item in items:
        check = "x" if item["done"] else " "
        text = item["text"]
        if item["owner"]:
            text += f" -- Owner: {item['owner']}"
        if item["due"]:
            text += f" -- Due: {item['due']}"
        lines.append(f"- [{check}] {text}")

    lines.append("")
    return "\n".join(lines)


def generate_action_items_section() -> str:
    """Generate empty action items section for facilitator to fill."""
    return """## New Action Items

*Fill in during the retrospective session.*

- [ ] (action item 1) -- Owner: TBD -- Due: TBD
- [ ] (action item 2) -- Owner: TBD -- Due: TBD
- [ ] (action item 3) -- Owner: TBD -- Due: TBD

"""


def generate_discussion_section() -> str:
    """Generate discussion notes section for facilitator to fill."""
    return """## Discussion Notes

### What Went Well

- (to be filled during retro)

### What Could Improve

- (to be filled during retro)

### Key Decisions

- (to be filled during retro)

"""


def generate_footer() -> str:
    return """---

*Generated by sprint-retrospective skill v2.0.0*
"""


# --- Main Report Assembly ---

def generate_report(velocity: dict, contributors: dict, churn: dict,
                    sprint_name: str, previous_retro_text: str = "",
                    previous_velocity: dict | None = None) -> str:
    """Assemble the full retrospective report."""
    sections = []

    # If velocity has comparison data, use it directly
    # If previous_velocity provided, compute comparison
    if previous_velocity and "comparison" not in velocity:
        v_current = velocity.get("current", velocity)
        v_prev = previous_velocity.get("current", previous_velocity)
        comparison = {}
        keys = [
            ("total_commits", "Commits"),
            ("total_merges", "PRs Merged"),
            ("throughput_per_day", "Throughput"),
            ("cycle_time_hours", "Cycle Time"),
            ("deploy_frequency_per_day", "Deploy Frequency"),
            ("avg_pr_size_loc", "Avg PR Size"),
        ]
        for key, label in keys:
            cur = v_current.get(key, 0)
            prev = v_prev.get(key, 0)
            comparison[label] = {
                "current": cur,
                "previous": prev,
                "delta": fmt_delta(cur, prev),
            }
        velocity = {"current": v_current, "previous": v_prev, "comparison": comparison}

    sections.append(generate_header(sprint_name, velocity))
    # Tweetable summary
    sections.append(generate_tweetable_summary(velocity, churn))
    sections.append(generate_executive_summary(velocity, contributors, churn))
    sections.append(generate_velocity_dashboard(velocity))
    sections.append(generate_contributor_spotlights(contributors))
    sections.append(generate_code_health(churn))

    # Previous action items
    if previous_retro_text:
        items = extract_action_items(previous_retro_text)
        if items:
            sections.append(generate_previous_items_section(items))

    sections.append(generate_discussion_section())
    sections.append(generate_action_items_section())
    sections.append(generate_footer())

    return "\n".join(sections)


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrospective Report Generator — comprehensive markdown reports"
    )
    parser.add_argument("-v", "--velocity", type=str, required=True,
                        help="Path to velocity analysis JSON file")
    parser.add_argument("-c", "--contributors", type=str, default=None,
                        help="Path to contributor insights JSON file")
    parser.add_argument("-u", "--churn", type=str, default=None,
                        help="Path to code churn analysis JSON file")
    parser.add_argument("-s", "--sprint-name", type=str, default="Sprint",
                        help="Sprint name for the report title")
    parser.add_argument("--previous-retro", type=str, default=None,
                        help="Path to previous retrospective markdown (for action item tracking)")
    parser.add_argument("--previous-velocity", type=str, default=None,
                        help="Path to previous period velocity JSON (for comparison)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--save", type=str, default=None,
                        help="Save sprint snapshot to directory (e.g., .retro-history/)")
    return parser.parse_args()


def main():
    args = parse_args()

    velocity = load_json(args.velocity)
    contributors = load_json(args.contributors) if args.contributors else {}
    churn = load_json(args.churn) if args.churn else {}

    previous_retro_text = ""
    if args.previous_retro:
        previous_retro_text = load_text(args.previous_retro)

    previous_velocity = None
    if args.previous_velocity:
        previous_velocity = load_json(args.previous_velocity)

    report = generate_report(
        velocity, contributors, churn,
        sprint_name=args.sprint_name,
        previous_retro_text=previous_retro_text,
        previous_velocity=previous_velocity,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # Word count
    word_count = len(report.split())
    print(f"\n[Word count: {word_count}]", file=sys.stderr)

    # Save snapshot if requested
    if args.save:
        from pathlib import Path
        save_dir = Path(args.save)
        save_dir.mkdir(parents=True, exist_ok=True)
        slug = args.sprint_name.lower().replace(" ", "-")
        # Save velocity, contributors, churn snapshots
        for name, data in [("velocity", velocity), ("contributors", contributors), ("churn", churn)]:
            path = save_dir / f"{slug}-{name}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        # Save report markdown
        report_path = save_dir / f"{slug}-report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Sprint snapshot saved to {save_dir}/{slug}-*.json", file=sys.stderr)


if __name__ == "__main__":
    main()
