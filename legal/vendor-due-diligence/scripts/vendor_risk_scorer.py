#!/usr/bin/env python3
"""
Vendor Risk Scorer

Scores a vendor across 6 risk dimensions based on questionnaire responses.
Calculates weighted composite score with optional 2x multiplier for critical
services on security and compliance dimensions.

Usage:
    python vendor_risk_scorer.py vendor_responses.json
    python vendor_risk_scorer.py vendor_responses.json --json
    python vendor_risk_scorer.py vendor_responses.json --critical

Input: JSON with vendor_name, service_description, and dimension objects
(financial, operational, compliance, security, reputational, strategic).
See SKILL.md for full input schema.
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple


# Dimension weights (standard)
STANDARD_WEIGHTS: Dict[str, float] = {
    "financial": 1.0, "operational": 1.0, "compliance": 1.0,
    "security": 1.0, "reputational": 0.8, "strategic": 0.8,
}

# Critical service weights (2x on security and compliance)
CRITICAL_WEIGHTS: Dict[str, float] = {
    "financial": 1.0, "operational": 1.0, "compliance": 2.0,
    "security": 2.0, "reputational": 0.8, "strategic": 0.8,
}

# Composite score interpretation
RISK_LEVELS: List[Tuple[float, str, str]] = [
    (1.5, "Low Risk", "Approve"),
    (2.5, "Moderate Risk", "Approve with Conditions"),
    (3.5, "High Risk", "Enhanced Due Diligence Required"),
    (5.0, "Critical Risk", "Reject or Require Remediation"),
]


def _clamp(score: int) -> int:
    """Clamp score to 1-5 range."""
    return max(1, min(5, score))


def score_financial(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score financial dimension (1=Low Risk, 5=Critical Risk)."""
    score, findings = 3, []
    revenue = data.get("annual_revenue", 0)
    if revenue > 100_000_000:
        score -= 1; findings.append("Large revenue base reduces financial risk")
    elif revenue < 5_000_000:
        score += 1; findings.append("Small revenue base increases financial risk")
    years = data.get("years_in_business", 0)
    if years >= 10:
        score -= 1; findings.append(f"{years} years in business -- established track record")
    elif years < 3:
        score += 1; findings.append(f"{years} years in business -- limited operating history")
    prof = data.get("profitability")
    if prof == "profitable":
        score -= 1; findings.append("Company is profitable")
    elif prof == "loss_making":
        score += 1; findings.append("Company is loss-making -- monitor cash runway")
    if data.get("audited_financials", False):
        findings.append("Audited financials available")
    else:
        score += 1; findings.append("No audited financials -- reduced transparency")
    findings.append("Insurance coverage in place" if data.get("insurance_coverage") else "No insurance coverage reported")
    return _clamp(score), findings


def score_operational(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score operational dimension."""
    score, findings = 3, []
    employees = data.get("employee_count", 0)
    if employees > 500:
        score -= 1; findings.append(f"{employees} employees -- robust operational capacity")
    elif employees < 20:
        score += 1; findings.append(f"{employees} employees -- limited operational capacity")
    for key, pos_msg, neg_msg, neg_score in [
        ("disaster_recovery_plan", "Disaster recovery plan in place", "No disaster recovery plan -- critical gap", 1),
        ("business_continuity_tested", "Business continuity plan tested", "Business continuity not tested", 1),
    ]:
        if data.get(key, False):
            score -= 1; findings.append(pos_msg)
        else:
            score += neg_score; findings.append(neg_msg)
    if data.get("geographic_redundancy", False):
        score -= 1; findings.append("Geographic redundancy in place")
    if data.get("key_person_dependency", False):
        score += 1; findings.append("Key person dependency identified -- concentration risk")
    if data.get("dedicated_support", False):
        findings.append("Dedicated support available")
    return _clamp(score), findings


def score_compliance(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score compliance dimension."""
    score, findings = 3, []
    certs = data.get("certifications", [])
    if len(certs) >= 3:
        score -= 2; findings.append(f"Strong certification portfolio: {', '.join(certs)}")
    elif len(certs) >= 1:
        score -= 1; findings.append(f"Certifications held: {', '.join(certs)}")
    else:
        score += 1; findings.append("No recognized certifications -- significant compliance gap")
    if data.get("compliance_team_exists", False):
        score -= 1; findings.append("Dedicated compliance team exists")
    else:
        findings.append("No dedicated compliance team")
    audit_freq = data.get("audit_frequency", "none")
    if audit_freq in ("quarterly", "semi_annual"):
        score -= 1; findings.append(f"Audit frequency: {audit_freq}")
    elif audit_freq == "annual":
        findings.append("Annual audit cycle")
    else:
        score += 1; findings.append("No regular audit cycle")
    if data.get("breach_history", False):
        score += 2; findings.append("Prior compliance breach on record -- elevated risk")
    return _clamp(score), findings


def score_security(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score security dimension."""
    score, findings = 3, []
    enc_rest, enc_transit = data.get("encryption_at_rest", False), data.get("encryption_in_transit", False)
    if enc_rest and enc_transit:
        score -= 1; findings.append("Full encryption (at rest and in transit)")
    elif not enc_rest and not enc_transit:
        score += 2; findings.append("No encryption reported -- critical security gap")
    else:
        findings.append("Partial encryption coverage")
    if data.get("mfa_enforced", False):
        score -= 1; findings.append("MFA enforced")
    else:
        score += 1; findings.append("MFA not enforced -- access control gap")
    pen_test = data.get("pen_test_frequency", "none")
    if pen_test in ("quarterly", "semi_annual"):
        score -= 1; findings.append(f"Penetration testing: {pen_test}")
    elif pen_test == "annual":
        findings.append("Annual penetration testing")
    else:
        score += 1; findings.append("No regular penetration testing")
    if data.get("incident_response_plan", False):
        findings.append("Incident response plan in place")
    else:
        score += 1; findings.append("No incident response plan")
    if data.get("soc2_type2", False):
        score -= 1; findings.append("SOC 2 Type II certified")
    if data.get("zero_trust_architecture", False):
        score -= 1; findings.append("Zero trust architecture implemented")
    return _clamp(score), findings


def score_reputational(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score reputational dimension."""
    score, findings = 2, []  # baseline low-moderate
    breaches = data.get("public_breaches", 0)
    if breaches > 2:
        score += 2; findings.append(f"{breaches} public breaches -- significant reputational concern")
    elif breaches > 0:
        score += 1; findings.append(f"{breaches} public breach(es) on record")
    else:
        findings.append("No public breaches on record")
    if data.get("litigation_history", False):
        score += 1; findings.append("Litigation history present")
    if data.get("negative_press", False):
        score += 1; findings.append("Negative press coverage identified")
    rating = data.get("glassdoor_rating", 0)
    if rating >= 4.0:
        score -= 1; findings.append(f"Glassdoor rating: {rating}/5 -- strong employee satisfaction")
    elif 0 < rating < 3.0:
        score += 1; findings.append(f"Glassdoor rating: {rating}/5 -- employee satisfaction concern")
    if data.get("client_references_available", False):
        findings.append("Client references available")
    else:
        score += 1; findings.append("No client references available")
    return _clamp(score), findings


def score_strategic(data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Score strategic dimension."""
    score, findings = 3, []
    position = data.get("market_position", "unknown")
    score += {"leader": -2, "established": -1, "growing": 0, "niche": 0, "declining": 2}.get(position, 0)
    findings.append(f"Market position: {position}")
    alignment = data.get("product_roadmap_alignment", "low")
    score += {"high": -1, "moderate": 0, "low": 1}.get(alignment, 0)
    findings.append(f"Product roadmap alignment: {alignment}")
    lock_in = data.get("lock_in_risk", "low")
    score += {"low": -1, "moderate": 0, "high": 1, "critical": 2}.get(lock_in, 0)
    findings.append(f"Lock-in risk: {lock_in}" + (" -- exit strategy critical" if lock_in in ("high", "critical") else ""))
    if data.get("exit_strategy_feasible", False):
        findings.append("Exit strategy assessed as feasible")
    else:
        score += 1; findings.append("Exit strategy not feasible -- significant strategic risk")
    return _clamp(score), findings


def calculate_composite(
    dimensions: Dict[str, Dict[str, Any]], critical: bool
) -> Tuple[float, str, str]:
    """Calculate weighted composite score and determine risk level and recommendation."""
    weights = CRITICAL_WEIGHTS if critical else STANDARD_WEIGHTS
    weighted_sum = sum(dimensions[d]["score"] * weights[d] for d in dimensions)
    total_weight = sum(weights[d] for d in dimensions)
    composite = weighted_sum / total_weight

    risk_level = "Critical Risk"
    recommendation = "Reject or Require Remediation"
    for threshold, level, rec in RISK_LEVELS:
        if composite <= threshold:
            risk_level = level
            recommendation = rec
            break

    return round(composite, 2), risk_level, recommendation


def generate_heat_map(dimensions: Dict[str, Dict[str, Any]]) -> List[str]:
    """Generate a text-based risk heat map."""
    labels = {1: "LOW", 2: "MOD-LOW", 3: "MODERATE", 4: "HIGH", 5: "CRITICAL"}
    lines: List[str] = []
    for dim, data in dimensions.items():
        score = data["score"]
        bar = "█" * score + "░" * (5 - score)
        label = labels.get(score, "???")
        lines.append(f"  {dim.title():<14} [{bar}] {score}/5 {label}")
    return lines


def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append(f"VENDOR RISK ASSESSMENT: {result['vendor_name']}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Service:          {result.get('service_description', 'N/A')}")
    lines.append(f"Critical Service: {'Yes (2x weight on Security & Compliance)' if result['critical'] else 'No (standard weighting)'}")
    lines.append(f"Composite Score:  {result['composite_score']:.2f} / 5.00")
    lines.append(f"Risk Level:       {result['risk_level']}")
    lines.append(f"Recommendation:   {result['recommendation']}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("RISK HEAT MAP")
    lines.append("-" * 70)
    lines.extend(generate_heat_map(result["dimensions"]))
    lines.append("")

    lines.append("-" * 70)
    lines.append("DIMENSION FINDINGS")
    lines.append("-" * 70)
    for dim, data in result["dimensions"].items():
        lines.append(f"\n  {dim.title()} (Score: {data['score']}/5):")
        for finding in data["findings"]:
            lines.append(f"    - {finding}")

    lines.append("")

    gaps = result.get("gaps", [])
    if gaps:
        lines.append("-" * 70)
        lines.append("GAP ANALYSIS")
        lines.append("-" * 70)
        for gap in gaps:
            lines.append(f"  [{gap['severity'].upper()}] {gap['dimension'].title()}: {gap['description']}")
        lines.append("")

    return "\n".join(lines)


def identify_gaps(dimensions: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """Identify gaps based on dimension scores."""
    gaps: List[Dict[str, str]] = []
    severity_map = {5: "blocker", 4: "major_concern", 3: "minor_gap"}

    for dim, data in dimensions.items():
        score = data["score"]
        if score >= 3:
            severity = severity_map.get(score, "minor_gap")
            for finding in data["findings"]:
                if any(w in finding.lower() for w in ["gap", "no ", "not ", "concern", "critical", "elevated"]):
                    gaps.append({"dimension": dim, "severity": severity, "description": finding})

    return gaps


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Score a vendor across 6 risk dimensions and generate recommendation."
    )
    parser.add_argument("input_file", help="Path to JSON file with vendor questionnaire responses")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--critical", action="store_true",
                        help="Apply 2x weight to security and compliance (critical services)")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Score each dimension
    scorers = {
        "financial": score_financial,
        "operational": score_operational,
        "compliance": score_compliance,
        "security": score_security,
        "reputational": score_reputational,
        "strategic": score_strategic,
    }

    dimensions: Dict[str, Dict[str, Any]] = {}
    for dim, scorer in scorers.items():
        dim_data = data.get(dim, {})
        score, findings = scorer(dim_data)
        dimensions[dim] = {"score": score, "findings": findings}

    composite, risk_level, recommendation = calculate_composite(dimensions, args.critical)
    gaps = identify_gaps(dimensions)

    result = {
        "vendor_name": data.get("vendor_name", "Unknown Vendor"),
        "service_description": data.get("service_description", "N/A"),
        "critical": args.critical,
        "composite_score": composite,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "dimensions": dimensions,
        "gaps": gaps,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
