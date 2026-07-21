#!/usr/bin/env python3
"""
method_recommender.py — Recommend a discovery research method from the question
type, decision reversibility, timeline, and participant access.

Reads a JSON research question spec and returns a primary method, a fallback
that fits a tighter constraint, the minimum viable sample, and the methods
explicitly ruled out with the reason each was rejected.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 method_recommender.py --input research_question.json
    python3 method_recommender.py --input research_question.json --format json

Input schema:
{
  "question": "How do support agents currently triage inbound tickets?",
  "question_type": "generative",
  "decision": "Whether to build an auto-triage queue",
  "reversibility": "costly",
  "timeline_days": 14,
  "participant_access": "existing_customers",
  "has_instrumentation": true,
  "traffic_per_week": 400
}

question_type:      generative | evaluative | comparative | descriptive |
                    prioritisation | desirability | diagnostic
reversibility:      sprint | quarter | costly | one_way_door
participant_access: none | panel | prospects | existing_customers | both
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALID_TYPES = ("generative", "evaluative", "comparative", "descriptive",
               "prioritisation", "desirability", "diagnostic")
VALID_REVERSIBILITY = ("sprint", "quarter", "costly", "one_way_door")
VALID_ACCESS = ("none", "panel", "prospects", "existing_customers", "both")

# Minimum weekly traffic for an experiment to resolve in a reasonable window.
EXPERIMENT_TRAFFIC_FLOOR = 300


@dataclass
class Method:
    """A candidate research method with its operating constraints."""

    name: str
    min_sample: str
    min_days: int
    needs_participants: bool
    answers: tuple[str, ...]
    note: str


METHODS: tuple[Method, ...] = (
    Method("Semi-structured interviews", "6-8 per segment", 7, True,
           ("generative", "diagnostic"),
           "Best instrument for understanding current behaviour and its cost."),
    Method("Contextual inquiry", "5-6 per segment", 10, True,
           ("generative",),
           "Observe the work in its real setting; surfaces workarounds people "
           "never think to mention."),
    Method("Moderated usability test", "5-8", 5, True,
           ("evaluative",),
           "Five participants surface the majority of severe usability defects."),
    Method("Unmoderated usability test", "12-20", 3, True,
           ("evaluative",),
           "Faster and cheaper than moderated, but you cannot probe surprises."),
    Method("A/B experiment", "traffic-powered", 14, False,
           ("comparative", "desirability"),
           "Observed behaviour at real scale — the strongest evidence available "
           "when traffic supports it."),
    Method("Instrumentation / log analysis", "full population", 2, False,
           ("descriptive", "diagnostic"),
           "Answers 'how many' and 'how often' exactly, with no sampling error."),
    Method("Survey with forced trade-offs", "100+ completes", 10, True,
           ("prioritisation", "descriptive"),
           "Forced trade-offs beat rating scales, which compress toward "
           "'everything is important'."),
    Method("Painted-door test", "traffic-powered", 7, False,
           ("desirability",),
           "Measures revealed interest rather than stated interest."),
    Method("Diary study", "8-12", 21, True,
           ("generative",),
           "Captures behaviour over time; the only way to see infrequent events."),
    Method("Support ticket / sales call analysis", "50+ artefacts", 2, False,
           ("generative", "diagnostic", "prioritisation"),
           "Evidence you already own; always run this before recruiting anyone."),
)


def _rank(method: Method, spec: dict[str, Any]) -> tuple[bool, str]:
    """Return whether a method is feasible for this spec, and why not if it is not."""
    qtype = spec["question_type"]
    if qtype not in method.answers:
        return False, f"does not answer a {qtype} question"
    if method.min_days > spec["timeline_days"]:
        return False, (f"needs about {method.min_days} days; timeline is "
                       f"{spec['timeline_days']}")
    if method.needs_participants and spec["participant_access"] == "none":
        return False, "requires participant access and none is available"
    if method.min_sample == "traffic-powered":
        traffic = int(spec.get("traffic_per_week", 0) or 0)
        if traffic < EXPERIMENT_TRAFFIC_FLOOR:
            return False, (f"needs at least {EXPERIMENT_TRAFFIC_FLOOR} weekly "
                           f"sessions; you have {traffic}")
    if method.name == "Instrumentation / log analysis" and not spec.get("has_instrumentation"):
        return False, "no instrumentation in place to query"
    return True, ""


def reversibility_guidance(reversibility: str, qtype: str) -> tuple[str, str]:
    """Return the evidence bar and any override recommendation for this decision."""
    if reversibility == "sprint":
        return ("Ship it and measure.",
                "This decision is reversible within a sprint. Formal research "
                "here is usually waste — ship behind a flag and read the "
                "behaviour. Spend the saved capacity on a one-way door.")
    if reversibility == "quarter":
        return ("One method, small sample.",
                "Reversible within a quarter. A single method at minimum sample "
                "is proportionate; do not over-invest.")
    if reversibility == "costly":
        return ("Mixed methods.",
                "Costly to reverse. Pair a qualitative method for the 'why' with "
                "a quantitative one for the size before committing.")
    return ("Triangulate across 3+ independent sources.",
            "One-way door. Do not decide on a single method regardless of how "
            "clean its result looks. Weeks of evidence are justified here.")


def recommend(spec: dict[str, Any]) -> dict[str, Any]:
    """Evaluate every method against the spec and rank the feasible ones."""
    for field, valid in (("question_type", VALID_TYPES),
                         ("reversibility", VALID_REVERSIBILITY),
                         ("participant_access", VALID_ACCESS)):
        value = spec.get(field)
        if value not in valid:
            raise ValueError(f"{field} is '{value}'; expected one of {list(valid)}")
    if int(spec.get("timeline_days", 0)) <= 0:
        raise ValueError("timeline_days must be a positive integer")

    feasible: list[Method] = []
    ruled_out: list[dict[str, str]] = []
    for method in METHODS:
        ok, reason = _rank(method, spec)
        if ok:
            feasible.append(method)
        elif spec["question_type"] in method.answers:
            # Only report exclusions of methods that could have answered the question.
            ruled_out.append({"method": method.name, "reason": reason})

    # Prefer the method that needs the fewest days — cheapest route to the answer.
    feasible.sort(key=lambda m: (m.min_days, m.name))
    bar, guidance = reversibility_guidance(spec["reversibility"],
                                           spec["question_type"])

    primary = feasible[0] if feasible else None
    second = feasible[1] if len(feasible) > 1 else None
    # For hard-to-reverse decisions the second method is a companion, not a
    # substitute — mixed methods are the evidence bar, not a nice-to-have.
    second_role = ("pair_with" if spec["reversibility"] in ("costly", "one_way_door")
                   else "fallback")

    return {
        "question": spec.get("question", ""),
        "decision": spec.get("decision", ""),
        "question_type": spec["question_type"],
        "reversibility": spec["reversibility"],
        "evidence_bar": bar,
        "guidance": guidance,
        "primary_method": None if primary is None else {
            "name": primary.name, "min_sample": primary.min_sample,
            "min_days": primary.min_days, "note": primary.note},
        "second_method_role": second_role,
        "second_method": None if second is None else {
            "name": second.name, "min_sample": second.min_sample,
            "min_days": second.min_days, "note": second.note},
        "other_feasible": [m.name for m in feasible[2:]],
        "ruled_out": ruled_out,
        "warning": (None if feasible else
                    "No method fits these constraints. Relax the timeline, "
                    "secure participant access, or reduce the question's scope."),
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the recommendation as human-readable text."""
    lines = [f"Research question: {report['question']}",
             f"Decision: {report['decision']}",
             f"Type: {report['question_type']} | Reversibility: {report['reversibility']}",
             "",
             f"Evidence bar: {report['evidence_bar']}",
             f"  {report['guidance']}", ""]
    primary = report["primary_method"]
    if primary:
        lines.append(f"PRIMARY: {primary['name']}")
        lines.append(f"  sample: {primary['min_sample']} | "
                     f"about {primary['min_days']} days")
        lines.append(f"  {primary['note']}")
    second = report["second_method"]
    if second:
        label = ("PAIR WITH" if report["second_method_role"] == "pair_with"
                 else "FALLBACK")
        lines.append("")
        lines.append(f"{label}: {second['name']}")
        lines.append(f"  sample: {second['min_sample']} | "
                     f"about {second['min_days']} days")
        lines.append(f"  {second['note']}")
    if report["other_feasible"]:
        lines.append("")
        lines.append("Also feasible: " + ", ".join(report["other_feasible"]))
    if report["ruled_out"]:
        lines.append("")
        lines.append("Ruled out:")
        for item in report["ruled_out"]:
            lines.append(f"  {item['method']} — {item['reason']}")
    if report["warning"]:
        lines.append("")
        lines.append(f"WARNING: {report['warning']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Recommend a discovery research method for a given question.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON research question spec")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = recommend(spec)
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
        print(f"error: invalid question spec: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
