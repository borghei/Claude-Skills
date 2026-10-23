#!/usr/bin/env python3
"""Score saved predictions, compare models, and give an offline readiness verdict.

Reports binary-classification or regression metrics side by side, fold stability, and
pass/fail against config thresholds. Does not train models. Standard library only.

Usage: python3 model_evaluation_suite.py --input preds.csv --folds 5 --config thresholds.json
"""

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NULLS = {"", "na", "n/a", "null", "none", "nan"}
CHECKS = {"min_accuracy": "accuracy", "min_precision": "precision", "min_recall": "recall",
          "min_f1": "f1", "min_auc": "auc", "max_log_loss": "log_loss", "max_brier": "brier",
          "min_r2": "r2", "max_rmse": "rmse", "max_mae": "mae", "max_mape": "mape"}
DEFAULT_CONFIG = {"classification": {"min_auc": 0.85, "max_brier": 0.15}, "regression": {}}
EXAMPLE = ("id,actual,model_a,model_b\nr01,1,0.91,0.70\nr02,0,0.12,0.40\n"
           "r03,1,0.78,0.45\nr04,0,0.35,0.62")


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


def numeric(values: List[str]) -> Optional[List[float]]:
    """All values as floats, or None if any is missing or not a number."""
    try:
        out = [float(v) for v in values]
    except (TypeError, ValueError):
        return None
    return out if all(math.isfinite(x) for x in out) else None


def why_unusable(values: List[str]) -> Optional[str]:
    """Why a column cannot be scored, or None when every value is a finite number."""
    if any((v or "").strip().lower() in NULLS for v in values):
        return "has missing values"
    return None if numeric(values) is not None else "has non-numeric values"


def r6(m: Dict[str, Any]) -> Dict[str, Any]:
    """Round the float values of a metrics dict to 6 places."""
    return {k: round(v, 6) if isinstance(v, float) else v for k, v in m.items()}


def auc(y: List[int], s: List[float]) -> Optional[float]:
    """ROC AUC by the rank-sum (Mann-Whitney) method, ties get average ranks."""
    n1, n0 = sum(y), len(y) - sum(y)
    if n1 == 0 or n0 == 0:
        return None
    counts = Counter(s)
    rank, below = {}, 0
    for v in sorted(counts):  # tied scores share the average of their 1-based ranks
        rank[v], below = below + (counts[v] + 1) / 2, below + counts[v]
    pos_rank_sum = sum(rank[v] for v, label in zip(s, y) if label == 1)
    return (pos_rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0)


def classify(y: List[int], p: List[float], kind: str, threshold: float) -> Dict[str, Any]:
    """Binary metrics: confusion matrix, rates, AUC and probability scores."""
    m: Dict[str, Any] = {}
    if kind != "score":
        pred = [1 if v >= (0.5 if kind == "label" else threshold) else 0 for v in p]
        pairs = list(zip(y, pred))
        tp, fp, fn, tn = (pairs.count(cell) for cell in ((1, 1), (0, 1), (1, 0), (0, 0)))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        m.update(confusion={"tp": tp, "fp": fp, "fn": fn, "tn": tn},
                 accuracy=(tp + tn) / len(y), precision=prec, recall=rec,
                 f1=2 * prec * rec / (prec + rec) if prec + rec else 0.0,
                 specificity=tn / (tn + fp) if tn + fp else 0.0)
    if kind != "label":
        m["auc"] = auc(y, p)
    if kind == "probability":
        eps = 1e-15
        m["log_loss"] = -statistics.fmean(
            a * math.log(max(v, eps)) + (1 - a) * math.log(max(1 - v, eps)) for a, v in zip(y, p))
        m["brier"] = statistics.fmean((v - a) ** 2 for a, v in zip(y, p))
    return r6(m)


def regress(y: List[float], p: List[float]) -> Dict[str, Any]:
    """Regression metrics. MAPE skips rows where the actual is zero."""
    err = [b - a for a, b in zip(y, p)]
    mean_y = statistics.fmean(y)
    sst = sum((a - mean_y) ** 2 for a in y)
    nonzero = [(a, b) for a, b in zip(y, p) if a != 0]
    return r6({"mae": statistics.fmean(abs(e) for e in err),
            "rmse": math.sqrt(statistics.fmean(e ** 2 for e in err)),
            "r2": 1 - sum(e ** 2 for e in err) / sst if sst else None,
            "mape": statistics.fmean(abs((b - a) / a) for a, b in nonzero) if nonzero else None,
            "mape_rows_skipped": len(y) - len(nonzero), "bias": statistics.fmean(err)})


def evaluate(path: str, target: str, cols: Optional[List[str]], task: str, positive: Optional[str],
             threshold: float, folds: int, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Score every prediction column, run fold stability and readiness checks."""
    header, rows = load_csv(path)
    if target not in header:
        sys.exit(f"ERROR: target column '{target}' not in {path}. Columns: {', '.join(header)}")
    rows, total = [r for r in rows if (r.get(target) or "").strip().lower() not in NULLS], len(rows)
    if not rows:
        sys.exit(f"ERROR: every '{target}' value in {path} is missing")
    actual = [(r.get(target) or "").strip() for r in rows]
    auto = cols is None
    cols = [h for h in header if h != target] if auto else cols
    if [c for c in cols if c not in header] or not cols:
        sys.exit(f"ERROR: prediction column(s) not found: "
                 f"{', '.join(c for c in cols if c not in header) or 'none besides the target'}")
    skipped = {c: why for c in cols if (why := why_unusable([r.get(c) for r in rows]))}
    if skipped and (not auto or len(skipped) == len(cols)):
        sys.exit(("ERROR: no usable prediction column: " if auto else "ERROR: ")
                 + "; ".join(f"column '{c}' {why}" for c, why in skipped.items()))
    cols = [c for c in cols if c not in skipped]
    if folds == 1 or folds < 0 or folds > len(rows):
        sys.exit(f"ERROR: --folds must be 0 (off) or between 2 and the row count ({len(rows)})")
    labels = sorted(set(actual))
    if len(labels) < 2:
        sys.exit(f"ERROR: '{target}' has a single value ({labels[0]!r}); "
                 "metrics need at least two classes or values")
    if task == "auto":
        task = "classification" if len(labels) == 2 else "regression"
    if task == "classification":
        if len(labels) != 2:
            sys.exit(f"ERROR: binary classification needs 2 classes in '{target}', found {len(labels)}")
        pos = positive if positive is not None else ("1" if "1" in labels else labels[1])
        if pos not in labels:
            sys.exit(f"ERROR: positive class '{pos}' not among {labels}")
        y: List[Any] = [1 if a == pos else 0 for a in actual]
    else:
        y = numeric(actual) or sys.exit(f"ERROR: '{target}' must be numeric for regression")
    models: Dict[str, Any] = {}
    for c in cols:
        p: List[float] = numeric([r.get(c) for r in rows]) or []
        kind = ("regression" if task == "regression" else "label" if set(p) <= {0.0, 1.0}
                else "probability" if all(0 <= v <= 1 for v in p) else "score")
        score = (lambda a, b: classify(a, b, kind, threshold)) if task == "classification" else regress
        primary = "rmse" if task == "regression" else ("f1" if kind == "label" else "auc")
        res: Dict[str, Any] = {"kind": kind, "metrics": score(y, p), "primary_metric": primary}
        if folds >= 2:
            vals = [v for v in (score(y[f::folds], p[f::folds]).get(primary) for f in range(folds))
                    if v is not None]
            res["folds"] = r6({"k": folds, "metric": primary, "values": vals,
                               "mean": statistics.fmean(vals) if vals else None,
                               "std": statistics.stdev(vals) if len(vals) > 1 else None})
        models[c] = res
    cfg = config if config is not None else DEFAULT_CONFIG[task]
    known = [k for k in cfg if k in CHECKS or k == "max_fold_std"]
    for res in models.values():
        checks = []
        for key, limit in ((k, cfg[k]) for k in known):
            if isinstance(limit, bool) or not isinstance(limit, (int, float)):
                sys.exit(f"ERROR: threshold {key} must be a number, got {limit!r}")
            value = (res.get("folds", {}).get("std") if key == "max_fold_std"
                     else res["metrics"].get(CHECKS[key]))
            ok = None if value is None else (value >= limit if key.startswith("min_") else value <= limit)
            checks.append({"check": key, "limit": limit, "value": value, "pass": ok})
        res["checks"] = checks
        res["not_applicable"] = [ch["check"] for ch in checks if ch["pass"] is None]
        res["ready"] = all(m) if (m := [c["pass"] for c in checks if c["pass"] is not None]) else None
    ranked = sorted((n for n in models if models[n]["metrics"].get(models[n]["primary_metric"])
                     is not None), key=lambda n: models[n]["metrics"][models[n]["primary_metric"]],
                    reverse=task != "regression")
    is_cls = task == "classification"
    return {"input": path, "rows": len(rows), "rows_skipped_missing_actual": total - len(rows),
            "task": task, "target": target, "positive_class": pos if is_cls else None,
            "threshold": threshold if is_cls else None, "thresholds": cfg,
            "ignored_config_keys": [k for k in cfg if k not in known], "models": models,
            "skipped_columns": skipped, "best_model": ranked[0] if ranked else None,
            "note": "Verdicts use only the checks a model can be measured on. Offline check "
                    "only: latency, error rate and drift need serving metrics."}


def fmt_num(v: Any) -> str:
    """Format a metric value for the text table."""
    return "n/a" if v is None else f"{v:.4f}" if isinstance(v, float) else str(v)


def output(rep: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as a side-by-side text table."""
    if fmt == "json":
        print(json.dumps(rep, indent=2))
        return
    names = list(rep["models"])
    extra = f", positive class '{rep['positive_class']}'" if rep["positive_class"] else ""
    if rep["rows_skipped_missing_actual"]:
        extra += f", {rep['rows_skipped_missing_actual']} row(s) with no actual skipped"
    print(f"Model evaluation: {rep['input']} ({rep['rows']} rows, {rep['task']}{extra})\n")
    print(f"  {'metric':<18}" + "".join(f"{n:>14}" for n in names))
    print(f"  {'kind':<18}" + "".join(f"{rep['models'][n]['kind']:>14}" for n in names))
    keys = [k for k in ("accuracy", "precision", "recall", "f1", "specificity", "auc", "log_loss",
                        "brier", "mae", "rmse", "r2", "mape", "mape_rows_skipped", "bias")
            if any(k in rep["models"][n]["metrics"] for n in names)]
    for k in keys:
        print(f"  {k:<18}" + "".join(f"{fmt_num(rep['models'][n]['metrics'].get(k)):>14}" for n in names))
    for n in names:
        cm = rep["models"][n]["metrics"].get("confusion")
        if cm:
            print(f"\n  {n} confusion (threshold {rep['threshold']}): "
                  + "  ".join(f"{k.upper()} {v}" for k, v in cm.items()))
        fo = rep["models"][n].get("folds")
        if fo and fo["values"]:
            print(f"  {n} {fo['k']}-fold {fo['metric']}: mean {fmt_num(fo['mean'])}, std "
                  f"{fmt_num(fo['std'])} ({', '.join(f'{v:.3f}' for v in fo['values'])})")
    if rep["skipped_columns"]:
        print("\n  Skipped: " + "; ".join(f"'{c}' {w}" for c, w in rep["skipped_columns"].items()))
    print(f"\nBest by primary metric: {rep['best_model']}")
    print("\nReadiness (offline thresholds):")
    for n in names:
        res = rep["models"][n]
        detail = ", ".join(f"{c['check']} {fmt_num(c['value'])} vs {c['limit']} "
                           f"{'PASS' if c['pass'] else 'FAIL'}" for c in res["checks"]
                           if c["pass"] is not None)
        if res["not_applicable"]:
            detail += f"{'; ' if detail else ''}not applicable: {', '.join(res['not_applicable'])}"
            detail += "" if res["ready"] is not None else " (set a measurable one, e.g. min_f1)"
        verdict = {True: "READY", False: "NOT READY", None: "NO VERDICT"}[res["ready"]]
        print(f"  {n:<12} {verdict:<11} {detail or 'no thresholds set (pass --config)'}")
    if rep["ignored_config_keys"]:
        print(f"  Ignored (not measurable from predictions): {', '.join(rep['ignored_config_keys'])}")
    print(f"  {rep['note']}")


def main() -> None:
    """Parse arguments, evaluate, print, and optionally write the report."""
    p = argparse.ArgumentParser(description="Evaluate saved predictions: metrics, folds, readiness.")
    p.add_argument("--input", "-i", help="CSV with an actual column and prediction columns")
    p.add_argument("--target", "-t", default="actual", help="actual/label column (default actual)")
    p.add_argument("--predictions", "-p", help="comma-separated prediction columns (default: all usable)")
    p.add_argument("--task", choices=["auto", "classification", "regression"], default="auto",
                   help="auto: classification when the target has exactly 2 values")
    p.add_argument("--positive", help="positive class label (default 1, else the last sorted label)")
    p.add_argument("--threshold", type=float, default=0.5, help="probability cut-off (0.5)")
    p.add_argument("--folds", "-k", type=int, default=0, help="round-robin folds for stability")
    p.add_argument("--config", "-c", help="thresholds JSON, e.g. {\"min_auc\": 0.85}")
    p.add_argument("--output", "-o", help="directory to write evaluation_report.json into")
    p.add_argument("--force", action="store_true", help="overwrite an existing file in --output")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    p.add_argument("--example", action="store_true", help="print a sample predictions CSV and exit")
    args = p.parse_args()
    if args.example:
        print(EXAMPLE)
        return
    if not args.input:
        p.error("--input is required (or use --example)")
    config = None
    if args.config:
        try:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"ERROR: file not found: {args.config}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            sys.exit(f"ERROR: {args.config} is not valid JSON: {exc}")
        if not isinstance(config, dict):
            sys.exit(f"ERROR: {args.config} must hold a JSON object of thresholds")
    cols = [c.strip() for c in args.predictions.split(",")] if args.predictions else None
    target = Path(args.output) / "evaluation_report.json" if args.output else None
    if target and target.exists() and not args.force:
        sys.exit(f"ERROR: {target} already exists; pass --force to overwrite")
    try:
        rep = evaluate(args.input, args.target, cols, args.task, args.positive, args.threshold,
                       args.folds, config)
    except OverflowError:
        sys.exit(f"ERROR: {args.input} has values too large to score (overflow); rescale them first")
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
