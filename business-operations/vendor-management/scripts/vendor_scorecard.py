#!/usr/bin/env python3
"""Score vendor candidates against weighted criteria with must-have gating.

Disqualifies candidates failing any must-have, computes weighted scores,
normalises cost into a value ratio, and runs a weight-sensitivity check so a
narrow win is not mistaken for a clear one.

Usage:
    python3 vendor_scorecard.py --input sample_vendor_candidates.json
    python3 vendor_scorecard.py --input sample_vendor_candidates.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Score gap below this share of the leader's score is inside the noise floor of
# subjective scoring; treat the result as a tie and decide on other grounds.
TIE_THRESHOLD = 0.05
# Weight perturbation applied in the sensitivity check.
SENSITIVITY_SWING = 0.5


def validate(data: Dict[str, Any]) -> None:
    """Raise ValueError if criteria or vendor definitions are malformed."""
    criteria = data.get("criteria", [])
    vendors = data.get("vendors", [])
    if not criteria:
        raise ValueError("input JSON needs a non-empty 'criteria' array")
    if not vendors:
        raise ValueError("input JSON needs a non-empty 'vendors' array")

    total_weight = sum(float(c.get("weight", 0)) for c in criteria)
    if total_weight <= 0:
        raise ValueError("criteria weights must sum to more than zero")

    names = [c.get("name") for c in criteria]
    if len(set(names)) != len(names):
        raise ValueError("criterion names must be unique")

    for v in vendors:
        scores = v.get("scores", {})
        missing = [n for n in names if n not in scores]
        if missing:
            raise ValueError(
                f"vendor '{v.get('name')}' is missing scores for: {', '.join(missing)}"
            )
        for n in names:
            s = float(scores[n])
            if not 0 <= s <= 10:
                raise ValueError(
                    f"vendor '{v.get('name')}' scored {s} on '{n}'; scores must be 0-10"
                )


def weighted_score(vendor: Dict[str, Any], criteria: List[Dict[str, Any]]) -> float:
    """Return a vendor's weighted score normalised to a 0-100 scale."""
    total_weight = sum(float(c.get("weight", 0)) for c in criteria)
    raw = sum(
        float(vendor["scores"][c["name"]]) * float(c.get("weight", 0)) for c in criteria
    )
    return raw / total_weight * 10.0


def disqualifications(vendor: Dict[str, Any], must_haves: List[str]) -> List[str]:
    """Return the must-have requirements this vendor fails."""
    met = vendor.get("meets_must_haves", {})
    return [m for m in must_haves if not met.get(m, False)]


def sensitivity_check(
    vendors: List[Dict[str, Any]], criteria: List[Dict[str, Any]], leader: str
) -> List[Dict[str, Any]]:
    """Re-score with each criterion's weight swung up and down; report leader flips."""
    flips: List[Dict[str, Any]] = []
    for target in criteria:
        for direction, factor in (("up", 1 + SENSITIVITY_SWING), ("down", 1 - SENSITIVITY_SWING)):
            adjusted = [
                {**c, "weight": float(c.get("weight", 0)) * (factor if c is target else 1.0)}
                for c in criteria
            ]
            ranked = sorted(
                vendors, key=lambda v: weighted_score(v, adjusted), reverse=True
            )
            if ranked and ranked[0]["name"] != leader:
                flips.append(
                    {
                        "criterion": target["name"],
                        "direction": direction,
                        "new_leader": ranked[0]["name"],
                    }
                )
    return flips


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Score all candidates, gate on must-haves, and test the result's stability."""
    validate(data)
    criteria = data.get("criteria", [])
    must_haves = data.get("must_haves", [])
    total_weight = sum(float(c.get("weight", 0)) for c in criteria)

    scored: List[Dict[str, Any]] = []
    for v in data["vendors"]:
        failures = disqualifications(v, must_haves)
        score = weighted_score(v, criteria)
        cost = float(v.get("annual_cost", 0))
        scored.append(
            {
                "name": v.get("name", "unnamed"),
                "weighted_score": round(score, 2),
                "annual_cost": cost,
                "value_ratio": round(score / (cost / 100000), 2) if cost else None,
                "disqualified": bool(failures),
                "failed_must_haves": failures,
                "scores": {c["name"]: float(v["scores"][c["name"]]) for c in criteria},
                "notes": v.get("notes", ""),
            }
        )

    qualified = [s for s in scored if not s["disqualified"]]
    qualified.sort(key=lambda s: -s["weighted_score"])
    scored.sort(key=lambda s: (s["disqualified"], -s["weighted_score"]))

    findings: List[str] = []
    recommendation: Optional[Dict[str, Any]] = None
    flips: List[Dict[str, Any]] = []

    if not qualified:
        findings.append(
            "Every candidate fails at least one must-have. Either the must-have list is "
            "aspirational, or this market cannot serve the requirement — revisit before re-running."
        )
    else:
        leader = qualified[0]
        raw_vendors = [v for v in data["vendors"] if v.get("name") in {q["name"] for q in qualified}]
        flips = sensitivity_check(raw_vendors, criteria, leader["name"])

        if len(qualified) > 1:
            runner_up = qualified[1]
            gap = (leader["weighted_score"] - runner_up["weighted_score"]) / leader["weighted_score"]
            if gap < TIE_THRESHOLD:
                margin = (
                    "score identically"
                    if gap == 0
                    else f"are separated by only {gap:.1%}"
                )
                findings.append(
                    f"{leader['name']} and {runner_up['name']} {margin} — inside the noise floor "
                    "of subjective scoring. Treat as a tie and decide on commercial terms, exit "
                    "cost, or reference checks."
                )
            if runner_up["annual_cost"] and leader["annual_cost"] > runner_up["annual_cost"] * 1.3:
                findings.append(
                    f"{leader['name']} costs {leader['annual_cost'] / runner_up['annual_cost']:.1f}x "
                    f"{runner_up['name']} for a {gap:.1%} score advantage. Confirm the delta is "
                    "worth the premium before committing."
                )
        if flips:
            criteria_flipped = sorted({f["criterion"] for f in flips})
            findings.append(
                f"Result is weight-sensitive: the leader changes if weighting on "
                f"{', '.join(criteria_flipped)} moves by 50%. Re-confirm those weights with the "
                "decision owner before proceeding."
            )
        else:
            findings.append(
                "Result is stable under a 50% swing on every criterion weight."
            )

        recommendation = {
            "vendor": leader["name"],
            "weighted_score": leader["weighted_score"],
            "annual_cost": leader["annual_cost"],
            "stable": not flips,
        }

    dq = [s for s in scored if s["disqualified"]]
    for d in dq:
        findings.append(
            f"{d['name']} disqualified on: {', '.join(d['failed_must_haves'])}."
        )

    return {
        "decision": data.get("decision", "vendor selection"),
        "criteria": [
            {"name": c["name"], "weight": float(c.get("weight", 0)),
             "weight_share": round(float(c.get("weight", 0)) / total_weight, 3)}
            for c in criteria
        ],
        "must_haves": must_haves,
        "vendors": scored,
        "qualified_count": len(qualified),
        "sensitivity_flips": flips,
        "recommendation": recommendation,
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the scorecard as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"VENDOR SCORECARD — {result['decision']}")
    print("=" * 76)
    print("Criteria: " + ", ".join(f"{c['name']} ({c['weight_share']:.0%})" for c in result["criteria"]))
    if result["must_haves"]:
        print("Must-haves: " + ", ".join(result["must_haves"]))
    print()
    print(f"{'Vendor':<26}{'Score':>8}{'Annual cost':>14}{'Value':>9}  Status")
    print("-" * 76)
    for v in result["vendors"]:
        status = "DISQUALIFIED" if v["disqualified"] else "qualified"
        value = f"{v['value_ratio']:.1f}" if v["value_ratio"] is not None else "n/a"
        print(
            f"{v['name'][:25]:<26}{v['weighted_score']:>8.1f}{v['annual_cost']:>14,.0f}"
            f"{value:>9}  {status}"
        )
    print("-" * 76)
    print("Score is 0-100 weighted. Value = score per 100k of annual cost.")

    if result["recommendation"]:
        r = result["recommendation"]
        print()
        print("RECOMMENDATION")
        print(
            f"  {r['vendor']} — score {r['weighted_score']:.1f} at {r['annual_cost']:,.0f}/year "
            f"({'stable' if r['stable'] else 'weight-sensitive'} result)"
        )
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, score the candidates, and print the result."""
    parser = argparse.ArgumentParser(
        description="Score vendor candidates against weighted criteria with must-have gating.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a candidates JSON file (see assets/sample_vendor_candidates.json)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        output(analyse(data), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not score vendors — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
