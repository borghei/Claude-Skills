#!/usr/bin/env python3
"""Roadmap Transformer - bucket initiatives into Now/Next/Later and check that
each one is stated as an outcome, not an output.

Writing the outcome is the model's or PM's job; this tool does the parts a
script does reliably: horizon placement from the quarter, the Now-column cap,
and per-item checks that Now/Next items carry an outcome statement, a metric
with baseline and target, and (for Now) a counter-metric. Items with no outcome
get the "so what?" prompts for their type.

Usage:
    python roadmap_transformer.py --input ../assets/sample_roadmap_clean.json
    python roadmap_transformer.py --demo --format markdown
    python roadmap_transformer.py --input roadmap.json --as-of "Q4 2026" --format json

Input: {"initiatives": [{"title", "description", "quarter": "Q3 2026",
         "type": "feature|improvement|infrastructure", "outcome": "Enable ... so that ...",
         "metric": {"name", "baseline", "target"}, "counter_metric": "..."}]}
"As of" defaults to the earliest quarter in the data, so a sample reads the
same on any day; pass --as-of with the current quarter for a live roadmap.

Exit codes: 0 no errors, 1 at least one error finding, 2 bad input.
Standard library only.
"""

import argparse
import json
import re
import sys

NOW_CAP = 3  # more Now items than this means the commitment level is not real
OUTPUT_VERBS = ("build", "launch", "ship", "add", "migrate", "implement", "release",
                "create", "develop", "redesign", "integrate", "deliver")

SO_WHAT = {
    "feature": ["What customer problem does this solve?",
                "How does the customer's workflow change after it ships?",
                "Which number moves: adoption, time on task, or satisfaction?"],
    "improvement": ["Which friction point does it remove, and what does it cost users today?",
                    "Which number moves: speed, retention, or related support tickets?"],
    "infrastructure": ["What becomes possible for customers that is not possible today?",
                       "Which number moves: reliability, headroom, or shipping speed?"],
}

DEMO_DATA = {
    "initiatives": [
        {"title": "Build advanced search", "quarter": "Q2 2026", "type": "feature",
         "description": "Full-text search with filters, autocomplete and relevance ranking."},
        {"title": "Improve onboarding flow", "quarter": "Q2 2026", "type": "improvement",
         "description": "Redesign the first-run experience with fewer steps.",
         "outcome": "Redesign onboarding with a checklist",
         "metric": {"name": "Day-7 activation", "baseline": None, "target": "45%"}},
        {"title": "Migrate to new database", "quarter": "Q2 2026", "type": "infrastructure",
         "description": "PostgreSQL upgrade with pooling and read replicas."},
        {"title": "Launch mobile app", "quarter": "Q2 2026", "type": "feature",
         "description": "iOS and Android apps with core web functionality."},
        {"title": "Add team collaboration", "quarter": "Q4 2026", "type": "feature",
         "description": "Shared workspaces, comments and real-time editing."},
    ]
}


def parse_quarter(text):
    """'Q3 2026' -> (2026, 3), or None."""
    m = re.fullmatch(r"\s*Q([1-4])\s+(\d{4})\s*", str(text or ""), re.IGNORECASE)
    return (int(m.group(2)), int(m.group(1))) if m else None


def horizon(q, as_of):
    distance = (q[0] - as_of[0]) * 4 + (q[1] - as_of[1])
    return "Now" if distance <= 0 else "Next" if distance == 1 else "Later"


def check_item(item, h):
    """Return a list of (severity, message) for one initiative."""
    out = []
    outcome = str(item.get("outcome") or "").strip()
    metric = item.get("metric") if isinstance(item.get("metric"), dict) else {}
    if h == "Later":
        if not outcome:
            out.append(("info", "no outcome yet; fine for Later, required before it moves to Next"))
        return out
    if not outcome:
        out.append(("error", "no outcome statement"))
    else:
        first = outcome.split()[0].lower()
        if first in OUTPUT_VERBS:
            out.append(("error", f"outcome starts with '{first}' and reads like an output; "
                                 "say what changes for the customer"))
        if "so that" not in outcome.lower():
            out.append(("warn", "outcome has no 'so that ...' business impact"))
    if not metric.get("name"):
        out.append(("error", "no success metric"))
    else:
        for key in ("baseline", "target"):
            if metric.get(key) in (None, ""):
                out.append(("error", f"metric '{metric['name']}' has no {key}"))
    if h == "Now" and not item.get("counter_metric"):
        out.append(("warn", "no counter-metric to catch the outcome being gamed"))
    return out


def analyze(data, as_of_text):
    items = data["initiatives"]
    quarters = [parse_quarter(i.get("quarter")) for i in items]
    if as_of_text:
        as_of = parse_quarter(as_of_text)
        if not as_of:
            raise ValueError(f"--as-of must look like 'Q3 2026', got {as_of_text!r}")
    else:
        valid = [q for q in quarters if q]
        if not valid:
            raise ValueError("no initiative has a quarter like 'Q3 2026'; pass --as-of")
        as_of = min(valid)
    results = []
    for item, q in zip(items, quarters):
        h = horizon(q, as_of) if q else "Later"
        issues = check_item(item, h)
        if not q:
            issues.insert(0, ("error", f"quarter {item.get('quarter')!r} is not 'Q[1-4] YYYY'"))
        elif q < as_of:
            issues.insert(0, ("warn", f"{item.get('quarter')} is before {as_of_text}: shipped, slipped, or re-plan?"))
        entry = {"title": item.get("title", "Untitled"), "quarter": item.get("quarter", ""),
                 "type": item.get("type", "feature"), "horizon": h,
                 "outcome": item.get("outcome") or None,
                 "issues": [{"severity": s, "message": m} for s, m in issues]}
        if not item.get("outcome"):
            entry["so_what_prompts"] = SO_WHAT.get(entry["type"], SO_WHAT["feature"])
        results.append(entry)
    roadmap_issues = []
    now = [r["title"] for r in results if r["horizon"] == "Now"]
    if len(now) > NOW_CAP:
        roadmap_issues.append({"severity": "error", "message":
                               f"{len(now)} Now items (cap {NOW_CAP}); move the rest to Next"})
    errors = sum(1 for r in results for i in r["issues"] if i["severity"] == "error")
    errors += sum(1 for i in roadmap_issues if i["severity"] == "error")
    counts = {h: sum(1 for r in results if r["horizon"] == h) for h in ("Now", "Next", "Later")}
    return {"as_of": f"Q{as_of[1]} {as_of[0]}", "horizon_counts": counts, "errors": errors,
            "roadmap_issues": roadmap_issues, "initiatives": results}


def format_text(report):
    lines = [f"Outcome roadmap check (as of {report['as_of']})",
             "  " + " | ".join(f"{k}: {v}" for k, v in report["horizon_counts"].items()),
             f"  Errors: {report['errors']}", ""]
    for i in report["roadmap_issues"]:
        lines.append(f"  [{i['severity'].upper()}] roadmap: {i['message']}")
    for h in ("Now", "Next", "Later"):
        items = [r for r in report["initiatives"] if r["horizon"] == h]
        if not items:
            continue
        lines.append(f"\n{h}")
        for r in items:
            lines.append(f"  - {r['title']} ({r['quarter']})")
            if r["outcome"]:
                lines.append(f"      outcome: {r['outcome']}")
            for i in r["issues"]:
                lines.append(f"      [{i['severity'].upper()}] {i['message']}")
            for p in r.get("so_what_prompts", []) if h != "Later" else []:
                lines.append(f"      ? {p}")
    return "\n".join(lines)


def format_markdown(report):
    lines = ["# Outcome Roadmap", "", f"**As of:** {report['as_of']}  |  **Errors:** {report['errors']}", ""]
    for i in report["roadmap_issues"]:
        lines.append(f"> **{i['severity']}:** {i['message']}")
    commitment = {"Now": "High: team assigned, scope defined", "Next": "Medium: direction set",
                  "Later": "Low: strategic intent only"}
    for h in ("Now", "Next", "Later"):
        items = [r for r in report["initiatives"] if r["horizon"] == h]
        if not items:
            continue
        lines += ["", f"## {h}", "", f"_Commitment: {commitment[h]}_", ""]
        for r in items:
            lines.append(f"### {r['title']} ({r['quarter']})")
            lines.append(f"**Outcome:** {r['outcome'] or '_to write_'}")
            for i in r["issues"]:
                lines.append(f"- {i['severity']}: {i['message']}")
            for p in r.get("so_what_prompts", []) if h != "Later" else []:
                lines.append(f"- [ ] {p}")
            lines.append("")
    return "\n".join(lines)


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise SystemExit(_fail(f"cannot read {path}: {e.strerror or e}"))
    except ValueError as e:
        raise SystemExit(_fail(f"invalid JSON in {path}: {e}"))
    items = data.get("initiatives") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items or not all(isinstance(i, dict) for i in items):
        raise SystemExit(_fail("input must be a JSON object with a non-empty 'initiatives' list of objects"))
    return data


def _fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    return 2


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Place roadmap initiatives in Now/Next/Later and check each is outcome-ready. "
                    "Exit 0 no errors, 1 errors found, 2 bad input.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="JSON file with an 'initiatives' list")
    src.add_argument("--demo", action="store_true", help="Run on built-in output-style roadmap (exits 1)")
    parser.add_argument("--as-of", help="Current quarter, e.g. 'Q4 2026' (default: earliest quarter in the data)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--output", help="Write to this file instead of stdout")
    args = parser.parse_args(argv)

    data = DEMO_DATA if args.demo else load(args.input)
    try:
        report = analyze(data, args.as_of)
    except ValueError as e:
        return _fail(str(e))
    render = {"json": lambda r: json.dumps(r, indent=2), "markdown": format_markdown, "text": format_text}
    out = render[args.format](report)
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out + "\n")
        except OSError as e:
            return _fail(f"cannot write {args.output}: {e.strerror or e}")
    else:
        print(out)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
