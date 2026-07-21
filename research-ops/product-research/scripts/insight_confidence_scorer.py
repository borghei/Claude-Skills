#!/usr/bin/env python3
"""
insight_confidence_scorer.py — Score each candidate insight's confidence from
evidence volume, evidence type, and source diversity.

Reads a JSON synthesis payload of insights and their supporting evidence.
Observed behaviour outweighs reported opinion, distinct participants outweigh
repeat quotes from one person, and multiple independent channels outweigh a
single channel. Returns a 0-100 confidence score, a band, and the specific gap
that would most raise each score.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 insight_confidence_scorer.py --input evidence.json
    python3 insight_confidence_scorer.py --input evidence.json --format json
    python3 insight_confidence_scorer.py --input evidence.json --min-band moderate

Input schema:
{
  "study": "Ticket triage discovery",
  "insights": [
      {"id": "I1",
       "claim": "Agents re-triage tickets manually because the auto-assigned
                 queue ignores account tier.",
       "evidence": [
          {"participant": "P1", "source": "interview", "kind": "observed",
           "note": "Reassigned 4 of 6 tickets during the session"},
          {"participant": "P3", "source": "support_tickets", "kind": "artefact",
           "note": "17 reassignment events in one week"}
       ]}
  ]
}

kind:   observed | artefact | reported | inferred
source: any channel label (interview, support_tickets, analytics, sales_call...)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Observed behaviour is the strongest evidence a discovery study can produce.
KIND_WEIGHT = {
    "observed": 1.0,
    "artefact": 0.85,
    "reported": 0.5,
    "inferred": 0.2,
}

# Score component ceilings; they sum to 100.
VOLUME_MAX = 40
DIVERSITY_MAX = 30
PARTICIPANT_MAX = 30

# Full volume credit at this much weighted evidence.
VOLUME_SATURATION = 6.0
DIVERSITY_SATURATION = 3
PARTICIPANT_SATURATION = 5

BANDS = (("high", 75), ("moderate", 55), ("low", 35), ("speculative", 0))
BAND_ORDER = {"speculative": 0, "low": 1, "moderate": 2, "high": 3}


def band_for(score: float) -> str:
    """Return the confidence band label for a numeric score."""
    for label, floor in BANDS:
        if score >= floor:
            return label
    return "speculative"


def score_insight(insight: dict[str, Any]) -> dict[str, Any]:
    """Score one insight from its evidence volume, diversity, and participant spread."""
    insight_id = str(insight.get("id", "?"))
    evidence = insight.get("evidence") or []
    if not evidence:
        return {
            "id": insight_id, "claim": insight.get("claim", ""),
            "score": 0.0, "band": "speculative",
            "evidence_count": 0, "distinct_participants": 0,
            "distinct_sources": 0, "weighted_volume": 0.0,
            "kind_mix": {},
            "biggest_gap": "no evidence attached — this is a hypothesis, not an insight",
        }

    weighted_volume = 0.0
    kinds: Counter[str] = Counter()
    participants: set[str] = set()
    sources: set[str] = set()

    for item in evidence:
        kind = str(item.get("kind", "reported")).lower()
        if kind not in KIND_WEIGHT:
            raise ValueError(
                f"insight '{insight_id}' has evidence kind '{kind}'; "
                f"expected one of {sorted(KIND_WEIGHT)}"
            )
        weighted_volume += KIND_WEIGHT[kind]
        kinds[kind] += 1
        if item.get("participant"):
            participants.add(str(item["participant"]))
        if item.get("source"):
            sources.add(str(item["source"]))

    volume_score = VOLUME_MAX * min(weighted_volume / VOLUME_SATURATION, 1.0)
    diversity_score = DIVERSITY_MAX * min(len(sources) / DIVERSITY_SATURATION, 1.0)
    participant_score = PARTICIPANT_MAX * min(
        len(participants) / PARTICIPANT_SATURATION, 1.0)
    score = volume_score + diversity_score + participant_score

    # A claim resting entirely on what people said is capped — stated preference
    # is the weakest evidence a discovery study produces.
    if kinds["observed"] == 0 and kinds["artefact"] == 0:
        score = min(score, 50.0)
    # A single participant is an anecdote no matter how many quotes they gave.
    if len(participants) <= 1:
        score = min(score, 35.0)

    gap = _biggest_gap(len(participants), len(sources), kinds, weighted_volume)

    return {
        "id": insight_id,
        "claim": insight.get("claim", ""),
        "score": round(score, 1),
        "band": band_for(score),
        "evidence_count": len(evidence),
        "distinct_participants": len(participants),
        "distinct_sources": len(sources),
        "weighted_volume": round(weighted_volume, 2),
        "kind_mix": dict(kinds),
        "biggest_gap": gap,
    }


def _biggest_gap(participants: int, sources: int, kinds: Counter[str],
                 volume: float) -> str:
    """Name the single change that would most raise this insight's confidence."""
    if participants <= 1:
        return ("only one participant — a second independent participant raises this "
                "more than any other single addition")
    if kinds["observed"] == 0 and kinds["artefact"] == 0:
        return ("entirely self-reported — one observation or one artefact (log, ticket, "
                "recording) would lift this out of the stated-preference cap")
    if sources < 2:
        return ("single channel — corroborate from a second source type such as "
                "analytics, support tickets, or sales calls")
    if volume >= VOLUME_SATURATION * 0.6 and participants >= 4 and sources >= 3:
        return "no structural gap — this insight is adequately evidenced"
    if participants < PARTICIPANT_SATURATION:
        return (f"{participants} participants — reaching {PARTICIPANT_SATURATION} would "
                "close the remaining participant-spread gap")
    if volume < VOLUME_SATURATION:
        return "evidence volume is thin — more instances of the same pattern would help"
    return "no structural gap — this insight is adequately evidenced"


def analyse(payload: dict[str, Any], min_band: str = "moderate") -> dict[str, Any]:
    """Score every insight and partition them against the decision threshold."""
    insights = payload.get("insights") or []
    if not insights:
        raise ValueError("payload must contain a non-empty 'insights' list")
    if min_band not in BAND_ORDER:
        raise ValueError(f"min_band '{min_band}'; expected one of {sorted(BAND_ORDER)}")

    scored = [score_insight(i) for i in insights]
    threshold = BAND_ORDER[min_band]
    decision_ready = [s for s in scored if BAND_ORDER[s["band"]] >= threshold]
    hypotheses = [s for s in scored if BAND_ORDER[s["band"]] < threshold]

    return {
        "study": payload.get("study", ""),
        "min_band": min_band,
        "insight_count": len(scored),
        "decision_ready_count": len(decision_ready),
        "hypothesis_count": len(hypotheses),
        "insights": sorted(scored, key=lambda s: -s["score"]),
        "summary": (f"{len(decision_ready)} of {len(scored)} insights meet the "
                    f"'{min_band}' bar; the rest must be labelled as hypotheses "
                    "if they appear in a readout"),
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the confidence scoring as human-readable text."""
    lines = [f"Insight confidence — {report['study']}",
             f"Threshold: {report['min_band']} | "
             f"{report['decision_ready_count']}/{report['insight_count']} decision-ready",
             ""]
    for s in report["insights"]:
        lines.append(f"[{s['band'].upper():12}] {s['score']:5.1f}  {s['id']}")
        lines.append(f"  {s['claim']}")
        lines.append(f"  evidence {s['evidence_count']} | "
                     f"participants {s['distinct_participants']} | "
                     f"sources {s['distinct_sources']} | "
                     f"mix {s['kind_mix']}")
        lines.append(f"  gap: {s['biggest_gap']}")
        lines.append("")
    lines.append(report["summary"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Score insight confidence from evidence volume and diversity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON synthesis payload")
    parser.add_argument("--min-band", choices=["speculative", "low", "moderate", "high"],
                        default="moderate",
                        help="Confidence band an insight must reach to count as "
                             "decision-ready (default: moderate)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(payload, args.min_band)
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
        print(f"error: invalid synthesis payload: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
