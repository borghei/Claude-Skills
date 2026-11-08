#!/usr/bin/env python3
"""Status Generator -- weekly executive status update from structured JSON.

Ingests a JSON dump (representing Jira/Linear/manual data for a reporting
period) and emits a structured status update with five sections:
  1. Highlights
  2. Blockers
  3. Risks
  4. Asks
  5. What's Next

Plus a traffic-light verdict (GREEN / YELLOW / RED) for the period.

Supports all six SHARED_OUTPUT_SCHEMA formats: json, markdown, mermaid,
confluence, notion, linear.

Usage:
    python status_generator.py --demo --format markdown
    python status_generator.py --input status_data.json --format confluence
    python status_generator.py --input data.json --format json --output update.json
    python status_generator.py --demo --format mermaid

Standard library only. No external dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from typing import Any

SCHEMA = "pm/status-update-generator/v1"
VALID_STATUS = {"green", "yellow", "red"}

# ============================================================
# Demo data
# ============================================================

DEMO_DATA: dict[str, Any] = {
    "period": "Week of 2026-05-18",
    "project": "Acme Search Platform",
    "author": "Jane Doe (PM)",
    "status": "yellow",
    "status_rationale": (
        "Index rebuild succeeded and exceeded latency targets; Phase 2 "
        "rollout blocked on security review."
    ),
    "highlights": [
        {
            "title": "Search latency p95 down to 210ms",
            "detail": (
                "Index rebuild dropped p95 from 480ms to 210ms. Customer reports "
                "of slow search resolved."
            ),
            "ticket": "PROJ-1234",
        },
        {
            "title": "Pilot tenant Acme Inc. migrated to v2 index",
            "detail": "Zero downtime; tenant confirmed acceptance.",
            "ticket": "PROJ-1240",
        },
        {
            "title": "12 support tickets closed",
            "detail": "All open 'slow search' tickets resolved post-rebuild.",
            "ticket": None,
        },
        {
            "title": "SDK documentation refresh published",
            "detail": "New partner docs live; first partner integration started.",
            "ticket": "PROJ-1251",
        },
    ],
    "blockers": [
        {
            "what": "Phase 2 rollout to enterprise tenants",
            "blocked_by": "Security review (InfoSec team)",
            "need": (
                "Schedule the threat-model review before Friday so rollout "
                "can begin next sprint."
            ),
        }
    ],
    "risks": [
        {
            "risk": "Cost overrun on infra during traffic ramp",
            "likelihood": "M",
            "impact": "M",
            "mitigation": "Add auto-scale ceiling; alert at 80% budget",
            "owner": "SRE lead",
            "due": "2026-05-30",
        },
        {
            "risk": "Index rebuild causes brief read latency on next refresh",
            "likelihood": "L",
            "impact": "M",
            "mitigation": "Rebuild during off-peak window; pre-warm cache",
            "owner": "Search infra eng",
            "due": "2026-06-05",
        },
    ],
    "asks": [
        {
            "what": "Approval to onboard 3 pilot enterprise tenants",
            "by_when": "2026-05-24",
            "from_whom": "VP Sales",
            "consequence": (
                "Slips the Q2 enterprise revenue target by ~$80K if delayed "
                "past 2026-05-31."
            ),
        }
    ],
    "next": [
        {
            "title": "Complete security review and start Phase 2 rollout",
            "detail": "Begin with the 3 pilot tenants pending VP Sales sign-off.",
        },
        {
            "title": "Q2 OKR mid-quarter readout",
            "detail": "KR1 (latency) is met; KR2 (rollout) tracking on plan.",
        },
        {
            "title": "Begin Phase 3 design",
            "detail": "Multi-tenant index sharding RFC drafted.",
        },
    ],
}


# ============================================================
# Helpers
# ============================================================

def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _badge(status: str) -> str:
    return {"green": "GREEN", "yellow": "YELLOW", "red": "RED"}.get(
        status.lower(), status.upper()
    )


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Apply defaults and minor normalization to incoming data."""
    out = dict(data)
    out["status"] = str(data.get("status") or "").lower()
    if out["status"] not in VALID_STATUS:
        # R/Y/G is a human judgment: never default it to green.
        raise ValueError("status must be green, yellow or red; set it in the file or with --status")
    out.setdefault("highlights", [])
    out.setdefault("blockers", [])
    out.setdefault("risks", [])
    out.setdefault("asks", [])
    out.setdefault("next", [])
    out.setdefault("status_rationale", "")
    out.setdefault("project", "Project")
    out.setdefault("author", "PM")
    out.setdefault("period", _now_iso())
    return out


# ============================================================
# Formatters
# ============================================================

def fmt_markdown(d: dict[str, Any]) -> str:
    lines = [
        f"# {d['project']} -- {d['period']}",
        "",
        f"**Author:** {d['author']} | **Status:** {_badge(d['status'])}",
        f"**Rationale:** {d['status_rationale']}",
        "",
        "## Highlights",
        "",
    ]
    if d["highlights"]:
        for h in d["highlights"]:
            ticket = f" ({h['ticket']})" if h.get("ticket") else ""
            lines.append(f"- **{h.get('title','(no title)')}**{ticket}")
            if h.get("detail"):
                lines.append(f"  - {h['detail']}")
    else:
        lines.append("None this week.")

    lines += ["", "## Blockers", ""]
    if d["blockers"]:
        for b in d["blockers"]:
            lines.append(f"- **{b.get('what','(no description)')}**")
            if b.get("blocked_by"):
                lines.append(f"  - Blocked by: {b['blocked_by']}")
            if b.get("need"):
                lines.append(f"  - Need: {b['need']}")
    else:
        lines.append("None this week.")

    lines += ["", "## Risks", ""]
    if d["risks"]:
        lines.append("| Risk | L | I | Mitigation | Owner | Due |")
        lines.append("|------|---|---|------------|-------|-----|")
        for r in d["risks"]:
            lines.append(
                "| {risk} | {l} | {i} | {m} | {o} | {d} |".format(
                    risk=r.get("risk", ""),
                    l=r.get("likelihood", ""),
                    i=r.get("impact", ""),
                    m=r.get("mitigation", ""),
                    o=r.get("owner", ""),
                    d=r.get("due", ""),
                )
            )
    else:
        lines.append("No new risks this week.")

    lines += ["", "## Asks", ""]
    if d["asks"]:
        for i, a in enumerate(d["asks"], 1):
            lines.append(f"{i}. **{a.get('what','(no ask)')}**")
            meta = []
            if a.get("from_whom"):
                meta.append(f"From: {a['from_whom']}")
            if a.get("by_when"):
                meta.append(f"By: {a['by_when']}")
            if meta:
                lines.append(f"   - {' -- '.join(meta)}")
            if a.get("consequence"):
                lines.append(f"   - Consequence: {a['consequence']}")
    else:
        lines.append("None this week.")

    lines += ["", "## What's Next", ""]
    if d["next"]:
        for n in d["next"]:
            lines.append(f"- **{n.get('title','(no title)')}**")
            if n.get("detail"):
                lines.append(f"  - {n['detail']}")
    else:
        lines.append("To be scoped.")

    lines += ["", "---", f"_Generated {_now_iso()}_"]
    return "\n".join(lines)


def fmt_json(d: dict[str, Any]) -> str:
    payload = {
        "schema": SCHEMA,
        "generated_at": _now_iso(),
        "data": d,
    }
    return json.dumps(payload, indent=2)


def fmt_mermaid(d: dict[str, Any]) -> str:
    counts = {
        "Highlights": len(d["highlights"]),
        "Blockers": len(d["blockers"]),
        "Risks": len(d["risks"]),
        "Asks": len(d["asks"]),
    }
    rows = "\n".join(f'    "{k} ({v})" : {v}' for k, v in counts.items() if v > 0)
    if not rows:
        rows = '    "No items" : 1'
    return "\n".join(
        [
            "```mermaid",
            f"pie title {d['project']} -- {d['period']} -- {_badge(d['status'])}",
            rows,
            "```",
        ]
    )


def fmt_confluence(d: dict[str, Any]) -> str:
    def esc(s: Any) -> str:
        return html.escape(str(s)) if s is not None else ""

    macro_color = {
        "green": "tip",
        "yellow": "note",
        "red": "warning",
    }.get(d["status"], "info")

    out = [
        f"<h2>{esc(d['project'])} -- {esc(d['period'])}</h2>",
        f"<p><strong>Author:</strong> {esc(d['author'])} | "
        f"<strong>Status:</strong> {esc(_badge(d['status']))}</p>",
        f'<ac:structured-macro ac:name="{macro_color}">',
        f"  <ac:rich-text-body><p>{esc(d['status_rationale'])}</p></ac:rich-text-body>",
        "</ac:structured-macro>",
        "<h3>Highlights</h3>",
        "<ul>",
    ]
    for h in d["highlights"]:
        ticket = f" ({esc(h.get('ticket'))})" if h.get("ticket") else ""
        detail = f" -- {esc(h.get('detail',''))}" if h.get("detail") else ""
        out.append(
            f"  <li><strong>{esc(h.get('title',''))}</strong>{ticket}{detail}</li>"
        )
    out.append("</ul>")

    out += ["<h3>Blockers</h3>"]
    if d["blockers"]:
        out.append("<ul>")
        for b in d["blockers"]:
            out.append(
                f"  <li><strong>{esc(b.get('what',''))}</strong> -- "
                f"Blocked by: {esc(b.get('blocked_by',''))} -- "
                f"Need: {esc(b.get('need',''))}</li>"
            )
        out.append("</ul>")
    else:
        out.append("<p>None this week.</p>")

    out += ["<h3>Risks</h3>"]
    if d["risks"]:
        out.append("<table><tr><th>Risk</th><th>L</th><th>I</th>"
                   "<th>Mitigation</th><th>Owner</th><th>Due</th></tr>")
        for r in d["risks"]:
            out.append(
                f"<tr><td>{esc(r.get('risk',''))}</td>"
                f"<td>{esc(r.get('likelihood',''))}</td>"
                f"<td>{esc(r.get('impact',''))}</td>"
                f"<td>{esc(r.get('mitigation',''))}</td>"
                f"<td>{esc(r.get('owner',''))}</td>"
                f"<td>{esc(r.get('due',''))}</td></tr>"
            )
        out.append("</table>")
    else:
        out.append("<p>No new risks this week.</p>")

    out += ["<h3>Asks</h3>"]
    if d["asks"]:
        out.append("<ol>")
        for a in d["asks"]:
            meta = (
                f"From: {esc(a.get('from_whom',''))} | "
                f"By: {esc(a.get('by_when',''))}"
            )
            out.append(
                f"  <li><strong>{esc(a.get('what',''))}</strong> -- "
                f"{meta} -- Consequence: {esc(a.get('consequence',''))}</li>"
            )
        out.append("</ol>")
    else:
        out.append("<p>None this week.</p>")

    out += ["<h3>What's Next</h3>", "<ul>"]
    for n in d["next"]:
        detail = f" -- {esc(n.get('detail',''))}" if n.get("detail") else ""
        out.append(
            f"  <li><strong>{esc(n.get('title',''))}</strong>{detail}</li>"
        )
    out.append("</ul>")
    return "\n".join(out)


def fmt_notion(d: dict[str, Any]) -> str:
    callout = {
        "green": "> [!TIP]",
        "yellow": "> [!NOTE]",
        "red": "> [!WARNING]",
    }.get(d["status"], "> [!NOTE]")

    out = [
        f"## {d['project']} -- {d['period']}",
        "",
        f"**Author:** {d['author']} | **Status:** {_badge(d['status'])}",
        "",
        callout,
        f"> {d['status_rationale']}",
        "",
        "### Highlights",
        "",
    ]
    if d["highlights"]:
        for h in d["highlights"]:
            ticket = f" ({h['ticket']})" if h.get("ticket") else ""
            line = f"- {h.get('title','')}{ticket}"
            if h.get("detail"):
                line += f" -- {h['detail']}"
            out.append(line)
    else:
        out.append("- None this week.")

    out += ["", "### Blockers", ""]
    if d["blockers"]:
        for b in d["blockers"]:
            out.append(
                f"- [ ] {b.get('what','')} -- Blocked by: "
                f"{b.get('blocked_by','')} -- Need: {b.get('need','')}"
            )
    else:
        out.append("- None this week.")

    out += ["", "### Risks", "", "| Risk | L | I | Mitigation | Owner | Due |",
            "|------|---|---|------------|-------|-----|"]
    if d["risks"]:
        for r in d["risks"]:
            out.append(
                f"| {r.get('risk','')} | {r.get('likelihood','')} | "
                f"{r.get('impact','')} | {r.get('mitigation','')} | "
                f"{r.get('owner','')} | {r.get('due','')} |"
            )
    else:
        out.append("| No new risks this week. | | | | | |")

    out += ["", "### Asks", ""]
    if d["asks"]:
        for a in d["asks"]:
            out.append(
                f"- [ ] **{a.get('what','')}** -- From: "
                f"{a.get('from_whom','')} -- By: {a.get('by_when','')} -- "
                f"Consequence: {a.get('consequence','')}"
            )
    else:
        out.append("- None this week.")

    out += ["", "### What's Next", ""]
    for n in d["next"]:
        line = f"- {n.get('title','')}"
        if n.get("detail"):
            line += f" -- {n['detail']}"
        out.append(line)

    out += ["", "---", f"_Generated {_now_iso()}_"]
    return "\n".join(out)


def fmt_linear(d: dict[str, Any]) -> str:
    prio = {
        "green": "~~Low~~",
        "yellow": "~~Medium~~",
        "red": "~~Urgent~~",
    }.get(d["status"], "~~Medium~~")

    out = [
        f"**{d['project']} -- {d['period']}**",
        "",
        f"Status: {_badge(d['status'])} {prio} | Author: {d['author']}",
        f"_{d['status_rationale']}_",
        "",
        "**Highlights**",
    ]
    for h in d["highlights"]:
        ticket = f" [{h['ticket']}]" if h.get("ticket") else ""
        out.append(f"- {h.get('title','')}{ticket}")

    out += ["", "**Blockers**"]
    if d["blockers"]:
        for b in d["blockers"]:
            out.append(
                f"- {b.get('what','')} -- blocked by {b.get('blocked_by','')} "
                f"-- need: {b.get('need','')}"
            )
    else:
        out.append("- None this week.")

    out += ["", "**Risks**"]
    if d["risks"]:
        for r in d["risks"]:
            out.append(
                f"- {r.get('risk','')} (L:{r.get('likelihood','')} "
                f"I:{r.get('impact','')}) -- {r.get('mitigation','')} "
                f"(@{r.get('owner','')}, due {r.get('due','')})"
            )
    else:
        out.append("- No new risks this week.")

    out += ["", "**Asks**"]
    if d["asks"]:
        for a in d["asks"]:
            out.append(
                f"- {a.get('what','')} -- @{a.get('from_whom','')} "
                f"by {a.get('by_when','')} (else: {a.get('consequence','')})"
            )
    else:
        out.append("- None this week.")

    out += ["", "**Next**"]
    for n in d["next"]:
        out.append(f"- {n.get('title','')}")
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

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Generate a structured weekly status update from JSON input."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python status_generator.py --demo --format markdown\n"
            "  python status_generator.py --input data.json --format confluence\n"
            "  python status_generator.py --demo --format json --output update.json\n"
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to JSON status data file")
    g.add_argument("--demo", action="store_true", help="Use built-in demo data")
    p.add_argument(
        "--format",
        choices=list(FORMATTERS.keys()),
        default="markdown",
        help="Output format (default: markdown)",
    )
    p.add_argument("--output", help="Write to file instead of stdout")
    p.add_argument("--period", help="Override period label")
    p.add_argument(
        "--status",
        choices=["green", "yellow", "red"],
        help="Override traffic light status",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.demo:
        data = DEMO_DATA
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

    if args.period:
        data = dict(data, period=args.period)
    if args.status:
        data = dict(data, status=args.status)

    if not isinstance(data, dict):
        print(f"ERROR: {args.input}: top level must be a JSON object (see --demo --format json)", file=sys.stderr)
        return 2
    try:
        data = _normalize(data)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rendered = FORMATTERS[args.format](data)

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
