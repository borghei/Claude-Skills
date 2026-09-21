#!/usr/bin/env python3
"""
agent_delegation_scorer.py - Score backlog tickets for AI-agent eligibility
and check planned agent work against human review capacity.

Each ticket gets a 0-100 eligibility score from clarity, risk, blast radius,
verifiability and ticket type, plus hard blocks for sensitive areas. Then
the review hours needed for tickets planned for agents (with a rework
allowance) are compared with the reviewer hours the team actually has.

Stdlib only. Deterministic.

Usage:
    python3 agent_delegation_scorer.py --input backlog.json
    python3 agent_delegation_scorer.py --input backlog.json --format json

Exit codes:
    0  plan fits review capacity and no policy violations
    1  tool error (bad path, invalid JSON, invalid field values)
    2  gate failed: planned agent review load exceeds review capacity, or a
       ticket planned for an agent is scored human-only / hard-blocked
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "pm/agents-in-the-team/delegation/v1"
RISK = {"low": 25, "medium": 12, "high": 0}
BLAST = {"isolated": 20, "module": 15, "service": 8, "cross-system": 0, "customer-data": 0}
COVERAGE = {"good": 15, "partial": 8, "none": 0}
TYPE_FIT = {"test": 10, "docs": 10, "dependency-update": 10, "chore": 9, "bug": 8,
            "refactor": 7, "feature": 5, "migration": 2, "spike": 1, "incident": 0,
            "architecture": 0, "security": 3}
HARD_BLOCK_AREAS = {"auth", "payments", "secrets", "pii", "iam", "prod-migration", "crypto"}
HARD_BLOCK_TYPES = {"incident", "architecture"}
RISK_REVIEW_MULT = {"low": 1.0, "medium": 1.5, "high": 2.0}


def fail(msg: str) -> None:
    """Print a tool error and exit 1."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def pick(t: dict[str, Any], field: str, table: dict[str, int], default: str) -> str:
    """Read an enumerated field and validate it against a table."""
    val = str(t.get(field, default)).lower()
    if val not in table:
        fail(f"ticket {t.get('id', '?')}: {field} must be one of {', '.join(table)}")
    return val


def score_ticket(t: dict[str, Any], model: dict[str, float]) -> dict[str, Any]:
    """Score one ticket and estimate its review hours."""
    tid = str(t.get("id", "?"))
    risk = pick(t, "risk", RISK, "medium")
    blast = pick(t, "blast_radius", BLAST, "module")
    cov = pick(t, "test_coverage", COVERAGE, "partial")
    ttype = pick(t, "type", TYPE_FIT, "feature")
    acs = t.get("acceptance_criteria") or []
    reasons: list[str] = []

    ac_pts = 20 if len(acs) >= 2 else (10 if len(acs) == 1 else 0)
    if ac_pts < 20:
        reasons.append(f"{len(acs)} acceptance criteria - agents need 2+ checkable criteria")
    ctx_pts = (5 if t.get("context_links") else 0) + (5 if t.get("constraints") else 0)
    if ctx_pts < 10:
        reasons.append("missing context links or constraints (files, patterns, do-not-touch)")
    score = ac_pts + ctx_pts + RISK[risk] + BLAST[blast] + COVERAGE[cov] + TYPE_FIT[ttype]
    if risk != "low":
        reasons.append(f"{risk} risk")
    if BLAST[blast] <= 8:
        reasons.append(f"blast radius '{blast}'")
    if cov == "none":
        reasons.append("no automated tests to verify the change")

    touches = {str(x).lower() for x in t.get("touches") or []}
    blocked = sorted(touches & HARD_BLOCK_AREAS)
    if blocked:
        reasons.append("hard block: touches " + ", ".join(blocked))
    if ttype in HARD_BLOCK_TYPES:
        blocked.append(ttype)
        reasons.append(f"hard block: type '{ttype}' needs human judgement")

    if blocked:
        band = "human-only"
    elif score >= 75:
        band = "agent-eligible"
    elif score >= 50:
        band = "agent-assisted"
    else:
        band = "human-only"

    if t.get("est_review_hours") is not None:
        try:
            review = float(t["est_review_hours"])
        except (TypeError, ValueError):
            fail(f"ticket {tid}: est_review_hours must be a number")
    else:
        pts = float(t.get("points", 1) or 1)
        review = (model["base_hours"] + model["hours_per_point"] * pts) * RISK_REVIEW_MULT[risk]
    review = round(review * (1 + model["rework_allowance"]), 2)
    planned = str(t.get("planned_assignee", "")).lower()
    return {"id": tid, "title": t.get("title", ""), "type": ttype, "score": score, "band": band,
            "planned_assignee": planned or "unplanned", "review_hours": review,
            "reasons": reasons or ["clear, low-risk, verifiable"]}


def analyze(doc: dict[str, Any]) -> dict[str, Any]:
    """Score the backlog and run the review-capacity gate."""
    tickets = doc.get("tickets")
    if not isinstance(tickets, list) or not tickets:
        fail("input needs a non-empty 'tickets' list")
    team = doc.get("team", {}) or {}
    reviewers = team.get("reviewers") or []
    try:
        hours = sum(float(r.get("review_hours_per_sprint", 0)) for r in reviewers)
        util = float(team.get("max_review_utilization", 0.8))
        m = team.get("review_model", {}) or {}
        model = {"base_hours": float(m.get("base_hours", 0.5)),
                 "hours_per_point": float(m.get("hours_per_point", 0.5)),
                 "rework_allowance": float(m.get("rework_allowance", 0.3))}
    except (TypeError, ValueError, AttributeError):
        fail("team.reviewers[].review_hours_per_sprint, max_review_utilization and "
             "review_model values must be numbers")
    if hours <= 0:
        fail("team.reviewers must list at least one reviewer with review_hours_per_sprint > 0")
    rows = [score_ticket(t, model) for t in tickets]
    rows.sort(key=lambda r: (-r["score"], r["id"]))

    planned = [r for r in rows if r["planned_assignee"] == "agent"]
    if not planned and not any(r["planned_assignee"] != "unplanned" for r in rows):
        planned = [r for r in rows if r["band"] == "agent-eligible"]
    need = round(sum(r["review_hours"] for r in planned), 2)
    budget = round(hours * util, 2)
    violations = [f"{r['id']} planned for an agent but scored {r['band']}"
                  for r in planned if r["band"] == "human-only"]
    warnings = [f"{r['id']} planned for an agent but scored agent-assisted - tighten the "
                "ticket or have a human lead with the agent drafting"
                for r in planned if r["band"] == "agent-assisted"]
    blocking = list(violations)
    if need > budget:
        blocking.append(f"agent work needs {need} review hours; budget is {budget} "
                        f"({hours} reviewer hours x {util} max utilization) - cut "
                        f"{round(need - budget, 2)} hours of agent work or add reviewers")
    return {"team": team.get("name", ""), "sprint": doc.get("sprint", ""),
            "reviewer_hours": hours, "review_budget": budget, "planned_agent_tickets":
            [r["id"] for r in planned], "planned_review_hours": need,
            "utilization": round(need / hours, 2), "review_model": model,
            "tickets": rows, "warnings": warnings, "blocking": blocking, "passed": not blocking}


def render_markdown(res: dict[str, Any]) -> str:
    """Render the analysis as markdown."""
    out = [f"# Agent Delegation Plan: {res['team'] or 'team'} {res['sprint']}".rstrip(), "",
           "| Ticket | Type | Score | Band | Planned | Review h | Reasons |",
           "|--------|------|-------|------|---------|----------|---------|"]
    for r in res["tickets"]:
        out.append(f"| {r['id']} | {r['type']} | {r['score']} | {r['band']} | "
                   f"{r['planned_assignee']} | {r['review_hours']} | {'; '.join(r['reasons'])} |")
    out += ["", "## Review capacity", "",
            f"- Reviewer hours this sprint: {res['reviewer_hours']}",
            f"- Review budget (after utilization cap): {res['review_budget']}",
            f"- Planned agent tickets: {', '.join(res['planned_agent_tickets']) or 'none'}",
            f"- Review hours needed (incl. {int(res['review_model']['rework_allowance'] * 100)}% "
            f"rework allowance): {res['planned_review_hours']} "
            f"({int(res['utilization'] * 100)}% of reviewer hours)", "", "## Gate", "",
            "**PASS**" if res["passed"] else "**FAIL**"]
    out += [f"- warning: {w}" for w in res["warnings"]]
    out += [f"- {b}" for b in res["blocking"]]
    return "\n".join(out) + "\n"


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Score tickets for agent eligibility and check review capacity.",
        epilog="Exit codes: 0 pass, 1 tool error, 2 gate failed (over review capacity "
               "or policy violation).")
    ap.add_argument("--input", required=True, help="backlog JSON (see assets/)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown",
                    help="output format (default: markdown)")
    ap.add_argument("--output", help="write to this file instead of stdout")
    args = ap.parse_args()
    try:
        doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {args.input}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {args.input}: {exc}")
    if not isinstance(doc, dict):
        fail("top-level JSON must be an object")
    res = analyze(doc)
    text = (json.dumps({"schema": SCHEMA, "generated_at": str(doc.get("as_of", "")),
                        "data": res}, indent=2) + "\n") if args.format == "json" \
        else render_markdown(res)
    try:
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except OSError as exc:
        fail(f"cannot write output: {exc}")
    sys.exit(0 if res["passed"] else 2)


if __name__ == "__main__":
    main()
