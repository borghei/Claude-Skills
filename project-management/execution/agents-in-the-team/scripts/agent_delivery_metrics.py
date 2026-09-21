#!/usr/bin/env python3
"""
agent_delivery_metrics.py - Delivery metrics split by author type (human vs
AI agent): PR acceptance, review rework, post-merge rework, review time,
reviewer effort, escaped defects, plus the DORA instability and recovery
metrics split by whether a deployment contained agent-authored changes.

Stdlib only. Deterministic.

Usage:
    python3 agent_delivery_metrics.py --input records.json
    python3 agent_delivery_metrics.py --input records.json --gate --tolerance 0.05

Exit codes:
    0  metrics produced (and, with --gate, agent cohort within tolerance)
    1  tool error (bad path, invalid JSON, bad timestamps)
    2  --gate only: the agent cohort's change fail rate, post-merge rework
       rate or escaped-defect rate exceeds the human cohort's by more than
       --tolerance
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

SCHEMA = "pm/agents-in-the-team/delivery-metrics/v1"
MIN_SAMPLE = 10


def fail(msg: str) -> None:
    """Print a tool error and exit 1."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def ts(value: Any, where: str) -> datetime | None:
    """Parse an ISO-8601 timestamp, or None when absent."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        fail(f"{where}: bad timestamp '{value}' (use ISO-8601)")
    return None


def hours(a: datetime | None, b: datetime | None) -> float | None:
    """Hours between two timestamps."""
    return None if a is None or b is None else (b - a).total_seconds() / 3600


def ratio(n: int, d: int) -> float | None:
    """Safe ratio rounded to 3 places."""
    return round(n / d, 3) if d else None


def med(xs: list[float]) -> float | None:
    """Median rounded to 1 place, or None."""
    return round(median(xs), 1) if xs else None


def cohort(prs: list[dict[str, Any]], defects: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute PR-level metrics for one author cohort."""
    merged = [p for p in prs if p.get("state") == "merged"]
    closed = [p for p in prs if p.get("state") == "closed"]
    reworked = [p for p in merged if int(p.get("changes_requested", 0) or 0) > 0]
    ids = {str(p.get("id")) for p in merged}
    fixed = {str(p.get("fix_of")) for p in prs if p.get("fix_of")} | \
        {str(p.get("id")) for p in merged if p.get("reverted")}
    post_rework = [i for i in ids if i in fixed]
    first_review, cycle, effort = [], [], []
    for p in prs:
        o = ts(p.get("opened_at"), f"pr {p.get('id')}")
        h = hours(o, ts(p.get("first_review_at"), f"pr {p.get('id')}"))
        if h is not None:
            first_review.append(h)
        c = hours(o, ts(p.get("merged_at"), f"pr {p.get('id')}"))
        if c is not None:
            cycle.append(c)
        if p.get("review_minutes") is not None:
            effort.append(float(p["review_minutes"]))
    escaped = [d for d in defects if str(d.get("caused_by_pr")) in ids]
    return {
        "prs": len(prs), "merged": len(merged), "closed_unmerged": len(closed),
        "acceptance_rate": ratio(len(merged), len(merged) + len(closed)),
        "review_rework_rate": ratio(len(reworked), len(merged)),
        "post_merge_rework_rate": ratio(len(post_rework), len(merged)),
        "median_hours_to_first_review": med(first_review),
        "median_hours_open_to_merge": med(cycle),
        "median_reviewer_minutes_per_pr": med(effort),
        "escaped_defects": len(escaped),
        "escaped_defects_per_10_merged": round(10 * len(escaped) / len(merged), 2)
        if merged else None,
        "small_sample": len(merged) < MIN_SAMPLE,
    }


def dora(deps: list[dict[str, Any]], agent_prs: set[str]) -> dict[str, Any]:
    """DORA instability + recovery split by deployments with / without agent changes."""
    out: dict[str, Any] = {}
    groups = {"with_agent_changes": [d for d in deps if set(map(str, d.get("prs") or [])) & agent_prs],
              "human_only": [d for d in deps if not set(map(str, d.get("prs") or [])) & agent_prs]}
    groups["all"] = deps
    for name, ds in groups.items():
        failed = [d for d in ds if d.get("failed")]
        rec = [h for d in failed if (h := hours(ts(d.get("at"), f"deploy {d.get('id')}"),
                                                 ts(d.get("recovered_at"), f"deploy {d.get('id')}")))
               is not None]
        out[name] = {"deployments": len(ds),
                     "change_fail_rate": ratio(len(failed), len(ds)),
                     "deployment_rework_rate": ratio(sum(1 for d in ds if d.get("unplanned")), len(ds)),
                     "median_failed_deployment_recovery_hours": med(rec)}
    return out


def analyze(doc: dict[str, Any], tolerance: float) -> dict[str, Any]:
    """Build the full metrics report and the optional regression findings."""
    prs = doc.get("prs")
    if not isinstance(prs, list) or not prs:
        fail("input needs a non-empty 'prs' list")
    for p in prs:
        if str(p.get("author_type", "")).lower() not in ("human", "agent"):
            fail(f"pr {p.get('id')}: author_type must be 'human' or 'agent'")
    defects = doc.get("defects") or []
    split = {k: [p for p in prs if str(p["author_type"]).lower() == k] for k in ("human", "agent")}
    res = {k: cohort(v, defects) for k, v in split.items()}
    agent_ids = {str(p.get("id")) for p in split["agent"]}
    d = dora(doc.get("deployments") or [], agent_ids)
    regressions: list[str] = []
    pairs = [("post_merge_rework_rate", res["agent"]["post_merge_rework_rate"],
              res["human"]["post_merge_rework_rate"]),
             ("change_fail_rate", d["with_agent_changes"]["change_fail_rate"],
              d["human_only"]["change_fail_rate"]),
             ("escaped_defects_per_merged", ratio(res["agent"]["escaped_defects"],
                                                  res["agent"]["merged"]),
              ratio(res["human"]["escaped_defects"], res["human"]["merged"]))]
    for name, a, h in pairs:
        if a is not None and h is not None and a - h > tolerance:
            regressions.append(f"agent {name} {a} exceeds human {h} by more than {tolerance}")
    return {"period": doc.get("period", {}), "by_author": res, "dora": d,
            "regressions": regressions}


def pct(v: float | None) -> str:
    """Format a ratio as a percentage."""
    return "n/a" if v is None else f"{v * 100:.1f}%"


def render_markdown(r: dict[str, Any]) -> str:
    """Render the report as markdown."""
    p = r["period"]
    h, a = r["by_author"]["human"], r["by_author"]["agent"]
    out = [f"# Agent Delivery Metrics {p.get('start', '')} to {p.get('end', '')}".rstrip(), "",
           "| Metric | Human | Agent |", "|--------|-------|-------|"]
    rows = [("PRs (merged)", f"{h['prs']} ({h['merged']})", f"{a['prs']} ({a['merged']})"),
            ("PR acceptance rate", pct(h["acceptance_rate"]), pct(a["acceptance_rate"])),
            ("Review rework rate", pct(h["review_rework_rate"]), pct(a["review_rework_rate"])),
            ("Post-merge rework rate", pct(h["post_merge_rework_rate"]),
             pct(a["post_merge_rework_rate"])),
            ("Median h to first review", h["median_hours_to_first_review"],
             a["median_hours_to_first_review"]),
            ("Median h open to merge", h["median_hours_open_to_merge"],
             a["median_hours_open_to_merge"]),
            ("Median reviewer min / PR", h["median_reviewer_minutes_per_pr"],
             a["median_reviewer_minutes_per_pr"]),
            ("Escaped defects / 10 merged", h["escaped_defects_per_10_merged"],
             a["escaped_defects_per_10_merged"])]
    out += [f"| {n} | {x} | {y} |" for n, x, y in rows]
    out += ["", "## DORA instability and recovery by deployment content", "",
            "| Deployments | Count | Change fail rate | Deployment rework rate | "
            "Median failed deployment recovery (h) |", "|---|---|---|---|---|"]
    for k, v in r["dora"].items():
        out.append(f"| {k} | {v['deployments']} | {pct(v['change_fail_rate'])} | "
                   f"{pct(v['deployment_rework_rate'])} | "
                   f"{v['median_failed_deployment_recovery_hours']} |")
    notes = [f"{k} cohort has fewer than {MIN_SAMPLE} merged PRs - read as directional"
             for k, c in r["by_author"].items() if c["small_sample"]]
    if notes or r["regressions"]:
        out += ["", "## Findings", ""] + [f"- {n}" for n in notes + r["regressions"]]
    return "\n".join(out) + "\n"


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Delivery metrics split by human vs agent authorship, with DORA split.",
        epilog="Exit codes: 0 ok, 1 tool error, 2 --gate regression beyond --tolerance.")
    ap.add_argument("--input", required=True, help="PR / deployment / defect records JSON")
    ap.add_argument("--gate", action="store_true",
                    help="exit 2 if agent cohort regresses beyond --tolerance")
    ap.add_argument("--tolerance", type=float, default=0.05,
                    help="allowed absolute gap, agent minus human (default 0.05)")
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
    res = analyze(doc, args.tolerance)
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
    sys.exit(2 if args.gate and res["regressions"] else 0)


if __name__ == "__main__":
    main()
