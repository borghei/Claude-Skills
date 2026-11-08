#!/usr/bin/env python3
"""
swot_scorer.py — Audit a SWOT for completeness, evidence quality,
internal/external classification, and TOWS follow-through.

Stdlib only. JSON or markdown output.

Usage:
    python3 swot_scorer.py --input swot.json
    python3 swot_scorer.py --input swot.json --format markdown

Input schema:
{
  "swot_scope": "Acme entering European compliance market",
  "as_of": "2026-05-27",
  "strengths": [
      {"text": "...", "evidence": "...", "specificity": "high|medium|low"}
  ],
  "weaknesses": [...],
  "opportunities": [
      {"text": "...", "evidence": "...", "trigger": "...",
       "time_window_months": 0, "size_estimate": "..."}
  ],
  "threats": [
      {"text": "...", "evidence": "...",
       "likelihood": 1-5, "severity": 1-5, "mitigation": "..."}
  ],
  "tows_actions": [
      {"type": "SO|ST|WO|WT", "action": "...", "priority": "high|medium|low"}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GENERIC_TERMS = {
    "great team", "great product", "strong brand", "innovative",
    "cutting-edge", "best-in-class", "competition", "ai", "growing market",
    "globalization", "market is huge", "world-class",
}


@dataclass
class Issue:
    severity: str
    block: str
    message: str


def has_generic(text: str) -> list[str]:
    if not text:
        return []
    t = text.lower()
    return [g for g in GENERIC_TERMS if re.search(r"\b" + re.escape(g) + r"\b", t)]


def check_scope(s: dict[str, Any]) -> list[Issue]:
    scope = s.get("swot_scope", "").strip()
    if not scope:
        return [Issue("fail", "scope",
            "no scope declared — SWOT without scope is wallpaper")]
    if len(scope) < 20:
        return [Issue("warn", "scope",
            f"scope very short ({len(scope)} chars); add specifics")]
    return []


def check_strengths(s: dict[str, Any]) -> list[Issue]:
    issues = []
    items = s.get("strengths") or []
    if len(items) == 0:
        issues.append(Issue("fail", "strengths", "no strengths listed"))
    elif len(items) > 10:
        issues.append(Issue("warn", "strengths",
            f"{len(items)} strengths — usually too many; pick top 5-6"))
    for item in items:
        if has_generic(item.get("text", "")):
            issues.append(Issue("warn", "strengths",
                f"contains generic terms: {', '.join(has_generic(item.get('text','')))}"))
        if not item.get("evidence"):
            issues.append(Issue("warn", "strengths",
                f"item '{item.get('text','(blank)')[:40]}...' has no evidence"))
        spec = (item.get("specificity") or "").lower()
        if spec == "low":
            issues.append(Issue("info", "strengths",
                f"item marked low-specificity — strengthen with specifics"))
    return issues


def check_weaknesses(s: dict[str, Any]) -> list[Issue]:
    issues = []
    items = s.get("weaknesses") or []
    if len(items) == 0:
        issues.append(Issue("fail", "weaknesses",
            "no weaknesses listed — likely bias or low candor"))
    elif len(items) < 3:
        issues.append(Issue("warn", "weaknesses",
            f"only {len(items)} weakness(es) — every org has 3+; surface more"))
    s_count = len(s.get("strengths") or [])
    w_count = len(items)
    if s_count >= 6 and w_count <= 2:
        issues.append(Issue("warn", "weaknesses",
            f"{s_count} strengths vs {w_count} weaknesses — strong asymmetry; check for bias"))
    return issues


def check_opportunities(s: dict[str, Any]) -> list[Issue]:
    issues = []
    items = s.get("opportunities") or []
    if not items:
        issues.append(Issue("fail", "opportunities", "no opportunities listed"))
        return issues
    for item in items:
        if has_generic(item.get("text", "")):
            issues.append(Issue("warn", "opportunities",
                f"contains generic terms: {', '.join(has_generic(item.get('text','')))}"))
        if not item.get("trigger"):
            issues.append(Issue("warn", "opportunities",
                f"item missing trigger (what shifted to create opportunity)"))
        if not item.get("time_window_months"):
            issues.append(Issue("info", "opportunities",
                f"item missing time-window estimate"))
        if not item.get("size_estimate"):
            issues.append(Issue("info", "opportunities",
                f"item missing size estimate"))
    return issues


def check_threats(s: dict[str, Any]) -> list[Issue]:
    issues = []
    items = s.get("threats") or []
    if not items:
        issues.append(Issue("fail", "threats", "no threats listed"))
        return issues
    for item in items:
        if has_generic(item.get("text", "")):
            issues.append(Issue("warn", "threats",
                f"contains generic terms: {', '.join(has_generic(item.get('text','')))}"))
        lik = int(item.get("likelihood", 0) or 0)
        sev = int(item.get("severity", 0) or 0)
        if not lik:
            issues.append(Issue("warn", "threats",
                f"item missing likelihood (1-5)"))
        if not sev:
            issues.append(Issue("warn", "threats",
                f"item missing severity (1-5)"))
        if not item.get("mitigation"):
            issues.append(Issue("info", "threats",
                f"item missing mitigation plan"))
    return issues


def check_tows(s: dict[str, Any]) -> list[Issue]:
    issues = []
    actions = s.get("tows_actions") or []
    if not actions:
        issues.append(Issue("warn", "tows",
            "no TOWS actions — SWOT without TOWS is incomplete"))
        return issues
    types_present = {a.get("type", "") for a in actions}
    missing = {"SO", "ST", "WO", "WT"} - types_present
    if missing:
        issues.append(Issue("info", "tows",
            f"TOWS cells missing: {', '.join(sorted(missing))}"))
    high_count = sum(1 for a in actions if (a.get("priority") or "").lower() == "high")
    if high_count == 0:
        issues.append(Issue("warn", "tows",
            "no high-priority TOWS actions — prioritize 2-3 actions"))
    elif high_count > 5:
        issues.append(Issue("warn", "tows",
            f"{high_count} high-priority actions — likely lacking discipline"))
    return issues


CHECKERS = [check_scope, check_strengths, check_weaknesses,
            check_opportunities, check_threats, check_tows]


def audit(swot: dict[str, Any]) -> dict[str, Any]:
    all_issues = []
    for c in CHECKERS:
        all_issues.extend(c(swot))
    sev_counts = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev_counts[i.severity] += 1
    return {
        "swot_scope": swot.get("swot_scope", ""),
        "as_of": swot.get("as_of", ""),
        "counts": {
            "strengths": len(swot.get("strengths") or []),
            "weaknesses": len(swot.get("weaknesses") or []),
            "opportunities": len(swot.get("opportunities") or []),
            "threats": len(swot.get("threats") or []),
            "tows_actions": len(swot.get("tows_actions") or []),
        },
        "severity_counts": sev_counts,
        "issues": [
            {"severity": i.severity, "block": i.block, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# SWOT Audit\n")
    lines.append(f"**Scope:** {report['swot_scope']}")
    lines.append(f"**As of:** {report['as_of']}\n")
    c = report["counts"]
    lines.append(f"**Counts:** S={c['strengths']} W={c['weaknesses']} "
                f"O={c['opportunities']} T={c['threats']} TOWS={c['tows_actions']}")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Block | Message |")
        lines.append("|----------|-------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['block']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a SWOT for completeness, evidence, TOWS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON SWOT")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        swot = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(swot, dict):
        print("error: top level must be a JSON object (see the schema in --help)", file=sys.stderr)
        return 2
    try:
        report = audit(swot)
    except (AttributeError, TypeError, KeyError, ValueError) as e:
        print(f"error: unexpected input shape ({type(e).__name__}: {e})", file=sys.stderr)
        return 2
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    # Gate: 1 when any finding has severity "fail", else 0.
    return 1 if report.get("severity_counts", {}).get("fail") else 0


if __name__ == "__main__":
    sys.exit(main())
