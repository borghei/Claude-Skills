#!/usr/bin/env python3
"""Profile a CSV and draft a feature plan: what to keep, transform or drop.

Infers types, null rate, cardinality and distribution; flags constant, ID-like
and highly correlated columns; with a target, scores features and flags leakage
suspects. Every column gets a suggested action. Standard library only.

Usage: python3 feature_engineering_pipeline.py --input data.csv --target churned --output out/
"""

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NULLS = {"", "na", "n/a", "null", "none", "nan"}
BOOL_WORDS = {"true", "false", "yes", "no", "y", "n", "t", "f"}
LEAKAGE_R = 0.90
EXAMPLE = """user_id,signup_date,plan,sessions,revenue,revenue_eur,converted
U01,2025-01-03,free,3,0,0,0
U02,2025-01-04,pro,14,49.0,45.1,1
U03,2025-01-04,free,1,0,0,0
U04,2025-01-05,team,22,199.0,183.1,1
U05,2025-01-06,free,,0,0,0
U06,2025-01-07,pro,9,0,0,0
U07,2025-01-08,free,2,0,0,0
U08,2025-01-09,team,30,398.0,366.2,1"""


def load_csv(path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Read the CSV into a header and rows, exiting on a ragged row or bad file."""
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header, rows = next(reader, []), []
            for rec in reader:
                if rec and len(rec) != len(header):
                    sys.exit(f"ERROR: {path} line {reader.line_num} has {len(rec)} field(s) "
                             f"but the header has {len(header)}")
                rows += [dict(zip(header, rec))] if rec else []
    except FileNotFoundError:
        sys.exit(f"ERROR: file not found: {path}")
    except (UnicodeDecodeError, csv.Error) as exc:
        sys.exit(f"ERROR: {path} is not a readable UTF-8 CSV: {exc}")
    if not header or not rows:
        sys.exit(f"ERROR: {path} needs a header row and at least one data row")
    return header, rows


def to_float(v: str) -> Optional[float]:
    """Parse a finite float, or return None."""
    try:
        x = float(v)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


def is_date(v: str) -> bool:
    """True when the value is an ISO date or datetime."""
    try:
        datetime.fromisoformat(v)
    except ValueError:
        return False
    return True


def quantile(sorted_xs: List[float], q: float) -> float:
    """Linear-interpolated quantile of an already sorted list."""
    pos = (len(sorted_xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def pearson(xs: List[Optional[float]], ys: List[Optional[float]]) -> Optional[float]:
    """Pearson r over rows where both values are present."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    mx = statistics.fmean(p[0] for p in pairs)
    my = statistics.fmean(p[1] for p in pairs)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    syy = sum((y - my) ** 2 for _, y in pairs)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def eta(cats: List[Optional[str]], ys: List[Optional[float]]) -> Optional[float]:
    """Correlation ratio: how much of the target's variance the categories explain."""
    pairs = [(c, y) for c, y in zip(cats, ys) if c is not None and y is not None]
    if len(pairs) < 3:
        return None
    mean = statistics.fmean(y for _, y in pairs)
    total = sum((y - mean) ** 2 for _, y in pairs)
    groups: Dict[str, List[float]] = {}
    for c, y in pairs:
        groups.setdefault(c, []).append(y)
    between = sum(len(g) * (statistics.fmean(g) - mean) ** 2 for g in groups.values())
    return math.sqrt(between / total) if total > 0 else None


def profile_column(name: str, raw: List[str]) -> Dict[str, Any]:
    """Type, completeness, cardinality and distribution of one column."""
    vals = [v.strip() for v in raw]
    present = [v for v in vals if v.lower() not in NULLS]
    n = len(vals)
    distinct = len(set(present))
    col: Dict[str, Any] = {"name": name, "rows": n, "null_rate": round(1 - len(present) / n, 4),
                           "distinct": distinct,
                           "unique_ratio": round(distinct / len(present), 4) if present else 0.0}
    nums = [to_float(v) for v in present]
    if present and all(x is not None for x in nums):
        col["type"] = "binary" if set(nums) <= {0.0, 1.0} else "numeric"
        xs = sorted(nums)  # type: ignore[arg-type]
        mean = statistics.fmean(xs)
        sd = statistics.pstdev(xs) if len(xs) > 1 else 0.0
        skew = (sum((x - mean) ** 3 for x in xs) / len(xs)) / sd ** 3 if sd > 0 else 0.0
        col.update(min=xs[0], max=xs[-1], mean=round(mean, 4), std=round(sd, 4),
                   p05=round(quantile(xs, .05), 4), p25=round(quantile(xs, .25), 4),
                   p50=round(quantile(xs, .5), 4), p75=round(quantile(xs, .75), 4),
                   p95=round(quantile(xs, .95), 4), skew=round(skew, 3))
        col["sequential"] = (distinct == len(xs) > 1 and all(x == int(x) for x in xs)
                             and xs[-1] - xs[0] + 1 == distinct)
        col["values"] = [to_float(v) if v.lower() not in NULLS else None for v in vals]
    elif present and all(is_date(v) for v in present):
        col["type"] = "datetime"
        dates = sorted(present, key=datetime.fromisoformat)
        col["min"], col["max"] = dates[0], dates[-1]
    elif present and {v.lower() for v in present} <= BOOL_WORDS and distinct == 2:
        col["type"] = "binary"
    else:
        col["type"] = "categorical" if present else "empty"
    if present:
        top, count = Counter(present).most_common(1)[0]
        col["top_value"], col["top_share"] = top, round(count / len(present), 4)
    col["labels"] = [v if v.lower() not in NULLS else None for v in vals]
    return col


def suggest(col: Dict[str, Any], max_onehot: int) -> Tuple[str, List[str]]:
    """Pick an action and transforms for a column from its profile."""
    t, notes = col["type"], []
    if t == "empty" or col["null_rate"] > 0.95:
        return "drop", ["more than 95% null"]
    if col["distinct"] <= 1:
        return "drop", ["constant"]
    if col.get("top_share", 0) >= 0.95:
        return "drop", [f"near-constant ({col['top_share']:.0%} one value)"]
    if t == "categorical" and col["unique_ratio"] >= 0.95 and (col["rows"] >= 20
                                                                or col["unique_ratio"] == 1):
        return "drop", ["ID-like: nearly every value is unique"]
    if col.get("sequential"):
        return "drop", ["ID-like: unique consecutive integers"]
    if col["null_rate"] > 0:
        notes.append("impute (median or mode) and add a was-missing indicator")
    if t == "numeric" and abs(col["skew"]) > 1:
        notes.append("log1p transform (right skew)" if col["min"] >= 0 and col["skew"] > 0
                     else "Yeo-Johnson transform (skewed, has negatives)")
    if t == "datetime":
        return "transform", notes + ["extract day-of-week, month and recency; drop the raw date"]
    if t == "categorical":
        notes.append("one-hot encode" if col["distinct"] <= max_onehot
                     else "target or frequency encode, fitted out-of-fold (high cardinality)")
    return ("transform" if notes else "keep"), notes


def build_plan(path: str, target: Optional[str], corr_threshold: float,
               max_onehot: int) -> Dict[str, Any]:
    """Profile every column, then add correlation, target and plan sections."""
    header, rows = load_csv(path)
    if target and target not in header:
        sys.exit(f"ERROR: target column '{target}' not in {path}. Columns: {', '.join(header)}")
    cols = [profile_column(h, [r.get(h) or "" for r in rows]) for h in header]
    by_name = {c["name"]: c for c in cols}
    numeric = [c for c in cols if "values" in c and c["name"] != target and c["distinct"] > 1]
    pairs = []
    for i, a in enumerate(numeric):
        for b in numeric[i + 1:]:
            r = pearson(a["values"], b["values"])
            if r is not None and abs(r) >= corr_threshold:
                pairs.append({"a": a["name"], "b": b["name"], "r": round(r, 4)})
    target_info: Dict[str, Any] = {}
    plan: Dict[str, Dict[str, Any]] = {}
    if target:
        tc = by_name[target]
        labels = sorted({v for v in tc["labels"] if v is not None})
        y = tc.get("values") or ([None if v is None else float(v == labels[1]) for v in tc["labels"]]
                                 if len(labels) == 2 else None)
        target_info = {"column": target, "type": tc["type"], "associations": [], "leakage_suspects": []}
        if y is None:
            target_info["note"] = "multi-class text target: associations not computed"
        for c in cols:
            id_like = c["type"] == "categorical" and c["unique_ratio"] >= 0.95
            if (y is None or c["name"] == target or id_like or c["distinct"] <= 1
                    or c["type"] not in ("numeric", "binary", "categorical")):
                continue
            score = pearson(c["values"], y) if "values" in c else eta(c["labels"], y)
            if score is None:
                continue
            kind = "pearson_r" if "values" in c else "eta"
            target_info["associations"].append({"feature": c["name"], kind: round(score, 4)})
            if abs(score) >= LEAKAGE_R:
                target_info["leakage_suspects"].append(c["name"])
        target_info["associations"].sort(key=lambda a: -abs(a.get("pearson_r", a.get("eta", 0))))
    for c in cols:
        if c["name"] == target:
            plan[target] = {"action": "target", "notes": []}
            continue
        action, notes = suggest(c, max_onehot)
        if c["name"] in target_info.get("leakage_suspects", []):
            action, notes = "drop", [f"leakage suspect: |association| >= {LEAKAGE_R} with target. "
                                     "confirm it is known before the outcome"]
        plan[c["name"]] = {"action": action, "notes": notes}
    assoc = {a["feature"]: abs(a.get("pearson_r", 0)) for a in target_info.get("associations", [])}
    for p in pairs:
        if plan[p["a"]]["action"] != "drop" and plan[p["b"]]["action"] != "drop":
            weaker = p["b"] if assoc.get(p["b"], 0) <= assoc.get(p["a"], 0) else p["a"]
            other = p["a"] if weaker == p["b"] else p["b"]
            plan[weaker] = {"action": "drop", "notes": [f"redundant with {other} (r = {p['r']})"]}
    for c in cols:
        c.pop("values", None)
        c.pop("labels", None)
    return {"input": path, "rows": len(rows), "columns": cols, "correlated_pairs": pairs,
            "corr_threshold": corr_threshold, "target": target_info or None, "plan": plan}


def output(rep: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as readable tables."""
    if fmt == "json":
        print(json.dumps(rep, indent=2))
        return
    print(f"Feature profile: {rep['input']} ({rep['rows']} rows, {len(rep['columns'])} columns)\n")
    print(f"  {'column':<18}{'type':<12}{'null%':>6}{'distinct':>9}  summary")
    for c in rep["columns"]:
        if c["type"] == "numeric":
            summ = (f"min {c['min']:.4g}, p50 {c['p50']:.4g}, max {c['max']:.4g}, "
                    f"mean {c['mean']:.4g}, sd {c['std']:.4g}, skew {c['skew']:+.2f}")
        elif c["type"] == "datetime":
            summ = f"{c['min']} to {c['max']}"
        else:
            summ = f"top '{c.get('top_value', '')}' {c.get('top_share', 0):.0%}"
        print(f"  {c['name']:<18}{c['type']:<12}{c['null_rate']:>6.0%}{c['distinct']:>9}  {summ}")
    print(f"\nCorrelated pairs (|r| >= {rep['corr_threshold']}):")
    for p in rep["correlated_pairs"] or [{"a": "none", "b": "", "r": ""}]:
        print(f"  {p['a']} ~ {p['b']}  r = {p['r']}" if p["b"] else "  none")
    if rep["target"]:
        t = rep["target"]
        print(f"\nAssociation with target '{t['column']}':")
        for a in t["associations"]:
            kind = "r" if "pearson_r" in a else "eta"
            print(f"  {a['feature']:<18}{kind} = {a.get('pearson_r', a.get('eta')):+.3f}")
        print(f"  Leakage suspects: {', '.join(t['leakage_suspects']) or 'none'}")
    print("\nFeature plan:")
    for name, step in rep["plan"].items():
        print(f"  {name:<18}{step['action']:<10}{'; '.join(step['notes'])}")


def main() -> None:
    """Parse arguments, build the profile and plan, and report."""
    p = argparse.ArgumentParser(description="Profile a CSV and draft a keep/transform/drop plan.")
    p.add_argument("--input", "-i", help="CSV file with a header row")
    p.add_argument("--target", "-t", help="target column to score features against")
    p.add_argument("--corr-threshold", type=float, default=0.95, help="flag pairs at |r| >= this")
    p.add_argument("--max-onehot", type=int, default=10,
                   help="one-hot categoricals up to this many levels (default 10)")
    p.add_argument("--output", "-o", help="directory to write feature_plan.json into")
    p.add_argument("--force", action="store_true", help="overwrite an existing file in --output")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    p.add_argument("--example", action="store_true", help="print a sample CSV and exit")
    args = p.parse_args()
    if args.example:
        print(EXAMPLE)
        return
    if not args.input:
        p.error("--input is required (or use --example)")
    target = Path(args.output) / "feature_plan.json" if args.output else None
    if target and target.exists() and not args.force:
        sys.exit(f"ERROR: {target} already exists; pass --force to overwrite")
    try:
        rep = build_plan(args.input, args.target, args.corr_threshold, args.max_onehot)
    except OverflowError:
        sys.exit(f"ERROR: {args.input} has values too large to summarize (overflow); rescale them")
    output(rep, args.format)
    if target:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            sys.exit(f"ERROR: cannot write {target}: {exc}")
        print(f"Wrote {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
