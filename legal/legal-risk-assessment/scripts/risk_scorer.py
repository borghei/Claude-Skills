#!/usr/bin/env python3
"""
Legal Risk Scorer

Calculates legal risk scores using a 5x5 Severity x Likelihood matrix.
Assigns GREEN/YELLOW/ORANGE/RED levels with recommended actions.
Supports single-risk and batch mode from JSON input.

Usage:
    python risk_scorer.py --severity 4 --likelihood 3 --category "Contract" --description "SLA breach"
    python risk_scorer.py --input risks.json --json
    python risk_scorer.py --severity 5 --likelihood 4 --category "Litigation" --description "Patent claim" --json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SEVERITY_LABELS: Dict[int, str] = {1: "Negligible", 2: "Minor", 3: "Moderate", 4: "Major", 5: "Critical"}
SEVERITY_EXPOSURE: Dict[int, str] = {1: "<0.1% revenue", 2: "0.1-1% revenue", 3: "1-5% revenue", 4: "5-15% revenue", 5: ">15% revenue"}
LIKELIHOOD_LABELS: Dict[int, str] = {1: "Remote", 2: "Unlikely", 3: "Possible", 4: "Likely", 5: "Almost Certain"}
LIKELIHOOD_PROBABILITY: Dict[int, str] = {1: "<5%", 2: "5-20%", 3: "20-50%", 4: "50-80%", 5: ">80%"}

VALID_CATEGORIES: List[str] = [
    "Contract", "Regulatory", "Litigation", "IP",
    "Data Privacy", "Employment", "Corporate",
]


def get_risk_level(score: int) -> str:
    """Return risk level color based on score."""
    if score <= 4:
        return "GREEN"
    elif score <= 9:
        return "YELLOW"
    elif score <= 15:
        return "ORANGE"
    else:
        return "RED"


def get_recommended_action(level: str) -> str:
    """Return recommended action for a risk level."""
    actions: Dict[str, str] = {
        "GREEN": "Accept — document risk, monitor quarterly, no immediate action required",
        "YELLOW": "Monitor — assign risk owner, implement controls, review monthly",
        "ORANGE": "Mitigate — escalate to senior counsel, develop contingency plan, consider outside counsel",
        "RED": "Escalate — immediate escalation, assemble response team, engage outside counsel, board reporting",
    }
    return actions.get(level, "Unknown")


def validate_risk(risk: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a risk entry has required fields and valid values."""
    required = ["severity", "likelihood", "category", "description"]
    for field in required:
        if field not in risk:
            return False, f"Missing required field: {field}"

    sev = risk["severity"]
    lik = risk["likelihood"]

    if not isinstance(sev, int) or sev < 1 or sev > 5:
        return False, f"Severity must be integer 1-5, got: {sev}"
    if not isinstance(lik, int) or lik < 1 or lik > 5:
        return False, f"Likelihood must be integer 1-5, got: {lik}"

    cat = risk["category"]
    if cat not in VALID_CATEGORIES:
        return False, f"Invalid category '{cat}'. Valid: {', '.join(VALID_CATEGORIES)}"

    if not risk["description"].strip():
        return False, "Description cannot be empty"

    return True, ""


def score_risk(risk: Dict[str, Any]) -> Dict[str, Any]:
    """Score a single risk and return enriched result."""
    sev: int = risk["severity"]
    lik: int = risk["likelihood"]
    score: int = sev * lik
    level: str = get_risk_level(score)

    return {
        "description": risk["description"],
        "category": risk["category"],
        "severity": sev,
        "severity_label": SEVERITY_LABELS[sev],
        "severity_exposure": SEVERITY_EXPOSURE[sev],
        "likelihood": lik,
        "likelihood_label": LIKELIHOOD_LABELS[lik],
        "likelihood_probability": LIKELIHOOD_PROBABILITY[lik],
        "score": score,
        "level": level,
        "recommended_action": get_recommended_action(level),
    }


def generate_summary(scored_risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for a list of scored risks."""
    total: int = len(scored_risks)
    if total == 0:
        return {"total": 0, "distribution": {}, "average_score": 0.0, "max_score": 0}

    distribution: Dict[str, int] = {"GREEN": 0, "YELLOW": 0, "ORANGE": 0, "RED": 0}
    scores: List[int] = []

    for risk in scored_risks:
        distribution[risk["level"]] += 1
        scores.append(risk["score"])

    avg_score: float = sum(scores) / total
    max_score: int = max(scores)
    max_risk = next(r for r in scored_risks if r["score"] == max_score)

    return {
        "total": total,
        "distribution": distribution,
        "average_score": round(avg_score, 1),
        "max_score": max_score,
        "highest_risk": max_risk["description"],
        "red_count": distribution["RED"],
        "orange_count": distribution["ORANGE"],
        "requires_escalation": distribution["RED"] > 0,
    }


def format_human_single(result: Dict[str, Any]) -> str:
    """Format a single risk result for human-readable output."""
    lines: List[str] = [
        "=" * 60,
        "LEGAL RISK ASSESSMENT",
        "=" * 60,
        "",
        f"Description:    {result['description']}",
        f"Category:       {result['category']}",
        "",
        f"Severity:       {result['severity']} — {result['severity_label']} ({result['severity_exposure']})",
        f"Likelihood:     {result['likelihood']} — {result['likelihood_label']} ({result['likelihood_probability']})",
        "",
        f"Risk Score:     {result['score']} / 25",
        f"Risk Level:     {result['level']}",
        "",
        f"Action:         {result['recommended_action']}",
        "",
        "=" * 60,
    ]
    return "\n".join(lines)


def format_human_batch(scored_risks: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    """Format batch results for human-readable output."""
    lines: List[str] = [
        "=" * 70,
        "LEGAL RISK REGISTER — SCORED RESULTS",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 70,
        "",
    ]

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total Risks:      {summary['total']}")
    lines.append(f"  Average Score:    {summary['average_score']}")
    lines.append(f"  Highest Score:    {summary['max_score']}")
    lines.append("")
    lines.append("  Distribution:")
    for level in ["RED", "ORANGE", "YELLOW", "GREEN"]:
        count = summary["distribution"][level]
        bar = "#" * count
        lines.append(f"    {level:8s}  {count:3d}  {bar}")
    lines.append("")

    if summary["requires_escalation"]:
        lines.append("  *** ESCALATION REQUIRED: RED-level risks detected ***")
        lines.append("")

    # Individual risks sorted by score descending
    lines.append("RISKS (sorted by score, highest first)")
    lines.append("-" * 70)

    for i, risk in enumerate(scored_risks, 1):
        lines.append(f"\n  [{i}] {risk['description']}")
        lines.append(f"      Category:    {risk['category']}")
        lines.append(f"      Severity:    {risk['severity']} ({risk['severity_label']})")
        lines.append(f"      Likelihood:  {risk['likelihood']} ({risk['likelihood_label']})")
        lines.append(f"      Score:       {risk['score']}  Level: {risk['level']}")
        lines.append(f"      Action:      {risk['recommended_action']}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def load_risks_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Load risks from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict) and "risks" in data:
        return data["risks"]
    elif isinstance(data, list):
        return data
    else:
        print("Error: JSON must contain a 'risks' array or be a top-level array", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Legal Risk Scorer — 5x5 Severity x Likelihood matrix"
    )
    parser.add_argument("--severity", type=int, choices=range(1, 6), help="Severity rating (1-5)")
    parser.add_argument("--likelihood", type=int, choices=range(1, 6), help="Likelihood rating (1-5)")
    parser.add_argument("--category", type=str, help=f"Risk category: {', '.join(VALID_CATEGORIES)}")
    parser.add_argument("--description", type=str, help="Risk description")
    parser.add_argument("--input", type=str, help="JSON file with multiple risks (batch mode)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Determine mode
    if args.input:
        # Batch mode
        risks = load_risks_from_file(args.input)
        scored: List[Dict[str, Any]] = []

        for idx, risk in enumerate(risks):
            valid, msg = validate_risk(risk)
            if not valid:
                print(f"Error in risk #{idx + 1}: {msg}", file=sys.stderr)
                sys.exit(1)
            scored.append(score_risk(risk))

        # Sort by score descending
        scored.sort(key=lambda r: r["score"], reverse=True)
        summary = generate_summary(scored)

        if args.json:
            output = {"risks": scored, "summary": summary, "generated": datetime.now().isoformat()}
            print(json.dumps(output, indent=2))
        else:
            print(format_human_batch(scored, summary))

    elif args.severity and args.likelihood and args.category and args.description:
        # Single risk mode
        risk = {
            "severity": args.severity,
            "likelihood": args.likelihood,
            "category": args.category,
            "description": args.description,
        }
        valid, msg = validate_risk(risk)
        if not valid:
            print(f"Error: {msg}", file=sys.stderr)
            sys.exit(1)

        result = score_risk(risk)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_human_single(result))
    else:
        parser.error(
            "Provide either --input for batch mode, or all of "
            "--severity, --likelihood, --category, --description for single risk mode"
        )


if __name__ == "__main__":
    main()
