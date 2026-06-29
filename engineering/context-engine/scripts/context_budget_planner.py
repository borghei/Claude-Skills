#!/usr/bin/env python3
"""Context Budget Planner - Allocate a context window across components and flag overflow.

Given a window size and the token sizes of each context component (system prompt,
persisted memory, conversation history, tool results, retrieved/RAG chunks) plus a
reserved output buffer, this tool reports the allocation, flags overflow, and suggests
what to compact or evict first using the Context Engine's eviction-priority order.

No third-party deps, no network, no LLM calls — pure stdlib.

Usage:
    python context_budget_planner.py --window-size 200000 \
        --system 4000 --memory 3000 --history 60000 \
        --tools 90000 --rag 40000 --reserve-output 8000
    python context_budget_planner.py --window-size 1000000 --tools 700000 --json
"""

import argparse
import json
import sys


# Eviction priority: what to reclaim first when over budget (highest value-per-token
# reclaimed first). Mirrors references/memory-and-context-editing.md.
# Each entry: component key, human label, suggested action.
EVICTION_ORDER = [
    ("tools", "stale tool outputs",
     "Evict superseded file reads / search results / command stdout; truncate large outputs (first 50 + last 50 lines); cache by (tool, args, file_hash)."),
    ("rag", "retrieved/RAG chunks",
     "Re-rank by relevance to the current task and drop low-scoring chunks; retrieve narrower next time."),
    ("history", "old conversation history",
     "Summarize-and-replace the oldest turns into a compact digest; keep anchors (task, decisions, last few turns)."),
    ("memory", "persisted memory",
     "Load only task-relevant memory files; trim/summarize oversized memory; store conclusions, not transcripts."),
    ("system", "system instructions",
     "Last resort — tighten wording only; never drop standing constraints or the task definition."),
]

# Recommended allocation bands (fraction of window) from the Token Budget Allocation
# Framework. Used to flag components that look oversized relative to the window.
RECOMMENDED_BANDS = {
    "system": (0.05, 0.10),
    "memory": (0.00, 0.10),
    "history": (0.10, 0.20),
    "tools": (0.05, 0.15),
    "rag": (0.25, 0.40),
    "reserve_output": (0.05, 0.10),
}

COMPONENT_LABELS = {
    "system": "System instructions",
    "memory": "Persisted memory",
    "history": "Conversation history",
    "tools": "Tool results",
    "rag": "Retrieved/RAG chunks",
    "reserve_output": "Reserved output buffer",
}

# Components that count as consumed input (reserve_output is protected, not "used input"
# but it does consume window capacity).
INPUT_COMPONENTS = ["system", "memory", "history", "tools", "rag"]


def build_plan(window, sizes):
    """Compute allocation, utilization, overflow, and recommendations."""
    used_input = sum(sizes[c] for c in INPUT_COMPONENTS)
    reserve = sizes["reserve_output"]
    total = used_input + reserve
    available = window - total  # negative => overflow

    components = []
    for key in INPUT_COMPONENTS + ["reserve_output"]:
        size = sizes[key]
        pct = (size / window) if window else 0.0
        band = RECOMMENDED_BANDS.get(key)
        flag = None
        if band and window:
            lo, hi = band
            if pct > hi:
                flag = "over_band"
            elif pct < lo and size > 0:
                flag = "under_band"
        components.append({
            "component": key,
            "label": COMPONENT_LABELS[key],
            "tokens": size,
            "pct_of_window": round(pct * 100, 1),
            "recommended_band_pct": [round(band[0] * 100, 1), round(band[1] * 100, 1)] if band else None,
            "flag": flag,
        })

    overflow = total > window
    overflow_by = total - window if overflow else 0

    # Suggestions: if overflowing, walk eviction order and propose reclaiming until
    # the deficit is covered. Always include actionable guidance.
    suggestions = []
    if overflow:
        deficit = overflow_by
        for key, label, action in EVICTION_ORDER:
            if deficit <= 0:
                break
            reclaimable = sizes.get(key, 0)
            if reclaimable <= 0:
                continue
            # Assume up to ~70% of a non-system component is reclaimable via
            # compaction/eviction; system only marginally.
            cap = 0.30 if key == "system" else 0.70
            take = min(reclaimable * cap, deficit)
            if take <= 0:
                continue
            suggestions.append({
                "evict": key,
                "label": label,
                "reclaim_up_to_tokens": int(round(take)),
                "action": action,
            })
            deficit -= take
        if deficit > 0:
            suggestions.append({
                "evict": None,
                "label": "still over budget",
                "reclaim_up_to_tokens": int(round(deficit)),
                "action": "Offload durable conclusions to the memory tool and reduce scope, OR move to a larger window / RAG-and-loop instead of loading everything.",
            })
    else:
        # Not overflowing — still surface the biggest oversized component if any.
        over = [c for c in components if c["flag"] == "over_band" and c["component"] != "reserve_output"]
        if over:
            biggest = max(over, key=lambda c: c["tokens"])
            for key, label, action in EVICTION_ORDER:
                if key == biggest["component"]:
                    suggestions.append({
                        "evict": key,
                        "label": label,
                        "reclaim_up_to_tokens": 0,
                        "action": "Within budget but oversized vs. recommended band — consider trimming proactively. " + action,
                    })
                    break

    return {
        "window_size": window,
        "total_allocated": total,
        "used_input": used_input,
        "reserved_output": reserve,
        "available_headroom": available,
        "utilization_pct": round((total / window) * 100, 1) if window else 0.0,
        "overflow": overflow,
        "overflow_by": overflow_by,
        "components": components,
        "suggestions": suggestions,
    }


def render_human(plan):
    lines = []
    w = plan["window_size"]
    lines.append("Context Budget Plan")
    lines.append("=" * 60)
    lines.append(f"Window size:        {w:>12,} tokens")
    lines.append(f"Allocated (total):  {plan['total_allocated']:>12,} tokens "
                 f"({plan['utilization_pct']}% of window)")
    lines.append(f"  Input:            {plan['used_input']:>12,} tokens")
    lines.append(f"  Reserved output:  {plan['reserved_output']:>12,} tokens")
    headroom = plan["available_headroom"]
    if plan["overflow"]:
        lines.append(f"Headroom:           {headroom:>12,} tokens  *** OVERFLOW ***")
    else:
        lines.append(f"Headroom:           {headroom:>12,} tokens")
    lines.append("")
    lines.append("Components:")
    lines.append(f"  {'Component':<24}{'Tokens':>12}{'% win':>8}  {'Band%':>10}  Flag")
    lines.append("  " + "-" * 64)
    for c in plan["components"]:
        band = c["recommended_band_pct"]
        band_s = f"{band[0]:.0f}-{band[1]:.0f}" if band else "-"
        flag = c["flag"] or ""
        flag_disp = {"over_band": "OVER band", "under_band": "under band", "": ""}.get(flag, flag)
        lines.append(f"  {c['label']:<24}{c['tokens']:>12,}{c['pct_of_window']:>7.1f}%  {band_s:>10}  {flag_disp}")
    lines.append("")
    if plan["overflow"]:
        lines.append(f"OVERFLOW by {plan['overflow_by']:,} tokens. Compact/evict in this order:")
    elif plan["suggestions"]:
        lines.append("Within budget. Proactive suggestion:")
    else:
        lines.append("Within budget. No action needed.")
    for i, s in enumerate(plan["suggestions"], 1):
        reclaim = s["reclaim_up_to_tokens"]
        head = f"  {i}. {s['label']}"
        if reclaim:
            head += f"  (reclaim up to ~{reclaim:,} tokens)"
        lines.append(head)
        lines.append(f"     -> {s['action']}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Plan a context-window budget across components; flag overflow and suggest what to compact/evict first.",
    )
    p.add_argument("--window-size", type=int, required=True,
                   help="Total context window size in tokens (e.g. 200000, 1000000).")
    p.add_argument("--system", type=int, default=0, help="System instructions tokens.")
    p.add_argument("--memory", type=int, default=0, help="Persisted memory tokens loaded into context.")
    p.add_argument("--history", type=int, default=0, help="Conversation history tokens.")
    p.add_argument("--tools", type=int, default=0, help="Tool result tokens (file reads, search, stdout).")
    p.add_argument("--rag", type=int, default=0, help="Retrieved / RAG chunk tokens.")
    p.add_argument("--reserve-output", type=int, default=0,
                   help="Reserved output-generation buffer in tokens.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text.")
    args = p.parse_args(argv)

    if args.window_size <= 0:
        p.error("--window-size must be positive")

    sizes = {
        "system": max(0, args.system),
        "memory": max(0, args.memory),
        "history": max(0, args.history),
        "tools": max(0, args.tools),
        "rag": max(0, args.rag),
        "reserve_output": max(0, args.reserve_output),
    }

    plan = build_plan(args.window_size, sizes)

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(render_human(plan))

    # Non-zero exit on overflow so the tool is usable as a CI/loop gate.
    return 1 if plan["overflow"] else 0


if __name__ == "__main__":
    sys.exit(main())
