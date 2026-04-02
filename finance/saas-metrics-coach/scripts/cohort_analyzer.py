#!/usr/bin/env python3
"""
Cohort Retention Analyzer

Performs cohort retention analysis from user signup and activity data.
Groups users by signup period and tracks retention over subsequent periods.

Expected CSV columns: user_id, signup_date, activity_date (or last_active_date)
Each row represents one activity event or the user record with last active date.

Usage:
    python cohort_analyzer.py users.csv
    python cohort_analyzer.py users.csv --cohort-period monthly
    python cohort_analyzer.py users.csv --cohort-period weekly --format json
    python cohort_analyzer.py users.csv --max-periods 12
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in common formats."""
    if not date_str or date_str.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def month_key(dt: datetime) -> str:
    """Return YYYY-MM key."""
    return dt.strftime("%Y-%m")


def week_key(dt: datetime) -> str:
    """Return ISO week key YYYY-Www."""
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def quarter_key(dt: datetime) -> str:
    """Return YYYY-Qq key."""
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"


def get_period_key(dt: datetime, period_type: str) -> str:
    """Get period key based on period type."""
    if period_type == "weekly":
        return week_key(dt)
    elif period_type == "quarterly":
        return quarter_key(dt)
    return month_key(dt)


def load_user_data(filepath: str) -> Tuple[Dict[str, datetime], Dict[str, Set[str]]]:
    """
    Load user data from CSV.
    Returns: (user_signups, user_activity_periods)
    - user_signups: {user_id: signup_date}
    - user_activity_periods: {user_id: set of period_keys where user was active}
    """
    user_signups = {}
    user_activities = defaultdict(list)

    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])

        has_signup = "signup_date" in fields
        activity_col = None
        for col in ["activity_date", "last_active_date", "event_date", "active_date"]:
            if col in fields:
                activity_col = col
                break

        if "user_id" not in fields:
            print("Error: CSV must have 'user_id' column", file=sys.stderr)
            sys.exit(1)

        if not has_signup:
            print("Error: CSV must have 'signup_date' column", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            uid = row["user_id"].strip()
            signup = parse_date(row.get("signup_date", ""))
            if signup and uid not in user_signups:
                user_signups[uid] = signup

            if activity_col:
                act_date = parse_date(row.get(activity_col, ""))
                if act_date:
                    user_activities[uid].append(act_date)
            elif signup:
                # If no activity column, treat signup as the only known activity
                user_activities[uid].append(signup)

    return user_signups, user_activities


def build_cohort_table(
    user_signups: Dict[str, datetime],
    user_activities: Dict[str, List[datetime]],
    period_type: str,
    max_periods: int,
) -> Dict[str, Any]:
    """Build cohort retention table."""
    # Group users into cohorts by signup period
    cohorts = defaultdict(set)
    for uid, signup in user_signups.items():
        cohort = get_period_key(signup, period_type)
        cohorts[cohort].add(uid)

    # Build activity period sets per user
    user_period_sets = {}
    for uid, activities in user_activities.items():
        user_period_sets[uid] = {get_period_key(a, period_type) for a in activities}

    # Get all periods in order
    all_periods = set()
    for uid, pset in user_period_sets.items():
        all_periods.update(pset)
    for cohort in cohorts:
        all_periods.add(cohort)
    sorted_periods = sorted(all_periods)

    period_index = {p: i for i, p in enumerate(sorted_periods)}

    # Build retention matrix
    cohort_names = sorted(cohorts.keys())
    retention_matrix = {}
    cohort_sizes = {}

    for cohort in cohort_names:
        users = cohorts[cohort]
        cohort_sizes[cohort] = len(users)
        cohort_idx = period_index.get(cohort, 0)
        retention = {}

        for offset in range(max_periods + 1):
            target_idx = cohort_idx + offset
            target_period = None
            for p, idx in period_index.items():
                if idx == target_idx:
                    target_period = p
                    break
            if target_period is None:
                break

            active_count = 0
            for uid in users:
                if uid in user_period_sets and target_period in user_period_sets[uid]:
                    active_count += 1

            rate = active_count / len(users) if users else 0
            retention[offset] = {
                "active": active_count,
                "total": len(users),
                "rate": round(rate, 4),
            }

        retention_matrix[cohort] = retention

    # Calculate average retention by period offset
    avg_retention = {}
    for offset in range(max_periods + 1):
        rates = []
        for cohort in cohort_names:
            if offset in retention_matrix.get(cohort, {}):
                rates.append(retention_matrix[cohort][offset]["rate"])
        if rates:
            avg_retention[offset] = round(sum(rates) / len(rates), 4)

    return {
        "period_type": period_type,
        "total_users": len(user_signups),
        "total_cohorts": len(cohort_names),
        "cohort_sizes": {c: cohort_sizes[c] for c in cohort_names},
        "retention_matrix": retention_matrix,
        "average_retention": avg_retention,
    }


def assess_retention(avg_retention: Dict[int, float]) -> List[str]:
    """Generate retention health assessment."""
    findings = []

    if 1 in avg_retention:
        r1 = avg_retention[1]
        if r1 < 0.5:
            findings.append(f"CRITICAL: Period 1 retention is {r1*100:.1f}% - severe activation problem")
        elif r1 < 0.7:
            findings.append(f"WARNING: Period 1 retention is {r1*100:.1f}% - activation needs improvement")
        else:
            findings.append(f"Period 1 retention is {r1*100:.1f}% - healthy activation")

    if 3 in avg_retention:
        r3 = avg_retention[3]
        if r3 < 0.3:
            findings.append(f"CRITICAL: Period 3 retention is {r3*100:.1f}% - weak product-market fit signal")
        elif r3 < 0.5:
            findings.append(f"WARNING: Period 3 retention is {r3*100:.1f}% - moderate product-market fit")
        else:
            findings.append(f"Period 3 retention is {r3*100:.1f}% - strong product-market fit signal")

    # Check for stabilization
    if len(avg_retention) >= 4:
        recent = [avg_retention.get(i, 0) for i in range(max(0, len(avg_retention) - 3), len(avg_retention))]
        if len(recent) >= 2:
            deltas = [abs(recent[i] - recent[i - 1]) for i in range(1, len(recent))]
            avg_delta = sum(deltas) / len(deltas) if deltas else 0
            if avg_delta < 0.02:
                findings.append("Retention curve has stabilized - healthy flattening pattern")
            elif avg_delta > 0.05:
                findings.append("WARNING: Retention continues declining without stabilization")

    # Check if later cohorts improve
    return findings


def print_human(data: Dict[str, Any]) -> None:
    """Print cohort analysis in human-readable format."""
    print("=" * 70)
    print(f"  Cohort Retention Analysis ({data['period_type']})")
    print("=" * 70)
    print(f"\n  Total Users: {data['total_users']}")
    print(f"  Total Cohorts: {data['total_cohorts']}")

    # Retention matrix
    matrix = data["retention_matrix"]
    cohorts = sorted(matrix.keys())

    if not cohorts:
        print("\n  No cohort data available.")
        return

    max_offset = max(max(matrix[c].keys()) for c in cohorts if matrix[c])

    # Header
    print(f"\n  {'Cohort':<12} {'Size':>6}", end="")
    for i in range(min(max_offset + 1, 13)):
        label = f"P{i}"
        print(f" {label:>7}", end="")
    print()
    print(f"  {'-' * 12} {'-' * 6}", end="")
    for i in range(min(max_offset + 1, 13)):
        print(f" {'-' * 7}", end="")
    print()

    for cohort in cohorts:
        size = data["cohort_sizes"][cohort]
        print(f"  {cohort:<12} {size:>6}", end="")
        for offset in range(min(max_offset + 1, 13)):
            if offset in matrix[cohort]:
                rate = matrix[cohort][offset]["rate"]
                print(f" {rate * 100:>6.1f}%", end="")
            else:
                print(f" {'':>7}", end="")
        print()

    # Average retention
    avg = data["average_retention"]
    print(f"\n  {'Average':<12} {'':>6}", end="")
    for offset in range(min(max_offset + 1, 13)):
        if offset in avg:
            print(f" {avg[offset] * 100:>6.1f}%", end="")
        else:
            print(f" {'':>7}", end="")
    print()

    # Assessment
    findings = assess_retention(avg)
    if findings:
        print(f"\n  --- Assessment ---")
        for f in findings:
            print(f"  {f}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Cohort retention analysis from user signup and activity data"
    )
    parser.add_argument("file", help="CSV file with user data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument(
        "--cohort-period",
        choices=["weekly", "monthly", "quarterly"],
        default="monthly",
        help="Cohort grouping period (default: monthly)",
    )
    parser.add_argument(
        "--max-periods", type=int, default=12, help="Maximum number of periods to track (default: 12)"
    )
    args = parser.parse_args()

    user_signups, user_activities = load_user_data(args.file)
    if not user_signups:
        print("Error: No valid user records found", file=sys.stderr)
        sys.exit(1)

    data = build_cohort_table(user_signups, user_activities, args.cohort_period, args.max_periods)

    if args.format == "json":
        # Convert integer keys to strings for JSON
        json_data = dict(data)
        json_data["average_retention"] = {str(k): v for k, v in data["average_retention"].items()}
        for cohort in json_data["retention_matrix"]:
            json_data["retention_matrix"][cohort] = {
                str(k): v for k, v in json_data["retention_matrix"][cohort].items()
            }
        print(json.dumps(json_data, indent=2))
    else:
        print_human(data)


if __name__ == "__main__":
    main()
