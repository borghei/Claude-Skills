#!/usr/bin/env python3
"""tool_choice_advisor.py — Recommend computer-use vs a structured API/MCP tool.

Given facts about a target — whether a real API/MCP tool exists, how stable the
GUI is, the expected volume, and whether the task is reversible — emit a
"use computer-use" vs "use API/MCP" recommendation with a scored rationale.

Standard library only. Supports --json and human-readable output.

Guiding principle: prefer a real programmatic interface (API / SDK / CLI / MCP)
whenever one exists. Computer-use is for GUIs with no programmatic surface,
one-off tasks, or bridging gaps a real interface does not cover.
"""

import argparse
import json
import sys

TRI = ["yes", "no", "unknown"]
LEVELS = ["low", "medium", "high"]


def normalize(value, allowed, name):
    v = (value or "unknown").strip().lower()
    if v not in allowed:
        sys.stderr.write(
            "error: --%s must be one of %s (got %r)\n" % (name, "/".join(allowed), value)
        )
        sys.exit(2)
    return v


def evaluate(api_exists, gui_stability, volume, reversible):
    """Return (recommendation, confidence, score, reasons).

    score > 0 favors API/MCP; score < 0 favors computer-use.
    """
    reasons = []
    score = 0

    # The dominant factor: does a real interface exist?
    if api_exists == "yes":
        score += 5
        reasons.append(
            "A real API/MCP tool exists — it is more reliable, cheaper, and "
            "verifiable than driving pixels. This is the dominant factor."
        )
    elif api_exists == "no":
        score -= 4
        reasons.append(
            "No API/MCP/SDK/CLI surface — the target is GUI-only, the primary "
            "justification for computer-use."
        )
    else:
        reasons.append(
            "API/MCP availability is UNKNOWN — investigate first; a missed API "
            "is the most common reason a computer-use agent should not exist."
        )

    # GUI stability: flaky UIs make computer-use brittle.
    if gui_stability == "low":
        score += 2
        reasons.append(
            "GUI is unstable (low) — layouts shift and break grounded actions, "
            "raising computer-use flakiness."
        )
    elif gui_stability == "high":
        score -= 1
        reasons.append(
            "GUI is stable (high) — grounded screenshot actions are more likely "
            "to stay valid run-to-run."
        )

    # Volume: high volume amplifies per-action flakiness and cost.
    if volume == "high":
        score += 2
        reasons.append(
            "High volume — per-action latency, cost, and flakiness compound; the "
            "cost of building/requesting an API is usually justified."
        )
    elif volume == "low":
        score -= 1
        reasons.append(
            "Low volume / one-off — computer-use overhead is acceptable for a "
            "task you run rarely."
        )

    # Reversibility: irreversible work raises the bar for pixel-driven control.
    if reversible == "no":
        score += 1
        reasons.append(
            "Task is irreversible — prefer a verifiable interface and add "
            "confirmation gates; pixel misclicks are costly here."
        )

    if score >= 2:
        rec = "use-api-mcp"
    elif score <= -2:
        rec = "use-computer-use"
    else:
        rec = "borderline"

    magnitude = abs(score)
    confidence = "high" if magnitude >= 4 else "medium" if magnitude >= 2 else "low"
    if api_exists == "unknown":
        confidence = "low"

    return rec, confidence, score, reasons


REC_LABEL = {
    "use-api-mcp": "Use a structured API / MCP tool (NOT computer-use)",
    "use-computer-use": "Computer-use is justified",
    "borderline": "Borderline — decide on secondary factors / investigate further",
}

REC_NEXT = {
    "use-api-mcp": [
        "Build against the documented API/SDK/CLI, or wire an MCP server.",
        "If the API has gaps, use computer-use only for those specific gaps.",
    ],
    "use-computer-use": [
        "Design the screenshot -> reason -> action loop; re-ground each step.",
        "Add a verification observation after every state-changing action.",
        "Add confirmation gates for destructive steps and run in a sandbox.",
    ],
    "borderline": [
        "Confirm whether any API/MCP surface exists before committing.",
        "Pilot a small computer-use slice and measure success rate before scaling.",
    ],
}


def render_human(data):
    lines = []
    lines.append("Tool Choice Advisor")
    lines.append("=" * 40)
    lines.append("Inputs:")
    lines.append("  api_exists    : %s" % data["inputs"]["api_exists"])
    lines.append("  gui_stability : %s" % data["inputs"]["gui_stability"])
    lines.append("  volume        : %s" % data["inputs"]["volume"])
    lines.append("  reversible    : %s" % data["inputs"]["reversible"])
    lines.append("")
    lines.append("Recommendation : %s" % REC_LABEL[data["recommendation"]])
    lines.append("Confidence     : %s (score %+d)" % (data["confidence"], data["score"]))
    lines.append("")
    lines.append("Rationale:")
    for r in data["reasons"]:
        lines.append("  - %s" % r)
    lines.append("")
    lines.append("Next steps:")
    for n in data["next_steps"]:
        lines.append("  -> %s" % n)
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(
        description="Recommend computer-use vs a structured API/MCP tool for a target."
    )
    p.add_argument("--api-exists", default="unknown",
                   help="Does a real API/SDK/CLI/MCP tool exist? yes|no|unknown")
    p.add_argument("--gui-stability", default="medium",
                   help="How stable is the GUI? low|medium|high")
    p.add_argument("--volume", default="medium",
                   help="Expected run volume? low|medium|high")
    p.add_argument("--reversible", default="unknown",
                   help="Is the task reversible? yes|no|unknown")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = p.parse_args()

    api_exists = normalize(args.api_exists, TRI, "api-exists")
    gui_stability = normalize(args.gui_stability, LEVELS, "gui-stability")
    volume = normalize(args.volume, LEVELS, "volume")
    reversible = normalize(args.reversible, TRI, "reversible")

    rec, confidence, score, reasons = evaluate(
        api_exists, gui_stability, volume, reversible
    )

    data = {
        "inputs": {
            "api_exists": api_exists,
            "gui_stability": gui_stability,
            "volume": volume,
            "reversible": reversible,
        },
        "recommendation": rec,
        "recommendation_label": REC_LABEL[rec],
        "confidence": confidence,
        "score": score,
        "reasons": reasons,
        "next_steps": REC_NEXT[rec],
    }

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render_human(data))


if __name__ == "__main__":
    main()
