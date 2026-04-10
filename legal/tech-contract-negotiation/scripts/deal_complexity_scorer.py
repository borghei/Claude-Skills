#!/usr/bin/env python3
"""
Deal Complexity Scorer

Takes deal parameters and scores complexity across 7 dimensions.
Recommends deal tier (1-5), expected timeline, number of rounds,
and key focus areas.

Usage:
    python deal_complexity_scorer.py deal_params.json
    python deal_complexity_scorer.py deal_params.json --json
    python deal_complexity_scorer.py deal_params.json --deal-value 5000000

Expected JSON input format:
{
    "deal_value": 1500000,
    "duration_months": 36,
    "parties": 2,
    "regulatory_requirements": ["GDPR", "DORA"],
    "service_criticality": "high",
    "technical_complexity": "moderate",
    "ip_sensitivity": "high",
    "multi_jurisdictional": false,
    "custom_development": true,
    "data_processing": true,
    "strategic_importance": "high"
}
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


# Deal tier definitions
DEAL_TIERS: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "Standard",
        "value_range": "$100K - $500K",
        "timeline_weeks": "2-4",
        "expected_rounds": "1-2",
        "focus": ["Standard terms review", "Basic SLA alignment", "Payment terms"],
        "approval_level": "Department Head",
    },
    2: {
        "name": "Enhanced",
        "value_range": "$500K - $1M",
        "timeline_weeks": "4-6",
        "expected_rounds": "2-3",
        "focus": ["Liability caps", "IP provisions", "SLA customization", "Data protection"],
        "approval_level": "VP / Director",
    },
    3: {
        "name": "Complex",
        "value_range": "$1M - $3M",
        "timeline_weeks": "6-10",
        "expected_rounds": "3-5",
        "focus": ["Full liability framework", "IP ownership structure", "Custom SLAs", "Regulatory compliance", "Indemnification"],
        "approval_level": "SVP / General Counsel",
    },
    4: {
        "name": "Strategic",
        "value_range": "$3M - $10M",
        "timeline_weeks": "10-16",
        "expected_rounds": "5-8",
        "focus": ["Enterprise liability framework", "Complex IP arrangements", "Multi-year SLAs with escalation", "Full regulatory suite", "Governance structure"],
        "approval_level": "C-Suite / Board Committee",
    },
    5: {
        "name": "Transformational",
        "value_range": "$10M+",
        "timeline_weeks": "16-26",
        "expected_rounds": "8-12",
        "focus": ["Bespoke liability and indemnification", "IP co-development framework", "Mission-critical SLAs", "Full regulatory and audit rights", "Joint governance", "Exit and transition planning"],
        "approval_level": "Board Approval",
    },
}

# Scoring criteria for each dimension (1-5 scale)
CRITICALITY_MAP = {"low": 1, "moderate": 2, "high": 4, "critical": 5}
COMPLEXITY_MAP = {"low": 1, "moderate": 2, "high": 4, "very_high": 5}
IMPORTANCE_MAP = {"low": 1, "moderate": 2, "high": 4, "strategic": 5}

# Regulatory complexity weights
REGULATORY_WEIGHTS: Dict[str, float] = {
    "GDPR": 1.5, "DORA": 2.0, "NIS2": 1.8, "SOX": 1.5,
    "HIPAA": 1.8, "PCI_DSS": 1.5, "ISO_27001": 1.0, "SOC_2": 1.0,
    "FedRAMP": 2.5, "CCPA": 1.0, "EU_AI_ACT": 2.0,
}


def score_value_dimension(deal_value: float) -> Tuple[int, str]:
    """Score the deal value dimension (1-5)."""
    if deal_value < 500_000:
        return 1, f"${deal_value:,.0f} -- Standard tier, minimal complexity from value alone"
    elif deal_value < 1_000_000:
        return 2, f"${deal_value:,.0f} -- Enhanced tier, moderate commercial scrutiny"
    elif deal_value < 3_000_000:
        return 3, f"${deal_value:,.0f} -- Complex tier, significant commercial and legal review"
    elif deal_value < 10_000_000:
        return 4, f"${deal_value:,.0f} -- Strategic tier, executive-level commercial terms"
    else:
        return 5, f"${deal_value:,.0f} -- Transformational tier, board-level commercial significance"


def score_regulatory_dimension(regulations: List[str]) -> Tuple[int, str]:
    """Score regulatory complexity based on applicable frameworks."""
    if not regulations:
        return 1, "No specific regulatory requirements identified"

    total_weight = sum(REGULATORY_WEIGHTS.get(r.upper().replace(" ", "_"), 1.0) for r in regulations)
    count = len(regulations)

    if total_weight <= 1.5:
        score = 1
    elif total_weight <= 3.0:
        score = 2
    elif total_weight <= 5.0:
        score = 3
    elif total_weight <= 8.0:
        score = 4
    else:
        score = 5

    reg_list = ", ".join(regulations)
    return score, f"{count} framework(s): {reg_list} (weighted complexity: {total_weight:.1f})"


def score_technical_dimension(params: Dict[str, Any]) -> Tuple[int, str]:
    """Score technical complexity."""
    base = COMPLEXITY_MAP.get(params.get("technical_complexity", "low"), 1)
    factors: List[str] = []

    if params.get("custom_development", False):
        base = min(5, base + 1)
        factors.append("custom development")
    if params.get("data_processing", False):
        base = min(5, base + 1)
        factors.append("data processing")
    if params.get("system_integration", False):
        base = min(5, base + 1)
        factors.append("system integration")

    detail = f"Base: {params.get('technical_complexity', 'low')}"
    if factors:
        detail += f" + {', '.join(factors)}"
    return min(5, base), detail


def score_multiparty_dimension(parties: int, multi_jurisdictional: bool) -> Tuple[int, str]:
    """Score multi-party and jurisdictional complexity."""
    if parties <= 2 and not multi_jurisdictional:
        return 1, f"{parties} parties, single jurisdiction"
    elif parties <= 2 and multi_jurisdictional:
        return 3, f"{parties} parties, multi-jurisdictional"
    elif parties <= 4:
        score = 3 if not multi_jurisdictional else 4
        return score, f"{parties} parties, {'multi-jurisdictional' if multi_jurisdictional else 'single jurisdiction'}"
    else:
        return 5, f"{parties} parties, {'multi-jurisdictional' if multi_jurisdictional else 'single jurisdiction'}"


def score_duration_dimension(months: int) -> Tuple[int, str]:
    """Score contract duration complexity."""
    if months <= 12:
        return 1, f"{months} months -- short-term, minimal long-term risk exposure"
    elif months <= 24:
        return 2, f"{months} months -- medium-term, moderate renewal and escalation considerations"
    elif months <= 36:
        return 3, f"{months} months -- multi-year, requires escalation caps and exit planning"
    elif months <= 60:
        return 4, f"{months} months -- long-term, significant lock-in and exit complexity"
    else:
        return 5, f"{months} months -- extended commitment, full lifecycle planning required"


def score_strategic_dimension(importance: str) -> Tuple[int, str]:
    """Score strategic importance."""
    score = IMPORTANCE_MAP.get(importance, 1)
    descriptions = {
        1: "Low strategic importance -- commodity service, easily replaceable",
        2: "Moderate strategic importance -- enhances operations but alternatives exist",
        4: "High strategic importance -- core to business operations, limited alternatives",
        5: "Strategic/transformational -- defines competitive advantage, no viable alternatives",
    }
    return score, descriptions.get(score, "Unknown importance level")


def score_ip_dimension(sensitivity: str, custom_dev: bool) -> Tuple[int, str]:
    """Score IP sensitivity."""
    base = CRITICALITY_MAP.get(sensitivity, 1)
    if custom_dev and base < 5:
        base = min(5, base + 1)

    descriptions = {
        1: "Low IP sensitivity -- standard off-the-shelf services",
        2: "Moderate IP sensitivity -- some customization, clear ownership lines",
        3: "Notable IP sensitivity -- significant customization, ownership negotiation needed",
        4: "High IP sensitivity -- custom development with co-created IP",
        5: "Critical IP sensitivity -- core technology, trade secrets, or competitive advantage at stake",
    }
    return base, descriptions.get(base, "Unknown IP sensitivity level")


def calculate_composite(dimensions: Dict[str, Dict[str, Any]]) -> Tuple[float, int]:
    """Calculate weighted composite score and determine deal tier."""
    weights = {
        "value": 1.5, "regulatory": 1.3, "technical": 1.0,
        "multi_party": 0.8, "duration": 0.8, "strategic": 1.2, "ip_sensitivity": 1.0,
    }

    weighted_sum = sum(dimensions[d]["score"] * weights[d] for d in dimensions)
    total_weight = sum(weights[d] for d in dimensions)
    composite = weighted_sum / total_weight

    # Map composite to tier
    if composite <= 1.5:
        tier = 1
    elif composite <= 2.5:
        tier = 2
    elif composite <= 3.3:
        tier = 3
    elif composite <= 4.2:
        tier = 4
    else:
        tier = 5

    return round(composite, 2), tier


def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("DEAL COMPLEXITY ASSESSMENT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Composite Score: {result['composite_score']:.2f} / 5.00")
    lines.append(f"Deal Tier:       {result['tier']} -- {result['tier_details']['name']}")
    lines.append(f"Value Range:     {result['tier_details']['value_range']}")
    lines.append(f"Timeline:        {result['tier_details']['timeline_weeks']} weeks")
    lines.append(f"Expected Rounds: {result['tier_details']['expected_rounds']}")
    lines.append(f"Approval Level:  {result['tier_details']['approval_level']}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("DIMENSION SCORES")
    lines.append("-" * 70)
    lines.append(f"{'Dimension':<20} {'Score':>5}  {'Detail'}")
    lines.append("-" * 70)

    for dim_name, dim_data in result["dimensions"].items():
        display_name = dim_name.replace("_", " ").title()
        bar = "#" * dim_data["score"] + "." * (5 - dim_data["score"])
        lines.append(f"  {display_name:<18} [{bar}] {dim_data['score']}/5  {dim_data['detail']}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("KEY FOCUS AREAS")
    lines.append("-" * 70)
    for i, focus in enumerate(result["tier_details"]["focus"], 1):
        lines.append(f"  {i}. {focus}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("HIGH-COMPLEXITY DIMENSIONS (score >= 4)")
    lines.append("-" * 70)
    high_dims = [
        (k, v) for k, v in result["dimensions"].items() if v["score"] >= 4
    ]
    if high_dims:
        for dim_name, dim_data in high_dims:
            lines.append(f"  * {dim_name.replace('_', ' ').title()} ({dim_data['score']}/5): {dim_data['detail']}")
    else:
        lines.append("  None -- all dimensions below high-complexity threshold")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Score deal complexity across 7 dimensions and recommend negotiation parameters."
    )
    parser.add_argument("input_file", help="Path to JSON file with deal parameters")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--deal-value", type=float, help="Override deal value in dollars")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            params = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply overrides
    if args.deal_value is not None:
        params["deal_value"] = args.deal_value

    # Validate required fields
    deal_value = params.get("deal_value", 0)
    if deal_value <= 0:
        print("Error: deal_value must be a positive number.", file=sys.stderr)
        sys.exit(1)

    # Score each dimension
    dimensions: Dict[str, Dict[str, Any]] = {}

    score, detail = score_value_dimension(deal_value)
    dimensions["value"] = {"score": score, "detail": detail}

    score, detail = score_regulatory_dimension(params.get("regulatory_requirements", []))
    dimensions["regulatory"] = {"score": score, "detail": detail}

    score, detail = score_technical_dimension(params)
    dimensions["technical"] = {"score": score, "detail": detail}

    score, detail = score_multiparty_dimension(
        params.get("parties", 2), params.get("multi_jurisdictional", False)
    )
    dimensions["multi_party"] = {"score": score, "detail": detail}

    score, detail = score_duration_dimension(params.get("duration_months", 12))
    dimensions["duration"] = {"score": score, "detail": detail}

    score, detail = score_strategic_dimension(params.get("strategic_importance", "moderate"))
    dimensions["strategic"] = {"score": score, "detail": detail}

    score, detail = score_ip_dimension(
        params.get("ip_sensitivity", "low"), params.get("custom_development", False)
    )
    dimensions["ip_sensitivity"] = {"score": score, "detail": detail}

    # Calculate composite and tier
    composite, tier = calculate_composite(dimensions)
    tier_details = DEAL_TIERS[tier]

    result = {
        "composite_score": composite,
        "tier": tier,
        "tier_details": tier_details,
        "dimensions": dimensions,
        "input_parameters": params,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
