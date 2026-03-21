#!/usr/bin/env python3
"""Optimize territory assignment balancing potential, workload, and coverage.

Reads account data and rep roster to produce balanced territory assignments
with variance analysis, coverage metrics, and fairness scoring.

Usage:
    python territory_planner.py --accounts accounts.csv --reps 8
    python territory_planner.py --accounts accounts.json --reps reps.csv --json
    python territory_planner.py --accounts accounts.csv --reps 10 --strategy balanced
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime


TIER_THRESHOLDS = {
    "tier_1": 70,
    "tier_2": 40,
    "tier_3": 0,
}

INDUSTRY_SCORES = {
    "technology": 25,
    "finance": 25,
    "financial_services": 25,
    "healthcare": 20,
    "manufacturing": 15,
    "retail": 15,
    "education": 10,
    "government": 10,
}


def load_data(filepath):
    """Load data from CSV or JSON file."""
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
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Parse int safely."""
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def score_account(account):
    """Score an account for territory assignment (0-100)."""
    score = 0

    # Company size (0-30 points)
    employees = safe_int(account.get("employees", account.get("employee_count", 0)))
    if employees > 5000:
        score += 30
    elif employees > 1000:
        score += 20
    elif employees > 200:
        score += 10
    elif employees > 50:
        score += 5

    # Revenue potential (0-25 points)
    revenue = safe_float(account.get("potential", account.get("arr_potential", account.get("revenue", 0))))
    if revenue > 500000:
        score += 25
    elif revenue > 200000:
        score += 20
    elif revenue > 100000:
        score += 15
    elif revenue > 50000:
        score += 10
    elif revenue > 0:
        score += 5

    # Industry fit (0-25 points)
    industry = str(account.get("industry", "")).lower().strip().replace(" ", "_")
    score += INDUSTRY_SCORES.get(industry, 8)

    # Engagement signals (0-20 points)
    engagement = safe_float(account.get("engagement_score", account.get("intent_score", 0)))
    if engagement > 80:
        score += 20
    elif engagement > 50:
        score += 12
    elif engagement > 20:
        score += 5

    return min(score, 100)


def assign_tier(score):
    """Assign account tier based on score."""
    if score >= TIER_THRESHOLDS["tier_1"]:
        return "Tier 1"
    elif score >= TIER_THRESHOLDS["tier_2"]:
        return "Tier 2"
    else:
        return "Tier 3"


def plan_territories(accounts, num_reps, rep_data=None, strategy="balanced"):
    """Create balanced territory assignments."""
    # Score all accounts
    scored_accounts = []
    for acct in accounts:
        account_score = score_account(acct)
        name = acct.get("name", acct.get("account_name", acct.get("company", "Unknown")))
        potential = safe_float(acct.get("potential", acct.get("arr_potential", acct.get("revenue", 0))))
        region = acct.get("region", acct.get("territory", acct.get("geo", "Unassigned")))
        industry = acct.get("industry", "Unknown")
        current_rep = acct.get("rep", acct.get("owner", acct.get("assigned_to", "")))

        scored_accounts.append({
            "name": name,
            "score": account_score,
            "tier": assign_tier(account_score),
            "potential": potential,
            "region": region,
            "industry": industry,
            "current_rep": current_rep,
            "employees": safe_int(acct.get("employees", 0)),
        })

    # Sort by score descending for assignment
    scored_accounts.sort(key=lambda x: x["score"], reverse=True)

    # Build rep list
    reps = []
    if rep_data:
        for r in rep_data:
            reps.append({
                "name": r.get("name", r.get("rep_name", f"Rep {len(reps)+1}")),
                "region": r.get("region", r.get("territory", "")),
                "ramping": str(r.get("ramping", r.get("is_ramping", "false"))).lower() in ("true", "1", "yes"),
                "capacity": safe_float(r.get("capacity", 1.0)) if safe_float(r.get("capacity", 1.0)) > 0 else 1.0,
            })
    else:
        for i in range(num_reps):
            reps.append({
                "name": f"Rep {i+1}",
                "region": "",
                "ramping": False,
                "capacity": 1.0,
            })

    # Initialize territory buckets
    territories = {rep["name"]: {
        "rep": rep["name"],
        "accounts": [],
        "total_potential": 0,
        "account_count": 0,
        "avg_score": 0,
        "tier_distribution": {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0},
        "ramping": rep["ramping"],
        "capacity": rep["capacity"],
    } for rep in reps}

    # Assignment strategy: round-robin by score tiers for balance
    if strategy == "balanced":
        # Distribute accounts trying to balance potential
        for acct in scored_accounts:
            # Find rep with lowest weighted potential
            best_rep = None
            best_weighted = float("inf")
            for rep_name, terr in territories.items():
                capacity = terr["capacity"]
                weighted_potential = terr["total_potential"] / capacity if capacity > 0 else float("inf")
                # Prefer region match
                rep_obj = next((r for r in reps if r["name"] == rep_name), None)
                if rep_obj and rep_obj["region"] and acct["region"]:
                    if rep_obj["region"].lower() == acct["region"].lower():
                        weighted_potential *= 0.8  # Prefer region match

                if weighted_potential < best_weighted:
                    best_weighted = weighted_potential
                    best_rep = rep_name

            if best_rep:
                territories[best_rep]["accounts"].append(acct)
                territories[best_rep]["total_potential"] += acct["potential"]
                territories[best_rep]["account_count"] += 1
                territories[best_rep]["tier_distribution"][acct["tier"]] += 1

    elif strategy == "geographic":
        # Group by region first, then balance within regions
        region_accounts = defaultdict(list)
        for acct in scored_accounts:
            region_accounts[acct["region"]].append(acct)

        rep_index = 0
        rep_names = list(territories.keys())
        for region, accts in region_accounts.items():
            for acct in accts:
                rep_name = rep_names[rep_index % len(rep_names)]
                territories[rep_name]["accounts"].append(acct)
                territories[rep_name]["total_potential"] += acct["potential"]
                territories[rep_name]["account_count"] += 1
                territories[rep_name]["tier_distribution"][acct["tier"]] += 1
                rep_index += 1

    # Calculate averages and metrics
    potentials = []
    for terr in territories.values():
        if terr["accounts"]:
            terr["avg_score"] = round(
                sum(a["score"] for a in terr["accounts"]) / len(terr["accounts"]), 1
            )
        terr["total_potential"] = round(terr["total_potential"], 2)
        potentials.append(terr["total_potential"])

    # Balance metrics
    avg_potential = sum(potentials) / len(potentials) if potentials else 0
    if avg_potential > 0 and len(potentials) > 1:
        variance = sum((p - avg_potential) ** 2 for p in potentials) / len(potentials)
        std_dev = math.sqrt(variance)
        cv = round(std_dev / avg_potential * 100, 1)  # Coefficient of variation
    else:
        cv = 0

    max_potential = max(potentials) if potentials else 0
    min_potential = min(potentials) if potentials else 0
    spread = round((max_potential - min_potential) / avg_potential * 100, 1) if avg_potential > 0 else 0

    if cv < 10:
        balance_rating = "Excellent"
        balance_advice = "Territories are well-balanced. Minor adjustments only if needed."
    elif cv < 20:
        balance_rating = "Good"
        balance_advice = "Acceptable balance. Review outlier territories for adjustment."
    elif cv < 30:
        balance_rating = "Fair"
        balance_advice = "Notable imbalance. Redistribute accounts from heaviest to lightest territories."
    else:
        balance_rating = "Poor"
        balance_advice = "Significant imbalance. Re-run with adjusted strategy or manual overrides."

    return {
        "summary": {
            "total_accounts": len(scored_accounts),
            "total_reps": len(reps),
            "total_potential": round(sum(potentials), 2),
            "avg_potential_per_rep": round(avg_potential, 2),
            "balance_cv_pct": cv,
            "balance_rating": balance_rating,
            "balance_advice": balance_advice,
            "potential_spread_pct": spread,
            "strategy_used": strategy,
        },
        "account_tier_distribution": {
            "Tier 1": sum(1 for a in scored_accounts if a["tier"] == "Tier 1"),
            "Tier 2": sum(1 for a in scored_accounts if a["tier"] == "Tier 2"),
            "Tier 3": sum(1 for a in scored_accounts if a["tier"] == "Tier 3"),
        },
        "territories": {
            name: {
                "rep": terr["rep"],
                "account_count": terr["account_count"],
                "total_potential": terr["total_potential"],
                "avg_account_score": terr["avg_score"],
                "tier_distribution": terr["tier_distribution"],
                "ramping": terr["ramping"],
                "top_accounts": [
                    {"name": a["name"], "potential": a["potential"], "tier": a["tier"]}
                    for a in sorted(terr["accounts"], key=lambda x: x["potential"], reverse=True)[:5]
                ],
            }
            for name, terr in territories.items()
        },
    }


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("TERRITORY PLANNING REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    s = results["summary"]
    lines.append(f"\n  Total Accounts:          {s['total_accounts']}")
    lines.append(f"  Total Reps:              {s['total_reps']}")
    lines.append(f"  Total Potential:         ${s['total_potential']:,.2f}")
    lines.append(f"  Avg Potential / Rep:     ${s['avg_potential_per_rep']:,.2f}")
    lines.append(f"  Strategy:                {s['strategy_used']}")
    lines.append(f"  Balance Rating:          {s['balance_rating']} (CV: {s['balance_cv_pct']}%)")
    lines.append(f"  Balance Advice:          {s['balance_advice']}")

    td = results["account_tier_distribution"]
    lines.append(f"\n  Account Tiers:  Tier 1: {td['Tier 1']}  |  Tier 2: {td['Tier 2']}  |  Tier 3: {td['Tier 3']}")

    lines.append(f"\n{'TERRITORY ASSIGNMENTS':^70}")
    lines.append("-" * 70)
    lines.append(f"  {'Rep':<20} {'Accts':>6} {'Potential':>14} {'Avg Score':>10} {'T1':>4} {'T2':>4} {'T3':>4}")
    lines.append("  " + "-" * 64)

    for name, terr in sorted(
        results["territories"].items(),
        key=lambda x: x[1]["total_potential"],
        reverse=True,
    ):
        ramp = " (R)" if terr["ramping"] else ""
        td = terr["tier_distribution"]
        lines.append(
            f"  {name:<20} {terr['account_count']:>6} "
            f"${terr['total_potential']:>12,.2f} "
            f"{terr['avg_account_score']:>9.1f} "
            f"{td.get('Tier 1', 0):>4} {td.get('Tier 2', 0):>4} {td.get('Tier 3', 0):>4}{ramp}"
        )

    # Top accounts per territory
    for name, terr in results["territories"].items():
        if terr["top_accounts"]:
            lines.append(f"\n  {name} - Top Accounts:")
            for acct in terr["top_accounts"]:
                lines.append(f"    {acct['name']:<35} ${acct['potential']:>10,.2f} [{acct['tier']}]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Optimize territory assignment balancing potential and workload."
    )
    parser.add_argument("--accounts", required=True, help="Path to accounts CSV or JSON file")
    parser.add_argument(
        "--reps",
        required=True,
        help="Number of reps (integer) or path to reps CSV/JSON file",
    )
    parser.add_argument(
        "--strategy",
        choices=["balanced", "geographic"],
        default="balanced",
        help="Assignment strategy (default: balanced)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.accounts):
        print(f"Error: File not found: {args.accounts}", file=sys.stderr)
        sys.exit(1)

    accounts = load_data(args.accounts)
    if not accounts:
        print("Error: No accounts found in input file.", file=sys.stderr)
        sys.exit(1)

    # Parse reps argument
    rep_data = None
    try:
        num_reps = int(args.reps)
    except ValueError:
        if os.path.exists(args.reps):
            rep_data = load_data(args.reps)
            num_reps = len(rep_data)
        else:
            print(f"Error: '{args.reps}' is not a valid number or file path.", file=sys.stderr)
            sys.exit(1)

    if num_reps < 1:
        print("Error: Need at least 1 rep.", file=sys.stderr)
        sys.exit(1)

    results = plan_territories(accounts, num_reps, rep_data, args.strategy)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    cv = results["summary"]["balance_cv_pct"]
    sys.exit(0 if cv < 25 else 1)


if __name__ == "__main__":
    main()
