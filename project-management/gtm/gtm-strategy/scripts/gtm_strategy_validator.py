#!/usr/bin/env python3
"""
gtm_strategy_validator.py — Audit a GTM strategy doc for ICP specificity,
motion fit, channel coherence, messaging clarity, metric definition,
and launch sequence realism.

Stdlib only. JSON or markdown output.

Usage:
    python3 gtm_strategy_validator.py --input gtm.json
    python3 gtm_strategy_validator.py --input gtm.json --format markdown

Input schema:
{
  "gtm_name": "Acme HR Analytics Q3 launch",
  "as_of": "2026-05-27",
  "icp": {
      "size_band": "200-2000 EE",
      "vertical": "SaaS",
      "role": "HR Director or VP People",
      "jtbd": "...",
      "trigger": "...",
      "geo": "US",
      "specific_enough": true
  },
  "beachhead_segment": "...",
  "motion": "sales-led",   # plg|sales-led|marketing-led|channel-led|community-led|hybrid
  "avg_acv_usd": 50000,
  "channels": [
      {"name": "...", "budget_allocated": true, "owner": "..."}
  ],
  "messaging": {
      "hero_message": "...",
      "differentiator_named": true,
      "tested_with_customers": true,
      "per_persona_talk_tracks": true
  },
  "metrics": [
      {"name": "...", "target": "...", "owner": "..."}
  ],
  "launch_sequence": {
      "t_minus_90_done": true,
      "t_minus_60_done": false,
      "t_minus_30_done": false,
      "lighthouse_customers_count": 0
  },
  "budget_usd": 400000,
  "cross_functional_aligned": true
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Issue:
    severity: str
    component: str
    message: str


def check_icp(state: dict[str, Any]) -> list[Issue]:
    issues = []
    icp = state.get("icp") or {}
    if not icp:
        return [Issue("fail", "icp", "no ICP defined")]
    required = ["size_band", "vertical", "role", "jtbd"]
    for r in required:
        if not icp.get(r):
            issues.append(Issue("warn", "icp", f"ICP missing {r}"))
    if not icp.get("trigger"):
        issues.append(Issue("info", "icp",
            "ICP has no trigger event — 'why now' is a sharp ICP signal"))
    if not icp.get("specific_enough"):
        issues.append(Issue("warn", "icp",
            "ICP not marked specific_enough — review for vagueness"))
    return issues


def check_motion_fit(state: dict[str, Any]) -> list[Issue]:
    issues = []
    if not (state.get("beachhead_segment") or "").strip():
        issues.append(Issue("warn", "beachhead",
            "no beachhead segment; launching to the whole ICP at once dilutes messaging and references"))
    motion = (state.get("motion") or "").lower()
    acv = float(state.get("avg_acv_usd", 0) or 0)
    if motion not in ("plg", "sales-led", "marketing-led", "channel-led",
                     "community-led", "hybrid"):
        issues.append(Issue("warn", "motion",
            f"motion '{motion}' not recognized"))
    # Fit checks
    if motion == "sales-led" and acv < 10000:
        issues.append(Issue("warn", "motion",
            f"sales-led motion with ACV ${acv:,.0f} — unit economics likely break (< $10K typically PLG or marketing-led)"))
    if motion == "plg" and acv > 100000:
        issues.append(Issue("info", "motion",
            f"PLG motion with ACV ${acv:,.0f} — usually requires sales-assist; consider hybrid"))
    return issues


def check_channels(state: dict[str, Any]) -> list[Issue]:
    issues = []
    chans = state.get("channels") or []
    if not chans:
        return [Issue("fail", "channels", "no channels defined")]
    if len(chans) > 6:
        issues.append(Issue("warn", "channels",
            f"{len(chans)} channels — usually 2-4 with real investment; avoid spread"))
    funded = sum(1 for c in chans if c.get("budget_allocated"))
    if funded == 0:
        issues.append(Issue("warn", "channels",
            "no channels marked budget_allocated — listed without investment = won't perform"))
    for c in chans:
        if not c.get("owner"):
            issues.append(Issue("warn", "channels",
                f"channel '{c.get('name','(unnamed)')}' has no owner"))
    return issues


def check_messaging(state: dict[str, Any]) -> list[Issue]:
    issues = []
    m = state.get("messaging") or {}
    hero = m.get("hero_message", "")
    if not hero:
        issues.append(Issue("fail", "messaging", "no hero message"))
        return issues
    if len(hero) > 120:
        issues.append(Issue("warn", "messaging",
            f"hero message {len(hero)} chars — keep < 120 for clarity"))
    generic_terms = ["ai-powered", "world-class", "cutting-edge", "best-in-class",
                    "innovative", "platform for everyone"]
    if any(t in hero.lower() for t in generic_terms):
        issues.append(Issue("warn", "messaging",
            "hero message contains generic term(s)"))
    if not m.get("differentiator_named"):
        issues.append(Issue("warn", "messaging",
            "differentiator not named — vs whom, why us?"))
    if not m.get("tested_with_customers"):
        issues.append(Issue("warn", "messaging",
            "messaging not tested with ICP customers — guesswork"))
    if not m.get("per_persona_talk_tracks"):
        issues.append(Issue("info", "messaging",
            "no per-persona talk tracks — different buyers need different framing"))
    return issues


def check_metrics(state: dict[str, Any]) -> list[Issue]:
    issues = []
    metrics = state.get("metrics") or []
    if not metrics:
        return [Issue("fail", "metrics", "no success metrics defined")]
    if len(metrics) < 3:
        issues.append(Issue("warn", "metrics",
            f"only {len(metrics)} metrics — usually 3-6 (pipeline + close + quality)"))
    for m in metrics:
        if not m.get("target"):
            issues.append(Issue("warn", "metrics",
                f"metric '{m.get('name','')}' has no target"))
        if not m.get("owner"):
            issues.append(Issue("warn", "metrics",
                f"metric '{m.get('name','')}' has no owner"))
    return issues


def check_launch_sequence(state: dict[str, Any]) -> list[Issue]:
    issues = []
    ls = state.get("launch_sequence") or {}
    if not ls:
        issues.append(Issue("warn", "launch_sequence",
            "no launch sequence — launch will be a moment, not a campaign"))
        return issues
    if not ls.get("t_minus_90_done"):
        issues.append(Issue("info", "launch_sequence",
            "T-90 milestones not done — verify launch date is realistic"))
    lh = int(ls.get("lighthouse_customers_count", 0) or 0)
    if lh < 3:
        issues.append(Issue("warn", "launch_sequence",
            f"only {lh} lighthouse customers — target 3+ for launch credibility"))
    return issues


def check_alignment(state: dict[str, Any]) -> list[Issue]:
    issues = []
    if not state.get("cross_functional_aligned"):
        issues.append(Issue("warn", "alignment",
            "cross-functional alignment not confirmed — PM/marketing/sales/CS/CEO must sync"))
    if not state.get("budget_usd"):
        issues.append(Issue("warn", "budget",
            "no budget allocated — GTM without budget under-performs"))
    return issues


def audit(state: dict[str, Any]) -> dict[str, Any]:
    all_issues = []
    all_issues.extend(check_icp(state))
    all_issues.extend(check_motion_fit(state))
    all_issues.extend(check_channels(state))
    all_issues.extend(check_messaging(state))
    all_issues.extend(check_metrics(state))
    all_issues.extend(check_launch_sequence(state))
    all_issues.extend(check_alignment(state))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    return {
        "gtm_name": state.get("gtm_name", ""),
        "as_of": state.get("as_of", ""),
        "motion": state.get("motion", ""),
        "avg_acv_usd": state.get("avg_acv_usd", 0),
        "channels_count": len(state.get("channels") or []),
        "metrics_count": len(state.get("metrics") or []),
        "lighthouse_customers_count": (state.get("launch_sequence") or {}).get("lighthouse_customers_count", 0),
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "component": i.component, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# GTM Strategy Audit — {report.get('gtm_name','(unnamed)')}\n")
    lines.append(f"_as of {report['as_of']}_\n")
    lines.append(f"**Motion:** {report['motion']} | **ACV:** ${report['avg_acv_usd']:,.0f}")
    lines.append(f"**Channels:** {report['channels_count']} | **Metrics:** {report['metrics_count']}")
    lines.append(f"**Lighthouse customers:** {report['lighthouse_customers_count']}\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Component | Message |")
        lines.append("|----------|-----------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['component']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a GTM strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON GTM doc")
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

    if not isinstance(state, dict):
        print("error: top level must be a JSON object (see the schema in --help)", file=sys.stderr)
        return 2
    try:
        report = audit(state)
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
