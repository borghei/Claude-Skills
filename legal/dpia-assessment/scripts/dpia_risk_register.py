#!/usr/bin/env python3
"""
DPIA Risk Register

Manages a DPIA risk register in JSON format. Supports adding risks,
applying mitigations, calculating residual risk, and checking Art. 36
consultation thresholds.

Usage:
    python dpia_risk_register.py init --output dpia_risks.json
    python dpia_risk_register.py add --register dpia_risks.json --description "Unauthorized access" --rights-category "right-to-privacy" --likelihood 4 --severity 3
    python dpia_risk_register.py mitigate --register dpia_risks.json --risk-id 1 --measure "RBAC" --likelihood-reduction 2 --severity-reduction 1
    python dpia_risk_register.py view --register dpia_risks.json
    python dpia_risk_register.py summary --register dpia_risks.json --json
    python dpia_risk_register.py art36-check --register dpia_risks.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


VALID_RIGHTS_CATEGORIES: List[str] = ["right-to-privacy", "non-discrimination", "freedom-of-expression", "right-to-information", "right-to-not-be-subject-to-automated-decisions", "right-to-physical-safety"]


def get_risk_level(score: int) -> str:
    """Return risk level based on score."""
    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Medium"
    elif score <= 15:
        return "High"
    return "Very High"


def clamp(value: int, lo: int, hi: int) -> int:
    """Clamp value to range."""
    return max(lo, min(hi, value))


def load_register(filepath: str) -> Dict[str, Any]:
    """Load risk register from file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: Register file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in register: {e}", file=sys.stderr)
        sys.exit(1)


def save_register(filepath: str, register: Dict[str, Any]) -> None:
    """Save risk register to file."""
    register["last_modified"] = datetime.now().isoformat()
    with open(filepath, "w") as f:
        json.dump(register, f, indent=2)


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new empty risk register."""
    register: Dict[str, Any] = {"dpia_title": "", "processing_activity": "", "controller": "",
        "created": datetime.now().isoformat(), "last_modified": datetime.now().isoformat(), "risks": [], "next_id": 1}
    output = args.output or "dpia_risks.json"
    save_register(output, register)
    print(f"Risk register initialized: {output}")


def cmd_add(args: argparse.Namespace) -> None:
    """Add a risk to the register."""
    if args.rights_category not in VALID_RIGHTS_CATEGORIES:
        print(f"Error: Invalid rights category '{args.rights_category}'", file=sys.stderr)
        print(f"Valid: {', '.join(VALID_RIGHTS_CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    likelihood = clamp(args.likelihood, 1, 5)
    severity = clamp(args.severity, 1, 5)
    score = likelihood * severity

    register = load_register(args.register)
    risk_id = register.get("next_id", len(register["risks"]) + 1)

    level = get_risk_level(score)
    risk: Dict[str, Any] = {"id": risk_id, "description": args.description, "rights_category": args.rights_category,
        "likelihood": likelihood, "severity": severity, "score": score, "level": level, "mitigations": [],
        "residual_likelihood": likelihood, "residual_severity": severity, "residual_score": score,
        "residual_level": level, "added": datetime.now().isoformat()}

    register["risks"].append(risk)
    register["next_id"] = risk_id + 1
    save_register(args.register, register)

    if args.json:
        print(json.dumps(risk, indent=2))
    else:
        print(f"Risk #{risk_id} added: {args.description}")
        print(f"  Score: {score} ({get_risk_level(score)})")
        print(f"  Rights: {args.rights_category}")


def cmd_mitigate(args: argparse.Namespace) -> None:
    """Add a mitigation to a risk."""
    register = load_register(args.register)

    risk = None
    for r in register["risks"]:
        if r["id"] == args.risk_id:
            risk = r
            break

    if risk is None:
        print(f"Error: Risk #{args.risk_id} not found", file=sys.stderr)
        sys.exit(1)

    mitigation: Dict[str, Any] = {
        "measure": args.measure,
        "likelihood_reduction": clamp(args.likelihood_reduction, 0, 4),
        "severity_reduction": clamp(args.severity_reduction, 0, 4),
        "added": datetime.now().isoformat(),
    }

    risk["mitigations"].append(mitigation)

    # Recalculate residual risk
    total_l_reduction = sum(m["likelihood_reduction"] for m in risk["mitigations"])
    total_s_reduction = sum(m["severity_reduction"] for m in risk["mitigations"])

    risk["residual_likelihood"] = clamp(risk["likelihood"] - total_l_reduction, 1, 5)
    risk["residual_severity"] = clamp(risk["severity"] - total_s_reduction, 1, 5)
    risk["residual_score"] = risk["residual_likelihood"] * risk["residual_severity"]
    risk["residual_level"] = get_risk_level(risk["residual_score"])

    save_register(args.register, register)

    if args.json:
        print(json.dumps(risk, indent=2))
    else:
        print(f"Mitigation added to Risk #{args.risk_id}")
        print(f"  Measure: {args.measure}")
        print(f"  Original: {risk['score']} ({risk['level']})")
        print(f"  Residual: {risk['residual_score']} ({risk['residual_level']})")


def cmd_view(args: argparse.Namespace) -> None:
    """Display risk register as table."""
    register = load_register(args.register)
    risks = register.get("risks", [])

    if not risks:
        print("Risk register is empty.")
        return

    if args.json:
        print(json.dumps(register, indent=2))
        return

    print(f"DPIA Risk Register — {register.get('dpia_title', 'Untitled')}")
    print(f"Total risks: {len(risks)}\n")
    print(f"{'ID':>3} | {'Description':<35} | {'L':>1}x{'S':>1} | {'Score':>5} | {'Level':<9} | {'ResScore':>8} | {'ResLevel':<9}")
    print("-" * 95)
    for risk in sorted(risks, key=lambda r: r["residual_score"], reverse=True):
        desc = risk["description"][:33] + ".." if len(risk["description"]) > 35 else risk["description"]
        print(f"{risk['id']:>3} | {desc:<35} | {risk['likelihood']}x{risk['severity']} | {risk['score']:>5} | {risk['level']:<9} | {risk['residual_score']:>8} | {risk['residual_level']:<9}")


def cmd_summary(args: argparse.Namespace) -> None:
    """Generate risk register summary."""
    register = load_register(args.register)
    risks = register.get("risks", [])

    if not risks:
        print("Risk register is empty.")
        return

    total = len(risks)
    mitigated = sum(1 for r in risks if len(r.get("mitigations", [])) > 0)

    # Distribution (original)
    orig_dist: Dict[str, int] = {"Low": 0, "Medium": 0, "High": 0, "Very High": 0}
    for r in risks:
        orig_dist[r["level"]] += 1

    # Distribution (residual)
    res_dist: Dict[str, int] = {"Low": 0, "Medium": 0, "High": 0, "Very High": 0}
    for r in risks:
        res_dist[r["residual_level"]] += 1

    # Rights category breakdown
    rights_breakdown: Dict[str, int] = {}
    for r in risks:
        cat = r.get("rights_category", "unknown")
        rights_breakdown[cat] = rights_breakdown.get(cat, 0) + 1

    # Art. 36 check
    very_high_residual = res_dist.get("Very High", 0)
    art36_triggered = very_high_residual > 0

    pct = round(100 * mitigated / total, 1)
    summary: Dict[str, Any] = {"total_risks": total, "mitigated_count": mitigated, "mitigated_percentage": pct,
        "original_distribution": orig_dist, "residual_distribution": res_dist, "rights_category_breakdown": rights_breakdown,
        "art36_consultation_triggered": art36_triggered, "very_high_residual_count": very_high_residual, "generated": datetime.now().isoformat()}

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    print("=" * 55)
    print("DPIA RISK REGISTER SUMMARY")
    print(f"Total: {total} | Mitigated: {mitigated} ({summary['mitigated_percentage']}%)\n")
    for label, dist in [("Original", orig_dist), ("Residual", res_dist)]:
        print(f"{label} Distribution:")
        for level in ["Very High", "High", "Medium", "Low"]:
            count = dist[level]
            print(f"  {level:<10}  {count:>3}  ({round(100*count/total,1):>5.1f}%)  {'#'*count}")
        print()
    print(f"Art. 36: {'TRIGGERED — ' + str(very_high_residual) + ' Very High residual risk(s)' if art36_triggered else 'NOT TRIGGERED'}")
    print("=" * 55)


def cmd_art36_check(args: argparse.Namespace) -> None:
    """Check Art. 36 prior consultation requirement."""
    register = load_register(args.register)
    risks = register.get("risks", [])

    very_high_risks = [r for r in risks if r.get("residual_level") == "Very High"]
    high_risks = [r for r in risks if r.get("residual_level") == "High"]

    if args.json:
        result = {
            "art36_triggered": len(very_high_risks) > 0,
            "very_high_count": len(very_high_risks),
            "high_count": len(high_risks),
            "very_high_risks": very_high_risks,
            "recommendation": "",
        }
        if very_high_risks:
            result["recommendation"] = (
                "Art. 36 prior consultation with supervisory authority is MANDATORY. "
                "Controller must consult before processing begins."
            )
        elif high_risks:
            result["recommendation"] = (
                "Art. 36 not strictly required, but voluntary consultation is recommended "
                "given High residual risks."
            )
        else:
            result["recommendation"] = "Art. 36 prior consultation is not required."
        print(json.dumps(result, indent=2))
        return

    print("ART. 36 PRIOR CONSULTATION CHECK")
    if very_high_risks:
        print(f"RESULT: CONSULTATION REQUIRED — {len(very_high_risks)} Very High residual risk(s)")
        for r in very_high_risks:
            print(f"  Risk #{r['id']}: {r['description']} (score: {r['residual_score']})")
        print("Action: Consult SA before processing (Art. 36(1)); SA has 8+6 weeks to respond")
    elif high_risks:
        print(f"RESULT: NOT STRICTLY REQUIRED — {len(high_risks)} High residual risk(s); voluntary consultation recommended")
    else:
        print("RESULT: NOT REQUIRED — all residual risks at Medium or Low")


def main() -> None:
    parser = argparse.ArgumentParser(description="DPIA Risk Register")
    sub = parser.add_subparsers(dest="command", help="Command")
    p_init = sub.add_parser("init", help="Initialize new risk register")
    p_init.add_argument("--output", type=str, help="Output file path")
    p_add = sub.add_parser("add", help="Add a risk")
    p_add.add_argument("--register", required=True); p_add.add_argument("--description", required=True)
    p_add.add_argument("--rights-category", required=True); p_add.add_argument("--likelihood", type=int, required=True)
    p_add.add_argument("--severity", type=int, required=True); p_add.add_argument("--json", action="store_true")
    p_mit = sub.add_parser("mitigate", help="Add mitigation")
    p_mit.add_argument("--register", required=True); p_mit.add_argument("--risk-id", type=int, required=True)
    p_mit.add_argument("--measure", required=True); p_mit.add_argument("--likelihood-reduction", type=int, required=True)
    p_mit.add_argument("--severity-reduction", type=int, required=True); p_mit.add_argument("--json", action="store_true")
    for name in ["view", "summary", "art36-check"]:
        p = sub.add_parser(name)
        p.add_argument("--register", required=True); p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "mitigate": cmd_mitigate,
        "view": cmd_view,
        "summary": cmd_summary,
        "art36-check": cmd_art36_check,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            cmd_func(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
