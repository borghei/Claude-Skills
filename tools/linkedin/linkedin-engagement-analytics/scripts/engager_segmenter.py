#!/usr/bin/env python3
"""Segment the people who engaged with a post and compare the mix with a target audience.

Reads one or more engagement exports (CSV or JSON) the user supplies, groups
engagers by seniority, function and company, and reports what share fit the
stated target audience, with an interval, against the user's own goal and
trailing baseline. Output is aggregate only: no per-person rows are printed.
Offline: it reads local files and contacts nothing.

Usage:
    python3 engager_segmenter.py --input engagers.csv --target target_audience.json
    python3 engager_segmenter.py --input post1.csv post2.csv post3.csv --target target.json
    python3 engager_segmenter.py --input engagers.json --target target.json \
        --format json --fail-on-miss

Exit codes:
    0  readout produced (and the post did not miss, if --fail-on-miss is set)
    1  --fail-on-miss is set and the core share is below the goal or baseline
    2  bad input: file missing, unreadable, wrong columns, empty, or bad target
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segment_rules import (  # noqa: E402
    FIT_LEVELS, classify, compare, fit_level, norm_company, validate_target, wilson)

ALIASES: Dict[str, Tuple[str, ...]] = {
    "name": ("name", "full_name", "member", "person"),
    "headline": ("headline", "title", "job_title", "occupation", "subtitle"),
    "company": ("company", "organisation", "organization", "employer"),
    "engagement": ("engagement", "type", "action", "interaction"),
    "comment": ("comment", "comment_text", "text"),
}


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def read_rows(path: Path) -> List[Dict[str, Any]]:
    """Read an export as a list of dict rows from CSV or JSON."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        fail(f"export not found: {path}")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}. Save the export as UTF-8 CSV or JSON.")
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
        rows = data.get("engagers") if isinstance(data, dict) else data
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            fail(f"{path} must be a JSON array of objects, or an object with an 'engagers' array.")
        return rows
    return list(csv.DictReader(text.splitlines()))


def normalise(rows: List[Dict[str, Any]], path: Path) -> List[Dict[str, str]]:
    """Map column aliases to standard keys and drop rows with no headline."""
    if not rows:
        fail(f"{path} contains no rows.")
    columns = {str(k).strip().lower(): k for k in rows[0] if k is not None}
    found = {std: next((columns[a] for a in names if a in columns), None)
             for std, names in ALIASES.items()}
    if found["headline"] is None:
        fail(f"{path} has no headline column. Expected one of: "
             + ", ".join(ALIASES["headline"]) + ". Found: " + ", ".join(columns))
    out: List[Dict[str, str]] = []
    for row in rows:
        item = {std: str(row.get(col) or "").strip() if col else "" for std, col in found.items()}
        if not item["headline"]:
            continue
        is_comment = "comment" in item["engagement"].lower() or bool(item["comment"])
        out.append({"name": item["name"], "headline": item["headline"], "company": item["company"],
                    "engagement": "comment" if is_comment else "reaction"})
    if not out:
        fail(f"{path} has rows but every headline is blank.")
    return out


def dedupe(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Merge repeat rows for one person, keeping a comment over a reaction."""
    merged: Dict[Tuple[str, str], Dict[str, str]] = {}
    for index, row in enumerate(rows):
        key = (row["name"].lower(), row["headline"].lower()) if row["name"] else (f"#{index}", "")
        kept = merged.get(key)
        if kept is None or (row["engagement"] == "comment" and kept["engagement"] != "comment"):
            merged[key] = row
    return list(merged.values())


def analyse(rows: List[Dict[str, str]], spec: Dict[str, Any]) -> Dict[str, Any]:
    """Classify each engager and aggregate counts by segment and fit."""
    target = spec.get("target") or {}
    own = {norm_company(c) for c in spec.get("own_companies") or []}
    named = {norm_company(c) for c in target.get("companies") or []}
    seniority, function, companies = Counter(), Counter(), Counter()
    fit: Counter = Counter()
    by_engagement = {"comment": Counter(), "reaction": Counter()}
    internal = unclassified = named_hits = 0
    for row in rows:
        person = classify(row["headline"], row["company"])
        company = norm_company(person["company"])
        if company and company in own:
            internal += 1
            continue
        if company:
            companies[person["company"]] += 1
            named_hits += company in named
        if person["seniority"] == "unknown" and person["function"] == "unknown":
            unclassified += 1
            continue
        seniority[person["seniority"]] += 1
        function[person["function"]] += 1
        level = fit_level(person, target)
        fit[level] += 1
        by_engagement[row["engagement"]][level] += 1
    classified = sum(fit.values())
    low, high = wilson(fit["core"], classified)
    return {"engagers": len(rows), "internal": internal, "external": len(rows) - internal,
            "unclassified": unclassified, "classified": classified,
            "fit": {k: fit[k] for k in FIT_LEVELS},
            "core_share": round(fit["core"] / classified, 4) if classified else 0.0,
            "core_interval": [round(low, 4), round(high, 4)],
            "by_engagement": {k: {"core": v["core"], "total": sum(v.values())}
                              for k, v in by_engagement.items()},
            "named_account_engagers": named_hits,
            "seniority": dict(seniority.most_common()), "function": dict(function.most_common()),
            "companies": {c: n for c, n in companies.most_common(8) if n >= 2}}


def verdict(result: Dict[str, Any], spec: Dict[str, Any], min_sample: int) -> Dict[str, Any]:
    """Judge the core share against the user's goal and trailing baseline."""
    notes: List[str] = []
    low, high = result["core_interval"]
    goal = spec.get("goal_core_share")
    baseline = (spec.get("baseline") or {}).get("core_share")
    out: Dict[str, Any] = {"sample_ok": result["classified"] >= min_sample,
                           "vs_goal": None, "vs_baseline": None, "missed": False}
    if not out["sample_ok"]:
        notes.append(f"Only {result['classified']} classified external engagers (minimum set to "
                     f"{min_sample}). Treat every share in this readout as a description, not a finding.")
    if result["external"] and result["unclassified"] / result["external"] > 0.4:
        notes.append("More than 40% of external headlines could not be classified. "
                     "Add a company column or extend the patterns before trusting the mix.")
    if result["engagers"] and result["internal"] / result["engagers"] > 0.3:
        notes.append("More than 30% of engagers are from your own company; "
                     "the post mostly reached colleagues.")
    if isinstance(goal, (int, float)) and not isinstance(goal, bool):
        out["vs_goal"] = compare(low, high, float(goal))
    if isinstance(baseline, (int, float)) and not isinstance(baseline, bool):
        out["vs_baseline"] = compare(low, high, float(baseline))
    if out["vs_goal"] is None and out["vs_baseline"] is None:
        notes.append("No goal or baseline supplied. Record this core share as a baseline point; "
                     "a single post has nothing to be compared with.")
    reference = out["vs_goal"] or out["vs_baseline"]
    out["missed"] = bool(out["sample_ok"] and reference == "below")
    out["notes"] = notes
    return out


def render(report: Dict[str, Any]) -> None:
    """Print the readout as text: fit, segments, verdict and cautions."""
    pooled, judge = report["pooled"], report["verdict"]

    def pct(part: int, whole: int) -> str:
        """Format a share as a whole percentage, or a dash for an empty base."""
        return f"{100 * part / whole:.0f}%" if whole else "-"

    print(f"Engagement readout: {report['post']}")
    print(f"Exports: {len(report['exports'])}   engagers: {pooled['engagers']}   duplicate rows merged: "
          f"{report['duplicates_merged']}   rows skipped (no headline): {report['rows_skipped']}")
    print(f"Own company: {pooled['internal']} ({pct(pooled['internal'], pooled['engagers'])})   "
          f"external: {pooled['external']}   classified: {pooled['classified']} "
          f"({pct(pooled['classified'], pooled['external'])} of external)")
    print("=" * 72)
    low, high = pooled["core_interval"]
    print("Fit with the target audience (external, classified)")
    for level in FIT_LEVELS:
        extra = f"   95% interval {low:.0%} to {high:.0%}" if level == "core" else ""
        print(f"  {level:<10}{pooled['fit'][level]:>4}  {pct(pooled['fit'][level], pooled['classified']):>4}{extra}")
    for kind, row in pooled["by_engagement"].items():
        print(f"  core among {'commenters' if kind == 'comment' else 'reaction-only'}: {row['core']} of {row['total']} ({pct(row['core'], row['total'])})")
    print(f"  engagers from named target companies: {pooled['named_account_engagers']}")
    for label in ("seniority", "function"):
        print(f"\nBy {label}")
        for name, count in pooled[label].items():
            print(f"  {name:<24}{count:>4}  {pct(count, pooled['classified']):>4}")
    print("\nCompanies with two or more engagers")
    for name, count in pooled["companies"].items():
        print(f"  {name:<32}{count:>4}")
    if not pooled["companies"]:
        print("  none")
    if len(report["exports"]) > 1:
        print("\nPer export")
        for row in report["exports"]:
            print(f"  {row['file']:<34} classified {row['classified']:>4}   core {row['core_share']:.0%}")
        print(f"  people appearing in more than one export: {report['repeat_engagers']}")
    print("\nVerdict")
    words = {"above": "above", "below": "below", "within": "not distinguishable from"}
    for label, key, ref in (("goal", "vs_goal", report["goal_core_share"]),
                            ("trailing baseline", "vs_baseline", report["baseline_core_share"])):
        if judge[key]:
            print(f"  Core share {pooled['core_share']:.0%} is {words[judge[key]]} your {label} of {ref:.0%}.")
    for note in judge["notes"]:
        print(f"  Note: {note}")


def main() -> None:
    """Parse arguments, segment the exports, print the readout and apply the gate."""
    parser = argparse.ArgumentParser(
        description="Segment post engagers from CSV or JSON exports by seniority, function and "
                    "company, and compare the mix with a stated target audience. Aggregate "
                    "output only. Offline: reads only the files you supply.",
        epilog="Exit codes: 0 readout produced, 1 --fail-on-miss and the post missed, 2 bad input.")
    parser.add_argument("--input", required=True, nargs="+",
                        help="One or more engagement exports (.csv or .json). Several files are "
                             "pooled, which is how a trailing baseline is built.")
    parser.add_argument("--target", required=True,
                        help="Target audience JSON (see assets/sample_target_audience.json).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--min-sample", type=int, default=None,
                        help="Classified external engagers needed before a verdict counts "
                             "(default: the target file's min_sample, else 30).")
    parser.add_argument("--fail-on-miss", action="store_true",
                        help="Exit 1 when the core share is below the goal (or the baseline "
                             "if no goal is set) on an adequate sample.")
    args = parser.parse_args()

    try:
        spec = json.loads(Path(args.target).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"target file not found: {args.target}. Copy assets/target_audience_template.json.")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"cannot use target file {args.target}: {exc}")
    if not isinstance(spec, dict) or not isinstance(spec.get("target"), dict):
        fail("target file must be a JSON object with a 'target' object inside it.")
    problems = validate_target(spec["target"])
    if problems:
        fail("target audience is not usable: " + "; ".join(problems)
             + ". Run segment_rules.py --list-rules for the valid names.")
    min_sample = args.min_sample if args.min_sample is not None else spec.get("min_sample", 30)
    if not isinstance(min_sample, int) or isinstance(min_sample, bool) or min_sample < 1:
        fail("min sample must be a whole number of 1 or more.")

    everyone: List[Dict[str, str]] = []
    exports: List[Dict[str, Any]] = []
    seen: List[Set[str]] = []
    merged = skipped = 0
    for name in args.input:
        path = Path(name)
        source = read_rows(path)
        raw = normalise(source, path)
        rows = dedupe(raw)
        merged, skipped = merged + len(raw) - len(rows), skipped + len(source) - len(raw)
        part = analyse(rows, spec)
        exports.append({"file": path.name, "engagers": part["engagers"],
                        "classified": part["classified"], "core_share": part["core_share"]})
        seen.append({f"{r['name'].lower()}|{r['headline'].lower()}" for r in rows if r["name"]})
        everyone.extend(rows)
    repeat = sum(1 for key in set().union(*seen) if sum(key in s for s in seen) > 1)
    pooled = analyse(everyone, spec)
    goal: Optional[float] = spec.get("goal_core_share")
    baseline: Optional[float] = (spec.get("baseline") or {}).get("core_share")
    report = {"post": str((spec.get("post") or {}).get("title") or "untitled post"),
              "exports": exports, "duplicates_merged": merged, "rows_skipped": skipped,
              "repeat_engagers": repeat,
              "goal_core_share": goal, "baseline_core_share": baseline,
              "pooled": pooled, "verdict": verdict(pooled, spec, min_sample)}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        render(report)
    if args.fail_on_miss and report["verdict"]["missed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
