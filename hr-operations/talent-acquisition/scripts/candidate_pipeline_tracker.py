#!/usr/bin/env python3
"""
Candidate Pipeline Tracker - Track and analyze recruiting funnel metrics.

Reads a CSV of candidate pipeline data and computes stage-by-stage conversion
rates, time-in-stage metrics, source effectiveness, and bottleneck identification.

Usage:
    python candidate_pipeline_tracker.py --file pipeline.csv
    python candidate_pipeline_tracker.py --file pipeline.csv --json

Input CSV columns:
    candidate_id    - Unique candidate identifier
    role            - Job title or requisition name
    source          - Sourcing channel (e.g., LinkedIn, Referral, Job Board)
    stage           - Current pipeline stage (Applied, Screened, Interviewed, Offered, Accepted, Rejected, Withdrawn)
    stage_date      - Date the candidate entered this stage (YYYY-MM-DD)
    applied_date    - Date of initial application (YYYY-MM-DD)

Output: Funnel metrics, conversion rates, source effectiveness, and bottleneck analysis.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


STAGE_ORDER = ["Applied", "Screened", "Interviewed", "Offered", "Accepted"]
TERMINAL_STAGES = ["Rejected", "Withdrawn"]

BENCHMARKS = {
    "Applied_to_Screened": (0.40, 0.50),
    "Screened_to_Interviewed": (0.30, 0.40),
    "Interviewed_to_Offered": (0.15, 0.25),
    "Offered_to_Accepted": (0.80, 0.90),
}


def read_csv(path: str) -> list:
    """Read CSV file and return list of dicts."""
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"candidate_id", "stage", "applied_date"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def get_candidate_max_stage(rows: list) -> dict:
    """Get the furthest stage each candidate reached."""
    candidates = defaultdict(lambda: {"max_stage_idx": -1, "stage": "Unknown", "source": "", "role": "", "applied_date": None, "stage_date": None})

    for row in rows:
        cid = row["candidate_id"]
        stage = row.get("stage", "").strip()
        source = row.get("source", "").strip()
        role = row.get("role", "").strip()
        applied_date = parse_date(row.get("applied_date", ""))
        stage_date = parse_date(row.get("stage_date", ""))

        if stage in STAGE_ORDER:
            idx = STAGE_ORDER.index(stage)
        elif stage in TERMINAL_STAGES:
            idx = -1  # terminal, but track separately
        else:
            idx = -1

        if source:
            candidates[cid]["source"] = source
        if role:
            candidates[cid]["role"] = role
        if applied_date:
            candidates[cid]["applied_date"] = applied_date

        if stage in TERMINAL_STAGES:
            candidates[cid]["terminal"] = stage
            if stage_date:
                candidates[cid]["terminal_date"] = stage_date

        if idx > candidates[cid]["max_stage_idx"]:
            candidates[cid]["max_stage_idx"] = idx
            candidates[cid]["stage"] = stage
            if stage_date:
                candidates[cid]["stage_date"] = stage_date

    return candidates


def compute_funnel(candidates: dict) -> dict:
    """Compute funnel metrics."""
    stage_counts = defaultdict(int)
    for cid, data in candidates.items():
        idx = data["max_stage_idx"]
        # Count each candidate at their max stage AND all previous stages
        for i in range(idx + 1):
            stage_counts[STAGE_ORDER[i]] += 1

    funnel = []
    for i, stage in enumerate(STAGE_ORDER):
        count = stage_counts.get(stage, 0)
        entry = {"stage": stage, "count": count}

        if i > 0:
            prev_count = stage_counts.get(STAGE_ORDER[i - 1], 0)
            if prev_count > 0:
                rate = count / prev_count
                entry["conversion_rate"] = round(rate, 3)
                key = f"{STAGE_ORDER[i-1]}_to_{stage}"
                bench = BENCHMARKS.get(key)
                if bench:
                    entry["benchmark_range"] = f"{bench[0]*100:.0f}-{bench[1]*100:.0f}%"
                    if rate < bench[0]:
                        entry["status"] = "BELOW_BENCHMARK"
                    elif rate > bench[1]:
                        entry["status"] = "ABOVE_BENCHMARK"
                    else:
                        entry["status"] = "ON_TARGET"

        funnel.append(entry)

    return funnel


def compute_source_effectiveness(candidates: dict) -> list:
    """Compute source channel effectiveness."""
    source_data = defaultdict(lambda: {"applied": 0, "screened": 0, "interviewed": 0, "offered": 0, "accepted": 0})

    for cid, data in candidates.items():
        source = data.get("source", "Unknown") or "Unknown"
        idx = data["max_stage_idx"]
        for i in range(idx + 1):
            stage_key = STAGE_ORDER[i].lower()
            source_data[source][stage_key] += 1

    results = []
    for source, counts in sorted(source_data.items()):
        applied = counts["applied"]
        if applied == 0:
            continue
        entry = {
            "source": source,
            "applied": applied,
            "screened": counts["screened"],
            "accepted": counts["accepted"],
            "overall_conversion": round(counts["accepted"] / applied, 3) if applied > 0 else 0,
            "screen_rate": round(counts["screened"] / applied, 3) if applied > 0 else 0,
        }
        results.append(entry)

    results.sort(key=lambda x: x["overall_conversion"], reverse=True)
    return results


def compute_time_metrics(candidates: dict) -> dict:
    """Compute time-based metrics."""
    times_to_current = []
    times_to_accept = []

    for cid, data in candidates.items():
        applied = data.get("applied_date")
        stage_date = data.get("stage_date")
        if applied and stage_date:
            days = (stage_date - applied).days
            if days >= 0:
                times_to_current.append(days)
                if data["stage"] == "Accepted":
                    times_to_accept.append(days)

    def stats(values):
        if not values:
            return {"count": 0, "avg": 0, "median": 0, "min": 0, "max": 0}
        s = sorted(values)
        n = len(s)
        return {
            "count": n,
            "avg": round(sum(s) / n, 1),
            "median": s[n // 2],
            "min": s[0],
            "max": s[-1],
        }

    return {
        "time_in_pipeline_days": stats(times_to_current),
        "time_to_accept_days": stats(times_to_accept),
    }


def compute_role_breakdown(candidates: dict) -> list:
    """Compute metrics by role."""
    role_data = defaultdict(lambda: defaultdict(int))

    for cid, data in candidates.items():
        role = data.get("role", "Unknown") or "Unknown"
        idx = data["max_stage_idx"]
        for i in range(idx + 1):
            role_data[role][STAGE_ORDER[i]] += 1

    results = []
    for role, counts in sorted(role_data.items()):
        applied = counts.get("Applied", 0)
        accepted = counts.get("Accepted", 0)
        offered = counts.get("Offered", 0)
        results.append({
            "role": role,
            "applied": applied,
            "accepted": accepted,
            "overall_conversion": round(accepted / applied, 3) if applied > 0 else 0,
            "offer_accept_rate": round(accepted / offered, 3) if offered > 0 else 0,
        })

    return results


def identify_bottlenecks(funnel: list) -> list:
    """Identify pipeline bottlenecks."""
    bottlenecks = []
    for entry in funnel:
        if entry.get("status") == "BELOW_BENCHMARK":
            bottlenecks.append({
                "stage_transition": f"{STAGE_ORDER[STAGE_ORDER.index(entry['stage'])-1]} -> {entry['stage']}",
                "actual_rate": f"{entry['conversion_rate']*100:.1f}%",
                "benchmark": entry["benchmark_range"],
                "severity": "HIGH" if entry["conversion_rate"] < 0.5 * float(entry["benchmark_range"].split("-")[0].replace("%", "")) / 100 else "MEDIUM",
            })
    return bottlenecks


def format_human(funnel: list, sources: list, time_metrics: dict, roles: list, bottlenecks: list, total: int) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 65)
    lines.append("CANDIDATE PIPELINE REPORT")
    lines.append("=" * 65)
    lines.append(f"  Total candidates: {total}")
    lines.append("")

    lines.append("-" * 65)
    lines.append("FUNNEL ANALYSIS")
    lines.append("-" * 65)
    lines.append(f"  {'Stage':<20} {'Count':>8} {'Conv Rate':>12} {'Benchmark':>14} {'Status':>16}")
    lines.append(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*14} {'-'*16}")
    for entry in funnel:
        conv = f"{entry['conversion_rate']*100:.1f}%" if "conversion_rate" in entry else "--"
        bench = entry.get("benchmark_range", "--")
        status = entry.get("status", "--")
        lines.append(f"  {entry['stage']:<20} {entry['count']:>8} {conv:>12} {bench:>14} {status:>16}")

    lines.append("")
    lines.append("-" * 65)
    lines.append("SOURCE EFFECTIVENESS")
    lines.append("-" * 65)
    lines.append(f"  {'Source':<25} {'Applied':>8} {'Screened':>9} {'Accepted':>9} {'Conv %':>8}")
    lines.append(f"  {'-'*25} {'-'*8} {'-'*9} {'-'*9} {'-'*8}")
    for s in sources:
        lines.append(f"  {s['source']:<25} {s['applied']:>8} {s['screened']:>9} {s['accepted']:>9} {s['overall_conversion']*100:>7.1f}%")

    tm = time_metrics
    lines.append("")
    lines.append("-" * 65)
    lines.append("TIME METRICS")
    lines.append("-" * 65)
    pip = tm["time_in_pipeline_days"]
    lines.append(f"  Time in pipeline:  avg {pip['avg']} days | median {pip['median']} days | range {pip['min']}-{pip['max']} days")
    acc = tm["time_to_accept_days"]
    if acc["count"] > 0:
        lines.append(f"  Time to accept:    avg {acc['avg']} days | median {acc['median']} days | range {acc['min']}-{acc['max']} days")

    if bottlenecks:
        lines.append("")
        lines.append("-" * 65)
        lines.append("BOTTLENECKS IDENTIFIED")
        lines.append("-" * 65)
        for b in bottlenecks:
            lines.append(f"  [{b['severity']}] {b['stage_transition']}: {b['actual_rate']} (benchmark: {b['benchmark']})")

    if roles:
        lines.append("")
        lines.append("-" * 65)
        lines.append("BY ROLE")
        lines.append("-" * 65)
        lines.append(f"  {'Role':<30} {'Applied':>8} {'Accepted':>9} {'Conv %':>8}")
        lines.append(f"  {'-'*30} {'-'*8} {'-'*9} {'-'*8}")
        for r in roles:
            lines.append(f"  {r['role']:<30} {r['applied']:>8} {r['accepted']:>9} {r['overall_conversion']*100:>7.1f}%")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track and analyze candidate pipeline funnel metrics."
    )
    parser.add_argument("--file", required=True, help="Path to pipeline CSV file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    candidates = get_candidate_max_stage(rows)
    funnel = compute_funnel(candidates)
    sources = compute_source_effectiveness(candidates)
    time_metrics = compute_time_metrics(candidates)
    roles = compute_role_breakdown(candidates)
    bottlenecks = identify_bottlenecks(funnel)

    if args.json:
        output = {
            "total_candidates": len(candidates),
            "funnel": funnel,
            "source_effectiveness": sources,
            "time_metrics": time_metrics,
            "role_breakdown": roles,
            "bottlenecks": bottlenecks,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(format_human(funnel, sources, time_metrics, roles, bottlenecks, len(candidates)))


if __name__ == "__main__":
    main()
