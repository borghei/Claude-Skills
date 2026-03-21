#!/usr/bin/env python3
"""
Headcount Planner - Model hiring plans with cost, timeline, and business cases.

Generates hiring plans with fully-loaded cost projections, ramp models,
and ROI justification per role. Produces board-ready headcount proposals.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def plan_headcount(data: dict) -> dict:
    """Generate headcount plan with financial projections."""
    roles = data.get("planned_hires", [])
    current_headcount = data.get("current_headcount", 0)
    current_arr = data.get("current_arr", 0)
    budget_quarterly = data.get("hiring_budget_quarterly", 0)

    results = {
        "timestamp": datetime.now().isoformat(),
        "current_state": {"headcount": current_headcount, "arr": current_arr, "arr_per_employee": round(current_arr / current_headcount) if current_headcount > 0 else 0},
        "planned_hires": [],
        "financial_impact": {},
        "timeline": [],
        "budget_analysis": {},
        "recommendations": [],
    }

    total_annual_cost = 0
    total_hires = 0
    quarterly_costs = {1: 0, 2: 0, 3: 0, 4: 0}

    for role in roles:
        title = role.get("title", "")
        department = role.get("department", "")
        level = role.get("level", "L3")
        base_salary = role.get("base_salary", 120000)
        equity_value = role.get("equity_annual", 20000)
        benefits_pct = role.get("benefits_pct", 25)
        start_quarter = role.get("target_quarter", 1)
        ramp_months = role.get("ramp_months", 3)
        revenue_impact = role.get("expected_revenue_impact", 0)
        risk_description = role.get("risk_if_not_filled", "")
        business_case = role.get("business_case", "")
        manager = role.get("reporting_to", "")

        # Fully loaded cost
        benefits = base_salary * (benefits_pct / 100)
        tools_overhead = 12000  # annual estimate
        fully_loaded = base_salary + benefits + equity_value + tools_overhead
        monthly_cost = fully_loaded / 12

        # Quarterly cost based on start quarter
        for q in range(start_quarter, 5):
            months_in_q = 3 if q > start_quarter else max(1, 3 - (start_quarter - 1))
            quarterly_costs[q] += monthly_cost * months_in_q

        # ROI calculation
        roi = ((revenue_impact - fully_loaded) / fully_loaded) if fully_loaded > 0 and revenue_impact > 0 else 0

        hire = {
            "title": title,
            "department": department,
            "level": level,
            "reporting_to": manager,
            "target_quarter": f"Q{start_quarter}",
            "base_salary": base_salary,
            "fully_loaded_annual": round(fully_loaded),
            "monthly_cost": round(monthly_cost),
            "ramp_months": ramp_months,
            "full_productivity_month": ramp_months,
            "expected_revenue_impact": revenue_impact,
            "roi": round(roi, 2),
            "business_case": business_case,
            "risk_if_not_filled": risk_description,
            "priority": "Critical" if roi > 2 or "critical" in risk_description.lower() else "High" if roi > 1 else "Medium" if roi > 0 else "Support",
        }
        results["planned_hires"].append(hire)
        total_annual_cost += fully_loaded
        total_hires += 1

    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Support": 3}
    results["planned_hires"].sort(key=lambda x: priority_order.get(x["priority"], 4))

    # Financial impact
    new_arr_per_emp = current_arr / (current_headcount + total_hires) if (current_headcount + total_hires) > 0 else 0
    results["financial_impact"] = {
        "total_new_hires": total_hires,
        "total_annual_cost": round(total_annual_cost),
        "quarterly_cost_breakdown": {f"Q{q}": round(c) for q, c in quarterly_costs.items()},
        "new_headcount": current_headcount + total_hires,
        "new_arr_per_employee": round(new_arr_per_emp),
        "arr_per_emp_change": round(new_arr_per_emp - results["current_state"]["arr_per_employee"]),
        "total_revenue_impact": sum(h["expected_revenue_impact"] for h in results["planned_hires"]),
        "plan_roi": round(sum(h["expected_revenue_impact"] for h in results["planned_hires"]) / total_annual_cost, 2) if total_annual_cost > 0 else 0,
    }

    # Timeline
    for q in range(1, 5):
        q_hires = [h for h in results["planned_hires"] if h["target_quarter"] == f"Q{q}"]
        if q_hires:
            results["timeline"].append({
                "quarter": f"Q{q}",
                "hires": len(q_hires),
                "roles": [h["title"] for h in q_hires],
                "quarterly_cost": quarterly_costs[q],
            })

    # Budget analysis
    if budget_quarterly > 0:
        over_budget_quarters = [f"Q{q}" for q, c in quarterly_costs.items() if c > budget_quarterly]
        results["budget_analysis"] = {
            "quarterly_budget": budget_quarterly,
            "over_budget_quarters": over_budget_quarters,
            "total_budget_annual": budget_quarterly * 4,
            "total_planned_cost": round(total_annual_cost),
            "within_budget": total_annual_cost <= budget_quarterly * 4,
        }

    # Recommendations
    critical = [h for h in results["planned_hires"] if h["priority"] == "Critical"]
    if critical:
        results["recommendations"].append(f"{len(critical)} critical hire(s). Prioritize these regardless of other sequencing.")

    fi = results["financial_impact"]
    if fi["arr_per_emp_change"] < -10000:
        results["recommendations"].append(f"ARR per employee decreases by ${abs(fi['arr_per_emp_change']):,.0f}. Ensure revenue hires compensate.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    cs = results["current_state"]
    fi = results["financial_impact"]
    lines = [
        "=" * 75,
        "HEADCOUNT PLAN",
        "=" * 75,
        f"Current: {cs['headcount']} employees  |  ARR: ${cs['arr']:,.0f}  |  ARR/emp: ${cs['arr_per_employee']:,.0f}",
        f"Planned: +{fi['total_new_hires']} hires  |  Cost: ${fi['total_annual_cost']:,.0f}/yr  |  Plan ROI: {fi['plan_roi']:.1f}x",
        "",
        f"{'Title':<22} {'Dept':<12} {'Q':>3} {'Loaded $':>10} {'Rev Impact':>11} {'ROI':>5} {'Priority':<10}",
        "-" * 75,
    ]

    for h in results["planned_hires"]:
        lines.append(
            f"{h['title']:<22} {h['department']:<12} {h['target_quarter']:>3} "
            f"${h['fully_loaded_annual']:>9,.0f} ${h['expected_revenue_impact']:>10,.0f} "
            f"{h['roi']:>4.1f}x {h['priority']:<10}"
        )

    lines.extend(["", "QUARTERLY COST:"])
    for q, cost in fi["quarterly_cost_breakdown"].items():
        lines.append(f"  {q}: ${cost:,.0f}")

    if results["budget_analysis"]:
        ba = results["budget_analysis"]
        status = "WITHIN BUDGET" if ba["within_budget"] else "OVER BUDGET"
        lines.extend(["", f"BUDGET: {status} (${ba['total_planned_cost']:,.0f} vs ${ba['total_budget_annual']:,.0f} annual)"])

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 75])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate headcount plan with financial projections")
    parser.add_argument("--input", "-i", help="JSON file with hiring plan data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "current_headcount": 35,
            "current_arr": 3000000,
            "hiring_budget_quarterly": 200000,
            "planned_hires": [
                {"title": "Sr Backend Engineer", "department": "Engineering", "level": "L4", "base_salary": 180000, "equity_annual": 30000, "target_quarter": 1, "ramp_months": 3, "expected_revenue_impact": 0, "risk_if_not_filled": "Critical path blocked on API redesign", "reporting_to": "CTO", "business_case": "Unblock API platform rebuild"},
                {"title": "Account Executive", "department": "Sales", "level": "L3", "base_salary": 140000, "equity_annual": 15000, "target_quarter": 1, "ramp_months": 4, "expected_revenue_impact": 500000, "risk_if_not_filled": "Pipeline uncovered in mid-market", "reporting_to": "CRO", "business_case": "Cover $2M pipeline gap"},
                {"title": "Product Manager", "department": "Product", "level": "L3", "base_salary": 160000, "equity_annual": 25000, "target_quarter": 2, "ramp_months": 3, "expected_revenue_impact": 300000, "risk_if_not_filled": "Enterprise features delayed", "reporting_to": "CPO", "business_case": "Own enterprise product line"},
                {"title": "SDR", "department": "Sales", "level": "L2", "base_salary": 65000, "equity_annual": 5000, "target_quarter": 1, "ramp_months": 2, "expected_revenue_impact": 200000, "risk_if_not_filled": "Pipeline generation below target", "reporting_to": "CRO", "business_case": "Generate 50 SQLs/quarter"},
                {"title": "People Partner", "department": "People", "level": "L3", "base_salary": 120000, "equity_annual": 15000, "target_quarter": 2, "ramp_months": 2, "expected_revenue_impact": 0, "risk_if_not_filled": "HR ratio at 1:35, below minimum", "reporting_to": "CHRO", "business_case": "Support scaling from 35 to 50"},
            ],
        }

    results = plan_headcount(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
