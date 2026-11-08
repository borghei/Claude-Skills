#!/usr/bin/env python3
"""
dashboard_designer.py — Audit a metrics dashboard spec for layering,
ownership, comparisons, and anti-vanity discipline.

Stdlib only. JSON or markdown output.

Usage:
    python3 dashboard_designer.py --input dashboard_spec.json
    python3 dashboard_designer.py --input dashboard_spec.json --format markdown

Exit codes: 0 no fail findings, 1 at least one fail finding, 2 bad input.

Input schema:
{
  "dashboard_name": "Product Growth Q3",
  "as_of": "2026-05-27",
  "audience": "team",   # team|exec|all-hands|partner|ic (board = exec, functional = team)
  "north_star": {
      "name": "...", "definition": "...", "owner": "...",
      "has_comparison": true, "has_target": true
  },
  "inputs": [
      {"name": "...", "definition": "...", "owner": "...",
       "drives_ns": true, "has_comparison": true}
  ],
  "guardrails": [
      {"name": "...", "definition": "...", "owner": "...",
       "threshold_alert": true, "has_comparison": true}
  ],
  "operational": [
      {"name": "...", "team": "...", "owner": "...",
       "actionable_test_passed": true, "has_comparison": true,
       "cadence": "real-time|hourly|daily|weekly"}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VANITY_KEYWORDS = {
    "page views", "pageviews", "total signups",
    "total users", "session count", "time on site",
}

AUDIENCE_MAX = {
    "exec": {"top_level": 8, "operational_per_team": 0},
    "team": {"top_level": 12, "operational_per_team": 8},
    "all-hands": {"top_level": 5, "operational_per_team": 0},
    "partner": {"top_level": 6, "operational_per_team": 0},
    "ic": {"top_level": 3, "operational_per_team": 0},
}
AUDIENCE_ALIAS = {"board": "exec", "functional": "team", "individual": "ic"}


@dataclass
class Issue:
    severity: str
    layer: str
    message: str


def has_vanity(name: str) -> list[str]:
    if not name:
        return []
    n = name.lower()
    return [v for v in VANITY_KEYWORDS if v in n]


def check_north_star(ns: dict[str, Any]) -> list[Issue]:
    issues = []
    if not ns or not ns.get("name"):
        return [Issue("fail", "north_star", "no North Star defined")]
    if has_vanity(ns.get("name", "")):
        issues.append(Issue("warn", "north_star",
            f"NS name uses vanity term: {', '.join(has_vanity(ns.get('name','')))}"))
    if not ns.get("definition"):
        issues.append(Issue("warn", "north_star", "NS has no definition"))
    if not ns.get("owner"):
        issues.append(Issue("warn", "north_star", "NS has no owner"))
    if not ns.get("has_comparison"):
        issues.append(Issue("warn", "north_star",
            "NS lacks comparison (vs period / vs target)"))
    if not ns.get("has_target"):
        issues.append(Issue("info", "north_star", "NS has no target set"))
    return issues


def check_inputs(inputs: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    if not inputs:
        return [Issue("fail", "inputs", "no input metrics — NS without inputs is undecomposed")]
    if len(inputs) > 6:
        issues.append(Issue("warn", "inputs",
            f"{len(inputs)} inputs — usually 3-5; consider trimming"))
    elif len(inputs) < 3:
        issues.append(Issue("info", "inputs",
            f"only {len(inputs)} input(s) — usually 3-5 needed to decompose NS"))
    for inp in inputs:
        name = inp.get("name", "")
        if has_vanity(name):
            issues.append(Issue("warn", "inputs",
                f"input '{name}' uses vanity term"))
        if not inp.get("owner"):
            issues.append(Issue("warn", "inputs", f"input '{name}' has no owner"))
        if not inp.get("has_comparison"):
            issues.append(Issue("warn", "inputs",
                f"input '{name}' lacks comparison"))
        if not inp.get("drives_ns"):
            issues.append(Issue("info", "inputs",
                f"input '{name}' not marked as driving NS — verify"))
    return issues


def check_guardrails(guards: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    if not guards:
        return [Issue("fail", "guardrails",
            "no guardrails — NS optimization without counter-metrics = risky")]
    if len(guards) < 3:
        issues.append(Issue("info", "guardrails",
            f"only {len(guards)} guardrail(s) — usually 3-5 for full coverage"))
    for g in guards:
        name = g.get("name", "")
        if not g.get("owner"):
            issues.append(Issue("warn", "guardrails", f"guardrail '{name}' has no owner"))
        if not g.get("threshold_alert"):
            issues.append(Issue("warn", "guardrails",
                f"guardrail '{name}' has no threshold alert — passive monitoring rarely catches issues"))
    return issues


def check_operational(ops: list[dict[str, Any]], audience: str) -> list[Issue]:
    issues = []
    if not ops:
        if audience == "team":
            issues.append(Issue("info", "operational",
                "no operational metrics — team dashboard usually has 4-8"))
        return issues

    # Per-team count check
    by_team: dict[str, int] = {}
    for op in ops:
        team = op.get("team", "(unknown)")
        by_team[team] = by_team.get(team, 0) + 1
    max_per_team = AUDIENCE_MAX.get(audience, {}).get("operational_per_team", 8)
    for team, count in by_team.items():
        if count > max_per_team and audience == "team":
            issues.append(Issue("warn", "operational",
                f"team '{team}' has {count} operational metrics — usually ≤{max_per_team}"))

    # Real-time discipline
    rt_count = sum(1 for op in ops if (op.get("cadence") or "").lower() == "real-time")
    if rt_count > 3:
        issues.append(Issue("warn", "operational",
            f"{rt_count} metrics on real-time cadence — usually expensive; reserve for triage"))

    for op in ops:
        name = op.get("name", "")
        if has_vanity(name):
            issues.append(Issue("warn", "operational",
                f"operational '{name}' uses vanity term"))
        if not op.get("owner"):
            issues.append(Issue("warn", "operational",
                f"operational '{name}' has no owner"))
        if not op.get("actionable_test_passed"):
            issues.append(Issue("info", "operational",
                f"operational '{name}' not confirmed actionable — apply +/-10% test"))
        if not op.get("has_comparison"):
            issues.append(Issue("info", "operational",
                f"operational '{name}' lacks comparison"))
    return issues


def check_top_level_count(state: dict[str, Any]) -> list[Issue]:
    issues = []
    audience = (state.get("audience") or "team").lower()
    audience = AUDIENCE_ALIAS.get(audience, audience)
    if audience not in AUDIENCE_MAX:
        issues.append(Issue("warn", "(top-level)", f"unknown audience '{audience}'; using team limits"))
    inputs = state.get("inputs") or []
    guards = state.get("guardrails") or []
    ns_count = 1 if (state.get("north_star") or {}).get("name") else 0
    top_total = ns_count + len(inputs) + len(guards)
    max_top = AUDIENCE_MAX.get(audience, {}).get("top_level", 12)
    if top_total > max_top:
        issues.append(Issue("warn", "(top-level)",
            f"top-level metric count {top_total} > recommended {max_top} for {audience}"))
    return issues


def audit(state: dict[str, Any]) -> dict[str, Any]:
    all_issues: list[Issue] = []
    all_issues.extend(check_north_star(state.get("north_star") or {}))
    all_issues.extend(check_inputs(state.get("inputs") or []))
    all_issues.extend(check_guardrails(state.get("guardrails") or []))
    all_issues.extend(check_operational(
        state.get("operational") or [],
        AUDIENCE_ALIAS.get(str(state.get("audience", "team")).lower(), str(state.get("audience", "team")).lower())))
    all_issues.extend(check_top_level_count(state))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    return {
        "dashboard_name": state.get("dashboard_name", ""),
        "as_of": state.get("as_of", ""),
        "audience": state.get("audience", ""),
        "counts": {
            "north_star": 1 if (state.get("north_star") or {}).get("name") else 0,
            "inputs": len(state.get("inputs") or []),
            "guardrails": len(state.get("guardrails") or []),
            "operational": len(state.get("operational") or []),
        },
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "layer": i.layer, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Dashboard Audit — {report.get('dashboard_name','(unnamed)')}\n")
    lines.append(f"_as of {report['as_of']} | audience: {report['audience']}_\n")
    c = report["counts"]
    lines.append(f"**Counts:** NS={c['north_star']} | inputs={c['inputs']} | "
                f"guardrails={c['guardrails']} | operational={c['operational']}")
    sc = report["severity_counts"]
    lines.append(f"\n**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Layer | Message |")
        lines.append("|----------|-------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['layer']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a dashboard spec for layering, owners, anti-vanity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON dashboard spec")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    report = audit(state)
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if report["severity_counts"]["fail"] else 0  # 1 = at least one fail finding


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        print(f"error: bad input ({type(exc).__name__}): {exc}", file=sys.stderr)
        sys.exit(2)
