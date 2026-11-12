#!/usr/bin/env python3
"""
funder_fit_scorer.py — Score funder fit across 7 dimensions before
investing weeks in a proposal.

Reads a JSON describing funder + project + team; scores 7 dimensions
(topic, mechanism, stage, geography, team-profile, budget envelope,
competitive density); returns total fit score + recommendation.

Stdlib only. JSON or markdown output.

Usage:
    python3 funder_fit_scorer.py --input funder_fit.json
    python3 funder_fit_scorer.py --input funder_fit.json --format markdown

Input schema:
{
  "funder": "NIH NIAID",
  "program": "R01",
  "project": "Antimicrobial resistance via X mechanism",
  "topic_in_scope": true|false,
  "topic_in_active_rfp": true|false,
  "mechanism_alignment": "high|medium|low|none",      # high = exact match
  "stage_alignment": "high|medium|low|none",
  "geo_alignment": "high|medium|low|none",
  "team_profile_alignment": "high|medium|low|none",
  "budget_envelope_match": "high|medium|low|none",    # vs typical award
  "estimated_acceptance_rate_pct": 15,
  "pi_track_record": "strong|moderate|weak|none",     # in funder's area
  "prior_funding_from_this_funder": true|false
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HIGH_MED_LOW = {"high": 15, "medium": 10, "low": 4, "none": 0}
GEO_FIT = {"high": 10, "medium": 7, "low": 3, "none": 0}  # geo weight is 10, not 15


@dataclass
class Score:
    dimension: str
    score: int
    max_score: int
    note: str


def score_topic(state: dict[str, Any]) -> Score:
    in_scope = bool(state.get("topic_in_scope"))
    in_rfp = bool(state.get("topic_in_active_rfp"))
    if in_scope and in_rfp:
        return Score("topic alignment", 20, 20, "topic in scope + matches active RFP")
    if in_scope:
        return Score("topic alignment", 12, 20, "topic in scope but not in active RFP")
    return Score("topic alignment", 0, 20, "topic NOT in funder scope — skip funder")


def score_mechanism(state: dict[str, Any]) -> Score:
    v = (state.get("mechanism_alignment") or "low").lower()
    s = HIGH_MED_LOW.get(v, 0)
    return Score("mechanism alignment", s, 15,
                f"funder mechanism (research / services / scale-up) match: {v}")


def score_stage(state: dict[str, Any]) -> Score:
    v = (state.get("stage_alignment") or "low").lower()
    s = HIGH_MED_LOW.get(v, 0)
    return Score("stage alignment", s, 15,
                f"project stage matches funder's typical: {v}")


def score_geo(state: dict[str, Any]) -> Score:
    v = (state.get("geo_alignment") or "low").lower()
    s = GEO_FIT.get(v, 0)
    return Score("geographic alignment", s, 10,
                f"geography fit: {v}")


def score_team(state: dict[str, Any]) -> Score:
    base = HIGH_MED_LOW.get((state.get("team_profile_alignment") or "low").lower(), 0)
    bonus = 0
    note_parts = [f"team profile fit: {state.get('team_profile_alignment')}"]
    pi_record = (state.get("pi_track_record") or "weak").lower()
    if pi_record == "strong":
        bonus += 10
        note_parts.append("strong PI track record in area")
    elif pi_record == "moderate":
        bonus += 5
    elif pi_record == "weak":
        note_parts.append("weak PI track record — consider mentor co-PI")
    if state.get("prior_funding_from_this_funder"):
        bonus += 5
        note_parts.append("prior funding from this funder = positive signal")
    return Score("team alignment", min(20, base + bonus), 20, "; ".join(note_parts))


def score_budget(state: dict[str, Any]) -> Score:
    v = (state.get("budget_envelope_match") or "low").lower()
    s = HIGH_MED_LOW.get(v, 0)
    return Score("budget envelope match", s, 15,
                f"requested budget vs funder's typical award: {v}")


def score_competition(state: dict[str, Any]) -> Score:
    rate = int(state.get("estimated_acceptance_rate_pct", 0) or 0)
    if rate >= 30:
        return Score("competitive density", 5, 5,
                    f"acceptance ~{rate}% (favorable)")
    if rate >= 15:
        return Score("competitive density", 3, 5,
                    f"acceptance ~{rate}% (typical)")
    if rate >= 8:
        return Score("competitive density", 2, 5,
                    f"acceptance ~{rate}% (competitive)")
    return Score("competitive density", 1, 5,
                f"acceptance ~{rate}% (very competitive)")


def assess(state: dict[str, Any]) -> dict[str, Any]:
    scores = [
        score_topic(state),
        score_mechanism(state),
        score_stage(state),
        score_geo(state),
        score_team(state),
        score_budget(state),
        score_competition(state),
    ]
    total = sum(s.score for s in scores)
    max_total = sum(s.max_score for s in scores)
    pct = round((total / max_total) * 100, 1) if max_total > 0 else 0

    if total == 0 and scores[0].score == 0:
        recommendation = "SKIP — topic not in funder scope"
    elif pct >= 80:
        recommendation = "STRONG FIT — proceed with high priority"
    elif pct >= 65:
        recommendation = "GOOD FIT — proceed; address weakest dimensions"
    elif pct >= 50:
        recommendation = "MARGINAL FIT — consider alternative funder first"
    else:
        recommendation = "POOR FIT — find a better-aligned funder"

    return {
        "funder": state.get("funder", ""),
        "program": state.get("program", ""),
        "project": state.get("project", ""),
        "total_score": total,
        "max_score": max_total,
        "fit_pct": pct,
        "recommendation": recommendation,
        "dimensions": [
            {"dimension": s.dimension, "score": s.score, "max": s.max_score, "note": s.note}
            for s in scores
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Funder Fit Assessment — {report.get('funder','')} / {report.get('program','')}\n")
    lines.append(f"**Project:** {report.get('project','')}\n")
    lines.append(f"## Total: **{report['total_score']}/{report['max_score']} ({report['fit_pct']}%)**\n")
    lines.append(f"### Recommendation: **{report['recommendation']}**\n")
    lines.append("## Dimension breakdown")
    lines.append("| Dimension | Score | Max | Note |")
    lines.append("|-----------|-------|-----|------|")
    for d in report["dimensions"]:
        lines.append(f"| {d['dimension']} | {d['score']} | {d['max']} | {d['note']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Score funder fit across 7 dimensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON of funder + project + team")
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

    report = assess(state)
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
