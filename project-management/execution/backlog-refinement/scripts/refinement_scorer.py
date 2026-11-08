#!/usr/bin/env python3
"""Refinement Scorer -- grade backlog stories against INVEST and emit readiness verdicts.

For each story in a JSON backlog, this tool scores six INVEST criteria
(Independent, Negotiable, Valuable, Estimable, Small, Testable) and
returns a per-story score 0-6 plus a backlog-level readiness summary.

Usage:
    python refinement_scorer.py --input backlog.json --format markdown
    python refinement_scorer.py --demo --format json
    python refinement_scorer.py --demo --format mermaid --output chart.md
    python refinement_scorer.py --input backlog.json --format confluence

Supported --format values (per project-management/SHARED_OUTPUT_SCHEMA.md):
    json, markdown, mermaid, confluence, notion, linear

Standard library only. No external dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any

SCHEMA = "pm/backlog-refinement/v1"
DEFAULT_THRESHOLD = 5

# ============================================================
# Scoring logic
# ============================================================

VALUE_KEYWORDS = re.compile(
    r"\b(okr|metric|revenue|retention|churn|adoption|activation|customer|user|ARR|MRR|"
    r"reduce|increase|grow|conversion|engagement|cost|risk|compliance|north star|nps)\b",
    re.IGNORECASE,
)


def score_invest(story: dict[str, Any]) -> dict[str, Any]:
    why = (story.get("why") or "").strip()
    what = (story.get("what") or story.get("description") or "").strip()
    acs = story.get("acceptance_criteria") or []
    estimate = story.get("estimate_days")
    dependencies = story.get("dependencies") or []

    criteria = {}

    # Independent: no listed dependencies
    criteria["Independent"] = {
        "pass": len(dependencies) == 0,
        "reason": (
            "No declared dependencies" if not dependencies
            else f"Depends on: {', '.join(str(d) for d in dependencies)}"
        ),
    }

    # Negotiable: WHAT exists and is under 800 chars
    criteria["Negotiable"] = {
        "pass": 0 < len(what) <= 800,
        "reason": (
            "WHAT is present and under 800 chars (open to implementation discussion)"
            if 0 < len(what) <= 800
            else (
                "WHAT is missing"
                if not what
                else f"WHAT is {len(what)} chars -- likely prescribes implementation"
            )
        ),
    }

    # Valuable: WHY exists and references a metric/outcome keyword
    has_value_signal = bool(why) and bool(VALUE_KEYWORDS.search(why))
    criteria["Valuable"] = {
        "pass": has_value_signal,
        "reason": (
            "WHY references a measurable outcome or customer/business signal"
            if has_value_signal
            else (
                "WHY is missing -- add a strategic reason"
                if not why
                else "WHY does not reference a metric, customer, or business outcome"
            )
        ),
    }

    # Estimable: estimate present and positive
    estimable = isinstance(estimate, (int, float)) and estimate > 0
    criteria["Estimable"] = {
        "pass": estimable,
        "reason": (
            f"Team estimated at {estimate} days"
            if estimable
            else "No estimate provided -- team cannot size the work"
        ),
    }

    # Small: estimate between 1 and 5 days inclusive
    small = estimable and 1 <= estimate <= 5
    criteria["Small"] = {
        "pass": small,
        "reason": (
            f"{estimate} days fits in a sprint"
            if small
            else (
                "No estimate to evaluate" if not estimable
                else f"{estimate} days exceeds the 5-day cap -- split required"
            )
        ),
    }

    # Testable: at least 4 acceptance criteria
    testable = isinstance(acs, list) and len(acs) >= 4
    criteria["Testable"] = {
        "pass": testable,
        "reason": (
            f"{len(acs)} acceptance criteria (>=4 required)"
            if testable
            else f"Only {len(acs)} acceptance criteria -- need at least 4"
        ),
    }

    score = sum(1 for c in criteria.values() if c["pass"])

    return {
        "id": story.get("id", "(no id)"),
        "title": story.get("title", "(untitled)"),
        "score": score,
        "max_score": 6,
        "criteria": criteria,
    }


def verdict_for_score(score: int, threshold: int) -> str:
    if score >= threshold:
        return "READY"
    if score >= 3:
        return "REFINE"
    return "SEND_TO_DISCOVERY"


def grade_backlog(stories: list[dict[str, Any]], threshold: int) -> dict[str, Any]:
    graded = [score_invest(s) for s in stories]
    for g in graded:
        g["verdict"] = verdict_for_score(g["score"], threshold)

    summary = {
        "total_stories": len(graded),
        "ready": sum(1 for g in graded if g["verdict"] == "READY"),
        "refine": sum(1 for g in graded if g["verdict"] == "REFINE"),
        "send_to_discovery": sum(
            1 for g in graded if g["verdict"] == "SEND_TO_DISCOVERY"
        ),
        "average_score": (
            round(sum(g["score"] for g in graded) / len(graded), 2) if graded else 0
        ),
        "threshold": threshold,
    }

    return {"stories": graded, "summary": summary}


# ============================================================
# Demo data
# ============================================================

DEMO_BACKLOG = {
    "stories": [
        {
            "id": "STORY-101",
            "title": "Add SSO login for enterprise users",
            "why": (
                "Enterprise customers cite missing SSO as the #1 blocker; supports "
                "our $2M ARR expansion target this quarter."
            ),
            "what": (
                "Add SAML 2.0 SSO option to the login page. Users with configured "
                "company domains see SSO as the primary login method; password "
                "login remains as fallback. Support Okta and Azure AD at launch."
            ),
            "acceptance_criteria": [
                "Users with configured domains see SSO as primary login option",
                "SAML 2.0 IdP-initiated flow works for Okta and Azure AD",
                "Failed SSO falls back to password with a helpful error",
                "Audit log records every SSO login attempt",
            ],
            "estimate_days": 4,
            "dependencies": [],
        },
        {
            "id": "STORY-102",
            "title": "Implement the new dashboard",
            "why": "Customers want a better dashboard.",
            "what": (
                "Build the new dashboard with all the widgets, charts, exports, "
                "filters, sharing, and customization features the team has been "
                "discussing for the last several months."
            ),
            "acceptance_criteria": [
                "It works",
                "Users like it",
            ],
            "estimate_days": 18,
            "dependencies": ["STORY-088", "STORY-091"],
        },
        {
            "id": "STORY-103",
            "title": "Export search results as CSV",
            "why": (
                "Power users export search results to feed downstream workflows; "
                "reduces support tickets related to manual copy-paste."
            ),
            "what": (
                "Add a 'Download CSV' button to the search results page. Generates "
                "a CSV of the current result set (max 10K rows) with the same "
                "columns visible on screen."
            ),
            "acceptance_criteria": [
                "Button visible on search results page when results > 0",
                "Downloaded CSV matches the on-screen columns and order",
                "Export capped at 10K rows with a clear notice when truncated",
                "Filename follows pattern: search-results-YYYY-MM-DD.csv",
            ],
            "estimate_days": 3,
            "dependencies": [],
        },
        {
            "id": "STORY-104",
            "title": "Refactor the auth module",
            "why": "Code is messy.",
            "what": "Clean up the auth module.",
            "acceptance_criteria": [
                "Code is cleaner",
            ],
            "estimate_days": None,
            "dependencies": [],
        },
    ]
}


# ============================================================
# Formatters
# ============================================================

def _verdict_emoji(verdict: str) -> str:
    return {
        "READY": "[READY]",
        "REFINE": "[REFINE]",
        "SEND_TO_DISCOVERY": "[DISCOVERY]",
    }.get(verdict, "[?]")


def fmt_markdown(graded: dict[str, Any]) -> str:
    s = graded["summary"]
    out = [
        "# Backlog Refinement Report",
        "",
        f"_Generated: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## Summary",
        "",
        f"- **Total stories graded:** {s['total_stories']}",
        f"- **Ready** (score >= {s['threshold']}): {s['ready']}",
        f"- **Refine** (score 3-{s['threshold']-1}): {s['refine']}",
        f"- **Send to discovery** (score 0-2): {s['send_to_discovery']}",
        f"- **Average INVEST score:** {s['average_score']}/6",
        "",
        "## Story-by-story",
        "",
        "| ID | Title | Score | Verdict |",
        "|----|-------|-------|---------|",
    ]
    for g in graded["stories"]:
        out.append(
            f"| {g['id']} | {g['title']} | {g['score']}/6 | "
            f"{_verdict_emoji(g['verdict'])} {g['verdict']} |"
        )

    out.append("")
    out.append("## Per-criterion detail")
    out.append("")
    for g in graded["stories"]:
        out.append(f"### {g['id']} -- {g['title']}")
        out.append("")
        out.append(f"**Score:** {g['score']}/6 -- **Verdict:** {g['verdict']}")
        out.append("")
        out.append("| Criterion | Pass | Reason |")
        out.append("|-----------|------|--------|")
        for name, c in g["criteria"].items():
            mark = "PASS" if c["pass"] else "FAIL"
            out.append(f"| {name} | {mark} | {c['reason']} |")
        out.append("")
    return "\n".join(out)


def fmt_json(graded: dict[str, Any]) -> str:
    payload = {
        "schema": SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": graded,
    }
    return json.dumps(payload, indent=2)


def fmt_mermaid(graded: dict[str, Any]) -> str:
    s = graded["summary"]
    return "\n".join(
        [
            "```mermaid",
            "pie title Backlog Readiness",
            f'    "Ready ({s["ready"]})" : {s["ready"]}',
            f'    "Refine ({s["refine"]})" : {s["refine"]}',
            f'    "Send to discovery ({s["send_to_discovery"]})" : '
            f"{s['send_to_discovery']}",
            "```",
        ]
    )


def fmt_confluence(graded: dict[str, Any]) -> str:
    s = graded["summary"]
    rows = []
    for g in graded["stories"]:
        rows.append(
            f"<tr><td>{g['id']}</td><td>{g['title']}</td>"
            f"<td>{g['score']}/6</td><td>{g['verdict']}</td></tr>"
        )
    rows_html = "\n".join(rows)
    return f"""<h2>Backlog Refinement Report</h2>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>Total: {s['total_stories']} -- Ready: {s['ready']} -- Refine: {s['refine']} -- Send back: {s['send_to_discovery']} -- Avg: {s['average_score']}/6</p>
  </ac:rich-text-body>
</ac:structured-macro>
<table>
<tr><th>ID</th><th>Title</th><th>Score</th><th>Verdict</th></tr>
{rows_html}
</table>"""


def fmt_notion(graded: dict[str, Any]) -> str:
    s = graded["summary"]
    out = [
        "## Backlog Refinement Report",
        "",
        "> [!NOTE]",
        f"> Total: {s['total_stories']} | Ready: {s['ready']} | "
        f"Refine: {s['refine']} | Send back: {s['send_to_discovery']} | "
        f"Avg: {s['average_score']}/6",
        "",
        "| ID | Title | Score | Verdict |",
        "|----|-------|-------|---------|",
    ]
    for g in graded["stories"]:
        out.append(
            f"| {g['id']} | {g['title']} | {g['score']}/6 | {g['verdict']} |"
        )
    out.append("")
    out.append("---")
    out.append("")
    out.append("### Action items")
    out.append("")
    for g in graded["stories"]:
        if g["verdict"] == "REFINE":
            out.append(f"- [ ] Refine {g['id']} -- {g['title']}")
        elif g["verdict"] == "SEND_TO_DISCOVERY":
            out.append(
                f"- [ ] Move {g['id']} -- {g['title']} to discovery backlog"
            )
    return "\n".join(out)


def fmt_linear(graded: dict[str, Any]) -> str:
    s = graded["summary"]
    out = [
        "**Backlog Refinement Report**",
        "",
        f"Total: {s['total_stories']} | Ready: {s['ready']} | "
        f"Refine: {s['refine']} | Send back: {s['send_to_discovery']} | "
        f"Avg score: {s['average_score']}/6",
        "",
    ]
    for g in graded["stories"]:
        prio = {
            "READY": "~~Low~~",
            "REFINE": "~~Medium~~",
            "SEND_TO_DISCOVERY": "~~High~~",
        }[g["verdict"]]
        out.append(
            f"- [{g['id']}] {g['title']} -- {g['score']}/6 "
            f"-- {g['verdict']} {prio}"
        )
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
            "Grade backlog stories against INVEST and emit readiness verdicts."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python refinement_scorer.py --demo --format markdown\n"
            "  python refinement_scorer.py --input backlog.json --format json\n"
            "  python refinement_scorer.py --demo --format mermaid\n"
        ),
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to JSON backlog file")
    g.add_argument(
        "--demo", action="store_true", help="Use the built-in demo backlog"
    )
    p.add_argument(
        "--format",
        choices=list(FORMATTERS.keys()),
        default="markdown",
        help="Output format (default: markdown)",
    )
    p.add_argument("--output", help="Write to file instead of stdout")
    p.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Min score to be considered READY (default: {DEFAULT_THRESHOLD})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.demo:
        backlog = DEMO_BACKLOG
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                backlog = json.load(f)
        except OSError:
            print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid JSON in {args.input}: {e}", file=sys.stderr)
            return 2

    stories = backlog.get("stories") if isinstance(backlog, dict) else None
    if not isinstance(stories, list) or not all(isinstance(s, dict) for s in stories):
        print("error: input must be a JSON object with a 'stories' list of objects", file=sys.stderr)
        return 2

    graded = grade_backlog(stories, threshold=args.threshold)
    rendered = FORMATTERS[args.format](graded)

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
    try:
        sys.exit(main())
    except (TypeError, ValueError, AttributeError, KeyError) as exc:  # field of the wrong type
        print(f"error: input has a field of the wrong type: {exc}", file=sys.stderr)
        sys.exit(2)
