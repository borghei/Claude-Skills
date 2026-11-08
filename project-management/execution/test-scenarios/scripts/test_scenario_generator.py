#!/usr/bin/env python3
"""
test_scenario_generator.py — Audit a feature's test scenario coverage
across 7+ categories; flag under-coverage based on feature type.
It audits scenarios you have written; it does not generate them.

Stdlib only. JSON or markdown output.

Usage:
    python3 test_scenario_generator.py --input feature_spec.json
    python3 test_scenario_generator.py --input feature_spec.json --format markdown

Input schema:
{
  "feature_name": "Signup form",
  "feature_type": "form",   # form|browse|realtime|upload|payment|bulk|generic
  "supported_locales": ["en","de","ar"],
  "supports_collaboration": false,
  "scenarios": [
      {
          "id": "S-001",
          "name": "User signs up with email + password",
          "category": "happy_path",   # happy_path|edge|error|empty|concurrent|a11y|security|performance|localization|cross_platform
          "priority": "P0",            # P0|P1|P2|P3
          "automated": true
      }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Recommended scenario counts by feature type and category
RECOMMENDED = {
    "form": {
        "happy_path": (1, 3), "edge": (4, 8), "error": (4, 6),
        "empty": (1, 2), "concurrent": (0, 2), "a11y": (3, 5),
        "security": (3, 5), "performance": (0, 2),
    },
    "browse": {
        "happy_path": (2, 3), "edge": (3, 5), "error": (2, 3),
        "empty": (2, 3), "concurrent": (0, 1), "a11y": (3, 4),
        "security": (2, 3), "performance": (1, 3),
    },
    "realtime": {
        "happy_path": (2, 4), "edge": (4, 6), "error": (4, 6),
        "empty": (1, 2), "concurrent": (4, 6), "a11y": (3, 4),
        "security": (3, 5), "performance": (1, 3),
    },
    "upload": {
        "happy_path": (1, 2), "edge": (6, 10), "error": (4, 6),
        "empty": (1, 1), "concurrent": (1, 2), "a11y": (2, 3),
        "security": (5, 10), "performance": (1, 3),
    },
    "payment": {
        "happy_path": (2, 3), "edge": (6, 10), "error": (8, 12),
        "empty": (1, 2), "concurrent": (4, 6), "a11y": (3, 4),
        "security": (8, 12), "performance": (1, 3),
    },
    "bulk": {
        "happy_path": (1, 2), "edge": (4, 6), "error": (4, 6),
        "empty": (1, 1), "concurrent": (2, 4), "a11y": (2, 3),
        "security": (3, 5), "performance": (2, 4),
    },
    "generic": {
        "happy_path": (1, 3), "edge": (3, 5), "error": (3, 5),
        "empty": (1, 2), "concurrent": (0, 2), "a11y": (3, 4),
        "security": (2, 4), "performance": (0, 2),
    },
}


@dataclass
class Issue:
    severity: str
    category: str
    message: str


def audit(state: dict[str, Any]) -> dict[str, Any]:
    feature_type = (state.get("feature_type") or "generic").lower()
    if feature_type not in RECOMMENDED:
        feature_type = "generic"
    recommended = RECOMMENDED[feature_type]

    scenarios = state.get("scenarios") or []
    by_category = Counter(s.get("category", "") for s in scenarios)
    by_priority = Counter(s.get("priority", "") for s in scenarios)

    all_issues: list[Issue] = []

    for cat, (low, high) in recommended.items():
        count = by_category.get(cat, 0)
        if count < low and low > 0:
            sev = "fail" if count == 0 and cat in ("happy_path", "edge", "error", "security") else "warn"
            all_issues.append(Issue(sev, cat,
                f"only {count} {cat} scenarios; recommended {low}-{high} for {feature_type}"))
        elif count > high and high > 0:
            all_issues.append(Issue("info", cat,
                f"{count} {cat} scenarios; recommended max {high}"))

    known = set().union(*(r.keys() for r in RECOMMENDED.values())) | {"localization", "cross_platform"}
    for cat in sorted(set(by_category) - known):
        all_issues.append(Issue("warn", cat or "(none)",
            f"{by_category[cat]} scenario(s) with unknown category '{cat}'; they are not counted"))

    # Collab + concurrent check
    if state.get("supports_collaboration") and by_category.get("concurrent", 0) < 3:
        all_issues.append(Issue("warn", "concurrent",
            "feature supports collaboration but has <3 concurrent scenarios"))

    # Localization check
    locales = state.get("supported_locales") or []
    if len(locales) > 1 and by_category.get("localization", 0) == 0:
        all_issues.append(Issue("warn", "localization",
            f"{len(locales)} locales supported but no localization scenarios"))

    # Cross-platform check
    if by_category.get("cross_platform", 0) == 0:
        all_issues.append(Issue("info", "cross_platform",
            "no cross-platform scenarios — verify browser/device matrix is covered elsewhere"))

    # Priority discipline
    if not by_priority.get("P0"):
        all_issues.append(Issue("warn", "priority",
            "no P0 scenarios — every feature needs at least one critical-path scenario"))

    sev_counts = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev_counts[i.severity] += 1

    return {
        "feature_name": state.get("feature_name", ""),
        "feature_type": feature_type,
        "scenario_count": len(scenarios),
        "by_category": dict(by_category),
        "by_priority": dict(by_priority),
        "recommended": recommended,
        "severity_counts": sev_counts,
        "issues": [
            {"severity": i.severity, "category": i.category, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Test Scenario Coverage Audit — {report.get('feature_name','')}\n")
    lines.append(f"_feature type: {report['feature_type']} | {report['scenario_count']} scenarios_\n")
    lines.append("## Coverage by category")
    lines.append("| Category | Actual | Recommended (min-max) |")
    lines.append("|----------|--------|----------------------|")
    for cat, (low, high) in report["recommended"].items():
        actual = report["by_category"].get(cat, 0)
        lines.append(f"| {cat} | {actual} | {low}-{high} |")
    for cat in ("localization", "cross_platform"):
        if cat not in report["recommended"]:
            actual = report["by_category"].get(cat, 0)
            if actual > 0:
                lines.append(f"| {cat} | {actual} | (situational) |")
    lines.append("")
    lines.append("## By priority")
    for p, c in report["by_priority"].items():
        lines.append(f"- {p}: {c}")
    lines.append("")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Category | Message |")
        lines.append("|----------|----------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['category']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit test scenario coverage by category",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON feature spec with scenarios")
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
