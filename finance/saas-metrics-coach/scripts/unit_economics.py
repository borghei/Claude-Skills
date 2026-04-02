#!/usr/bin/env python3
"""
Unit Economics Calculator

Calculates LTV, CAC, LTV:CAC ratio, payback period, and related unit economics
metrics from SaaS business data.

Expected JSON input with fields:
  total_customers, new_customers, churned_customers, total_mrr,
  arpu, gross_margin, sales_marketing_spend, monthly_churn_rate

Usage:
    python unit_economics.py metrics.json
    python unit_economics.py metrics.json --format json
    python unit_economics.py metrics.json --discount-rate 0.10
    python unit_economics.py --interactive
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple


REQUIRED_FIELDS = [
    "total_customers",
    "new_customers",
    "total_mrr",
    "sales_marketing_spend",
]


def validate_input(data: Dict[str, Any]) -> List[str]:
    """Validate input data and return list of errors."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "total_customers" in data and data["total_customers"] <= 0:
        errors.append("total_customers must be positive")
    if "new_customers" in data and data["new_customers"] < 0:
        errors.append("new_customers cannot be negative")
    if "sales_marketing_spend" in data and data["sales_marketing_spend"] < 0:
        errors.append("sales_marketing_spend cannot be negative")

    return errors


def derive_missing_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Derive fields that can be calculated from other fields."""
    d = dict(data)

    # Derive ARPU if not provided
    if "arpu" not in d and "total_mrr" in d and "total_customers" in d:
        d["arpu"] = d["total_mrr"] / d["total_customers"] if d["total_customers"] > 0 else 0

    # Derive monthly churn rate if not provided
    if "monthly_churn_rate" not in d:
        if "churned_customers" in d and "total_customers" in d and d["total_customers"] > 0:
            d["monthly_churn_rate"] = d["churned_customers"] / d["total_customers"]
        else:
            d["monthly_churn_rate"] = 0.05  # Default assumption

    # Default gross margin if not provided
    if "gross_margin" not in d:
        d["gross_margin"] = 0.80  # SaaS typical default

    return d


def calculate_ltv_simple(arpu: float, churn_rate: float) -> float:
    """Simple LTV = ARPU / churn rate."""
    if churn_rate <= 0:
        return arpu * 120  # Cap at 10 years if no churn
    return arpu / churn_rate


def calculate_ltv_gross_margin(arpu: float, gross_margin: float, churn_rate: float) -> float:
    """Gross margin adjusted LTV = (ARPU * GM) / churn rate."""
    if churn_rate <= 0:
        return arpu * gross_margin * 120
    return (arpu * gross_margin) / churn_rate


def calculate_ltv_dcf(
    arpu: float, gross_margin: float, churn_rate: float, monthly_discount_rate: float, months: int = 60
) -> float:
    """DCF-based LTV calculation over projected lifetime."""
    ltv = 0.0
    survival_rate = 1.0
    for month in range(1, months + 1):
        survival_rate *= (1 - churn_rate)
        monthly_value = arpu * gross_margin * survival_rate
        discount_factor = 1 / ((1 + monthly_discount_rate) ** month)
        ltv += monthly_value * discount_factor
    return ltv


def calculate_cac(sales_marketing_spend: float, new_customers: int) -> float:
    """Calculate Customer Acquisition Cost."""
    if new_customers <= 0:
        return 0.0
    return sales_marketing_spend / new_customers


def calculate_payback_months(cac: float, arpu: float, gross_margin: float) -> float:
    """Calculate CAC payback period in months."""
    monthly_contribution = arpu * gross_margin
    if monthly_contribution <= 0:
        return float("inf")
    return cac / monthly_contribution


def calculate_unit_economics(data: Dict[str, Any], annual_discount_rate: float = 0.10) -> Dict[str, Any]:
    """Calculate comprehensive unit economics."""
    d = derive_missing_fields(data)

    arpu = d["arpu"]
    churn = d["monthly_churn_rate"]
    gm = d["gross_margin"]
    monthly_dr = (1 + annual_discount_rate) ** (1 / 12) - 1

    # LTV calculations (three methods)
    ltv_simple = calculate_ltv_simple(arpu, churn)
    ltv_gm = calculate_ltv_gross_margin(arpu, gm, churn)
    ltv_dcf = calculate_ltv_dcf(arpu, gm, churn, monthly_dr)

    # CAC
    cac = calculate_cac(d["sales_marketing_spend"], d["new_customers"])

    # Ratios
    ltv_cac_simple = ltv_simple / cac if cac > 0 else float("inf")
    ltv_cac_gm = ltv_gm / cac if cac > 0 else float("inf")
    ltv_cac_dcf = ltv_dcf / cac if cac > 0 else float("inf")

    # Payback
    payback = calculate_payback_months(cac, arpu, gm)

    # Expected lifetime in months
    avg_lifetime = 1 / churn if churn > 0 else 120

    # Monthly contribution margin per customer
    monthly_contribution = arpu * gm

    # Annual unit profit (LTV GM - CAC, annualized)
    annual_unit_profit = (ltv_gm - cac) / (avg_lifetime / 12) if avg_lifetime > 0 else 0

    # Magic number: Net New ARR / Prior Quarter S&M Spend
    magic_number = None
    if "net_new_mrr" in d and d["sales_marketing_spend"] > 0:
        magic_number = (d["net_new_mrr"] * 12) / (d["sales_marketing_spend"] * 3)

    return {
        "period": d.get("period", "current"),
        "inputs": {
            "total_customers": d["total_customers"],
            "new_customers": d["new_customers"],
            "churned_customers": d.get("churned_customers", "N/A"),
            "total_mrr": round(d["total_mrr"], 2),
            "arpu": round(arpu, 2),
            "gross_margin": round(gm, 4),
            "monthly_churn_rate": round(churn, 4),
            "sales_marketing_spend": round(d["sales_marketing_spend"], 2),
            "annual_discount_rate": annual_discount_rate,
        },
        "ltv": {
            "simple": round(ltv_simple, 2),
            "gross_margin_adjusted": round(ltv_gm, 2),
            "dcf": round(ltv_dcf, 2),
        },
        "cac": round(cac, 2),
        "ltv_cac_ratio": {
            "simple": round(ltv_cac_simple, 2) if ltv_cac_simple != float("inf") else "infinite",
            "gross_margin_adjusted": round(ltv_cac_gm, 2) if ltv_cac_gm != float("inf") else "infinite",
            "dcf": round(ltv_cac_dcf, 2) if ltv_cac_dcf != float("inf") else "infinite",
        },
        "payback_months": round(payback, 1) if payback != float("inf") else "infinite",
        "avg_customer_lifetime_months": round(avg_lifetime, 1),
        "monthly_contribution_margin": round(monthly_contribution, 2),
        "magic_number": round(magic_number, 2) if magic_number is not None else "N/A",
    }


def assess_health(results: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate health assessment from unit economics."""
    findings = []

    # LTV:CAC assessment
    ratio = results["ltv_cac_ratio"]["gross_margin_adjusted"]
    if isinstance(ratio, (int, float)):
        if ratio < 1:
            findings.append({
                "metric": "LTV:CAC",
                "status": "CRITICAL",
                "message": f"LTV:CAC is {ratio:.1f}x - losing money on every customer acquired",
                "action": "Immediately reduce CAC or improve retention/pricing",
            })
        elif ratio < 3:
            findings.append({
                "metric": "LTV:CAC",
                "status": "WARNING",
                "message": f"LTV:CAC is {ratio:.1f}x - below the 3x healthy threshold",
                "action": "Focus on reducing churn and optimizing acquisition spend",
            })
        elif ratio > 5:
            findings.append({
                "metric": "LTV:CAC",
                "status": "OPPORTUNITY",
                "message": f"LTV:CAC is {ratio:.1f}x - potentially under-investing in growth",
                "action": "Consider increasing marketing spend to accelerate growth",
            })
        else:
            findings.append({
                "metric": "LTV:CAC",
                "status": "HEALTHY",
                "message": f"LTV:CAC is {ratio:.1f}x - within healthy 3-5x range",
                "action": "Maintain current balance, optimize incrementally",
            })

    # Payback assessment
    payback = results["payback_months"]
    if isinstance(payback, (int, float)):
        if payback > 24:
            findings.append({
                "metric": "CAC Payback",
                "status": "CRITICAL",
                "message": f"Payback period is {payback:.0f} months - strains cash flow severely",
                "action": "Reduce CAC, increase prices, or improve gross margin",
            })
        elif payback > 18:
            findings.append({
                "metric": "CAC Payback",
                "status": "WARNING",
                "message": f"Payback period is {payback:.0f} months - above ideal range",
                "action": "Target sub-18-month payback through pricing or efficiency",
            })
        elif payback <= 12:
            findings.append({
                "metric": "CAC Payback",
                "status": "HEALTHY",
                "message": f"Payback period is {payback:.0f} months - strong cash efficiency",
                "action": "Healthy position, consider scaling spend",
            })

    # Churn assessment
    churn = results["inputs"]["monthly_churn_rate"]
    if churn > 0.05:
        findings.append({
            "metric": "Monthly Churn",
            "status": "CRITICAL",
            "message": f"Monthly churn is {churn*100:.1f}% - losing >5% of customers monthly",
            "action": "Prioritize retention: onboarding, engagement, customer success",
        })
    elif churn > 0.03:
        findings.append({
            "metric": "Monthly Churn",
            "status": "WARNING",
            "message": f"Monthly churn is {churn*100:.1f}% - above target range",
            "action": "Investigate churn reasons, improve activation and engagement",
        })

    return findings


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def print_human(results: Dict[str, Any]) -> None:
    """Print results in human-readable format."""
    print("=" * 60)
    print(f"  Unit Economics Dashboard - {results['period']}")
    print("=" * 60)

    inp = results["inputs"]
    print(f"\n  --- Inputs ---")
    print(f"  Total Customers:      {inp['total_customers']:,}")
    print(f"  New Customers:        {inp['new_customers']:,}")
    print(f"  ARPU:                 {format_currency(inp['arpu'])}")
    print(f"  Gross Margin:         {inp['gross_margin']*100:.1f}%")
    print(f"  Monthly Churn Rate:   {inp['monthly_churn_rate']*100:.2f}%")
    print(f"  S&M Spend:            {format_currency(inp['sales_marketing_spend'])}")

    print(f"\n  --- Lifetime Value ---")
    ltv = results["ltv"]
    print(f"  LTV (Simple):              {format_currency(ltv['simple'])}")
    print(f"  LTV (Gross Margin Adj):    {format_currency(ltv['gross_margin_adjusted'])}")
    print(f"  LTV (DCF, {inp['annual_discount_rate']*100:.0f}% discount):  {format_currency(ltv['dcf'])}")

    print(f"\n  --- Acquisition ---")
    print(f"  CAC:                  {format_currency(results['cac'])}")
    print(f"  LTV:CAC (GM Adj):     {results['ltv_cac_ratio']['gross_margin_adjusted']}x")
    pb = results['payback_months']
    print(f"  Payback Period:       {pb} months")
    print(f"  Avg Lifetime:         {results['avg_customer_lifetime_months']} months")
    print(f"  Monthly Contribution: {format_currency(results['monthly_contribution_margin'])}")

    if results["magic_number"] != "N/A":
        print(f"  Magic Number:         {results['magic_number']}")

    # Health assessment
    findings = assess_health(results)
    if findings:
        print(f"\n  --- Health Assessment ---")
        for f in findings:
            status_icon = {"CRITICAL": "!!!", "WARNING": " ! ", "OPPORTUNITY": " * ", "HEALTHY": " + "}
            icon = status_icon.get(f["status"], "   ")
            print(f"  [{icon}] {f['metric']}: {f['message']}")
            print(f"        Action: {f['action']}")

    print()


def interactive_mode() -> Dict[str, Any]:
    """Collect metrics interactively from stdin."""
    print("Unit Economics Calculator - Interactive Mode")
    print("-" * 40)
    data = {}
    data["total_customers"] = int(input("Total active customers: "))
    data["new_customers"] = int(input("New customers this period: "))
    data["churned_customers"] = int(input("Churned customers this period: "))
    data["total_mrr"] = float(input("Total MRR ($): "))
    data["gross_margin"] = float(input("Gross margin (0.0-1.0): "))
    data["sales_marketing_spend"] = float(input("Sales & marketing spend ($): "))
    data["period"] = input("Period label (e.g., 2025-Q4): ") or "current"
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Calculate LTV, CAC, LTV:CAC ratio, and payback period"
    )
    parser.add_argument("file", nargs="?", help="JSON file with unit economics data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument(
        "--discount-rate", type=float, default=0.10, help="Annual discount rate for DCF LTV (default: 0.10)"
    )
    parser.add_argument("--interactive", action="store_true", help="Enter data interactively")
    args = parser.parse_args()

    if args.interactive:
        data = interactive_mode()
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Error: Provide a JSON file or use --interactive mode", file=sys.stderr)
        sys.exit(1)

    errors = validate_input(data)
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = calculate_unit_economics(data, args.discount_rate)

    if args.format == "json":
        output = {"unit_economics": results, "assessment": assess_health(results)}
        print(json.dumps(output, indent=2, default=str))
    else:
        print_human(results)


if __name__ == "__main__":
    main()
