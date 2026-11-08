#!/usr/bin/env python3
"""
dependency_graph.py - Cross-team dependency analyzer: risk-ranked summary, critical
path (the longest chain of hand-offs, with slack per link), Mermaid graph, and
team-pair counts. Formats: json | markdown | mermaid | confluence | notion | linear.

Usage:
    python dependency_graph.py --input ../assets/dependency-template.json --format markdown
    python dependency_graph.py --demo --format mermaid --criticality critical,high
Exit codes: 0 report written, 2 bad input. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from typing import Any


SCHEMA_ID = "pm/dependency-map/v1"

VALID_STATUSES = {"not_started", "in_progress", "at_risk", "blocked", "done"}
VALID_CRITICALITIES = {"critical", "high", "medium", "low"}
DEFAULT_CRITICALITY = "medium"

# Risk score: higher = more urgent
RISK_RANK = {
    "blocked": 4,
    "at_risk": 3,
    "in_progress": 2,
    "not_started": 1,
    "done": 0,
}

CRIT_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}


# ---------- helpers ----------

def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------- demo data ----------

DEMO_DATA = {
    "program": "Q3 Mobile Launch",
    "as_of": "2026-05-25",
    "dependencies": [
        {"id": "DEP-001", "from_team": "Mobile", "to_team": "Platform",
         "description": "OAuth refresh token rotation API",
         "needed_by": "2026-06-15", "expected_delivery": "2026-06-10",
         "status": "in_progress", "criticality": "critical",
         "owner": "Alex Lee", "notes": "Blocking iOS auth refactor"},
        {"id": "DEP-002", "from_team": "Mobile", "to_team": "Design",
         "description": "Final iOS dark-mode color tokens",
         "needed_by": "2026-06-01", "expected_delivery": "2026-05-29",
         "status": "in_progress", "criticality": "high",
         "owner": "Priya Patel", "notes": ""},
        {"id": "DEP-003", "from_team": "Platform", "to_team": "Data",
         "description": "Event schema for new authentication telemetry",
         "needed_by": "2026-06-05", "expected_delivery": "2026-06-12",
         "status": "at_risk", "criticality": "high",
         "owner": "Sam Park", "notes": "Data team capacity constrained"},
        {"id": "DEP-004", "from_team": "Marketing", "to_team": "Legal",
         "description": "Press release review",
         "needed_by": "2026-07-01", "expected_delivery": "2026-06-25",
         "status": "not_started", "criticality": "medium",
         "owner": "Jordan Kim", "notes": ""},
        {"id": "DEP-005", "from_team": "Mobile", "to_team": "Platform",
         "description": "Push-notification certificate rotation",
         "needed_by": "2026-06-20", "expected_delivery": "2026-06-30",
         "status": "blocked", "criticality": "critical",
         "owner": "Alex Lee", "notes": "Blocked on AWS account access (SEC-44)"},
        {"id": "DEP-006", "from_team": "Support", "to_team": "Mobile",
         "description": "Mobile feature runbook",
         "needed_by": "2026-07-05", "expected_delivery": "2026-07-05",
         "status": "not_started", "criticality": "medium",
         "owner": "Casey Romero", "notes": ""},
        {"id": "DEP-007", "from_team": "Sales", "to_team": "Marketing",
         "description": "Sales enablement deck",
         "needed_by": "2026-07-03", "expected_delivery": "2026-07-01",
         "status": "in_progress", "criticality": "high",
         "owner": "Jordan Kim", "notes": ""},
        {"id": "DEP-008", "from_team": "Platform", "to_team": "SRE",
         "description": "Capacity for 3x peak load",
         "needed_by": "2026-06-20", "expected_delivery": "2026-06-18",
         "status": "done", "criticality": "critical",
         "owner": "Morgan Webb", "notes": "Verified in staging load test"},
    ],
}


# ---------- normalization ----------

def normalize_dep(dep: dict[str, Any], idx: int) -> dict[str, Any]:
    required = ["id", "from_team", "to_team", "description", "needed_by", "expected_delivery", "status"]
    missing = [k for k in required if k not in dep]
    if missing:
        raise ValueError(f"Dependency {dep.get('id', f'<index {idx}>')} missing fields: {', '.join(missing)}")
    status = dep["status"]
    if status not in VALID_STATUSES:
        raise ValueError(f"Dependency {dep['id']} has invalid status: {status}")
    criticality = dep.get("criticality", DEFAULT_CRITICALITY)
    if criticality not in VALID_CRITICALITIES:
        raise ValueError(f"Dependency {dep['id']} has invalid criticality: {criticality}")
    return {
        "id": dep["id"],
        "from_team": dep["from_team"],
        "to_team": dep["to_team"],
        "description": dep["description"],
        "needed_by": dep["needed_by"],
        "expected_delivery": dep["expected_delivery"],
        "status": status,
        "criticality": criticality,
        "owner": dep.get("owner", ""),
        "notes": dep.get("notes", ""),
    }


# ---------- risk and slack ----------

def slack_days(dep: dict[str, Any]) -> int:
    """Positive = on time; negative = late."""
    needed = parse_date(dep["needed_by"])
    expected = parse_date(dep["expected_delivery"])
    return (needed - expected).days


def risk_label(dep: dict[str, Any], as_of: date) -> str:
    if dep["status"] == "done":
        return "none"
    if dep["status"] == "blocked":
        return "blocked"
    slack = slack_days(dep)
    days_to_needed = (parse_date(dep["needed_by"]) - as_of).days
    if dep["status"] == "at_risk" or slack < 0:
        return "high"
    if dep["status"] == "not_started" and days_to_needed <= 14:
        return "high"
    if dep["status"] == "in_progress" and slack < 7:
        return "medium"
    if dep["status"] == "not_started" and days_to_needed > 14:
        return "low"
    return "medium"


def risk_rank(label: str) -> int:
    return {"blocked": 4, "high": 3, "medium": 2, "low": 1, "none": 0}[label]


# ---------- critical path ----------

def compute_critical_path(as_of: date, deps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify the longest dependency chain by team handoff.

    Build a directed graph where dep B follows dep A if A's to_team == B's from_team
    AND A's expected_delivery <= B's needed_by (within 30 days).
    The critical path is the longest such chain by accumulated duration.
    Duration of a dep = (expected_delivery - earliest_start) when chained.
    """
    if not deps:
        return []

    active = [d for d in deps if d["status"] != "done"]
    if not active:
        return []

    # Build adjacency: next[d.id] = list of ids that can follow d
    by_id = {d["id"]: d for d in active}
    successors: dict[str, list[str]] = defaultdict(list)
    for a in active:
        a_end = parse_date(a["expected_delivery"])
        for b in active:
            if a["id"] == b["id"]:
                continue
            if a["to_team"] != b["from_team"]:
                continue
            b_start = parse_date(b["needed_by"])
            gap = (b_start - a_end).days
            if -30 <= gap <= 30:
                successors[a["id"]].append(b["id"])

    # Longest path via DFS with memoization
    best_chain_from: dict[str, list[str]] = {}

    def dfs(node_id: str, visiting: set[str]) -> list[str]:
        if node_id in best_chain_from:
            return best_chain_from[node_id]
        if node_id in visiting:
            return [node_id]
        visiting.add(node_id)
        best: list[str] = [node_id]
        for nxt in successors.get(node_id, []):
            if nxt in visiting:
                continue
            candidate = [node_id] + dfs(nxt, visiting)
            if len(candidate) > len(best):
                best = candidate
        visiting.remove(node_id)
        best_chain_from[node_id] = best
        return best

    longest: list[str] = []
    for d in active:
        chain = dfs(d["id"], set())
        if len(chain) > len(longest):
            longest = chain

    # If no chain longer than 1, pick the single most-critical open dep as the "path"
    if len(longest) <= 1:
        # Highest risk, then highest criticality, then earliest needed_by
        scored = sorted(
            active,
            key=lambda d: (
                -risk_rank(risk_label(d, as_of)),
                -CRIT_RANK[d["criticality"]],
                parse_date(d["needed_by"]),
            ),
        )
        longest = [scored[0]["id"]] if scored else []

    return [by_id[i] for i in longest]


# ---------- top-level compute ----------

def compute(
    payload: dict[str, Any],
    criticality_filter: set[str] | None,
    team_filter: set[str] | None,
    as_of: date,
) -> dict[str, Any]:
    program = payload.get("program", "Unnamed Program")
    raw_deps = payload.get("dependencies", [])
    if not isinstance(raw_deps, list):
        raise ValueError("Input JSON must contain a 'dependencies' list.")

    deps = [normalize_dep(d, i) for i, d in enumerate(raw_deps)]

    # Apply filters
    if criticality_filter:
        deps = [d for d in deps if d["criticality"] in criticality_filter]
    if team_filter:
        deps = [d for d in deps if d["from_team"] in team_filter or d["to_team"] in team_filter]

    # Enrich
    for d in deps:
        d["slack_days"] = slack_days(d)
        d["risk"] = risk_label(d, as_of)

    # Sort: blocked first, then by risk, then by needed_by
    sorted_deps = sorted(
        deps,
        key=lambda d: (
            d["status"] != "blocked",
            -risk_rank(d["risk"]),
            -CRIT_RANK[d["criticality"]],
            parse_date(d["needed_by"]),
        ),
    )

    # Critical path
    cpath = compute_critical_path(as_of, deps)

    # At risk (high or blocked) excluding done
    at_risk = [d for d in sorted_deps if d["risk"] in ("blocked", "high")]

    # By team-pair (Conway's diagnostic)
    pair_counter: Counter = Counter()
    for d in deps:
        pair_counter[(d["from_team"], d["to_team"])] += 1
    by_team_pair = [
        {"from_team": k[0], "to_team": k[1], "count": v}
        for k, v in pair_counter.most_common()
    ]

    # Summary counts
    status_counts = Counter(d["status"] for d in deps)

    return {
        "program": program,
        "as_of": as_of.isoformat(),
        "summary": {
            "total_dependencies": len(deps),
            "done": status_counts.get("done", 0),
            "blocked": status_counts.get("blocked", 0),
            "at_risk": status_counts.get("at_risk", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "not_started": status_counts.get("not_started", 0),
            "critical_path_length": len(cpath),
            "at_risk_count": len(at_risk),
        },
        "critical_path": cpath,
        "at_risk": at_risk,
        "by_team_pair": by_team_pair,
        "all_dependencies": sorted_deps,
    }


# ---------- renderers ----------

def render_json(data: dict[str, Any]) -> str:
    return json.dumps(
        {"schema": SCHEMA_ID, "generated_at": now_iso(), "data": data},
        indent=2,
    )


def _dep_row(d: dict[str, Any]) -> str:
    return (
        f"| {d['id']} | {d['from_team']} | {d['to_team']} | {d['description']} | "
        f"{d['owner'] or '-'} | {d['status']} | {d['needed_by']} | {d['expected_delivery']} | "
        f"{d['slack_days']:+d} | {d['risk']} |"
    )


def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Dependency Map: {data['program']}")
    lines.append("")
    lines.append(f"_As of {data['as_of']}._")
    lines.append("")
    s = data["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total dependencies | {s['total_dependencies']} |")
    lines.append(f"| Done | {s['done']} |")
    lines.append(f"| Blocked | {s['blocked']} |")
    lines.append(f"| At risk | {s['at_risk']} |")
    lines.append(f"| In progress | {s['in_progress']} |")
    lines.append(f"| Not started | {s['not_started']} |")
    lines.append(f"| Critical-path length | {s['critical_path_length']} |")
    lines.append(f"| High/blocked risk | {s['at_risk_count']} |")
    lines.append("")

    lines.append("## Critical Path (longest hand-off chain; negative slack = late)")
    lines.append("")
    if not data["critical_path"]:
        lines.append("_No active dependencies._")
    else:
        lines.append("| # | ID | From | To | Description | Owner | Needed By | Expected | Slack | Risk |")
        lines.append("|---:|---|---|---|---|---|---|---|---:|---|")
        for i, d in enumerate(data["critical_path"], 1):
            lines.append(
                f"| {i} | {d['id']} | {d['from_team']} | {d['to_team']} | {d['description']} | "
                f"{d['owner'] or '-'} | {d['needed_by']} | {d['expected_delivery']} | "
                f"{d['slack_days']:+d} | {d['risk']} |"
            )
    lines.append("")

    lines.append("## At-Risk Dependencies")
    lines.append("")
    if not data["at_risk"]:
        lines.append("_No high-risk or blocked dependencies._")
    else:
        lines.append("| ID | From | To | Description | Owner | Status | Needed By | Expected | Slack | Risk |")
        lines.append("|---|---|---|---|---|---|---|---|---:|---|")
        for d in data["at_risk"]:
            lines.append(_dep_row(d))
    lines.append("")

    lines.append("## All Dependencies")
    lines.append("")
    lines.append("| ID | From | To | Description | Owner | Status | Needed By | Expected | Slack | Risk |")
    lines.append("|---|---|---|---|---|---|---|---|---:|---|")
    for d in data["all_dependencies"]:
        lines.append(_dep_row(d))
    lines.append("")

    lines.append("## By Team Pair (Conway's diagnostic)")
    lines.append("")
    lines.append("| From | To | Count |")
    lines.append("|---|---|---:|")
    for row in data["by_team_pair"]:
        lines.append(f"| {row['from_team']} | {row['to_team']} | {row['count']} |")
    return "\n".join(lines) + "\n"


def render_mermaid(data: dict[str, Any]) -> str:
    """Render as a `graph LR` Mermaid diagram. Nodes are teams; edges are deps."""
    deps = data["all_dependencies"]
    if not deps:
        return "```mermaid\ngraph LR\n    empty[No dependencies]\n```\n"

    # Build set of teams as nodes
    teams: set[str] = set()
    for d in deps:
        teams.add(d["from_team"])
        teams.add(d["to_team"])

    # Sanitize team names into Mermaid ids
    def node_id(name: str) -> str:
        return "T_" + "".join(c if c.isalnum() else "_" for c in name)

    critical_ids = {d["id"] for d in data["critical_path"]}

    lines = ["```mermaid", "graph LR"]
    for t in sorted(teams):
        lines.append(f'    {node_id(t)}["{t}"]')

    for d in deps:
        # Edge label: short description + status icon
        status_marker = {
            "blocked": " [BLOCKED]",
            "at_risk": " [AT RISK]",
            "in_progress": "",
            "not_started": " [TBD]",
            "done": " [DONE]",
        }.get(d["status"], "")
        label = f"{d['id']}: {d['description']}{status_marker}"
        # Mermaid edge syntax; use thick arrow for critical-path items
        arrow = "==>" if d["id"] in critical_ids else "-->"
        # Note: edge direction is from producer to consumer (work flows producer -> consumer)
        lines.append(
            f'    {node_id(d["to_team"])} {arrow}|"{label}"| {node_id(d["from_team"])}'
        )

    # Style legend
    lines.append("    classDef critical stroke:#f00,stroke-width:3px;")
    if critical_ids:
        critical_teams = set()
        for d in data["critical_path"]:
            critical_teams.add(d["from_team"])
            critical_teams.add(d["to_team"])
        if critical_teams:
            lines.append(
                "    class " + ",".join(sorted(node_id(t) for t in critical_teams)) + " critical;"
            )

    lines.append("```")
    return "\n".join(lines) + "\n"


def render_confluence(data: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append(f"<h2>Dependency Map: {data['program']}</h2>")
    parts.append(f"<p><em>As of {data['as_of']}.</em></p>")
    s = data["summary"]
    parts.append("<h3>Summary</h3>")
    parts.append("<table>")
    parts.append("<tr><th>Metric</th><th>Value</th></tr>")
    for label, key in [
        ("Total dependencies", "total_dependencies"),
        ("Blocked", "blocked"),
        ("At risk", "at_risk"),
        ("In progress", "in_progress"),
        ("Not started", "not_started"),
        ("Done", "done"),
        ("Critical-path length", "critical_path_length"),
    ]:
        parts.append(f"<tr><td>{label}</td><td>{s[key]}</td></tr>")
    parts.append("</table>")

    parts.append("<h3>Critical Path</h3>")
    parts.append("<table>")
    parts.append("<tr><th>ID</th><th>From</th><th>To</th><th>Description</th>"
                 "<th>Owner</th><th>Needed</th><th>Expected</th><th>Slack</th></tr>")
    for d in data["critical_path"]:
        parts.append(
            f"<tr><td>{d['id']}</td><td>{d['from_team']}</td><td>{d['to_team']}</td>"
            f"<td>{d['description']}</td><td>{d['owner'] or '-'}</td>"
            f"<td>{d['needed_by']}</td><td>{d['expected_delivery']}</td>"
            f"<td>{d['slack_days']:+d}</td></tr>"
        )
    parts.append("</table>")

    parts.append("<h3>At Risk</h3>")
    parts.append("<table>")
    parts.append("<tr><th>ID</th><th>From</th><th>To</th><th>Description</th>"
                 "<th>Status</th><th>Slack</th></tr>")
    for d in data["at_risk"]:
        parts.append(
            f"<tr><td>{d['id']}</td><td>{d['from_team']}</td><td>{d['to_team']}</td>"
            f"<td>{d['description']}</td><td>{d['status']}</td>"
            f"<td>{d['slack_days']:+d}</td></tr>"
        )
    parts.append("</table>")

    parts.append('<ac:structured-macro ac:name="info"><ac:rich-text-body>'
                 '<p>Update this page weekly. Stale dependency maps mislead.</p>'
                 '</ac:rich-text-body></ac:structured-macro>')
    return "\n".join(parts) + "\n"


def render_notion(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"## Dependency Map: {data['program']}")
    lines.append("")
    lines.append(f"_As of {data['as_of']}_")
    lines.append("")
    s = data["summary"]
    lines.append("### Summary")
    lines.append("")
    lines.append(f"- **Total:** {s['total_dependencies']}")
    lines.append(f"- **Blocked:** {s['blocked']}")
    lines.append(f"- **At risk:** {s['at_risk']}")
    lines.append(f"- **In progress:** {s['in_progress']}")
    lines.append(f"- **Critical-path length:** {s['critical_path_length']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Critical Path")
    lines.append("")
    for d in data["critical_path"]:
        lines.append(f"- [ ] **{d['id']}** {d['from_team']} <- {d['to_team']}: {d['description']} (slack {d['slack_days']:+d}d)")
    lines.append("")
    lines.append("> [!WARNING]")
    lines.append(f"> {s['blocked']} blocked, {s['at_risk']} at risk. Walk these in the next sync.")
    lines.append("")
    lines.append("### At Risk")
    lines.append("")
    for d in data["at_risk"]:
        lines.append(f"- [ ] **{d['id']}** {d['description']} (slack {d['slack_days']:+d}d, status {d['status']})")
    return "\n".join(lines) + "\n"


def render_linear(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"**Dependency Map: {data['program']}**")
    lines.append("")
    s = data["summary"]
    lines.append(f"As of {data['as_of']}. {s['total_dependencies']} total ({s['blocked']} blocked, {s['at_risk']} at risk).")
    lines.append("")
    lines.append("**Critical Path**")
    for d in data["critical_path"]:
        priority = "~~Urgent~~" if d["status"] == "blocked" else "~~High~~"
        lines.append(f"- [{d['id']}] {d['from_team']} <- {d['to_team']}: {d['description']} (slack {d['slack_days']:+d}d) {priority}")
    lines.append("")
    lines.append("**At Risk**")
    for d in data["at_risk"]:
        priority = "~~Urgent~~" if d["status"] == "blocked" else "~~High~~"
        lines.append(f"- [{d['id']}] {d['description']} (slack {d['slack_days']:+d}d, {d['status']}) {priority}")
    return "\n".join(lines) + "\n"


RENDERERS = {
    "json": render_json,
    "markdown": render_markdown,
    "mermaid": render_mermaid,
    "confluence": render_confluence,
    "notion": render_notion,
    "linear": render_linear,
}


# ---------- CLI ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dependency_graph.py",
        description="Cross-team dependency analyzer with critical-path detection and Mermaid output.",
    )
    parser.add_argument("--input", help="JSON file with program + dependencies")
    parser.add_argument("--demo", action="store_true", help="Use built-in demo data")
    parser.add_argument("--format", default="markdown", choices=list(RENDERERS.keys()),
                        help="Output format (default: markdown)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument("--criticality",
                        help="Comma-separated criticality filter (critical,high,medium,low)")
    parser.add_argument("--team", action="append", default=None,
                        help="Filter to dependencies involving this team (repeatable)")
    parser.add_argument("--as-of", default=None,
                        help="Reference date for risk (YYYY-MM-DD; default: the file's as_of, else today)")
    args = parser.parse_args(argv)

    if not args.input and not args.demo:
        parser.error("Provide --input or --demo.")

    if args.demo:
        payload = DEMO_DATA
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, ValueError) as exc:
            print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
            return 2
    if not isinstance(payload, dict) or not isinstance(payload.get("dependencies"), list) \
            or not payload["dependencies"]:
        print("error: input must be a JSON object with a non-empty 'dependencies' list", file=sys.stderr)
        return 2

    crit_filter: set[str] | None = None
    if args.criticality:
        crit_filter = set(c.strip() for c in args.criticality.split(",") if c.strip())
        invalid = crit_filter - VALID_CRITICALITIES
        if invalid:
            print(f"Invalid criticality filter values: {', '.join(invalid)}", file=sys.stderr)
            return 2

    team_filter: set[str] | None = set(args.team) if args.team else None

    # As-of: --as-of, else the file's own "as_of", else today. A fixed date in the
    # file keeps samples and archived snapshots reading the same on any day.
    try:
        as_of = date.fromisoformat(args.as_of or payload.get("as_of") or date.today().isoformat())
        data = compute(payload, crit_filter, team_filter, as_of)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"error: bad input: {exc}", file=sys.stderr)
        return 2

    output = RENDERERS[args.format](data)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
