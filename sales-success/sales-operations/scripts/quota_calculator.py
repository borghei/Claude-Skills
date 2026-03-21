#!/usr/bin/env python3
"""Track quota attainment with pacing indicators and gap analysis.

Reads rep performance data and quota assignments to calculate attainment,
pacing against plan, and projected finish with required run rates.

Usage:
    python quota_calculator.py --data performance.csv --quarter Q1-2026
    python quota_calculator.py --data performance.json --json
    python quota_calculator.py --data performance.csv --weeks-elapsed 8 --total-weeks 13
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


ATTAINMENT_LABELS = {
    (0, 50): ("Far Behind", "Critical intervention needed. Review pipeline and activity."),
    (50, 75): ("Behind Plan", "Accelerate pipeline. Focus on commit and best-case deals."),
    (75, 90): ("Tracking", "On pace with room to improve. Push best-case deals to commit."),
    (90, 100): ("Near Target", "Close to plan. Focus on closing committed deals."),
    (100, 150): ("At or Above", "Hitting quota. Pursue accelerators and overachievement."),
    (150, 500): ("Crushing It", "Exceptional performance. Maximize accelerator earnings."),
}

COMMISSION_TIERS = [
    (0, 50, 0.5),
    (50, 100, 1.0),
    (100, 150, 1.5),
    (150, float("inf"), 2.0),
]


def load_data(filepath):
    """Load performance data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def safe_float(value, default=0.0):
    """Parse float safely."""
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return default


def calculate_commission_multiplier(attainment_pct):
    """Calculate blended commission multiplier based on attainment tiers."""
    for lo, hi, rate in COMMISSION_TIERS:
        if attainment_pct <= hi:
            return rate
    return COMMISSION_TIERS[-1][2]


def calculate_attainment(rep_data, weeks_elapsed, total_weeks):
    """Calculate quota attainment and projections for a single rep."""
    name = rep_data.get("name", rep_data.get("rep_name", rep_data.get("rep", "Unknown")))
    quota = safe_float(rep_data.get("quota", 0))
    closed = safe_float(rep_data.get("closed", rep_data.get("closed_won", rep_data.get("bookings", 0))))
    commit = safe_float(rep_data.get("commit", rep_data.get("commit_pipeline", 0)))
    best_case = safe_float(rep_data.get("best_case", rep_data.get("best_case_pipeline", 0)))
    pipeline = safe_float(rep_data.get("pipeline", rep_data.get("open_pipeline", 0)))
    team = rep_data.get("team", rep_data.get("segment", ""))
    ramping = str(rep_data.get("ramping", "false")).lower() in ("true", "1", "yes")

    if quota <= 0:
        return None

    # Core attainment
    attainment_pct = round(closed / quota * 100, 1)

    # Pacing
    elapsed_pct = round(weeks_elapsed / total_weeks * 100, 1) if total_weeks > 0 else 0
    expected_at_pace = round(quota * (weeks_elapsed / total_weeks), 2) if total_weeks > 0 else 0
    pace_delta = round(closed - expected_at_pace, 2)
    pace_status = "ahead" if pace_delta > 0 else "behind" if pace_delta < 0 else "on_pace"

    # Projections
    weeks_remaining = max(total_weeks - weeks_elapsed, 0)
    if weeks_elapsed > 0:
        weekly_run_rate = closed / weeks_elapsed
        projected_finish = round(closed + (weekly_run_rate * weeks_remaining), 2)
        projected_attainment = round(projected_finish / quota * 100, 1)
    else:
        weekly_run_rate = 0
        projected_finish = closed
        projected_attainment = attainment_pct

    # Gap analysis
    gap = max(quota - closed, 0)
    required_weekly_rate = round(gap / weeks_remaining, 2) if weeks_remaining > 0 else gap
    required_win_amount = gap

    # Weighted pipeline check
    weighted_pipeline = (commit * 0.90) + (best_case * 0.50) + (pipeline * 0.20)
    coverage_of_gap = round(weighted_pipeline / gap, 2) if gap > 0 else float("inf")

    # Commission tier
    commission_multiplier = calculate_commission_multiplier(attainment_pct)

    # Label
    label = "Unknown"
    advice = ""
    for (lo, hi), (lbl, adv) in ATTAINMENT_LABELS.items():
        if lo <= attainment_pct < hi:
            label = lbl
            advice = adv
            break

    return {
        "rep_name": name,
        "team": team,
        "ramping": ramping,
        "quota": round(quota, 2),
        "closed": round(closed, 2),
        "attainment_pct": attainment_pct,
        "attainment_label": label,
        "attainment_advice": advice,
        "pacing": {
            "weeks_elapsed": weeks_elapsed,
            "total_weeks": total_weeks,
            "elapsed_pct": elapsed_pct,
            "expected_at_pace": expected_at_pace,
            "pace_delta": pace_delta,
            "pace_status": pace_status,
        },
        "projection": {
            "weekly_run_rate": round(weekly_run_rate, 2),
            "projected_finish": projected_finish,
            "projected_attainment_pct": projected_attainment,
        },
        "gap_analysis": {
            "gap_to_quota": round(gap, 2),
            "required_weekly_rate": required_weekly_rate,
            "weeks_remaining": weeks_remaining,
            "commit_pipeline": round(commit, 2),
            "best_case_pipeline": round(best_case, 2),
            "open_pipeline": round(pipeline, 2),
            "weighted_pipeline": round(weighted_pipeline, 2),
            "coverage_of_gap": coverage_of_gap if coverage_of_gap != float("inf") else "N/A (no gap)",
        },
        "commission_multiplier": commission_multiplier,
    }


def format_human(results, team_summary):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("QUOTA ATTAINMENT REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    ts = team_summary
    lines.append(f"\n  Team Summary")
    lines.append(f"  Total Reps:           {ts['total_reps']}")
    lines.append(f"  Team Quota:           ${ts['team_quota']:,.2f}")
    lines.append(f"  Team Closed:          ${ts['team_closed']:,.2f}")
    lines.append(f"  Team Attainment:      {ts['team_attainment_pct']}%")
    lines.append(f"  Reps at 100%+:        {ts['reps_at_quota']} ({ts['pct_at_quota']}%)")
    lines.append(f"  Reps Below 50%:       {ts['reps_below_50']}")
    lines.append(f"  Team Gap:             ${ts['team_gap']:,.2f}")

    lines.append(f"\n{'REP ATTAINMENT':^70}")
    lines.append("-" * 70)
    lines.append(
        f"  {'Rep':<18} {'Quota':>10} {'Closed':>10} {'Attn%':>7} {'Pace':>8} "
        f"{'Proj%':>7} {'Gap':>10}"
    )
    lines.append("  " + "-" * 62)

    for r in sorted(results, key=lambda x: x["attainment_pct"], reverse=True):
        pace = r["pacing"]["pace_status"]
        pace_flag = "+" if pace == "ahead" else "-" if pace == "behind" else "="
        ramp = " (R)" if r["ramping"] else ""
        lines.append(
            f"  {r['rep_name']:<18} ${r['quota']:>8,.0f} ${r['closed']:>8,.0f} "
            f"{r['attainment_pct']:>6.1f}% {pace_flag:>7}  "
            f"{r['projection']['projected_attainment_pct']:>6.1f}% "
            f"${r['gap_analysis']['gap_to_quota']:>8,.0f}{ramp}"
        )

    lines.append(f"\n{'DETAILED ANALYSIS':^70}")
    lines.append("-" * 70)

    for r in sorted(results, key=lambda x: x["attainment_pct"]):
        lines.append(f"\n  {r['rep_name']} [{r['attainment_label']}]")
        lines.append(f"  {r['attainment_advice']}")
        lines.append(f"  Closed: ${r['closed']:,.2f} / ${r['quota']:,.2f} ({r['attainment_pct']}%)")
        lines.append(
            f"  Pacing: ${r['pacing']['pace_delta']:+,.2f} vs plan "
            f"(expected ${r['pacing']['expected_at_pace']:,.2f} at week {r['pacing']['weeks_elapsed']})"
        )
        lines.append(
            f"  Projection: ${r['projection']['projected_finish']:,.2f} "
            f"({r['projection']['projected_attainment_pct']}%) at current rate"
        )
        ga = r["gap_analysis"]
        lines.append(
            f"  Gap: ${ga['gap_to_quota']:,.2f} | "
            f"Need ${ga['required_weekly_rate']:,.2f}/wk over {ga['weeks_remaining']} weeks"
        )
        lines.append(
            f"  Pipeline: Commit ${ga['commit_pipeline']:,.2f} | "
            f"Best Case ${ga['best_case_pipeline']:,.2f} | "
            f"Open ${ga['open_pipeline']:,.2f}"
        )
        cov = ga["coverage_of_gap"]
        cov_str = f"{cov}x" if isinstance(cov, (int, float)) else cov
        lines.append(f"  Weighted Pipeline vs Gap: {cov_str}")
        lines.append(f"  Commission Tier: {r['commission_multiplier']}x")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track quota attainment with pacing and gap analysis."
    )
    parser.add_argument("--data", required=True, help="Path to rep performance CSV or JSON file")
    parser.add_argument("--quarter", default=None, help="Quarter label (e.g., Q1-2026)")
    parser.add_argument(
        "--weeks-elapsed", type=int, default=6, help="Weeks elapsed in quarter (default: 6)"
    )
    parser.add_argument(
        "--total-weeks", type=int, default=13, help="Total weeks in quarter (default: 13)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    reps = load_data(args.data)
    if not reps:
        print("Error: No rep data found in input file.", file=sys.stderr)
        sys.exit(1)

    results = []
    for rep in reps:
        result = calculate_attainment(rep, args.weeks_elapsed, args.total_weeks)
        if result:
            results.append(result)

    if not results:
        print("Error: No valid quota data found.", file=sys.stderr)
        sys.exit(1)

    # Team summary
    team_quota = sum(r["quota"] for r in results)
    team_closed = sum(r["closed"] for r in results)
    reps_at_quota = sum(1 for r in results if r["attainment_pct"] >= 100)
    reps_below_50 = sum(1 for r in results if r["attainment_pct"] < 50)

    team_summary = {
        "quarter": args.quarter or "Current",
        "total_reps": len(results),
        "team_quota": round(team_quota, 2),
        "team_closed": round(team_closed, 2),
        "team_attainment_pct": round(team_closed / team_quota * 100, 1) if team_quota > 0 else 0,
        "team_gap": round(max(team_quota - team_closed, 0), 2),
        "reps_at_quota": reps_at_quota,
        "pct_at_quota": round(reps_at_quota / len(results) * 100, 1),
        "reps_below_50": reps_below_50,
    }

    if args.json:
        output = {"team_summary": team_summary, "rep_details": results}
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, team_summary))

    sys.exit(0 if team_summary["team_attainment_pct"] >= 80 else 1)


if __name__ == "__main__":
    main()
