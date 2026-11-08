#!/usr/bin/env python3
"""
flow_metrics.py - Kanban flow metrics analyzer.

Computes lead time, cycle time, throughput, WIP, aging WIP, and a cumulative
flow diagram from issue status-transition history. Outputs follow the shared
PM tool schema (json | markdown | mermaid | confluence | notion | linear).

Usage:
    python flow_metrics.py --input ../assets/sample_issues.json --format markdown
    python flow_metrics.py --demo --format mermaid
    python flow_metrics.py --input issues.json --type bug --as-of 2026-11-08

Input: {"issues": [{id, title, type, team, created_at,
         status_history: [{status, entered_at}]}]} - see assets/sample_issues.json.
"as of" defaults to the latest timestamp in the data. Exit 0 report, 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any


SCHEMA_ID = "pm/cycle-time-analyzer/v1"

DEFAULT_READY_STATES = ["Ready", "To Do", "Selected for Development"]
DEFAULT_IN_PROGRESS_STATES = ["In Progress", "In Development", "In Review", "Code Review"]
DEFAULT_DONE_STATES = ["Done", "Closed", "Deployed", "Accepted", "Resolved"]


# ---------- I/O helpers ----------

def parse_iso(s: str) -> datetime:
    """Parse an ISO-8601 timestamp. Accept trailing Z."""
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def latest_event(issues: list) -> datetime | None:
    """Latest status-history timestamp in the data: the default as-of date,
    so a fixed sample (or an old export) reads the same on any day."""
    stamps = [h.get("entered_at") for i in issues if isinstance(i, dict)
              for h in (i.get("status_history") or []) if isinstance(h, dict)]
    parsed = []
    for st in stamps:
        try:
            parsed.append(parse_iso(st))
        except (TypeError, ValueError):
            continue
    return max(parsed) if parsed else None


def percentile(values: list[float], p: float) -> float:
    """Linear interpolation percentile. p in [0, 100]."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return s[int(k)]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# ---------- demo data ----------

DEMO_DATA = {
    "issues": [
        # Recent completed - feature
        {
            "id": "ENG-101", "title": "Add CSV export", "type": "feature", "team": "platform",
            "created_at": "2026-04-01T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-01T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-10T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-12T10:00:00Z"},
                {"status": "In Review", "entered_at": "2026-04-15T16:00:00Z"},
                {"status": "Done", "entered_at": "2026-04-17T10:00:00Z"},
            ],
        },
        {
            "id": "ENG-102", "title": "Dashboard sharing", "type": "feature", "team": "platform",
            "created_at": "2026-04-02T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-02T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-15T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-17T10:00:00Z"},
                {"status": "Done", "entered_at": "2026-04-24T10:00:00Z"},
            ],
        },
        {
            "id": "ENG-103", "title": "OAuth provider", "type": "feature", "team": "platform",
            "created_at": "2026-03-25T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-03-25T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-05T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-10T10:00:00Z"},
                {"status": "In Review", "entered_at": "2026-04-20T16:00:00Z"},
                {"status": "Done", "entered_at": "2026-04-28T10:00:00Z"},
            ],
        },
        {
            "id": "ENG-104", "title": "Mobile push fix", "type": "bug", "team": "platform",
            "created_at": "2026-04-18T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-18T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-19T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-20T10:00:00Z"},
                {"status": "Done", "entered_at": "2026-04-21T16:00:00Z"},
            ],
        },
        {
            "id": "ENG-105", "title": "Billing rounding", "type": "bug", "team": "platform",
            "created_at": "2026-04-25T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-25T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-26T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-27T10:00:00Z"},
                {"status": "Done", "entered_at": "2026-04-28T16:00:00Z"},
            ],
        },
        {
            "id": "ENG-106", "title": "Audit log export", "type": "feature", "team": "platform",
            "created_at": "2026-04-08T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-08T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-18T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-22T10:00:00Z"},
                {"status": "Done", "entered_at": "2026-05-04T10:00:00Z"},
            ],
        },
        {
            "id": "ENG-107", "title": "SSO debug page", "type": "feature", "team": "platform",
            "created_at": "2026-04-22T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-22T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-25T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-04-29T10:00:00Z"},
                {"status": "Done", "entered_at": "2026-05-06T10:00:00Z"},
            ],
        },
        # Currently in flight
        {
            "id": "ENG-201", "title": "OAuth migration", "type": "feature", "team": "platform",
            "created_at": "2026-04-15T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-15T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-04-25T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-05-01T10:00:00Z"},
            ],
        },
        {
            "id": "ENG-202", "title": "Webhook retry", "type": "feature", "team": "platform",
            "created_at": "2026-04-20T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-04-20T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-05-05T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-05-10T10:00:00Z"},
                {"status": "In Review", "entered_at": "2026-05-18T16:00:00Z"},
            ],
        },
        {
            "id": "ENG-203", "title": "API rate limit error UX", "type": "bug", "team": "platform",
            "created_at": "2026-05-12T10:00:00Z",
            "status_history": [
                {"status": "Backlog", "entered_at": "2026-05-12T10:00:00Z"},
                {"status": "Ready", "entered_at": "2026-05-15T09:00:00Z"},
                {"status": "In Progress", "entered_at": "2026-05-17T10:00:00Z"},
            ],
        },
    ]
}


# ---------- core computation ----------

def classify_state(state: str, ready: set, in_progress: set, done: set) -> str:
    if state in done:
        return "done"
    if state in in_progress:
        return "in_progress"
    if state in ready:
        return "ready"
    return "backlog"


def first_entry_into(history: list[dict[str, Any]], category_states: set, classify_fn) -> datetime | None:
    """Return the earliest entered_at where the status falls in any of the target states.
    For 'in_progress' we want the earliest transition into the active category."""
    for entry in history:
        if entry["status"] in category_states:
            return parse_iso(entry["entered_at"])
    return None


def first_entry_into_category(
    history: list[dict[str, Any]],
    target: str,
    ready: set,
    in_progress: set,
    done: set,
) -> datetime | None:
    for entry in history:
        cat = classify_state(entry["status"], ready, in_progress, done)
        if cat == target:
            return parse_iso(entry["entered_at"])
    return None


def current_status(history: list[dict[str, Any]]) -> str:
    if not history:
        return "Unknown"
    return sorted(history, key=lambda h: parse_iso(h["entered_at"]))[-1]["status"]


def compute_metrics(
    issues: list[dict[str, Any]],
    ready_states: list[str],
    in_progress_states: list[str],
    done_states: list[str],
    as_of: datetime,
    window_days: int,
    type_filter: str | None,
    ignore_missing: bool,
) -> dict[str, Any]:
    ready = set(ready_states)
    in_progress = set(in_progress_states)
    done = set(done_states)

    lead_times: list[float] = []
    cycle_times: list[float] = []
    done_dates: list[date] = []
    in_flight: list[dict[str, Any]] = []
    rejected = 0

    for issue in issues:
        if type_filter and issue.get("type") != type_filter:
            continue

        history = sorted(issue.get("status_history", []), key=lambda h: parse_iso(h["entered_at"]))
        if not history:
            if ignore_missing:
                rejected += 1
                continue
            raise ValueError(f"Issue {issue.get('id', '?')} has no status_history. Use --ignore-missing to skip.")

        ready_at = first_entry_into_category(history, "ready", ready, in_progress, done)
        in_progress_at = first_entry_into_category(history, "in_progress", ready, in_progress, done)
        done_at = first_entry_into_category(history, "done", ready, in_progress, done)

        if done_at:
            if ready_at and done_at >= ready_at:
                lead_times.append((done_at - ready_at).total_seconds() / 86400.0)
            if in_progress_at and done_at >= in_progress_at:
                cycle_times.append((done_at - in_progress_at).total_seconds() / 86400.0)
            done_dates.append(done_at.date())
        else:
            if in_progress_at and in_progress_at <= as_of:
                age_days = (as_of - in_progress_at).total_seconds() / 86400.0
                in_flight.append({
                    "id": issue.get("id", "?"),
                    "title": issue.get("title", ""),
                    "type": issue.get("type", ""),
                    "status": current_status(history),
                    "started_at": in_progress_at.date().isoformat(),
                    "age_days": round(age_days, 2),
                })

    # Throughput: items finished within trailing window
    window_start = (as_of - timedelta(days=window_days)).date()
    recent_done = [d for d in done_dates if d >= window_start and d <= as_of.date()]
    weeks = max(window_days / 7.0, 1.0)
    throughput_per_week = len(recent_done) / weeks if recent_done else 0.0

    # Weekly bucket for trend
    weekly_buckets: dict[str, int] = OrderedDict()
    for i in range(int(weeks), 0, -1):
        end = as_of.date() - timedelta(days=(i - 1) * 7)
        weekly_buckets[end.isoformat()] = 0
    for d in recent_done:
        # Find bucket whose end is the first >= d
        for bucket_end_str in weekly_buckets:
            bucket_end = date.fromisoformat(bucket_end_str)
            if bucket_end >= d and (bucket_end - d).days < 7:
                weekly_buckets[bucket_end_str] += 1
                break

    p85_cycle = percentile(cycle_times, 85) if cycle_times else 0.0
    aging_threshold = p85_cycle
    for item in in_flight:
        item["at_risk"] = bool(aging_threshold and item["age_days"] > aging_threshold)
        item["days_over_threshold"] = round(item["age_days"] - aging_threshold, 2) if aging_threshold else 0.0

    in_flight.sort(key=lambda x: x["age_days"], reverse=True)

    # Cumulative flow diagram: daily snapshot of state counts over the window
    cfd = build_cumulative_flow(issues, ready, in_progress, done, as_of, window_days, type_filter)

    return {
        "as_of": as_of.date().isoformat(),
        "window_days": window_days,
        "type_filter": type_filter,
        "rejected": rejected,
        "summary": {
            "lead_time_p50_days": round(percentile(lead_times, 50), 2),
            "lead_time_p85_days": round(percentile(lead_times, 85), 2),
            "lead_time_p95_days": round(percentile(lead_times, 95), 2),
            "cycle_time_p50_days": round(percentile(cycle_times, 50), 2),
            "cycle_time_p85_days": round(percentile(cycle_times, 85), 2),
            "cycle_time_p95_days": round(percentile(cycle_times, 95), 2),
            "throughput_per_week": round(throughput_per_week, 2),
            "wip_count": len(in_flight),
            "aging_wip_count": sum(1 for x in in_flight if x["at_risk"]),
            "completed_in_window": len(recent_done),
        },
        "throughput_trend": [
            {"week_ending": k, "completed": v} for k, v in weekly_buckets.items()
        ],
        "aging_wip": in_flight,
        "cumulative_flow": cfd,
    }


def build_cumulative_flow(
    issues: list[dict[str, Any]],
    ready: set,
    in_progress: set,
    done: set,
    as_of: datetime,
    window_days: int,
    type_filter: str | None,
) -> list[dict[str, Any]]:
    """Compute daily snapshot of items in each high-level state over the trailing window."""
    start_date = as_of.date() - timedelta(days=window_days)
    dates = [start_date + timedelta(days=i) for i in range(window_days + 1)]

    # For each date, count items in each category as of end of that day
    cfd_rows: list[dict[str, Any]] = []
    for d in dates:
        eod = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc) + timedelta(days=1)
        counts = defaultdict(int)
        for issue in issues:
            if type_filter and issue.get("type") != type_filter:
                continue
            history = sorted(issue.get("status_history", []), key=lambda h: parse_iso(h["entered_at"]))
            if not history:
                continue
            # Find the last status entered at or before eod
            current = None
            for entry in history:
                if parse_iso(entry["entered_at"]) <= eod:
                    current = entry["status"]
                else:
                    break
            if current is None:
                continue
            cat = classify_state(current, ready, in_progress, done)
            counts[cat] += 1
        cfd_rows.append({
            "date": d.isoformat(),
            "backlog": counts["backlog"],
            "ready": counts["ready"],
            "in_progress": counts["in_progress"],
            "done": counts["done"],
        })
    return cfd_rows


# ---------- format renderers ----------

def render_json(data: dict[str, Any]) -> str:
    envelope = {
        "schema": SCHEMA_ID,
        "generated_at": now_utc().isoformat().replace("+00:00", "Z"),
        "data": data,
    }
    return json.dumps(envelope, indent=2)


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = []
    lines.append(f"# Flow Metrics Report")
    lines.append("")
    lines.append(f"_As of {data['as_of']}; window {data['window_days']} days"
                 + (f"; type filter `{data['type_filter']}`" if data.get('type_filter') else "")
                 + "._")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Lead time (median) | {s['lead_time_p50_days']} days |")
    lines.append(f"| Lead time (85th percentile) | {s['lead_time_p85_days']} days |")
    lines.append(f"| Lead time (95th percentile) | {s['lead_time_p95_days']} days |")
    lines.append(f"| Cycle time (median) | {s['cycle_time_p50_days']} days |")
    lines.append(f"| Cycle time (85th percentile) | {s['cycle_time_p85_days']} days |")
    lines.append(f"| Cycle time (95th percentile) | {s['cycle_time_p95_days']} days |")
    lines.append(f"| Throughput (items/week) | {s['throughput_per_week']} |")
    lines.append(f"| Completed in window | {s['completed_in_window']} |")
    lines.append(f"| Current WIP | {s['wip_count']} |")
    lines.append(f"| Aging WIP (above 85th %ile) | {s['aging_wip_count']} |")
    lines.append("")

    lines.append("## Throughput Trend (weekly)")
    lines.append("")
    lines.append("| Week ending | Completed |")
    lines.append("|---|---:|")
    for row in data["throughput_trend"]:
        lines.append(f"| {row['week_ending']} | {row['completed']} |")
    lines.append("")

    lines.append("## Aging WIP")
    lines.append("")
    if not data["aging_wip"]:
        lines.append("_No items currently in flight._")
    else:
        lines.append("| ID | Title | Type | Status | Started | Age (days) | At Risk |")
        lines.append("|---|---|---|---|---|---:|:---:|")
        for item in data["aging_wip"]:
            risk = "AT RISK" if item["at_risk"] else "ok"
            lines.append(
                f"| {item['id']} | {item['title']} | {item['type']} | {item['status']} | "
                f"{item['started_at']} | {item['age_days']} | {risk} |"
            )
    lines.append("")

    lines.append("## Cumulative Flow (snapshot)")
    lines.append("")
    lines.append("| Date | Backlog | Ready | In Progress | Done |")
    lines.append("|---|---:|---:|---:|---:|")
    # Sample every 7 days to keep table compact
    for row in data["cumulative_flow"][::7]:
        lines.append(
            f"| {row['date']} | {row['backlog']} | {row['ready']} | "
            f"{row['in_progress']} | {row['done']} |"
        )
    return "\n".join(lines) + "\n"


def render_mermaid(data: dict[str, Any]) -> str:
    """Render a cumulative flow diagram using Mermaid xychart-beta."""
    cfd = data["cumulative_flow"]
    if not cfd:
        return "```mermaid\nxychart-beta\n    title \"Cumulative Flow (no data)\"\n```\n"

    # Sample every 7 days to keep readable
    sampled = cfd[::7]
    if sampled[-1] != cfd[-1]:
        sampled.append(cfd[-1])

    dates = [row["date"] for row in sampled]
    backlog = [row["backlog"] for row in sampled]
    ready = [row["ready"] for row in sampled]
    in_prog = [row["in_progress"] for row in sampled]
    done = [row["done"] for row in sampled]
    max_y = max([max(backlog or [0]), max(ready or [0]), max(in_prog or [0]), max(done or [0]), 1])

    lines = ["```mermaid"]
    lines.append("xychart-beta")
    lines.append('    title "Cumulative Flow Diagram"')
    lines.append(f"    x-axis [{', '.join(dates)}]")
    lines.append(f'    y-axis "Items" 0 --> {max_y + 2}')
    lines.append(f"    line [{', '.join(str(x) for x in backlog)}]")
    lines.append(f"    line [{', '.join(str(x) for x in ready)}]")
    lines.append(f"    line [{', '.join(str(x) for x in in_prog)}]")
    lines.append(f"    line [{', '.join(str(x) for x in done)}]")
    lines.append("```")
    return "\n".join(lines) + "\n"


def render_confluence(data: dict[str, Any]) -> str:
    s = data["summary"]
    parts = []
    parts.append(f"<h2>Flow Metrics Report</h2>")
    parts.append(f"<p><em>As of {data['as_of']}; window {data['window_days']} days.</em></p>")
    parts.append("<h3>Summary</h3>")
    parts.append("<table><tr><th>Metric</th><th>Value</th></tr>")
    rows = [
        ("Lead time (median)", f"{s['lead_time_p50_days']} days"),
        ("Lead time (85th)", f"{s['lead_time_p85_days']} days"),
        ("Cycle time (median)", f"{s['cycle_time_p50_days']} days"),
        ("Cycle time (85th)", f"{s['cycle_time_p85_days']} days"),
        ("Throughput (items/week)", str(s['throughput_per_week'])),
        ("Current WIP", str(s['wip_count'])),
        ("Aging WIP", str(s['aging_wip_count'])),
    ]
    for k, v in rows:
        parts.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
    parts.append("</table>")

    parts.append("<h3>Aging WIP</h3>")
    if not data["aging_wip"]:
        parts.append("<p>No items currently in flight.</p>")
    else:
        parts.append("<table><tr><th>ID</th><th>Title</th><th>Status</th><th>Age (days)</th><th>At Risk</th></tr>")
        for item in data["aging_wip"]:
            risk = "AT RISK" if item["at_risk"] else "ok"
            parts.append(
                f"<tr><td>{item['id']}</td><td>{item['title']}</td>"
                f"<td>{item['status']}</td><td>{item['age_days']}</td><td>{risk}</td></tr>"
            )
        parts.append("</table>")

    parts.append('<ac:structured-macro ac:name="info"><ac:rich-text-body>'
                 '<p>Flow metrics are team-level signals. Do not use for individual performance ranking.</p>'
                 '</ac:rich-text-body></ac:structured-macro>')
    return "\n".join(parts) + "\n"


def render_notion(data: dict[str, Any]) -> str:
    """Notion-compatible markdown with callouts."""
    s = data["summary"]
    lines = []
    lines.append("## Flow Metrics Report")
    lines.append("")
    lines.append(f"_As of {data['as_of']}_")
    lines.append("")
    lines.append("### Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Lead time (median) | {s['lead_time_p50_days']} days |")
    lines.append(f"| Cycle time (85th) | {s['cycle_time_p85_days']} days |")
    lines.append(f"| Throughput (items/week) | {s['throughput_per_week']} |")
    lines.append(f"| Current WIP | {s['wip_count']} |")
    lines.append(f"| Aging WIP | {s['aging_wip_count']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Aging WIP")
    lines.append("")
    if not data["aging_wip"]:
        lines.append("> [!NOTE]")
        lines.append("> No items currently in flight.")
    else:
        for item in data["aging_wip"]:
            marker = "[ ]"
            tag = " (at risk)" if item["at_risk"] else ""
            lines.append(f"- {marker} **{item['id']}** {item['title']} — {item['age_days']}d{tag}")
    lines.append("")
    lines.append("> [!TIP]")
    lines.append("> Treat aging WIP as the most actionable daily-standup signal.")
    return "\n".join(lines) + "\n"


def render_linear(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = []
    lines.append("**Flow Metrics Report**")
    lines.append("")
    lines.append(f"As of {data['as_of']}, window {data['window_days']}d.")
    lines.append("")
    lines.append(f"- Lead time (median): {s['lead_time_p50_days']}d")
    lines.append(f"- Cycle time (85th): {s['cycle_time_p85_days']}d")
    lines.append(f"- Throughput: {s['throughput_per_week']}/week")
    lines.append(f"- WIP: {s['wip_count']} (aging: {s['aging_wip_count']})")
    lines.append("")
    if data["aging_wip"]:
        lines.append("**Aging WIP**")
        for item in data["aging_wip"]:
            label = "~~High~~" if item["at_risk"] else "~~Medium~~"
            lines.append(f"- [{item['id']}] {item['title']} — {item['age_days']}d {label}")
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
        prog="flow_metrics.py",
        description="Compute Kanban flow metrics (lead/cycle time, throughput, WIP, aging WIP, CFD).",
    )
    parser.add_argument("--input", help="Input JSON file with issue history")
    parser.add_argument("--demo", action="store_true", help="Use built-in demo data")
    parser.add_argument("--format", default="markdown", choices=list(RENDERERS.keys()),
                        help="Output format (default: markdown)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument("--ready-state", action="append", default=None,
                        help="State name(s) for committed-not-started (repeatable)")
    parser.add_argument("--in-progress-state", action="append", default=None,
                        help="State name(s) for active work (repeatable)")
    parser.add_argument("--done-state", action="append", default=None,
                        help="State name(s) for delivered (repeatable)")
    parser.add_argument("--type", default=None, help="Filter by issue type")
    parser.add_argument("--window-days", type=int, default=60,
                        help="Trailing window for throughput and CFD (default 60)")
    parser.add_argument("--ignore-missing", action="store_true",
                        help="Skip issues that lack status_history")
    parser.add_argument("--as-of", default=None, help="YYYY-MM-DD to compute metrics as of (default: latest timestamp in the data; "
                             "pass today's date for a live board)")
    args = parser.parse_args(argv)

    if not args.input and not args.demo:
        parser.error("Provide --input or --demo.")

    if args.demo:
        payload = DEMO_DATA
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
            return 2

    issues = payload.get("issues") if isinstance(payload, dict) else None
    if not isinstance(issues, list) or not issues:
        print("error: input must be a JSON object with a non-empty 'issues' list", file=sys.stderr)
        return 2

    try:
        as_of = parse_iso(args.as_of + "T00:00:00Z") if args.as_of else latest_event(issues)
    except ValueError:
        print(f"error: --as-of must be YYYY-MM-DD, got {args.as_of!r}", file=sys.stderr)
        return 2
    if as_of is None:
        print("error: no parseable status_history timestamps; pass --as-of", file=sys.stderr)
        return 2

    ready = args.ready_state or DEFAULT_READY_STATES
    in_progress = args.in_progress_state or DEFAULT_IN_PROGRESS_STATES
    done = args.done_state or DEFAULT_DONE_STATES

    try:
        data = compute_metrics(
            issues=issues,
            ready_states=ready,
            in_progress_states=in_progress,
            done_states=done,
            as_of=as_of,
            window_days=args.window_days,
            type_filter=args.type,
            ignore_missing=args.ignore_missing,
        )
    except (ValueError, TypeError, AttributeError) as exc:
        print(f"error: bad issue data: {exc}", file=sys.stderr)
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
