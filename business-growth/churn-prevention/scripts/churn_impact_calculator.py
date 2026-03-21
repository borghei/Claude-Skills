#!/usr/bin/env python3
"""
Churn Impact Calculator

Calculate the revenue impact of churn reduction at various improvement levels.
Models voluntary churn savings, involuntary churn recovery, and cancel flow
save rate contributions to annual revenue retention.

Usage:
    python churn_impact_calculator.py --mrr 500000 --churn-rate 4.0 --save-rate 20
    python churn_impact_calculator.py --mrr 500000 --churn-rate 4.0 --save-rate 20 --json
"""

import argparse
import json
import sys


def calculate_impact(mrr: float, churn_rate: float, save_rate: float,
                     target_churn: float) -> dict:
    """Calculate revenue impact of churn reduction."""
    monthly_mrr_lost = mrr * (churn_rate / 100.0)
    annual_mrr_lost = monthly_mrr_lost * 12

    # Impact of reducing churn rate to target
    reduction_pct = churn_rate - target_churn
    monthly_savings_from_reduction = mrr * (reduction_pct / 100.0)
    annual_savings_from_reduction = monthly_savings_from_reduction * 12

    # Impact of save rate on remaining churn
    remaining_monthly_churn = mrr * (target_churn / 100.0)
    monthly_savings_from_saves = remaining_monthly_churn * (save_rate / 100.0)
    annual_savings_from_saves = monthly_savings_from_saves * 12

    total_annual_impact = annual_savings_from_reduction + annual_savings_from_saves

    # Scenario modeling at different improvement levels
    scenarios = []
    for improvement in [0.5, 1.0, 1.5, 2.0]:
        new_rate = max(0.1, churn_rate - improvement)
        new_monthly_lost = mrr * (new_rate / 100.0)
        saved = (monthly_mrr_lost - new_monthly_lost) * 12
        scenarios.append({
            "churn_reduction_pct": improvement,
            "new_churn_rate": round(new_rate, 2),
            "annual_mrr_saved": round(saved, 2),
        })

    # Save rate scenarios
    save_scenarios = []
    for sr in [10, 15, 20, 25, 30]:
        monthly_saved = monthly_mrr_lost * (sr / 100.0)
        save_scenarios.append({
            "save_rate_pct": sr,
            "monthly_mrr_saved": round(monthly_saved, 2),
            "annual_mrr_saved": round(monthly_saved * 12, 2),
        })

    # Net Revenue Retention estimate
    nrr = ((mrr - monthly_mrr_lost + monthly_savings_from_reduction +
            monthly_savings_from_saves) / mrr) * 100

    return {
        "inputs": {
            "current_mrr": mrr,
            "current_churn_rate_pct": churn_rate,
            "target_churn_rate_pct": target_churn,
            "save_rate_pct": save_rate,
        },
        "current_state": {
            "monthly_mrr_at_risk": round(monthly_mrr_lost, 2),
            "annual_mrr_at_risk": round(annual_mrr_lost, 2),
            "annual_arr": round(mrr * 12, 2),
            "churn_as_pct_of_arr": round((annual_mrr_lost / (mrr * 12)) * 100, 2),
        },
        "projected_impact": {
            "annual_savings_from_churn_reduction": round(annual_savings_from_reduction, 2),
            "annual_savings_from_save_offers": round(annual_savings_from_saves, 2),
            "total_annual_impact": round(total_annual_impact, 2),
            "estimated_nrr_pct": round(nrr, 2),
        },
        "churn_reduction_scenarios": scenarios,
        "save_rate_scenarios": save_scenarios,
        "recommendations": _generate_recommendations(churn_rate, save_rate, monthly_mrr_lost),
    }


def _generate_recommendations(churn_rate: float, save_rate: float,
                              monthly_lost: float) -> list:
    """Generate actionable recommendations based on inputs."""
    recs = []
    if churn_rate > 5.0:
        recs.append({
            "priority": "CRITICAL",
            "area": "Overall churn",
            "recommendation": "Churn rate above 5% indicates systemic issues beyond cancel flow optimization. Review ICP, product-market fit, and pricing.",
        })
    if churn_rate > 3.0:
        recs.append({
            "priority": "HIGH",
            "area": "Voluntary churn",
            "recommendation": "Implement or optimize cancel flow with exit survey and dynamic save offers. Target 15-25% save rate.",
        })
    if save_rate < 10:
        recs.append({
            "priority": "HIGH",
            "area": "Save rate",
            "recommendation": "Save rate below 10% suggests offers do not match exit reasons. Rebuild reason-to-offer mapping.",
        })
    if save_rate < 20:
        recs.append({
            "priority": "MEDIUM",
            "area": "Save rate",
            "recommendation": "Test stronger save offers: pause option for LOW_USAGE, 30-50% discount for PRICE, free onboarding for COMPLEXITY.",
        })
    recs.append({
        "priority": "MEDIUM",
        "area": "Involuntary churn",
        "recommendation": f"Enable card updater service and optimize dunning. Recovering 30% of failed payments saves ${monthly_lost * 0.3 * 0.3 * 12:,.0f}/year (assuming 30% of churn is involuntary).",
    })
    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("CHURN IMPACT CALCULATOR")
    lines.append("=" * 60)

    inp = result["inputs"]
    lines.append(f"\nCurrent MRR:        ${inp['current_mrr']:>12,.2f}")
    lines.append(f"Churn Rate:         {inp['current_churn_rate_pct']:>12.1f}%")
    lines.append(f"Target Churn Rate:  {inp['target_churn_rate_pct']:>12.1f}%")
    lines.append(f"Save Rate:          {inp['save_rate_pct']:>12.1f}%")

    cs = result["current_state"]
    lines.append(f"\n--- Current State ---")
    lines.append(f"Monthly MRR at Risk:   ${cs['monthly_mrr_at_risk']:>12,.2f}")
    lines.append(f"Annual MRR at Risk:    ${cs['annual_mrr_at_risk']:>12,.2f}")
    lines.append(f"Annual ARR:            ${cs['annual_arr']:>12,.2f}")
    lines.append(f"Churn as % of ARR:     {cs['churn_as_pct_of_arr']:>12.1f}%")

    pi = result["projected_impact"]
    lines.append(f"\n--- Projected Impact ---")
    lines.append(f"From Churn Reduction:  ${pi['annual_savings_from_churn_reduction']:>12,.2f}/year")
    lines.append(f"From Save Offers:      ${pi['annual_savings_from_save_offers']:>12,.2f}/year")
    lines.append(f"Total Annual Impact:   ${pi['total_annual_impact']:>12,.2f}/year")
    lines.append(f"Estimated NRR:         {pi['estimated_nrr_pct']:>12.1f}%")

    lines.append(f"\n--- Churn Reduction Scenarios ---")
    lines.append(f"{'Reduction':>10}  {'New Rate':>10}  {'Annual Saved':>14}")
    for s in result["churn_reduction_scenarios"]:
        lines.append(f"{s['churn_reduction_pct']:>9.1f}%  {s['new_churn_rate']:>9.1f}%  ${s['annual_mrr_saved']:>12,.2f}")

    lines.append(f"\n--- Save Rate Scenarios ---")
    lines.append(f"{'Save Rate':>10}  {'Monthly Saved':>14}  {'Annual Saved':>14}")
    for s in result["save_rate_scenarios"]:
        lines.append(f"{s['save_rate_pct']:>9d}%  ${s['monthly_mrr_saved']:>12,.2f}  ${s['annual_mrr_saved']:>12,.2f}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['area']}: {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate revenue impact of churn reduction at various improvement levels."
    )
    parser.add_argument("--mrr", type=float, required=True,
                        help="Current monthly recurring revenue in dollars")
    parser.add_argument("--churn-rate", type=float, required=True,
                        help="Current monthly churn rate as percentage (e.g., 4.0 for 4%%)")
    parser.add_argument("--save-rate", type=float, default=15.0,
                        help="Cancel flow save rate as percentage (default: 15)")
    parser.add_argument("--target-churn", type=float, default=None,
                        help="Target churn rate as percentage (default: current minus 1)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    if args.mrr <= 0:
        print("Error: --mrr must be positive.", file=sys.stderr)
        sys.exit(1)
    if args.churn_rate <= 0 or args.churn_rate > 100:
        print("Error: --churn-rate must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)
    if args.save_rate < 0 or args.save_rate > 100:
        print("Error: --save-rate must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)

    target = args.target_churn if args.target_churn is not None else max(0.1, args.churn_rate - 1.0)

    result = calculate_impact(args.mrr, args.churn_rate, args.save_rate, target)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
