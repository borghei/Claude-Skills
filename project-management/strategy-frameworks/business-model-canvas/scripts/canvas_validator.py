#!/usr/bin/env python3
"""
canvas_validator.py — Audit a Business Model Canvas for completeness,
coherence, and common anti-patterns.

Reads a JSON BMC; checks each of the 9 blocks for emptiness, generic content,
length, and cross-block coherence (segments x channels, segments x VPs,
revenue x cost orientation, etc.).

Stdlib only. JSON or markdown output.

Usage:
    python3 canvas_validator.py --input canvas.json
    python3 canvas_validator.py --input canvas.json --format markdown

Input schema:
{
  "canvas_name": "Acme HR Analytics — v3",
  "as_of": "2026-05-27",
  "orientation": "value-driven",       # value-driven|cost-driven
  "customer_segments": [
      {"name": "Mid-market HR teams (200-2000 employees)",
       "primary": true, "segment_archetype": "niche"}
  ],
  "value_propositions": [
      {"target_segment": "Mid-market HR teams",
       "statement": "Cut HR reporting time 60%; reduce error rate 80%",
       "value_types": ["performance","cost reduction"]}
  ],
  "channels": [
      {"target_segment": "Mid-market HR teams",
       "channel": "Web direct",
       "phases_covered": ["awareness","evaluation","purchase","delivery"]}
  ],
  "customer_relationships": [
      {"target_segment": "Mid-market HR teams",
       "type": "self-service + CSM at $20K ARR+"}
  ],
  "revenue_streams": [
      {"target_segment": "Mid-market HR teams",
       "type": "subscription", "mechanism": "tiered fixed list",
       "per_unit": "per-employee/month"}
  ],
  "key_resources": ["Engineering team","Customer dataset","HRIS integrations"],
  "key_activities": ["Product dev","Integration maintenance","Customer success"],
  "key_partnerships": [
      {"partner": "HRIS vendors",
       "role": "data integration + co-marketing"}
  ],
  "cost_structure": {
      "fixed_pct_estimate": 70,
      "top_lines": ["People (eng/sales/CS)","Cloud infra","Integration maintenance"]
  },
  "assumptions": [
      {"block": "value_propositions",
       "statement": "HR teams will pay for time savings",
       "evidence": "low", "risk": "high", "testability": "high"}
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


GENERIC_TERMS = {
    "everyone", "all businesses", "all companies", "tbd", "to be determined",
    "great customer service", "excellent service", "amazing", "world-class",
    "cutting-edge", "best-in-class", "online", "internet",
}

REQUIRED_BLOCKS = [
    "customer_segments", "value_propositions", "channels",
    "customer_relationships", "revenue_streams", "key_resources",
    "key_activities", "key_partnerships", "cost_structure",
]


@dataclass
class Issue:
    severity: str  # fail|warn|info
    block: str
    message: str


def is_generic(text: str) -> list[str]:
    """Return list of generic terms found in text."""
    if not text:
        return []
    text_lower = text.lower()
    return [g for g in GENERIC_TERMS if g in text_lower]


def check_segments(c: dict[str, Any]) -> list[Issue]:
    issues = []
    segs = c.get("customer_segments") or []
    if not segs:
        issues.append(Issue("fail", "customer_segments", "no segments defined"))
        return issues
    for s in segs:
        gen = is_generic(s.get("name", ""))
        if gen:
            issues.append(Issue("warn", "customer_segments",
                f"segment '{s.get('name')}' uses generic term(s): {', '.join(gen)}"))
        name = s.get("name", "")
        if len(name) < 15:
            issues.append(Issue("warn", "customer_segments",
                f"segment '{name}' may be too vague ({len(name)} chars); add size/sector/use-case"))
    if len(segs) > 5:
        issues.append(Issue("info", "customer_segments",
            f"{len(segs)} segments — consider whether all are real beachheads or aspirational"))
    primary_count = sum(1 for s in segs if s.get("primary"))
    if len(segs) > 1 and primary_count == 0:
        issues.append(Issue("warn", "customer_segments",
            "multiple segments but none marked primary — pick a beachhead"))
    return issues


def check_value_props(c: dict[str, Any]) -> list[Issue]:
    issues = []
    vps = c.get("value_propositions") or []
    segs = c.get("customer_segments") or []
    seg_names = {s.get("name", "") for s in segs}
    if not vps:
        issues.append(Issue("fail", "value_propositions", "no value propositions defined"))
        return issues
    for vp in vps:
        stmt = vp.get("statement", "")
        gen = is_generic(stmt)
        if gen:
            issues.append(Issue("warn", "value_propositions",
                f"VP contains generic terms: {', '.join(gen)}"))
        if len(stmt) < 30:
            issues.append(Issue("warn", "value_propositions",
                f"VP statement short ({len(stmt)} chars) — add specifics + outcomes"))
        # Outcome language check
        has_outcome = any(k in stmt.lower() for k in
                         ["cut", "reduce", "save", "increase", "boost", "%", "x ",
                          "x.", "fewer", "more", "faster", "instead of"])
        if not has_outcome:
            issues.append(Issue("info", "value_propositions",
                f"VP for {vp.get('target_segment', '?')} lacks outcome-language "
                "(measurable change) — consider strengthening"))
        target = vp.get("target_segment", "")
        if seg_names and target and not any(target in s or s in target for s in seg_names):
            issues.append(Issue("warn", "value_propositions",
                f"VP targets '{target}' which doesn't match a defined segment"))
    # Segments without VP
    for s in segs:
        sname = s.get("name", "")
        # An empty target_segment must not match every segment.
        matched = any(vp.get("target_segment") and (sname in vp["target_segment"] or
                     vp["target_segment"] in sname) for vp in vps)
        if not matched:
            issues.append(Issue("fail", "value_propositions",
                f"segment '{sname}' has no matching VP"))
    return issues


def check_channels(c: dict[str, Any]) -> list[Issue]:
    issues = []
    chans = c.get("channels") or []
    segs = c.get("customer_segments") or []
    if not chans:
        issues.append(Issue("fail", "channels", "no channels defined"))
        return issues
    for ch in chans:
        gen = is_generic(ch.get("channel", ""))
        if gen:
            issues.append(Issue("warn", "channels",
                f"channel '{ch.get('channel')}' uses generic term"))
        phases = ch.get("phases_covered") or []
        if not phases:
            issues.append(Issue("info", "channels",
                f"channel '{ch.get('channel')}' has no phases declared"))
        elif len(phases) == 5:
            issues.append(Issue("info", "channels",
                f"channel '{ch.get('channel')}' claims all 5 phases — verify (rare)"))
    # Segments without channel
    seg_names = {s.get("name", "") for s in segs}
    covered = set()
    for ch in chans:
        target = ch.get("target_segment", "")
        for sn in seg_names:
            if target and (sn in target or target in sn):
                covered.add(sn)
    missing = seg_names - covered
    for sn in missing:
        if sn:
            issues.append(Issue("warn", "channels",
                f"segment '{sn}' has no channel mapped"))
    return issues


def check_relationships(c: dict[str, Any]) -> list[Issue]:
    issues = []
    rels = c.get("customer_relationships") or []
    if not rels:
        issues.append(Issue("fail", "customer_relationships",
                          "no customer relationships defined"))
        return issues
    for r in rels:
        gen = is_generic(r.get("type", ""))
        if gen:
            issues.append(Issue("warn", "customer_relationships",
                f"relationship '{r.get('type')}' too generic"))
    return issues


def check_revenue(c: dict[str, Any]) -> list[Issue]:
    issues = []
    revs = c.get("revenue_streams") or []
    if not revs:
        issues.append(Issue("fail", "revenue_streams", "no revenue streams defined"))
        return issues
    for r in revs:
        if not r.get("mechanism"):
            issues.append(Issue("warn", "revenue_streams",
                f"stream '{r.get('type')}' missing pricing mechanism (list / negotiation / etc.)"))
        if not r.get("per_unit"):
            issues.append(Issue("info", "revenue_streams",
                f"stream '{r.get('type')}' missing per-unit dimension (per-seat/per-tx/etc)"))
    return issues


def check_resources(c: dict[str, Any]) -> list[Issue]:
    issues = []
    res = c.get("key_resources") or []
    if not res:
        issues.append(Issue("fail", "key_resources", "no key resources defined"))
        return issues
    for r in res:
        if is_generic(r):
            issues.append(Issue("warn", "key_resources", f"resource '{r}' is generic"))
    if len(res) > 8:
        issues.append(Issue("info", "key_resources",
            f"{len(res)} resources — usually 3-6 truly key; consider trimming"))
    return issues


def check_activities(c: dict[str, Any]) -> list[Issue]:
    issues = []
    acts = c.get("key_activities") or []
    if not acts:
        issues.append(Issue("fail", "key_activities", "no key activities defined"))
        return issues
    if len(acts) > 6:
        issues.append(Issue("warn", "key_activities",
            f"{len(acts)} activities — usually 3-5; pick the top"))
    return issues


def check_partnerships(c: dict[str, Any]) -> list[Issue]:
    issues = []
    parts = c.get("key_partnerships") or []
    if not parts:
        issues.append(Issue("info", "key_partnerships",
            "no partnerships defined — confirm this is accurate"))
        return issues
    for p in parts:
        if not p.get("role"):
            issues.append(Issue("warn", "key_partnerships",
                f"partnership with '{p.get('partner', '?')}' missing role (give + get)"))
    return issues


def check_costs(c: dict[str, Any]) -> list[Issue]:
    issues = []
    costs = c.get("cost_structure") or {}
    if not costs:
        issues.append(Issue("fail", "cost_structure", "no cost structure defined"))
        return issues
    top = costs.get("top_lines") or []
    if not top:
        issues.append(Issue("warn", "cost_structure",
            "no top cost lines listed"))
    elif len(top) < 3:
        issues.append(Issue("info", "cost_structure",
            "fewer than 3 cost lines listed — usually missing something"))
    orient = (c.get("orientation") or "").lower()
    if orient not in ("value-driven", "cost-driven"):
        issues.append(Issue("info", "cost_structure",
            "orientation not declared (value-driven vs cost-driven) — picking matters"))
    return issues


def check_assumptions(c: dict[str, Any]) -> list[Issue]:
    issues = []
    asums = c.get("assumptions") or []
    if not asums:
        issues.append(Issue("info", "assumptions",
            "no assumptions identified — every canvas has riskiest 3; surface them"))
        return issues
    high_risk_low_evidence = [
        a for a in asums
        if (a.get("risk") or "").lower() == "high"
        and (a.get("evidence") or "").lower() == "low"
    ]
    if high_risk_low_evidence:
        issues.append(Issue("warn", "assumptions",
            f"{len(high_risk_low_evidence)} assumption(s) are high-risk + low-evidence — test these first"))
    return issues


CHECKERS = [
    check_segments, check_value_props, check_channels,
    check_relationships, check_revenue, check_resources,
    check_activities, check_partnerships, check_costs,
    check_assumptions,
]


def validate(canvas: dict[str, Any]) -> dict[str, Any]:
    all_issues: list[Issue] = []
    for chk in CHECKERS:
        all_issues.extend(chk(canvas))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    # Block completeness
    completeness: dict[str, str] = {}
    for block in REQUIRED_BLOCKS:
        v = canvas.get(block)
        if not v:
            completeness[block] = "empty"
        elif isinstance(v, list) and len(v) == 0:
            completeness[block] = "empty"
        elif isinstance(v, dict) and not v:
            completeness[block] = "empty"
        else:
            completeness[block] = "populated"

    # Score
    populated_count = sum(1 for s in completeness.values() if s == "populated")
    completeness_pct = round((populated_count / len(REQUIRED_BLOCKS)) * 100)
    penalty = sev["fail"] * 10 + sev["warn"] * 3 + sev["info"] * 1
    quality_pct = max(0, completeness_pct - penalty)

    return {
        "canvas_name": canvas.get("canvas_name", ""),
        "as_of": canvas.get("as_of", ""),
        "completeness_pct": completeness_pct,
        "quality_pct": quality_pct,
        "block_completeness": completeness,
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "block": i.block, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# BMC Validation — {report.get('canvas_name','(unnamed)')}\n")
    lines.append(f"_as of {report['as_of']}_\n")
    lines.append(f"**Completeness:** {report['completeness_pct']}% of blocks populated")
    lines.append(f"**Quality:** {report['quality_pct']}/100 (after issue penalties)\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    lines.append("## Block status")
    lines.append("| Block | Status |")
    lines.append("|-------|--------|")
    for b, s in report["block_completeness"].items():
        lines.append(f"| {b} | {s} |")
    lines.append("")
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
        description="Validate a Business Model Canvas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON canvas")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        canvas = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(canvas, dict):
        print("error: top level must be a JSON object (see the schema in --help)", file=sys.stderr)
        return 2
    try:
        report = validate(canvas)
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
