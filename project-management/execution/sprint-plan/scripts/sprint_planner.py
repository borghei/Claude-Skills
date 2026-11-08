#!/usr/bin/env python3
"""
sprint_planner.py — Audit a sprint plan for capacity discipline,
commit/stretch split, dependency clarity, and DoD coverage.

Stdlib only. JSON or markdown output.

Usage:
    python3 sprint_planner.py --input ../assets/sample_sprint_plan.json --format markdown

Input: a JSON object with goal, capacity {team_members[{name, available_hours}],
total_available_hours, commit_target_pct, stretch_pct}, velocity_history_pts and
items[{id, title, type: commit|stretch, estimated_pts, estimated_hours, assignee,
dependencies[{description, owner, needed_by, confirmed}], risks[{description,
mitigation, owner}], dod_items[], refined}]. See assets/sample_sprint_plan.json.

Exit codes: 0 no fail findings, 1 at least one fail finding, 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STANDARD_DOD = {"code reviewed", "tests", "telemetry", "docs"}


@dataclass
class Issue:
    severity: str
    item: str
    message: str


def check_goal(plan: dict[str, Any]) -> list[Issue]:
    goal = plan.get("goal", "").strip()
    if not goal:
        return [Issue("fail", "(sprint)", "no sprint goal defined")]
    if len(goal) > 200:
        return [Issue("warn", "(sprint)",
            f"sprint goal {len(goal)} chars — keep to 1 sentence")]
    return []


def check_capacity(plan: dict[str, Any]) -> list[Issue]:
    issues = []
    cap = plan.get("capacity") or {}
    total = float(cap.get("total_available_hours", 0) or 0)
    if total <= 0:
        issues.append(Issue("fail", "(capacity)", "no total_available_hours"))
        return issues
    members = cap.get("team_members") or []
    if not members:
        issues.append(Issue("warn", "(capacity)",
            "no per-member capacity breakdown — likely missing PTO / on-call"))
    else:
        member_sum = sum(float(m.get("available_hours", 0) or 0) for m in members)
        if abs(member_sum - total) > 0.05 * total:
            issues.append(Issue("warn", "(capacity)",
                f"team_members sum to {member_sum:.0f}h but total_available_hours is {total:.0f}h — reconcile"))
    commit_pct = float(cap.get("commit_target_pct", 0) or 0)
    stretch_pct = float(cap.get("stretch_pct", 0) or 0)
    if commit_pct > 90:
        issues.append(Issue("warn", "(capacity)",
            f"commit target {commit_pct}% — too high; usually 75-85%"))
    if commit_pct + stretch_pct > 100:
        issues.append(Issue("warn", "(capacity)",
            f"commit_target_pct + stretch_pct = {commit_pct + stretch_pct:.0f}% — targets leave no reserve"))
    return issues


def check_items(plan: dict[str, Any]) -> list[Issue]:
    issues = []
    items = plan.get("items") or []
    if not items:
        return [Issue("fail", "(items)", "no items in sprint")]

    cap = plan.get("capacity") or {}
    total_hrs = float(cap.get("total_available_hours", 0) or 0)
    commit_target_hrs = total_hrs * (float(cap.get("commit_target_pct", 80)) / 100.0)
    stretch_target_hrs = total_hrs * (float(cap.get("stretch_pct", 15)) / 100.0)

    commit_hrs = sum(
        float(i.get("estimated_hours", 0) or 0)
        for i in items if (i.get("type") or "").lower() == "commit"
    )
    stretch_hrs = sum(
        float(i.get("estimated_hours", 0) or 0)
        for i in items if (i.get("type") or "").lower() == "stretch"
    )

    # Fill bands from the SKILL.md commitment table: >100% always misses, 90-100% usually misses.
    fill = (commit_hrs + stretch_hrs) / total_hrs if total_hrs else 0
    if commit_hrs > total_hrs:
        issues.append(Issue("fail", "(commits)",
            f"commits {commit_hrs:.0f}h exceed capacity {total_hrs:.0f}h"))
    elif commit_hrs > commit_target_hrs * 1.1:
        issues.append(Issue("warn", "(commits)",
            f"commits {commit_hrs:.0f}h > target {commit_target_hrs:.0f}h — over-committed"))
    if fill > 1.0:
        issues.append(Issue("fail", "(capacity)",
            f"commit + stretch = {fill:.0%} of capacity — no reserve for unknowns"))
    elif fill > 0.9:
        issues.append(Issue("warn", "(capacity)",
            f"commit + stretch = {fill:.0%} of capacity — plans above 90% usually miss"))
    if stretch_hrs > stretch_target_hrs * 1.5:
        issues.append(Issue("info", "(stretch)",
            f"stretch {stretch_hrs:.0f}h > target {stretch_target_hrs:.0f}h — stretch should be reserved"))

    for item in items:
        iid = item.get("id", "(no-id)")
        if not item.get("refined"):
            issues.append(Issue("warn", iid,
                "item not marked refined — don't commit unrefined items"))
        pts = float(item.get("estimated_pts", 0) or 0)
        if pts >= 13:
            issues.append(Issue("warn", iid,
                f"{pts} pts — split into smaller stories"))
        if not item.get("assignee"):
            issues.append(Issue("warn", iid, "no assignee"))

        # Dependencies
        deps = item.get("dependencies") or []
        for d in deps:
            if not d.get("owner"):
                issues.append(Issue("warn", iid,
                    f"dependency '{d.get('description','')[:40]}' has no owner"))
            if not d.get("confirmed"):
                issues.append(Issue("warn", iid,
                    f"dependency '{d.get('description','')[:40]}' not confirmed by owner"))

        # Risks
        risks = item.get("risks") or []
        if not risks and (item.get("type") or "").lower() == "commit":
            issues.append(Issue("info", iid,
                "no risks identified — every commit item has 1-2 risks worth noting"))

        # DoD
        dod = set((item.get("dod_items") or []))
        missing_std = STANDARD_DOD - dod
        if missing_std:
            issues.append(Issue("info", iid,
                f"DoD missing standard items: {', '.join(sorted(missing_std))}"))

    return issues


def check_velocity_alignment(plan: dict[str, Any]) -> list[Issue]:
    issues = []
    vh = plan.get("velocity_history_pts") or []
    if not vh:
        return []
    avg_velocity = sum(vh) / len(vh)
    items = plan.get("items") or []
    commit_pts = sum(
        float(i.get("estimated_pts", 0) or 0)
        for i in items if (i.get("type") or "").lower() == "commit"
    )
    if commit_pts > avg_velocity * 1.05:
        issues.append(Issue("warn", "(velocity)",
            f"commit {commit_pts}pts > avg velocity {avg_velocity:.0f}pts — likely to miss"))
    return issues


def audit(plan: dict[str, Any]) -> dict[str, Any]:
    all_issues = []
    all_issues.extend(check_goal(plan))
    all_issues.extend(check_capacity(plan))
    all_issues.extend(check_items(plan))
    all_issues.extend(check_velocity_alignment(plan))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    items = plan.get("items") or []
    commit_items = [i for i in items if (i.get("type") or "").lower() == "commit"]
    stretch_items = [i for i in items if (i.get("type") or "").lower() == "stretch"]
    commit_hrs = sum(float(i.get("estimated_hours", 0) or 0) for i in commit_items)
    stretch_hrs = sum(float(i.get("estimated_hours", 0) or 0) for i in stretch_items)

    return {
        "sprint_name": plan.get("sprint_name", ""),
        "dates": plan.get("dates", ""),
        "goal": plan.get("goal", ""),
        "total_available_hours": (plan.get("capacity") or {}).get("total_available_hours", 0),
        "commit_count": len(commit_items),
        "commit_hours": commit_hrs,
        "stretch_count": len(stretch_items),
        "stretch_hours": stretch_hrs,
        "total_hours_committed": commit_hrs + stretch_hrs,
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "item": i.item, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Sprint Plan Audit — {report.get('sprint_name','')}\n")
    lines.append(f"_dates: {report['dates']}_")
    lines.append(f"\n**Goal:** {report['goal']}\n")
    lines.append(f"**Capacity:** {report['total_available_hours']}h available\n")
    lines.append(f"**Commits:** {report['commit_count']} items / {report['commit_hours']:.0f}h")
    lines.append(f"**Stretch:** {report['stretch_count']} items / {report['stretch_hours']:.0f}h")
    lines.append(f"**Total committed:** {report['total_hours_committed']:.0f}h\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Item | Message |")
        lines.append("|----------|------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['item']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a sprint plan for discipline + capacity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON sprint plan")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(plan, dict) or not isinstance(plan.get("items"), list) or not plan["items"] \
            or not all(isinstance(i, dict) for i in plan["items"]) \
            or not isinstance(plan.get("capacity", {}), dict):
        print("error: input must be a JSON object with a 'capacity' object and a non-empty 'items' list", file=sys.stderr)
        return 2

    report = audit(plan)
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if report["severity_counts"]["fail"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (TypeError, ValueError, AttributeError, KeyError) as exc:  # field of the wrong type
        print(f"error: input has a field of the wrong type: {exc}", file=sys.stderr)
        sys.exit(2)
