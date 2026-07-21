#!/usr/bin/env python3
"""Find handoffs, ping-pong loops and system switches in a process definition.

Handoffs are where transactional processes lose time: each owner change adds a
queue, and each system change adds re-keying and error risk. This tool scores
every handoff, detects owners the work returns to repeatedly, and maps rework
loops that cross team boundaries.

Usage:
    python3 handoff_analyzer.py --input sample_process.json
    python3 handoff_analyzer.py --input sample_process.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Handoff density above this many owner changes per step signals fragmentation.
HANDOFF_DENSITY_ALERT = 0.5
# A handoff whose receiving step waits longer than this is a hard queue.
HANDOFF_WAIT_ALERT_MIN = 240.0
# Risk score at or above this needs a named owner and a fix date.
HIGH_RISK_SCORE = 6


def build_handoffs(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return one record per owner change, scored for delay and failure risk."""
    handoffs: List[Dict[str, Any]] = []
    for prev, curr in zip(steps, steps[1:]):
        from_owner = prev.get("owner", "unassigned")
        to_owner = curr.get("owner", "unassigned")
        if from_owner == to_owner:
            continue
        wait = float(curr.get("wait_time_min", 0))
        system_switch = prev.get("system") != curr.get("system")
        manual_transfer = not bool(curr.get("automated", False))
        rework = float(curr.get("rework_rate", 0))

        score = 0
        reasons: List[str] = []
        if wait >= 60:
            score += 3 if wait >= HANDOFF_WAIT_ALERT_MIN else 2
            reasons.append(f"{wait:.0f} min queue on receipt")
        elif wait > 0:
            score += 1
        if system_switch:
            score += 2
            reasons.append(f"system change {prev.get('system')} -> {curr.get('system')}")
        if manual_transfer:
            score += 1
            reasons.append("manual transfer")
        if rework >= 0.10:
            score += 2
            reasons.append(f"{rework:.0%} rework on the receiving step")

        handoffs.append(
            {
                "from_step": prev.get("id"),
                "to_step": curr.get("id"),
                "from_owner": from_owner,
                "to_owner": to_owner,
                "wait_min": wait,
                "system_switch": system_switch,
                "manual_transfer": manual_transfer,
                "receiving_rework_rate": rework,
                "risk_score": score,
                "risk_band": "HIGH" if score >= HIGH_RISK_SCORE else ("MEDIUM" if score >= 3 else "LOW"),
                "reasons": reasons,
            }
        )
    return handoffs


def find_ping_pong(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify owners the work leaves and later returns to."""
    visits: Dict[str, List[int]] = {}
    last_owner = None
    for i, s in enumerate(steps):
        owner = s.get("owner", "unassigned")
        if owner != last_owner:
            visits.setdefault(owner, []).append(i)
        last_owner = owner
    results = []
    for owner, indices in visits.items():
        if len(indices) > 1:
            results.append(
                {
                    "owner": owner,
                    "visit_count": len(indices),
                    "step_indices": indices,
                    "note": f"work returns to {owner} {len(indices) - 1} time(s) after leaving",
                }
            )
    return sorted(results, key=lambda r: -r["visit_count"])


def find_rework_loops(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map rework loops and flag those crossing an owner boundary."""
    id_to_index = {s.get("id"): i for i, s in enumerate(steps)}
    loops = []
    for i, s in enumerate(steps):
        rate = float(s.get("rework_rate", 0))
        target = s.get("rework_to")
        if rate <= 0 or not target:
            continue
        start = id_to_index.get(target)
        if start is None:
            raise ValueError(f"step '{s.get('id')}' has rework_to '{target}' which is not a known step id")
        if start > i:
            raise ValueError(f"step '{s.get('id')}' loops forward to '{target}'; rework must go backward")
        span = steps[start : i + 1]
        owners = sorted({x.get("owner", "unassigned") for x in span})
        loop_minutes = sum(
            float(x.get("process_time_min", 0)) + float(x.get("wait_time_min", 0)) for x in span
        )
        loops.append(
            {
                "detected_at_step": s.get("id"),
                "returns_to_step": target,
                "steps_replayed": len(span),
                "owners_involved": owners,
                "crosses_owner_boundary": len(owners) > 1,
                "rework_rate": rate,
                "loop_minutes": round(loop_minutes, 1),
                "expected_minutes_per_unit": round(rate * loop_minutes, 1),
            }
        )
    return sorted(loops, key=lambda x: -x["expected_minutes_per_unit"])


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Produce the full handoff, ping-pong and loop analysis for a process."""
    steps = data.get("steps", [])
    if not steps:
        raise ValueError("input JSON needs a non-empty 'steps' array")

    handoffs = build_handoffs(steps)
    ping_pong = find_ping_pong(steps)
    loops = find_rework_loops(steps)

    owners: Dict[str, Dict[str, float]] = {}
    for s in steps:
        o = s.get("owner", "unassigned")
        bucket = owners.setdefault(o, {"steps": 0, "touch_min": 0.0, "wait_min": 0.0})
        bucket["steps"] += 1
        bucket["touch_min"] += float(s.get("process_time_min", 0))
        bucket["wait_min"] += float(s.get("wait_time_min", 0))

    handoff_wait = sum(h["wait_min"] for h in handoffs)
    total_wait = sum(float(s.get("wait_time_min", 0)) for s in steps)
    density = len(handoffs) / len(steps)
    handoff_wait_share = round(handoff_wait / total_wait, 3) if total_wait else 0.0

    findings: List[str] = []
    if density > HANDOFF_DENSITY_ALERT:
        findings.append(
            f"{len(handoffs)} handoffs across {len(steps)} steps ({density:.2f} per step) — "
            "the process is fragmented; consolidating ownership will beat optimising any single step."
        )
    if handoff_wait_share > 0.6:
        findings.append(
            f"{handoff_wait_share:.0%} of all wait time sits at handoffs. "
            "Target the queues between teams, not the work inside them."
        )
    for h in handoffs:
        if h["risk_band"] == "HIGH":
            findings.append(
                f"High-risk handoff {h['from_owner']} -> {h['to_owner']} "
                f"({h['from_step']} -> {h['to_step']}): " + "; ".join(h["reasons"])
            )
    for p in ping_pong:
        if p["visit_count"] >= 3:
            findings.append(
                f"{p['owner']} is visited {p['visit_count']} separate times — "
                "consolidate their steps or give them end-to-end ownership of the segment."
            )
    for lp in loops:
        if lp["crosses_owner_boundary"]:
            findings.append(
                f"Cross-team rework loop at '{lp['detected_at_step']}' replaying "
                f"{lp['steps_replayed']} steps across {', '.join(lp['owners_involved'])} — "
                f"{lp['expected_minutes_per_unit']:.0f} min per unit. Move the check upstream."
            )
    switches = sum(1 for h in handoffs if h["system_switch"])
    if switches:
        findings.append(
            f"{switches} handoff(s) involve a system change — each is a re-keying and data-loss point."
        )

    return {
        "process_name": data.get("process_name", "unnamed process"),
        "step_count": len(steps),
        "handoff_count": len(handoffs),
        "handoff_density_per_step": round(density, 2),
        "handoffs": handoffs,
        "wait_at_handoffs_min": round(handoff_wait, 1),
        "total_wait_min": round(total_wait, 1),
        "handoff_wait_share": handoff_wait_share,
        "owner_load": {
            k: {
                "steps": int(v["steps"]),
                "touch_min": round(v["touch_min"], 1),
                "wait_min": round(v["wait_min"], 1),
            }
            for k, v in sorted(owners.items())
        },
        "ping_pong": ping_pong,
        "rework_loops": loops,
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the handoff analysis as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"HANDOFF ANALYSIS — {result['process_name']}")
    print("=" * 78)
    print(
        f"{result['handoff_count']} handoffs across {result['step_count']} steps "
        f"({result['handoff_density_per_step']} per step) | "
        f"{result['handoff_wait_share']:.0%} of wait time is at handoffs"
    )
    print()
    print(f"{'From -> To':<44}{'Wait':>8}{'Sys':>6}{'Score':>7}  Band")
    print("-" * 78)
    for h in result["handoffs"]:
        pair = f"{h['from_owner'][:20]} -> {h['to_owner'][:20]}"
        print(
            f"{pair:<44}{h['wait_min']:>8.0f}{'yes' if h['system_switch'] else 'no':>6}"
            f"{h['risk_score']:>7}  {h['risk_band']}"
        )
    print("-" * 78)
    print()
    print("OWNER LOAD")
    for owner, v in result["owner_load"].items():
        print(
            f"  {owner[:22]:<24}{v['steps']:>3} steps{v['touch_min']:>9.0f} min touch"
            f"{v['wait_min']:>9.0f} min wait"
        )
    if result["ping_pong"]:
        print()
        print("PING-PONG")
        for p in result["ping_pong"]:
            print(f"  {p['owner'][:22]:<24}{p['note']}")
    if result["rework_loops"]:
        print()
        print("REWORK LOOPS")
        for lp in result["rework_loops"]:
            cross = "cross-team" if lp["crosses_owner_boundary"] else "within-team"
            print(
                f"  {lp['detected_at_step']} -> {lp['returns_to_step']}  "
                f"{lp['rework_rate']:.0%} x {lp['loop_minutes']:.0f} min = "
                f"{lp['expected_minutes_per_unit']:.0f} min/unit ({cross})"
            )
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, run the handoff analysis, and print the result."""
    parser = argparse.ArgumentParser(
        description="Find handoffs, ping-pong loops and system switches in a process.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a process definition JSON file (see assets/sample_process.json)",
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
        print(f"Error: could not analyse handoffs — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
