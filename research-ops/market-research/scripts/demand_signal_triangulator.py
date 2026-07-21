#!/usr/bin/env python3
"""
demand_signal_triangulator.py — Combine heterogeneous demand signals into one
weighted index and surface the contradictions between them.

Reads a JSON set of observed demand signals, each with a direction (up, flat,
down), a strength, a source class, and an independence marker. Produces a
weighted demand index in the range -100..+100, a source-concentration read, and
an explicit list of signal pairs that disagree.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 demand_signal_triangulator.py --input demand_signals.json
    python3 demand_signal_triangulator.py --input demand_signals.json --format json
    python3 demand_signal_triangulator.py --input demand_signals.json --segment enterprise

Input schema (see assets/sample_demand_signals.json for a complete example):
{
  "market": str, "period": str,
  "signals": [{"id", "name", "segment",
               "source_class": "first_party"|"third_party"|"analyst"|"anecdotal",
               "direction": "up"|"flat"|"down",
               "strength": 0.0-1.0, "observations": int,
               "derived_from": signal id | null}]
}
derived_from names another signal when the two are not independent.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# First-party signals are weighted highest: they are observed, not reported.
SOURCE_WEIGHT = {
    "first_party": 1.0,
    "third_party": 0.7,
    "analyst": 0.5,
    "anecdotal": 0.25,
}

DIRECTION_SIGN = {"up": 1.0, "flat": 0.0, "down": -1.0}

# A signal seen once is a story; repeated observation earns full weight.
OBSERVATION_CAP = 6
CONCENTRATION_WARN = 0.60
MIN_INDEPENDENT_SIGNALS = 3


@dataclass
class Finding:
    """A caution about the signal set rather than about the market."""

    severity: str
    message: str


def _observation_factor(observations: int) -> float:
    """Scale a signal's weight by how many times it has been observed."""
    if observations <= 0:
        return 0.4
    return min(observations, OBSERVATION_CAP) / OBSERVATION_CAP


def score_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Compute the weighted contribution of a single demand signal."""
    source_class = str(signal.get("source_class", "anecdotal")).lower()
    if source_class not in SOURCE_WEIGHT:
        raise ValueError(
            f"signal '{signal.get('id', '?')}' has source_class '{source_class}'; "
            f"expected one of {sorted(SOURCE_WEIGHT)}"
        )
    direction = str(signal.get("direction", "flat")).lower()
    if direction not in DIRECTION_SIGN:
        raise ValueError(
            f"signal '{signal.get('id', '?')}' has direction '{direction}'; "
            f"expected one of {sorted(DIRECTION_SIGN)}"
        )
    strength = float(signal.get("strength", 0.5))
    if not 0.0 <= strength <= 1.0:
        raise ValueError(f"signal '{signal.get('id', '?')}' strength must be in [0, 1]")

    weight = (SOURCE_WEIGHT[source_class]
              * _observation_factor(int(signal.get("observations", 1))))
    # A derived signal is not new evidence; halve its weight.
    if signal.get("derived_from"):
        weight *= 0.5
    contribution = weight * strength * DIRECTION_SIGN[direction]

    return {
        "id": str(signal.get("id", "?")),
        "name": signal.get("name", ""),
        "source_class": source_class,
        "direction": direction,
        "strength": strength,
        "weight": round(weight, 4),
        "contribution": round(contribution, 4),
        "independent": not bool(signal.get("derived_from")),
        "segment": str(signal.get("segment", "all")),
    }


def find_contradictions(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pair up signals pointing in opposite directions with real weight behind them."""
    conflicts: list[dict[str, Any]] = []
    ups = [s for s in scored if s["direction"] == "up" and s["contribution"] >= 0.2]
    downs = [s for s in scored if s["direction"] == "down" and s["contribution"] <= -0.2]
    for up in ups:
        for down in downs:
            conflicts.append({
                "signal_a": up["id"],
                "signal_b": down["id"],
                "note": (f"'{up['name']}' points up while '{down['name']}' points down"
                         + (" within the same segment"
                            if up["segment"] == down["segment"]
                            else f" ({up['segment']} vs {down['segment']})")),
                "same_segment": up["segment"] == down["segment"],
            })
    return conflicts


def check_set(scored: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> list[Finding]:
    """Flag structural weaknesses in the evidence base itself."""
    findings: list[Finding] = []
    independent = [s for s in scored if s["independent"]]
    if len(independent) < MIN_INDEPENDENT_SIGNALS:
        findings.append(Finding("fail",
                                f"only {len(independent)} independent signals — you need at "
                                f"least {MIN_INDEPENDENT_SIGNALS} before calling this "
                                "triangulation"))

    total_weight = sum(s["weight"] for s in scored) or 1.0
    by_class = Counter()
    for s in scored:
        by_class[s["source_class"]] += s["weight"]
    top_class, top_weight = by_class.most_common(1)[0]
    if top_weight / total_weight >= CONCENTRATION_WARN:
        findings.append(Finding("warn",
                                f"{top_weight / total_weight:.0%} of the weight comes from "
                                f"'{top_class}' sources — the read is one source class wide"))

    same_segment_conflicts = [c for c in conflicts if c["same_segment"]]
    if same_segment_conflicts:
        findings.append(Finding("warn",
                                f"{len(same_segment_conflicts)} contradiction(s) inside a single "
                                "segment — investigate before averaging; this usually means a "
                                "segmentation boundary is missing"))
    if all(s["direction"] == "flat" for s in scored):
        findings.append(Finding("warn",
                                "every signal is flat — either the market is genuinely static "
                                "or the measures are too coarse to move"))
    return findings


def analyse(payload: dict[str, Any], segment: str | None = None) -> dict[str, Any]:
    """Score, index, and stress-test the full signal set."""
    signals = payload.get("signals") or []
    if not signals:
        raise ValueError("payload must contain a non-empty 'signals' list")

    scored = [score_signal(s) for s in signals]
    if segment:
        scored = [s for s in scored if s["segment"] in (segment, "all")]
        if not scored:
            raise ValueError(f"no signals match segment '{segment}'")

    total_weight = sum(s["weight"] for s in scored)
    index = 0.0
    if total_weight > 0:
        index = 100.0 * sum(s["contribution"] for s in scored) / total_weight

    conflicts = find_contradictions(scored)
    findings = check_set(scored, conflicts)

    if index >= 40:
        verdict = "expanding — demand evidence supports investment"
        confidence = "act on it"
    elif index >= 15:
        verdict = "mildly positive — directional only"
        confidence = "size before committing"
    elif index > -15:
        verdict = "flat — no directional signal"
        confidence = "do not build a case on this"
    else:
        verdict = "contracting — evidence points down"
        confidence = "re-examine the thesis"

    counts = {"fail": 0, "warn": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    return {
        "market": payload.get("market", ""),
        "period": payload.get("period", ""),
        "segment_filter": segment or "all",
        "demand_index": round(index, 1),
        "verdict": verdict,
        "recommended_posture": confidence,
        "signal_count": len(scored),
        "independent_signal_count": sum(1 for s in scored if s["independent"]),
        "signals": scored,
        "contradictions": conflicts,
        "severity_counts": counts,
        "findings": [{"severity": f.severity, "message": f.message} for f in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the triangulation as human-readable text."""
    lines = [f"Demand triangulation — {report['market']} ({report['period']})",
             f"Segment filter: {report['segment_filter']}", "",
             f"Demand index: {report['demand_index']:+.1f} / 100 — {report['verdict']}",
             f"Posture: {report['recommended_posture']}",
             f"Signals: {report['signal_count']} "
             f"({report['independent_signal_count']} independent)", "",
             "Signal contributions:",
             f"  {'ID':6} {'DIR':5} {'SRC':13} {'WT':>6} {'CONTRIB':>8}  NAME",
             ]
    for s in sorted(report["signals"], key=lambda x: -abs(x["contribution"])):
        lines.append(f"  {s['id']:6} {s['direction']:5} {s['source_class']:13} "
                     f"{s['weight']:6.2f} {s['contribution']:+8.2f}  {s['name']}")
    lines.append("")
    if report["contradictions"]:
        lines.append("Contradictions:")
        for c in report["contradictions"]:
            lines.append(f"  {c['signal_a']} vs {c['signal_b']}: {c['note']}")
    else:
        lines.append("Contradictions: none")
    lines.append("")
    counts = report["severity_counts"]
    lines.append(f"Findings: {counts.get('fail', 0)} fail, {counts.get('warn', 0)} warn")
    for f in report["findings"]:
        lines.append(f"  [{f['severity'].upper():4}] {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Triangulate demand signals into a weighted index.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON demand signal set")
    parser.add_argument("--segment",
                        help="Restrict the index to one segment (plus signals marked 'all')")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any finding has severity 'fail'")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(payload, args.segment)
        out = json.dumps(report, indent=2) if args.format == "json" else render_text(report)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid signal set: {exc}", file=sys.stderr)
        return 1

    if args.strict and report["severity_counts"].get("fail", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
