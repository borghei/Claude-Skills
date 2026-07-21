#!/usr/bin/env python3
"""
E-commerce Unit Economics Calculator — model gross margin, contribution margin,
CAC payback, and break-even repeat rate from a structured input file.

Usage:
    python ecom_unit_economics_calculator.py model.json
    python ecom_unit_economics_calculator.py model.json --json

Input model schema:
{
  "channel": "DTC site",
  "average_order_value": 80.00,
  "units_per_order": 1,
  "cogs_per_unit": 16.00,
  "shipping_charged_to_customer": 5.00,
  "shipping_actual_cost": 8.50,
  "fulfillment_pick_pack_per_order": 3.50,
  "payment_processing_pct": 2.9,
  "payment_processing_fixed": 0.30,
  "return_rate_pct": 12.0,
  "return_cost_per_returned_order": 12.00,
  "marketing_spend_per_acquired_customer": 38.00,
  "repeat_orders_in_first_year": 1.4
}
"""

import argparse
import json
import sys
from pathlib import Path


def calculate(model):
    aov = float(model.get("average_order_value", 0))
    units = float(model.get("units_per_order", 1))
    cogs = float(model.get("cogs_per_unit", 0)) * units
    ship_charged = float(model.get("shipping_charged_to_customer", 0))
    ship_cost = float(model.get("shipping_actual_cost", 0))
    pick_pack = float(model.get("fulfillment_pick_pack_per_order", 0))
    pay_pct = float(model.get("payment_processing_pct", 2.9)) / 100.0
    pay_fixed = float(model.get("payment_processing_fixed", 0.30))
    return_rate = float(model.get("return_rate_pct", 0)) / 100.0
    return_cost = float(model.get("return_cost_per_returned_order", 0))
    cac = float(model.get("marketing_spend_per_acquired_customer", 0))
    repeat_orders = float(model.get("repeat_orders_in_first_year", 0))

    # Revenue per order (customer pays AOV + shipping, but AOV already includes the product cost)
    revenue_per_order = aov + ship_charged

    # Variable costs per order (before returns & CAC)
    variable_costs = cogs + ship_cost + pick_pack + (pay_pct * revenue_per_order) + pay_fixed

    # Returns: probability-weighted cost
    expected_return_cost = return_rate * (cogs + return_cost)  # lose COGS on returned orders + reverse logistics

    contribution_per_order_pre_cac = revenue_per_order - variable_costs - expected_return_cost

    gross_margin_per_order = revenue_per_order - cogs - (pay_pct * revenue_per_order) - pay_fixed
    gross_margin_pct = (gross_margin_per_order / revenue_per_order) * 100 if revenue_per_order else 0

    contribution_margin_pct = (contribution_per_order_pre_cac / revenue_per_order) * 100 if revenue_per_order else 0

    # Customer-level economics
    orders_per_customer_year_one = 1 + repeat_orders
    contribution_per_customer_year_one = contribution_per_order_pre_cac * orders_per_customer_year_one

    profit_per_customer_year_one = contribution_per_customer_year_one - cac

    # CAC payback (in orders)
    cac_payback_orders = cac / contribution_per_order_pre_cac if contribution_per_order_pre_cac > 0 else None
    # CAC payback in months — assume orders are evenly spaced over 12 months
    cac_payback_months = (cac_payback_orders / orders_per_customer_year_one * 12) if cac_payback_orders and orders_per_customer_year_one else None

    # Break-even repeat rate (orders beyond first to recover CAC)
    break_even_extra_orders = max(0, (cac - contribution_per_order_pre_cac) / contribution_per_order_pre_cac) if contribution_per_order_pre_cac > 0 else None

    return {
        "channel": model.get("channel", "(unspecified)"),
        "revenue_per_order": round(revenue_per_order, 2),
        "variable_costs_per_order": round(variable_costs, 2),
        "expected_return_cost_per_order": round(expected_return_cost, 2),
        "gross_margin_per_order": round(gross_margin_per_order, 2),
        "gross_margin_pct": round(gross_margin_pct, 1),
        "contribution_per_order_pre_cac": round(contribution_per_order_pre_cac, 2),
        "contribution_margin_pct": round(contribution_margin_pct, 1),
        "cac": round(cac, 2),
        "orders_per_customer_year_one": round(orders_per_customer_year_one, 2),
        "contribution_per_customer_year_one": round(contribution_per_customer_year_one, 2),
        "profit_per_customer_year_one": round(profit_per_customer_year_one, 2),
        "cac_payback_orders": round(cac_payback_orders, 2) if cac_payback_orders else None,
        "cac_payback_months": round(cac_payback_months, 1) if cac_payback_months else None,
        "break_even_extra_repeat_orders_required": round(break_even_extra_orders, 2) if break_even_extra_orders is not None else None,
    }


def render_human(r):
    lines = [f"Unit Economics — {r['channel']}"]
    lines.append("=" * 60)
    lines.append("")
    lines.append("Per-order economics:")
    lines.append(f"  Revenue per order:                ${r['revenue_per_order']:>10.2f}")
    lines.append(f"  Variable costs:                   ${r['variable_costs_per_order']:>10.2f}")
    lines.append(f"  Expected return cost (probabilistic):${r['expected_return_cost_per_order']:>7.2f}")
    lines.append(f"  Gross margin:                     ${r['gross_margin_per_order']:>10.2f}  ({r['gross_margin_pct']}%)")
    lines.append(f"  Contribution margin (pre-CAC):    ${r['contribution_per_order_pre_cac']:>10.2f}  ({r['contribution_margin_pct']}%)")
    lines.append("")
    lines.append("Customer-level (Year 1):")
    lines.append(f"  CAC:                              ${r['cac']:>10.2f}")
    lines.append(f"  Orders per customer (year 1):     {r['orders_per_customer_year_one']}")
    lines.append(f"  Contribution per customer:        ${r['contribution_per_customer_year_one']:>10.2f}")
    lines.append(f"  Profit per customer:              ${r['profit_per_customer_year_one']:>10.2f}")
    lines.append("")
    lines.append("CAC payback:")
    if r["cac_payback_orders"] is not None:
        lines.append(f"  Orders to recover CAC:            {r['cac_payback_orders']}")
        lines.append(f"  Months to recover CAC:            {r['cac_payback_months']}")
    else:
        lines.append("  CAC cannot be recovered with current contribution margin")
    if r["break_even_extra_repeat_orders_required"] is not None:
        lines.append(f"  Extra repeat orders to break even:{r['break_even_extra_repeat_orders_required']}")
    lines.append("")
    lines.append("Verdict:")
    if r["contribution_margin_pct"] < 0:
        lines.append("  Negative contribution margin — every order loses money. Restructure costs or kill the SKU.")
    elif r["cac_payback_months"] is not None and r["cac_payback_months"] > 12:
        lines.append("  CAC payback over 12 months — likely unsustainable in DTC at this CAC.")
    elif r["cac_payback_months"] is not None and r["cac_payback_months"] > 6:
        lines.append("  CAC payback 6-12 months — workable but tight; expect cash-flow strain.")
    elif r["cac_payback_months"] is not None and r["cac_payback_months"] <= 6:
        lines.append("  CAC payback under 6 months — healthy DTC economics.")
    else:
        lines.append("  Insufficient data for verdict.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate ecommerce unit economics from a JSON model.")
    parser.add_argument("model", help="Path to model.json (see script docstring for schema)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.model)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    result = calculate(model)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
