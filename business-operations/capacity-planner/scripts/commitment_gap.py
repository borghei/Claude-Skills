#!/usr/bin/env python3
"""Compare committed roadmap demand against effective capacity and find the cut line.

Inflates estimates by confidence band, reserves a buffer for unplanned work,
fills capacity in priority order, and reports what fits, what does not, and how
much over-commitment exists per discipline.

Usage:
    python3 commitment_gap.py --input sample_commitments.json
    python3 commitment_gap.py --input sample_commitments.json --buffer-pct 25 --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Multipliers applied to raw estimates. Derived from the systematic optimism of
# bottom-up estimation: the less the team knows, the further the estimate is off.
CONFIDENCE_INFLATION: Dict[str, float] = {
    "high": 1.15,
    "medium": 1.40,
    "low": 1.90,
    "unknown": 1.90,
}

# Share of effective capacity held back for interrupts, incidents and support.
DEFAULT_BUFFER_PCT = 20.0

# Over-commitment above this share of available capacity is a red plan.
RED_OVERCOMMIT_RATIO = 1.10
AMBER_OVERCOMMIT_RATIO = 1.00


def inflate(item: Dict[str, Any]) -> float:
    """Return the risk-adjusted hour estimate for one commitment."""
    raw = float(item.get("estimate_hours", 0))
    if raw < 0:
        raise ValueError(f"commitment '{item.get('name')}' has a negative estimate")
    confidence = str(item.get("confidence", "unknown")).lower()
    return raw * CONFIDENCE_INFLATION.get(confidence, CONFIDENCE_INFLATION["unknown"])


def analyse(data: Dict[str, Any], buffer_pct: float) -> Dict[str, Any]:
    """Fill capacity in priority order and report the gap per discipline."""
    capacity = data.get("capacity", {})
    commitments = data.get("commitments", [])
    if not capacity:
        raise ValueError("input JSON needs a 'capacity' object of {discipline: effective_hours}")
    if not commitments:
        raise ValueError("input JSON needs a non-empty 'commitments' array")

    available = {
        d: float(h) * (1 - buffer_pct / 100.0) for d, h in capacity.items()
    }
    remaining = dict(available)

    ordered = sorted(
        commitments,
        key=lambda c: (int(c.get("priority", 999)), -inflate(c)),
    )

    scheduled: List[Dict[str, Any]] = []
    for item in ordered:
        discipline = item.get("discipline", "engineering")
        adjusted = inflate(item)
        pool = remaining.get(discipline)
        if pool is None:
            verdict = "no-capacity-pool"
            fits = False
        elif adjusted <= pool:
            remaining[discipline] = pool - adjusted
            verdict = "fits"
            fits = True
        else:
            verdict = "above-cut-line"
            fits = False
        scheduled.append(
            {
                "name": item.get("name", "unnamed"),
                "discipline": discipline,
                "priority": int(item.get("priority", 999)),
                "committed": bool(item.get("committed", False)),
                "raw_hours": round(float(item.get("estimate_hours", 0)), 1),
                "confidence": str(item.get("confidence", "unknown")).lower(),
                "adjusted_hours": round(adjusted, 1),
                "fits": fits,
                "verdict": verdict,
            }
        )

    by_discipline: Dict[str, Dict[str, Any]] = {}
    for discipline, gross in capacity.items():
        demand = sum(
            s["adjusted_hours"] for s in scheduled if s["discipline"] == discipline
        )
        avail = available[discipline]
        ratio = demand / avail if avail else 0.0
        if ratio >= RED_OVERCOMMIT_RATIO:
            status = "RED"
        elif ratio >= AMBER_OVERCOMMIT_RATIO:
            status = "AMBER"
        else:
            status = "GREEN"
        by_discipline[discipline] = {
            "effective_hours": round(float(gross), 1),
            "available_after_buffer": round(avail, 1),
            "adjusted_demand": round(demand, 1),
            "gap_hours": round(avail - demand, 1),
            "load_ratio": round(ratio, 3),
            "status": status,
        }

    orphans = sorted({
        s["discipline"] for s in scheduled if s["discipline"] not in capacity
    })
    broken_promises = [
        s["name"] for s in scheduled if s["committed"] and not s["fits"]
    ]

    findings: List[str] = []
    for discipline, b in sorted(by_discipline.items()):
        if b["status"] == "RED":
            findings.append(
                f"{discipline}: {b['load_ratio']:.0%} loaded — cut "
                f"{abs(b['gap_hours']):.0f}h or the quarter slips."
            )
        elif b["status"] == "AMBER":
            findings.append(
                f"{discipline}: {b['load_ratio']:.0%} loaded — zero slack; any incident costs a commitment."
            )
    if broken_promises:
        findings.append(
            "Already-committed work above the cut line (renegotiate now, not in week 10): "
            + ", ".join(broken_promises)
        )
    if orphans:
        findings.append(
            "Demand with no capacity pool declared: " + ", ".join(orphans)
        )

    return {
        "quarter": data.get("quarter", "unspecified"),
        "buffer_pct": buffer_pct,
        "by_discipline": by_discipline,
        "commitments": scheduled,
        "summary": {
            "total_adjusted_demand": round(sum(s["adjusted_hours"] for s in scheduled), 1),
            "total_available": round(sum(available.values()), 1),
            "items_fitting": sum(1 for s in scheduled if s["fits"]),
            "items_above_cut_line": sum(1 for s in scheduled if not s["fits"]),
            "committed_at_risk": len(broken_promises),
        },
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the gap analysis as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"CAPACITY vs COMMITMENT — {result['quarter']}")
    print("=" * 74)
    print(f"Unplanned-work buffer held back: {result['buffer_pct']:.0f}%")
    print()
    print(f"{'Discipline':<16}{'Available':>11}{'Demand':>11}{'Gap':>10}{'Load':>8}  Status")
    print("-" * 74)
    for name, b in sorted(result["by_discipline"].items()):
        print(
            f"{name[:15]:<16}{b['available_after_buffer']:>11.0f}{b['adjusted_demand']:>11.0f}"
            f"{b['gap_hours']:>10.0f}{b['load_ratio']:>8.0%}  {b['status']}"
        )
    print("-" * 74)
    print()
    print("PRIORITY ORDER (cut line marked)")
    cut_drawn = False
    for item in result["commitments"]:
        if not item["fits"] and not cut_drawn:
            print("  " + "- " * 30 + " CUT LINE")
            cut_drawn = True
        flag = "*" if item["committed"] else " "
        print(
            f"  {item['priority']:>3}{flag} {item['name'][:34]:<35}"
            f"{item['discipline'][:12]:<13}{item['raw_hours']:>7.0f}h "
            f"-> {item['adjusted_hours']:>7.0f}h ({item['confidence']})"
        )
    print("\n  * = externally committed")
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, run the gap analysis, and print the result."""
    parser = argparse.ArgumentParser(
        description="Compare roadmap commitments against effective capacity and find the cut line.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a commitments JSON file (see assets/sample_commitments.json)",
    )
    parser.add_argument(
        "--buffer-pct",
        type=float,
        default=DEFAULT_BUFFER_PCT,
        help="Percent of effective capacity reserved for unplanned work",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    if not 0 <= args.buffer_pct < 100:
        print("Error: --buffer-pct must be between 0 and 99", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        output(analyse(data, args.buffer_pct), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not analyse commitments — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
