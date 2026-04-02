#!/usr/bin/env python3
"""
MRR Calculator

Calculates MRR, ARR, growth rate, churn rate, net new MRR, and SaaS quick ratio
from subscription data in CSV format.

Expected CSV columns: customer_id, plan, mrr, start_date, end_date, status
- end_date can be empty for active subscriptions
- status: active, churned, or cancelled

Usage:
    python mrr_calculator.py subscriptions.csv
    python mrr_calculator.py subscriptions.csv --format json
    python mrr_calculator.py subscriptions.csv --breakdown
    python mrr_calculator.py subscriptions.csv --period 2025-06
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


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
    """Return YYYY-MM string from datetime."""
    return dt.strftime("%Y-%m")


def load_subscriptions(filepath: str) -> List[Dict[str, Any]]:
    """Load subscription data from CSV."""
    subscriptions = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"customer_id", "plan", "mrr", "start_date"}
        if not required.issubset(set(reader.fieldnames or [])):
            missing = required - set(reader.fieldnames or [])
            print(f"Error: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)
        for row in reader:
            try:
                sub = {
                    "customer_id": row["customer_id"].strip(),
                    "plan": row.get("plan", "unknown").strip(),
                    "mrr": float(row["mrr"]),
                    "start_date": parse_date(row["start_date"]),
                    "end_date": parse_date(row.get("end_date", "")),
                    "status": row.get("status", "active").strip().lower(),
                }
                if sub["start_date"] is None:
                    continue
                subscriptions.append(sub)
            except (ValueError, KeyError):
                continue
    return subscriptions


def get_active_mrr_at(subscriptions: List[Dict], target: datetime) -> Tuple[float, int]:
    """Calculate total MRR and active customer count at a given date."""
    total_mrr = 0.0
    active_count = 0
    seen = set()
    for sub in subscriptions:
        if sub["start_date"] <= target:
            if sub["end_date"] is None or sub["end_date"] > target:
                if sub["customer_id"] not in seen:
                    total_mrr += sub["mrr"]
                    active_count += 1
                    seen.add(sub["customer_id"])
    return total_mrr, active_count


def calculate_mrr_components(subscriptions: List[Dict], period: str) -> Dict[str, Any]:
    """Calculate MRR components for a given YYYY-MM period."""
    year, month = int(period[:4]), int(period[5:7])
    period_start = datetime(year, month, 1)
    if month == 12:
        period_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        period_end = datetime(year, month + 1, 1) - timedelta(days=1)

    # Previous period
    if month == 1:
        prev_start = datetime(year - 1, 12, 1)
    else:
        prev_start = datetime(year, month - 1, 1)

    beginning_mrr, beginning_customers = get_active_mrr_at(subscriptions, period_start - timedelta(days=1))
    ending_mrr, ending_customers = get_active_mrr_at(subscriptions, period_end)

    new_mrr = 0.0
    new_count = 0
    churned_mrr = 0.0
    churned_count = 0

    customer_mrr_start = {}
    customer_mrr_end = {}

    for sub in subscriptions:
        cid = sub["customer_id"]
        if sub["start_date"] <= period_start - timedelta(days=1):
            if sub["end_date"] is None or sub["end_date"] > period_start - timedelta(days=1):
                customer_mrr_start[cid] = sub["mrr"]

        if sub["start_date"] <= period_end:
            if sub["end_date"] is None or sub["end_date"] > period_end:
                customer_mrr_end[cid] = sub["mrr"]

    # New customers: in end but not in start
    for cid, mrr in customer_mrr_end.items():
        if cid not in customer_mrr_start:
            new_mrr += mrr
            new_count += 1

    # Churned customers: in start but not in end
    for cid, mrr in customer_mrr_start.items():
        if cid not in customer_mrr_end:
            churned_mrr += mrr
            churned_count += 1

    # Expansion and contraction
    expansion_mrr = 0.0
    contraction_mrr = 0.0
    for cid in customer_mrr_start:
        if cid in customer_mrr_end:
            diff = customer_mrr_end[cid] - customer_mrr_start[cid]
            if diff > 0:
                expansion_mrr += diff
            elif diff < 0:
                contraction_mrr += abs(diff)

    net_new_mrr = new_mrr + expansion_mrr - churned_mrr - contraction_mrr
    gross_churn_rate = (churned_mrr + contraction_mrr) / beginning_mrr if beginning_mrr > 0 else 0.0
    net_churn_rate = (churned_mrr + contraction_mrr - expansion_mrr) / beginning_mrr if beginning_mrr > 0 else 0.0
    nrr = (beginning_mrr + expansion_mrr - churned_mrr - contraction_mrr) / beginning_mrr if beginning_mrr > 0 else 0.0
    growth_rate = (ending_mrr - beginning_mrr) / beginning_mrr if beginning_mrr > 0 else 0.0

    # SaaS Quick Ratio
    inflows = new_mrr + expansion_mrr
    outflows = churned_mrr + contraction_mrr
    quick_ratio = inflows / outflows if outflows > 0 else float("inf")

    return {
        "period": period,
        "beginning_mrr": round(beginning_mrr, 2),
        "ending_mrr": round(ending_mrr, 2),
        "arr": round(ending_mrr * 12, 2),
        "new_mrr": round(new_mrr, 2),
        "expansion_mrr": round(expansion_mrr, 2),
        "contraction_mrr": round(contraction_mrr, 2),
        "churned_mrr": round(churned_mrr, 2),
        "net_new_mrr": round(net_new_mrr, 2),
        "beginning_customers": beginning_customers,
        "ending_customers": ending_customers,
        "new_customers": new_count,
        "churned_customers": churned_count,
        "gross_churn_rate": round(gross_churn_rate, 4),
        "net_churn_rate": round(net_churn_rate, 4),
        "net_revenue_retention": round(nrr, 4),
        "mom_growth_rate": round(growth_rate, 4),
        "saas_quick_ratio": round(quick_ratio, 2) if quick_ratio != float("inf") else "infinite",
    }


def breakdown_by_plan(subscriptions: List[Dict], period: str) -> Dict[str, Dict]:
    """Break down MRR by plan tier."""
    year, month = int(period[:4]), int(period[5:7])
    if month == 12:
        period_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        period_end = datetime(year, month + 1, 1) - timedelta(days=1)

    plan_data = defaultdict(lambda: {"mrr": 0.0, "customers": 0})
    for sub in subscriptions:
        if sub["start_date"] <= period_end:
            if sub["end_date"] is None or sub["end_date"] > period_end:
                plan = sub["plan"]
                plan_data[plan]["mrr"] += sub["mrr"]
                plan_data[plan]["customers"] += 1

    total_mrr = sum(p["mrr"] for p in plan_data.values())
    result = {}
    for plan, data in sorted(plan_data.items()):
        result[plan] = {
            "mrr": round(data["mrr"], 2),
            "customers": data["customers"],
            "arpu": round(data["mrr"] / data["customers"], 2) if data["customers"] > 0 else 0,
            "mix_pct": round(data["mrr"] / total_mrr * 100, 1) if total_mrr > 0 else 0,
        }
    return result


def detect_periods(subscriptions: List[Dict]) -> List[str]:
    """Detect all months with subscription activity."""
    months = set()
    for sub in subscriptions:
        if sub["start_date"]:
            months.add(month_key(sub["start_date"]))
        if sub["end_date"]:
            months.add(month_key(sub["end_date"]))
    return sorted(months)


def format_currency(amount: float) -> str:
    """Format number as currency."""
    return f"${amount:,.2f}"


def format_pct(value: float) -> str:
    """Format decimal as percentage."""
    return f"{value * 100:.1f}%"


def print_human(results: Dict, breakdown: Optional[Dict] = None) -> None:
    """Print results in human-readable format."""
    print("=" * 60)
    print(f"  SaaS MRR Report - {results['period']}")
    print("=" * 60)

    print(f"\n  MRR:                {format_currency(results['ending_mrr'])}")
    print(f"  ARR:                {format_currency(results['arr'])}")
    print(f"  Beginning MRR:      {format_currency(results['beginning_mrr'])}")
    print(f"  Net New MRR:        {format_currency(results['net_new_mrr'])}")

    print(f"\n  --- MRR Components ---")
    print(f"  New MRR:            {format_currency(results['new_mrr'])} ({results['new_customers']} customers)")
    print(f"  Expansion MRR:      {format_currency(results['expansion_mrr'])}")
    print(f"  Contraction MRR:   -{format_currency(results['contraction_mrr'])}")
    print(f"  Churned MRR:       -{format_currency(results['churned_mrr'])} ({results['churned_customers']} customers)")

    print(f"\n  --- Health Metrics ---")
    print(f"  Gross Churn Rate:   {format_pct(results['gross_churn_rate'])}")
    print(f"  Net Churn Rate:     {format_pct(results['net_churn_rate'])}")
    print(f"  Net Revenue Retention: {format_pct(results['net_revenue_retention'])}")
    print(f"  MoM Growth Rate:    {format_pct(results['mom_growth_rate'])}")
    qr = results['saas_quick_ratio']
    print(f"  SaaS Quick Ratio:   {qr}")

    print(f"\n  --- Customers ---")
    print(f"  Active Customers:   {results['ending_customers']}")
    arpu = results['ending_mrr'] / results['ending_customers'] if results['ending_customers'] > 0 else 0
    print(f"  ARPU:               {format_currency(arpu)}")

    # Health assessment
    print(f"\n  --- Assessment ---")
    warnings = []
    if results['gross_churn_rate'] > 0.05:
        warnings.append("Gross churn rate exceeds 5% monthly threshold")
    if results['net_revenue_retention'] < 0.90:
        warnings.append("Net revenue retention below 90% - significant revenue leakage")
    elif results['net_revenue_retention'] < 1.00:
        warnings.append("Net revenue retention below 100% - expansion not offsetting churn")
    if isinstance(qr, (int, float)) and qr < 2:
        warnings.append("SaaS Quick Ratio below 2 - growth efficiency is low")

    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    else:
        print("  All metrics within healthy ranges")

    if breakdown:
        print(f"\n  --- Plan Breakdown ---")
        print(f"  {'Plan':<15} {'MRR':>12} {'Customers':>10} {'ARPU':>10} {'Mix':>8}")
        print(f"  {'-'*55}")
        for plan, data in breakdown.items():
            print(f"  {plan:<15} {format_currency(data['mrr']):>12} {data['customers']:>10} {format_currency(data['arpu']):>10} {data['mix_pct']:>7.1f}%")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate MRR, ARR, growth rate, and churn from subscription CSV data"
    )
    parser.add_argument("file", help="CSV file with subscription data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--period", help="Period to analyze (YYYY-MM). Default: latest detected period")
    parser.add_argument("--breakdown", action="store_true", help="Include breakdown by plan tier")
    parser.add_argument("--all-periods", action="store_true", help="Show metrics for all detected periods")
    args = parser.parse_args()

    subscriptions = load_subscriptions(args.file)
    if not subscriptions:
        print("Error: No valid subscription records found", file=sys.stderr)
        sys.exit(1)

    periods = detect_periods(subscriptions)
    if not periods:
        print("Error: No periods detected in data", file=sys.stderr)
        sys.exit(1)

    if args.all_periods:
        target_periods = periods
    elif args.period:
        target_periods = [args.period]
    else:
        target_periods = [periods[-1]]

    all_results = []
    for period in target_periods:
        results = calculate_mrr_components(subscriptions, period)
        bd = breakdown_by_plan(subscriptions, period) if args.breakdown else None
        all_results.append({"metrics": results, "breakdown": bd})

    if args.format == "json":
        output = all_results if len(all_results) > 1 else all_results[0]
        print(json.dumps(output, indent=2, default=str))
    else:
        for item in all_results:
            print_human(item["metrics"], item.get("breakdown"))


if __name__ == "__main__":
    main()
