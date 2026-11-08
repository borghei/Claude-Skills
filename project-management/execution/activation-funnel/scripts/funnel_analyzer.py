#!/usr/bin/env python3
"""Funnel Analyzer -- activation / Pirate Metrics funnel analysis.

Ingests a JSON funnel definition (stages with counts) and emits stage-by-stage
conversion + drop-off math, a Mermaid flowchart, and a bottleneck call-out.

Supports all six SHARED_OUTPUT_SCHEMA formats: json, markdown, mermaid,
confluence, notion, linear.

Usage:
    python funnel_analyzer.py --demo --format markdown
    python funnel_analyzer.py --input funnel.json --format mermaid
    python funnel_analyzer.py --demo --format json --output funnel.json

Standard library only. No external dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from typing import Any

SCHEMA = "pm/activation-funnel/v1"

# ============================================================
# Demo data
# ============================================================

DEMO_DATA: dict[str, Any] = {
    "name": "SaaS Free Trial Activation Funnel",
    "cohort": "Signups in the week of 2026-05-04",
    "framework": "AARRR",
    "stages": [
        {
            "name": "Landing page visit",
            "stage": "acquisition",
            "count": 10000,
            "counter_metric": "Bounce rate must stay below 60%",
        },
        {
            "name": "Signup started",
            "stage": "acquisition",
            "count": 2400,
            "counter_metric": "Real-email signup share above 90%",
        },
        {
            "name": "Email verified",
            "stage": "acquisition",
            "count": 1800,
            "counter_metric": None,
        },
        {
            "name": "First workspace created",
            "stage": "activation",
            "count": 1100,
            "counter_metric": None,
        },
        {
            "name": "Aha event: 3 docs + 1 collaborator in week 1",
            "stage": "activation",
            "count": 410,
            "counter_metric": "D7 retention of activated above 55%",
        },
        {
            "name": "D30 retained",
            "stage": "retention",
            "count": 290,
            "counter_metric": "Engagement events/day above 4",
        },
        {
            "name": "Converted to paid",
            "stage": "revenue",
            "count": 180,
            "counter_metric": "First-month churn below 8%",
        },
    ],
}


# ============================================================
# Helpers
# ============================================================


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _validate(data: dict[str, Any]) -> None:
    if "stages" not in data or not isinstance(data["stages"], list):
        raise ValueError("Funnel JSON must include a 'stages' list")
    if len(data["stages"]) < 2:
        raise ValueError("Funnel must have at least 2 stages")
    for i, s in enumerate(data["stages"]):
        if "name" not in s:
            raise ValueError(f"Stage {i} missing 'name'")
        if "count" not in s or not isinstance(s["count"], (int, float)):
            raise ValueError(f"Stage {i} ('{s.get('name')}') missing numeric 'count'")
        if s["count"] < 0:
            raise ValueError(f"Stage {i} ('{s['name']}') has negative count")


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    """Compute conversion, drop-off, cumulative, and bottleneck."""
    _validate(data)
    stages = data["stages"]
    rows: list[dict[str, Any]] = []
    top = stages[0]["count"] or 1  # avoid division by zero
    for i, s in enumerate(stages):
        cur = s["count"]
        if i == 0:
            conv = 1.0
            drop_abs = 0
            drop_rate = 0.0
        else:
            prev = stages[i - 1]["count"] or 1
            conv = cur / prev
            drop_abs = stages[i - 1]["count"] - cur
            drop_rate = 1.0 - conv
        rows.append(
            {
                "index": i,
                "name": s["name"],
                "stage": s.get("stage"),
                "count": cur,
                "conversion_from_prev": conv,
                "drop_absolute": drop_abs,
                "drop_rate": drop_rate,
                "cumulative_conversion": cur / top,
                "counter_metric": s.get("counter_metric"),
            }
        )

    # Largest absolute drop and largest relative drop (excluding stage 0)
    transitions = rows[1:]
    if transitions:
        worst_abs = max(transitions, key=lambda r: r["drop_absolute"])
        worst_rate = min(transitions, key=lambda r: r["conversion_from_prev"])
    else:
        worst_abs = worst_rate = None
    # Top-of-funnel stages almost always lose the most, which says little. The actionable
    # bottleneck is the worst conversion once users are in the product (past acquisition).
    inside = [r for r in transitions if r.get("stage") not in ("acquisition", "awareness")] or transitions[1:]
    worst_inside = min(inside, key=lambda r: r["conversion_from_prev"]) if inside else None

    return {
        "name": data.get("name", "Funnel"),
        "cohort": data.get("cohort", ""),
        "framework": data.get("framework", "AARRR"),
        "stages": rows,
        "bottleneck_absolute": worst_abs,
        "bottleneck_rate": worst_rate,
        "bottleneck_post_acquisition": worst_inside,
        "overall_top_to_bottom": rows[-1]["cumulative_conversion"] if rows else 0,
    }


# ============================================================
# Formatters
# ============================================================


def fmt_json(a: dict[str, Any]) -> str:
    return json.dumps(
        {"schema": SCHEMA, "generated_at": _now_iso(), "data": a}, indent=2
    )


def fmt_markdown(a: dict[str, Any]) -> str:
    lines = [
        f"# Funnel Analysis: {a['name']}",
        "",
        f"**Framework:** {a['framework']}  ",
        f"**Cohort:** {a['cohort']}  ",
        f"**Overall top-to-bottom conversion:** {_pct(a['overall_top_to_bottom'])}",
        "",
        "## Stage-by-stage",
        "",
        "| # | Stage | Bucket | Count | Conv. from prev | Drop (abs) | Drop rate | Cumulative | Counter-metric |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in a["stages"]:
        lines.append(
            "| {i} | {n} | {b} | {c} | {cv} | {da} | {dr} | {cu} | {cm} |".format(
                i=r["index"],
                n=r["name"],
                b=r.get("stage") or "",
                c=r["count"],
                cv="-" if r["index"] == 0 else _pct(r["conversion_from_prev"]),
                da="-" if r["index"] == 0 else r["drop_absolute"],
                dr="-" if r["index"] == 0 else _pct(r["drop_rate"]),
                cu=_pct(r["cumulative_conversion"]),
                cm=r.get("counter_metric") or "(none)",
            )
        )

    lines += ["", "## Bottlenecks", ""]
    if a.get("bottleneck_absolute"):
        ba = a["bottleneck_absolute"]
        lines.append(
            f"- **Largest absolute drop:** stage {ba['index']} "
            f"({ba['name']}) -- lost {ba['drop_absolute']} users "
            f"({_pct(ba['drop_rate'])} of the prior stage)."
        )
    if a.get("bottleneck_rate"):
        br = a["bottleneck_rate"]
        lines.append(
            f"- **Worst conversion rate:** stage {br['index']} "
            f"({br['name']}) -- only {_pct(br['conversion_from_prev'])} "
            f"converted from the prior stage."
        )
    if a.get("bottleneck_post_acquisition"):
        bi = a["bottleneck_post_acquisition"]
        lines.append(
            f"- **Worst conversion past acquisition (start here):** stage {bi['index']} "
            f"({bi['name']}) -- {_pct(bi['conversion_from_prev'])} converted from the prior stage."
        )

    lines += ["", "## Funnel diagram", "", _mermaid_block(a), ""]
    lines += ["---", f"_Generated {_now_iso()}_"]
    return "\n".join(lines)


def _mermaid_block(a: dict[str, Any]) -> str:
    return "\n".join(["```mermaid", fmt_mermaid_raw(a), "```"])


def fmt_mermaid_raw(a: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    stages = a["stages"]
    for i, r in enumerate(stages):
        label = (r["name"][:60] + "...") if len(r["name"]) > 63 else r["name"]
        label = label.replace('"', "'")
        lines.append(f'    S{i}["{label}<br/>{r["count"]}"]')
    for i in range(1, len(stages)):
        conv = _pct(stages[i]["conversion_from_prev"])
        lines.append(f"    S{i-1} -->|{conv}| S{i}")

    ba = a.get("bottleneck_absolute")
    br = a.get("bottleneck_rate")
    note_lines = []
    if ba:
        note_lines.append(
            f"Largest abs drop at S{ba['index']}: -{ba['drop_absolute']} users"
        )
    if br and (not ba or br["index"] != ba["index"]):
        note_lines.append(
            f"Worst conv at S{br['index']}: {_pct(br['conversion_from_prev'])}"
        )
    if note_lines:
        joined = " / ".join(note_lines).replace('"', "'")
        lines.append(f'    BN["BOTTLENECK: {joined}"]')
        lines.append("    style BN fill:#fde68a,stroke:#b45309")
    return "\n".join(lines)


def fmt_mermaid(a: dict[str, Any]) -> str:
    return _mermaid_block(a)


def fmt_confluence(a: dict[str, Any]) -> str:
    def esc(s: Any) -> str:
        return html.escape(str(s)) if s is not None else ""

    out = [
        f"<h2>Funnel Analysis: {esc(a['name'])}</h2>",
        f"<p><strong>Framework:</strong> {esc(a['framework'])} | "
        f"<strong>Cohort:</strong> {esc(a['cohort'])} | "
        f"<strong>Overall conversion:</strong> {_pct(a['overall_top_to_bottom'])}</p>",
        "<h3>Stage-by-stage</h3>",
        "<table><tr>"
        "<th>#</th><th>Stage</th><th>Bucket</th><th>Count</th>"
        "<th>Conv. from prev</th><th>Drop (abs)</th>"
        "<th>Drop rate</th><th>Cumulative</th><th>Counter-metric</th>"
        "</tr>",
    ]
    for r in a["stages"]:
        out.append(
            "<tr><td>{i}</td><td>{n}</td><td>{b}</td><td>{c}</td>"
            "<td>{cv}</td><td>{da}</td><td>{dr}</td><td>{cu}</td>"
            "<td>{cm}</td></tr>".format(
                i=r["index"],
                n=esc(r["name"]),
                b=esc(r.get("stage") or ""),
                c=r["count"],
                cv="-" if r["index"] == 0 else _pct(r["conversion_from_prev"]),
                da="-" if r["index"] == 0 else r["drop_absolute"],
                dr="-" if r["index"] == 0 else _pct(r["drop_rate"]),
                cu=_pct(r["cumulative_conversion"]),
                cm=esc(r.get("counter_metric") or "(none)"),
            )
        )
    out.append("</table>")
    out.append("<h3>Bottlenecks</h3>")
    if a.get("bottleneck_absolute"):
        ba = a["bottleneck_absolute"]
        out.append(
            '<ac:structured-macro ac:name="warning"><ac:rich-text-body>'
            f"<p><strong>Largest absolute drop</strong> at stage {ba['index']} "
            f"({esc(ba['name'])}): {ba['drop_absolute']} users "
            f"({_pct(ba['drop_rate'])} of the prior stage).</p>"
            "</ac:rich-text-body></ac:structured-macro>"
        )
    if a.get("bottleneck_rate"):
        br = a["bottleneck_rate"]
        out.append(
            '<ac:structured-macro ac:name="info"><ac:rich-text-body>'
            f"<p><strong>Worst conversion rate</strong> at stage {br['index']} "
            f"({esc(br['name'])}): "
            f"{_pct(br['conversion_from_prev'])} from the prior stage.</p>"
            "</ac:rich-text-body></ac:structured-macro>"
        )
    out.append("<h3>Funnel diagram</h3>")
    out.append(
        '<ac:structured-macro ac:name="code">'
        '<ac:parameter ac:name="language">none</ac:parameter>'
        "<ac:plain-text-body><![CDATA["
        + fmt_mermaid_raw(a)
        + "]]></ac:plain-text-body></ac:structured-macro>"
    )
    return "\n".join(out)


def fmt_notion(a: dict[str, Any]) -> str:
    lines = [
        f"## Funnel Analysis: {a['name']}",
        "",
        f"**Framework:** {a['framework']} | **Cohort:** {a['cohort']}",
        "",
        f"> [!TIP]",
        f"> Overall top-to-bottom conversion: {_pct(a['overall_top_to_bottom'])}",
        "",
        "### Stage-by-stage",
        "",
        "| # | Stage | Count | Conv. | Drop (abs) | Cumulative | Counter-metric |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for r in a["stages"]:
        lines.append(
            "| {i} | {n} | {c} | {cv} | {da} | {cu} | {cm} |".format(
                i=r["index"],
                n=r["name"],
                c=r["count"],
                cv="-" if r["index"] == 0 else _pct(r["conversion_from_prev"]),
                da="-" if r["index"] == 0 else r["drop_absolute"],
                cu=_pct(r["cumulative_conversion"]),
                cm=r.get("counter_metric") or "-",
            )
        )

    lines += ["", "### Bottlenecks", ""]
    if a.get("bottleneck_absolute"):
        ba = a["bottleneck_absolute"]
        lines.append(
            f"> [!WARNING]"
        )
        lines.append(
            f"> Largest absolute drop: stage {ba['index']} ({ba['name']}) -- "
            f"{ba['drop_absolute']} users lost ({_pct(ba['drop_rate'])} of prior)."
        )
        lines.append("")
    if a.get("bottleneck_rate"):
        br = a["bottleneck_rate"]
        lines.append(f"> [!NOTE]")
        lines.append(
            f"> Worst conversion rate: stage {br['index']} ({br['name']}) -- "
            f"{_pct(br['conversion_from_prev'])} from prior stage."
        )
        lines.append("")
    lines += ["### Funnel diagram", "", _mermaid_block(a), ""]
    return "\n".join(lines)


def fmt_linear(a: dict[str, Any]) -> str:
    lines = [
        f"**Funnel: {a['name']}**",
        "",
        f"Framework: {a['framework']} | Cohort: {a['cohort']}",
        f"Overall conversion: {_pct(a['overall_top_to_bottom'])}",
        "",
        "**Stages**",
    ]
    for r in a["stages"]:
        if r["index"] == 0:
            lines.append(f"- {r['name']}: {r['count']} (top of funnel)")
        else:
            lines.append(
                f"- {r['name']}: {r['count']} "
                f"(conv {_pct(r['conversion_from_prev'])}, "
                f"-{r['drop_absolute']} from prev) "
                f"~~{_priority_tag(r['drop_rate'])}~~"
            )
            if r.get("counter_metric"):
                lines.append(f"  - counter-metric: {r['counter_metric']}")

    lines += ["", "**Bottlenecks**"]
    if a.get("bottleneck_absolute"):
        ba = a["bottleneck_absolute"]
        lines.append(
            f"- ~~Urgent~~ largest abs drop at stage {ba['index']} "
            f"({ba['name']}): -{ba['drop_absolute']} users"
        )
    if a.get("bottleneck_rate"):
        br = a["bottleneck_rate"]
        lines.append(
            f"- ~~High~~ worst rate at stage {br['index']} "
            f"({br['name']}): {_pct(br['conversion_from_prev'])}"
        )
    return "\n".join(lines)


def _priority_tag(drop_rate: float) -> str:
    if drop_rate >= 0.6:
        return "Urgent"
    if drop_rate >= 0.4:
        return "High"
    if drop_rate >= 0.2:
        return "Medium"
    return "Low"


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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Analyze an activation / Pirate Metrics funnel from JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python funnel_analyzer.py --demo --format markdown\n"
            "  python funnel_analyzer.py --input funnel.json --format mermaid\n"
            "  python funnel_analyzer.py --demo --format json --output out.json\n"
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to JSON funnel definition")
    g.add_argument("--demo", action="store_true", help="Use built-in demo funnel")
    p.add_argument(
        "--format",
        choices=list(FORMATTERS.keys()),
        default="markdown",
        help="Output format (default: markdown)",
    )
    p.add_argument("--output", help="Write to file instead of stdout")
    p.add_argument("--name", help="Override funnel name")
    p.add_argument("--cohort", help="Override cohort label")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.demo:
        data = json.loads(json.dumps(DEMO_DATA))  # deep copy
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid JSON in {args.input}: {e}", file=sys.stderr)
            return 2

    if args.name:
        data["name"] = args.name
    if args.cohort:
        data["cohort"] = args.cohort

    try:
        analysis = analyze(data)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    rendered = FORMATTERS[args.format](analysis)

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
