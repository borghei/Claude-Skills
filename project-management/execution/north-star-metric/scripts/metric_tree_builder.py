#!/usr/bin/env python3
"""Metric Tree Builder -- render an NSM spec as a Mermaid tree (or other formats).

Reads a JSON NSM specification with the NSM, input metrics, leading indicators,
anti-metrics, and counter-metrics. Emits the spec as a Mermaid `graph TD`
diagram, structured JSON, formatted Markdown, Confluence storage format,
Notion-compatible Markdown, or Linear-flavored Markdown.

Usage:
    python metric_tree_builder.py --demo --format mermaid
    python metric_tree_builder.py --input nsm_spec.json --format markdown
    python metric_tree_builder.py --input nsm_spec.json --format json --output spec.json

Standard library only. No external dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any

SCHEMA = "pm/north-star-metric/v1"

# ============================================================
# Demo data (SaaS productivity archetype)
# ============================================================

DEMO_SPEC: dict[str, Any] = {
    "nsm": {
        "name": "Weekly active accounts publishing >=1 deliverable",
        "archetype": "productivity",
        "formula": "WAA * (publishers / WAA)",
        "current": 12400,
        "target": 22000,
        "due": "2027-06-30",
    },
    "inputs": [
        {
            "name": "Weekly active accounts (WAA)",
            "formula_role": "WAA",
            "current": 28000,
            "target": 40000,
            "leading_indicators": [
                "Day-1 session count for new signups",
                "Returning signups in week 1",
                "Invites accepted in first 7 days",
            ],
        },
        {
            "name": "Publisher rate (publishers / WAA)",
            "formula_role": "publishers / WAA",
            "current": 0.44,
            "target": 0.55,
            "leading_indicators": [
                "Templates opened by new users",
                "First-deliverable started within session 1",
            ],
        },
    ],
    "anti_metrics": [
        {"name": "Weekly churn", "threshold": "must stay below 4.0%"},
        {
            "name": "Time-to-publish (median)",
            "threshold": "must stay below 22 minutes",
        },
    ],
    "counter_metrics": [
        {
            "name": "Server cost per published deliverable",
            "threshold": "must stay below $0.08",
        }
    ],
}

# ============================================================
# Helpers
# ============================================================


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_id(prefix: str, n: int) -> str:
    return f"{prefix}{n}"


def _mermaid_escape(text: str) -> str:
    """Sanitize labels for safe inclusion inside Mermaid double-quoted strings."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("\"", "&quot;")
        .replace("\n", " ")
        .strip()
    )


def _fmt_value(v: Any) -> str:
    if v is None:
        return "?"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return str(v)


# ============================================================
# Formatters
# ============================================================


def fmt_mermaid(spec: dict[str, Any]) -> str:
    nsm = spec.get("nsm", {})
    inputs = spec.get("inputs", []) or []
    anti = spec.get("anti_metrics", []) or []
    counter = spec.get("counter_metrics", []) or []

    lines = ["```mermaid", "graph TD"]
    nsm_label = (
        f"NSM: {nsm.get('name','(unnamed NSM)')}<br/>"
        f"Current: {_fmt_value(nsm.get('current'))} -> "
        f"Target: {_fmt_value(nsm.get('target'))} by "
        f"{nsm.get('due','(no date)')}"
    )
    lines.append(f"    NSM[\"{_mermaid_escape(nsm_label)}\"]")

    for i, inp in enumerate(inputs, 1):
        node = _safe_id("I", i)
        label = (
            f"Input: {inp.get('name','(unnamed input)')}<br/>"
            f"{_fmt_value(inp.get('current'))} -> "
            f"{_fmt_value(inp.get('target'))}"
        )
        lines.append(f"    {node}[\"{_mermaid_escape(label)}\"]")
        lines.append(f"    NSM --> {node}")

        for j, lead in enumerate(inp.get("leading_indicators") or [], 1):
            lead_node = f"L{i}_{j}"
            lines.append(
                f"    {lead_node}([\"Lead: {_mermaid_escape(lead)}\"])"
            )
            lines.append(f"    {node} --> {lead_node}")

    for k, am in enumerate(anti, 1):
        node = _safe_id("A", k)
        label = f"Anti: {am.get('name','')}<br/>{am.get('threshold','')}"
        lines.append(f"    {node}{{{{\"{_mermaid_escape(label)}\"}}}}")
        lines.append(f"    NSM -.-> {node}")

    for k, cm in enumerate(counter, 1):
        node = _safe_id("C", k)
        label = f"Counter: {cm.get('name','')}<br/>{cm.get('threshold','')}"
        lines.append(f"    {node}[/{_mermaid_escape(label)}/]")
        lines.append(f"    NSM -.-> {node}")

    lines.append("```")
    return "\n".join(lines)


def fmt_markdown(spec: dict[str, Any]) -> str:
    nsm = spec.get("nsm", {})
    inputs = spec.get("inputs", []) or []
    anti = spec.get("anti_metrics", []) or []
    counter = spec.get("counter_metrics", []) or []

    out = [
        "# North Star Metric Specification",
        "",
        f"_Generated {_now_iso()}_",
        "",
        "## North Star Metric",
        "",
        f"- **Name:** {nsm.get('name','(unnamed)')}",
        f"- **Archetype:** {nsm.get('archetype','(unspecified)')}",
        f"- **Formula:** `{nsm.get('formula','(no formula)')}`",
        f"- **Current:** {_fmt_value(nsm.get('current'))}",
        f"- **Target:** {_fmt_value(nsm.get('target'))} "
        f"by {nsm.get('due','(no date)')}",
        "",
        "## Input metrics",
        "",
        "| # | Input | Formula role | Current | Target |",
        "|---|-------|--------------|---------|--------|",
    ]
    for i, inp in enumerate(inputs, 1):
        out.append(
            f"| {i} | {inp.get('name','')} | "
            f"`{inp.get('formula_role','')}` | "
            f"{_fmt_value(inp.get('current'))} | "
            f"{_fmt_value(inp.get('target'))} |"
        )

    out += ["", "## Leading indicators", ""]
    for i, inp in enumerate(inputs, 1):
        out.append(f"**Input {i}: {inp.get('name','')}**")
        for lead in inp.get("leading_indicators") or []:
            out.append(f"- {lead}")
        out.append("")

    out += ["## Anti-metrics", "", "| Anti-metric | Threshold |",
            "|-------------|-----------|"]
    for am in anti:
        out.append(f"| {am.get('name','')} | {am.get('threshold','')} |")

    out += ["", "## Counter-metrics", "",
            "| Counter-metric | Threshold |",
            "|----------------|-----------|"]
    for cm in counter:
        out.append(f"| {cm.get('name','')} | {cm.get('threshold','')} |")

    return "\n".join(out)


def fmt_json(spec: dict[str, Any]) -> str:
    payload = {
        "schema": SCHEMA,
        "generated_at": _now_iso(),
        "data": spec,
    }
    return json.dumps(payload, indent=2)


def fmt_confluence(spec: dict[str, Any]) -> str:
    import html

    def esc(s: Any) -> str:
        return html.escape(str(s)) if s is not None else ""

    nsm = spec.get("nsm", {})
    inputs = spec.get("inputs", []) or []
    anti = spec.get("anti_metrics", []) or []
    counter = spec.get("counter_metrics", []) or []

    out = [
        "<h2>North Star Metric Specification</h2>",
        f"<h3>NSM: {esc(nsm.get('name',''))}</h3>",
        "<ul>",
        f"  <li>Archetype: {esc(nsm.get('archetype',''))}</li>",
        f"  <li>Formula: <code>{esc(nsm.get('formula',''))}</code></li>",
        f"  <li>Current: {esc(_fmt_value(nsm.get('current')))}</li>",
        f"  <li>Target: {esc(_fmt_value(nsm.get('target')))} "
        f"by {esc(nsm.get('due',''))}</li>",
        "</ul>",
        "<h3>Inputs</h3>",
        "<table><tr><th>#</th><th>Input</th><th>Formula role</th>"
        "<th>Current</th><th>Target</th></tr>",
    ]
    for i, inp in enumerate(inputs, 1):
        out.append(
            f"<tr><td>{i}</td><td>{esc(inp.get('name',''))}</td>"
            f"<td>{esc(inp.get('formula_role',''))}</td>"
            f"<td>{esc(_fmt_value(inp.get('current')))}</td>"
            f"<td>{esc(_fmt_value(inp.get('target')))}</td></tr>"
        )
    out.append("</table>")

    out.append("<h3>Leading indicators</h3>")
    for i, inp in enumerate(inputs, 1):
        out.append(f"<p><strong>Input {i}: {esc(inp.get('name',''))}</strong></p>")
        out.append("<ul>")
        for lead in inp.get("leading_indicators") or []:
            out.append(f"  <li>{esc(lead)}</li>")
        out.append("</ul>")

    out.append("<h3>Anti-metrics</h3>")
    out.append("<table><tr><th>Anti-metric</th><th>Threshold</th></tr>")
    for am in anti:
        out.append(
            f"<tr><td>{esc(am.get('name',''))}</td>"
            f"<td>{esc(am.get('threshold',''))}</td></tr>"
        )
    out.append("</table>")

    out.append("<h3>Counter-metrics</h3>")
    out.append("<table><tr><th>Counter-metric</th><th>Threshold</th></tr>")
    for cm in counter:
        out.append(
            f"<tr><td>{esc(cm.get('name',''))}</td>"
            f"<td>{esc(cm.get('threshold',''))}</td></tr>"
        )
    out.append("</table>")
    return "\n".join(out)


def fmt_notion(spec: dict[str, Any]) -> str:
    md = fmt_markdown(spec)
    callout = (
        "> [!TIP]\n"
        f"> North Star: {spec.get('nsm',{}).get('name','')} "
        f"-- Target {_fmt_value(spec.get('nsm',{}).get('target'))} "
        f"by {spec.get('nsm',{}).get('due','')}\n\n"
    )
    return callout + md


def fmt_linear(spec: dict[str, Any]) -> str:
    nsm = spec.get("nsm", {})
    inputs = spec.get("inputs", []) or []
    anti = spec.get("anti_metrics", []) or []
    counter = spec.get("counter_metrics", []) or []

    out = [
        f"**NSM:** {nsm.get('name','')} "
        f"({_fmt_value(nsm.get('current'))} -> "
        f"{_fmt_value(nsm.get('target'))} by {nsm.get('due','')})",
        f"_Archetype: {nsm.get('archetype','')} | "
        f"Formula: {nsm.get('formula','')}_",
        "",
        "**Inputs:**",
    ]
    for i, inp in enumerate(inputs, 1):
        out.append(
            f"- {i}. {inp.get('name','')} "
            f"({_fmt_value(inp.get('current'))} -> "
            f"{_fmt_value(inp.get('target'))})"
        )
        for lead in inp.get("leading_indicators") or []:
            out.append(f"  - lead: {lead}")

    out.append("")
    out.append("**Anti-metrics:** ~~High~~")
    for am in anti:
        out.append(f"- {am.get('name','')} -- {am.get('threshold','')}")

    out.append("")
    out.append("**Counter-metrics:** ~~Medium~~")
    for cm in counter:
        out.append(f"- {cm.get('name','')} -- {cm.get('threshold','')}")

    return "\n".join(out)


FORMATTERS = {
    "json": fmt_json,
    "markdown": fmt_markdown,
    "mermaid": fmt_mermaid,
    "confluence": fmt_confluence,
    "notion": fmt_notion,
    "linear": fmt_linear,
}


# ============================================================
# CLI
# ============================================================


def _validate(spec: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if not isinstance(spec, dict):
        return ["Spec must be a JSON object"]
    if "nsm" not in spec or not isinstance(spec["nsm"], dict):
        errs.append("Missing or invalid 'nsm' object")
    if "inputs" not in spec or not isinstance(spec["inputs"], list):
        errs.append("Missing or invalid 'inputs' array")
    else:
        for i, inp in enumerate(spec["inputs"], 1):
            if not isinstance(inp, dict) or "name" not in inp:
                errs.append(f"Input #{i} missing 'name'")
    return errs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Render an NSM spec as Mermaid tree / Markdown / JSON / "
            "Confluence / Notion / Linear."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python metric_tree_builder.py --demo --format mermaid\n"
            "  python metric_tree_builder.py --input nsm.json --format markdown\n"
            "  python metric_tree_builder.py --demo --format json "
            "--output spec.json\n"
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to JSON NSM spec file")
    g.add_argument("--demo", action="store_true", help="Use built-in demo NSM")
    p.add_argument(
        "--format",
        choices=list(FORMATTERS.keys()),
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.demo:
        spec = DEMO_SPEC
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except OSError as e:
            print(f"ERROR: cannot read {args.input}: {e.strerror or e}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid JSON in {args.input}: {e}", file=sys.stderr)
            return 2

    errs = _validate(spec)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    rendered = FORMATTERS[args.format](spec)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rendered)
            if not rendered.endswith("\n"):
                f.write("\n")
    else:
        sys.stdout.write(rendered)
        if not rendered.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
