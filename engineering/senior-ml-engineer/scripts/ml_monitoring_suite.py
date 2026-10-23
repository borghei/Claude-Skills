#!/usr/bin/env python3
"""Detect data, prediction and performance drift between a baseline and a current CSV.

Per feature: Population Stability Index (quantile bins from the baseline for
numeric columns, category shares for categorical ones), a two-sample
Kolmogorov-Smirnov statistic with asymptotic p-value for numeric columns, and
the change in missing rate. With --label-col and --prediction-col it also
compares accuracy (classification) or MAE (regression). Each check maps to
OK / WARN / ALERT. Optionally writes drift_report.json and alert_rules.yaml.

Exit codes: 0 no alert-level drift, 1 alert-level drift (CI gate, see
--fail-on), 2 bad input.

Usage:
    python ml_monitoring_suite.py --baseline base.csv --current cur.csv [--output monitoring/]
"""

import argparse
import bisect
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULTS: Dict[str, float] = {
    "psi_warn": 0.1, "psi_alert": 0.25, "ks_pvalue": 0.05, "ks_warn": 0.1, "ks_alert": 0.2,
    "missing_warn": 0.05, "missing_alert": 0.10, "accuracy_drop_warn": 0.02,
    "accuracy_drop_alert": 0.05, "mae_increase_warn": 0.10, "mae_increase_alert": 0.25,
    "categorical_max_unique": 10, "bins": 10, "categorical_top_n": 20, "id_like_unique_ratio": 0.9,
    "ks_min_samples": 50,
}
INT_KEYS = {"categorical_max_unique", "bins", "categorical_top_n", "ks_min_samples"}
MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,62}")
MISSING = {"", "na", "n/a", "nan", "null", "none"}
LEVELS = ["OK", "WARN", "ALERT"]
EPS = 1e-4


def load_csv(path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Read a CSV with a header row; reject rows whose field count differs from the header."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header or len(set(header)) != len(header):
            raise ValueError(f"{path} has no header row or repeats a column name")
        rows = []
        for rec in reader:
            if not rec:
                continue
            if len(rec) != len(header):
                raise ValueError(f"{path} line {reader.line_num}: {len(rec)} fields, header has {len(header)}")
            rows.append(dict(zip(header, rec)))
        if not rows:
            raise ValueError(f"{path} has no data rows")
        return header, rows


def to_float(v: str) -> Optional[float]:
    """Parse a float, returning None for missing or non-numeric values."""
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except ValueError:
        return None


def is_missing(v: Optional[str]) -> bool:
    """True when a cell counts as missing."""
    return v is None or v.strip().lower() in MISSING


def psi(base: List[float], cur: List[float]) -> float:
    """PSI = sum((c - b) * ln(c / b)) over bins, with EPS smoothing for empty bins."""
    return sum((c - b) * math.log(c / b) for b, c in zip(base, cur))


def shares(counts: List[int]) -> List[float]:
    """Turn bin counts into smoothed proportions."""
    total = sum(counts) or 1
    return [max(c / total, EPS) for c in counts]


def numeric_psi(base: List[float], cur: List[float], bins: int) -> Tuple[float, int]:
    """PSI with bin edges at baseline quantiles (duplicate edges merged); returns (psi, bins used)."""
    s = sorted(base)
    edges = sorted({s[min(len(s) - 1, (i * len(s)) // bins)] for i in range(1, bins)})
    return psi(shares(_bin_counts(base, edges)), shares(_bin_counts(cur, edges))), len(edges) + 1


def _bin_counts(xs: List[float], edges: List[float]) -> List[int]:
    """Count values per interval (-inf, e1], (e1, e2], ..., (ek, inf)."""
    counts = [0] * (len(edges) + 1)
    for x in xs:
        counts[bisect.bisect_left(edges, x)] += 1
    return counts


def categorical_psi(base: List[str], cur: List[str], top_n: int) -> Tuple[float, float]:
    """PSI over the baseline's top_n categories plus __other__ and __unseen__ buckets.

    Bucketing keeps PSI meaningful for high-cardinality columns: values never seen in the
    baseline land in __unseen__, so disjoint distributions give a large PSI instead of
    spreading over thousands of near-empty bins. Returns (psi, share of current unseen)."""
    bc, cc = Counter(base), Counter(cur)
    top = [c for c, _ in sorted(bc.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]]
    def bucket(counts: Counter) -> List[int]:
        known = sum(counts[c] for c in top)
        unseen = sum(n for c, n in counts.items() if c not in bc)
        return [counts[c] for c in top] + [sum(counts.values()) - known - unseen, unseen]
    unseen_share = bucket(cc)[-1] / max(len(cur), 1)
    return psi(shares(bucket(bc)), shares(bucket(cc))), unseen_share


def ks_2samp(a: List[float], b: List[float]) -> Tuple[float, float]:
    """Two-sample KS statistic D and asymptotic p-value (Kolmogorov distribution)."""
    sa, sb, n, m = sorted(a), sorted(b), len(a), len(b)
    d = max(abs(bisect.bisect_right(sa, v) / n - bisect.bisect_right(sb, v) / m) for v in set(sa) | set(sb))
    en = math.sqrt(n * m / (n + m))
    lam = (en + 0.12 + 0.11 / en) * d
    total, sign, prev = 0.0, 1.0, 0.0
    for j in range(1, 101):
        term = sign * 2.0 * math.exp(-2.0 * j * j * lam * lam)
        total += term
        if abs(term) <= 1e-3 * prev or abs(term) <= 1e-8 * total:
            return d, min(max(total, 0.0), 1.0)
        sign, prev = -sign, abs(term)
    return d, 1.0


def level(value: float, warn: float, alert: float) -> str:
    """Map a value to OK/WARN/ALERT against two thresholds."""
    return "ALERT" if value >= alert else "WARN" if value >= warn else "OK"


def worst(*levels: str) -> str:
    """Highest severity among levels."""
    return max(levels, key=LEVELS.index) if levels else "OK"


def analyze_feature(col: str, base: List[str], cur: List[str], t: Dict[str, float]) -> Dict[str, Any]:
    """Compute PSI, KS (numeric) and missing-rate change for one column."""
    b_present = [v.strip() for v in base if not is_missing(v)]
    c_present = [v.strip() for v in cur if not is_missing(v)]
    nums = [to_float(v) for v in b_present]
    numeric = bool(b_present) and None not in nums and len(set(nums)) > t["categorical_max_unique"]
    res: Dict[str, Any] = {"feature": col, "type": "numeric" if numeric else "categorical"}
    if numeric:
        c_nums = [to_float(v) for v in c_present]
        bad = sum(x is None for x in c_nums)
        c_vals = [x for x in c_nums if x is not None]
        if bad:
            res["non_numeric_in_current"] = bad
        miss_c = (len(cur) - len(c_vals)) / len(cur)
    else:
        miss_c = (len(cur) - len(c_present)) / len(cur)
    miss_b = (len(base) - len(b_present)) / len(base)
    res["missing_rate"] = {"baseline": round(miss_b, 4), "current": round(miss_c, 4),
                           "change": round(miss_c - miss_b, 4)}
    checks = {"missing": level(abs(miss_c - miss_b), t["missing_warn"], t["missing_alert"])}
    c_has = bool(c_vals) if numeric else bool(c_present)
    if not b_present or not c_has:
        both = not b_present and not c_has
        res.update(psi=None, status="OK" if both else checks["missing"], flags=[] if both else ["missing"],
                   note="all values missing in both files" if both else "no non-missing values on one side")
        return res
    distinct = len(set(b_present))
    if not numeric and distinct > t["categorical_top_n"] and distinct / len(b_present) >= t["id_like_unique_ratio"]:
        res.update(type="id-like", psi=None, flags=[k for k, v in checks.items() if v != "OK"],
                   status=checks["missing"], note=f"{distinct} distinct values in {len(b_present)} rows; "
                   "distribution checks skipped (exclude it or bucket it upstream)")
        return res
    if numeric:
        p, n_bins = numeric_psi(nums, c_vals, int(t["bins"]))
        d, pv = ks_2samp(nums, c_vals)
        res["ks"] = {"statistic": round(d, 4), "p_value": round(pv, 6)}
        if min(len(nums), len(c_vals)) < t["ks_min_samples"]:
            res["ks"]["note"] = "small sample: asymptotic p-value is approximate"
        checks["ks"] = level(d, t["ks_warn"], t["ks_alert"]) if pv < t["ks_pvalue"] else "OK"
    else:
        p, unseen = categorical_psi(b_present, c_present, int(t["categorical_top_n"]))
        n_bins = min(distinct, int(t["categorical_top_n"])) + 1
        if unseen:
            res["unseen_share"] = round(unseen, 4)
            res["new_categories"] = sorted(set(c_present) - set(b_present))[:10]
    res["psi"] = round(p, 4)
    floor = (n_bins - 1) * (1 / len(b_present) + 1 / (len(c_vals) if numeric else len(c_present)))
    if floor > t["psi_warn"] / 2:
        res["psi_note"] = (f"expected PSI from sampling noise alone is about {floor:.3f} at this size; "
                           "use fewer bins or more rows before trusting the status")
    checks["psi"] = level(p, t["psi_warn"], t["psi_alert"])
    res["flags"] = [k for k in ("psi", "ks", "missing") if checks.get(k, "OK") != "OK"]
    res["status"] = worst(*checks.values())
    return res


def analyze_performance(base: List[Dict[str, str]], cur: List[Dict[str, str]], pred: str, label: str,
                        t: Dict[str, float]) -> Dict[str, Any]:
    """Compare accuracy (categorical labels) or MAE (numeric labels) between the two sets."""
    def pairs(rows: List[Dict[str, str]]) -> List[Tuple[str, str]]:
        return [(r[pred].strip(), r[label].strip()) for r in rows
                if not is_missing(r.get(pred)) and not is_missing(r.get(label))]
    bp, cp = pairs(base), pairs(cur)
    if not bp or not cp:
        return {"status": "WARN", "note": "no rows with both prediction and label"}
    labels = [to_float(y) for _, y in bp]
    regression = None not in labels and len(set(labels)) > t["categorical_max_unique"]
    if regression:
        def mae(ps: List[Tuple[str, str]]) -> float:
            vals = [(to_float(p), to_float(y)) for p, y in ps]
            vals = [(p, y) for p, y in vals if p is not None and y is not None]
            return sum(abs(p - y) for p, y in vals) / max(len(vals), 1)
        b, c = mae(bp), mae(cp)
        rel = (c - b) / b if b else (0.0 if c == 0 else float("inf"))
        return {"metric": "mae", "baseline": round(b, 4), "current": round(c, 4), "relative_change": round(rel, 4),
                "status": level(rel, t["mae_increase_warn"], t["mae_increase_alert"])}
    same = lambda p, y: p == y or (to_float(p) is not None and to_float(p) == to_float(y))
    acc = lambda ps: sum(same(p, y) for p, y in ps) / len(ps)
    b, c = acc(bp), acc(cp)
    return {"metric": "accuracy", "baseline": round(b, 4), "current": round(c, 4), "drop": round(b - c, 4),
            "status": level(b - c, t["accuracy_drop_warn"], t["accuracy_drop_alert"])}


def alert_rules(report: Dict[str, Any], model: str, t: Dict[str, float]) -> str:
    """Prometheus-style rule YAML for flagged features; assumes you export the named gauges."""
    lines = ["groups:", f"  - name: {model}-drift", "    rules:"]
    def rule(name: str, expr: str, sev: str, summary: str) -> None:
        lines.extend([f"      - alert: {name}", f"        expr: {json.dumps(expr)}", "        for: 1h",
                      "        labels:", f"          severity: {sev}", "        annotations:",
                      f"          summary: {json.dumps(summary)}"])
    for f in report["features"]:
        if f["status"] == "OK":
            continue
        feat = f["feature"].replace("\\", "\\\\").replace('"', '\\"')
        sel = f'{{model="{model}",feature="{feat}"}}'
        tag = "".join(ch if ch.isalnum() else "_" for ch in f["feature"])
        for sev, key in (("warning", "psi_warn"), ("critical", "psi_alert")):
            if not {"psi", "ks"} & set(f.get("flags", [])):
                break
            rule(f"FeatureDrift_{tag}_{sev}", f"feature_psi{sel} > {t[key]}", sev,
                 f"PSI for {f['feature']} above {t[key]} (observed {f.get('psi')} at analysis time)")
        if "missing" in f.get("flags", []) and f["missing_rate"]["change"] > 0:
            rule(f"FeatureMissing_{tag}", f"feature_missing_rate{sel} > {f['missing_rate']['baseline'] + t['missing_warn']:.4f}",
                 "warning", f"Missing rate for {f['feature']} rose to {f['missing_rate']['current']}")
    perf = report.get("performance")
    if perf and perf.get("status") not in (None, "OK") and "metric" in perf:
        op, limit = ("<", perf["baseline"] - t["accuracy_drop_alert"]) if perf["metric"] == "accuracy" \
            else (">", perf["baseline"] * (1 + t["mae_increase_alert"]))
        rule("ModelPerformanceDrift", f'model_{perf["metric"]}{{model="{model}"}} {op} {limit:.4f}', "critical",
             f"{perf['metric']} moved from {perf['baseline']} to {perf['current']}")
    if len(lines) == 3:
        lines[-1] = "    rules: []"
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> Dict[str, Any]:
    """Load both CSVs, analyze every shared column and assemble the report."""
    t = dict(DEFAULTS)
    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
        if not isinstance(cfg, dict):
            raise ValueError("config must be a JSON object of threshold names to numbers (see --example)")
        unknown = set(cfg) - set(DEFAULTS)
        if unknown:
            raise ValueError(f"unknown threshold keys in config: {', '.join(sorted(unknown))}")
        for k, v in cfg.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or (k in INT_KEYS and v != int(v)):
                raise ValueError(f"config {k} must be a non-negative {'integer' if k in INT_KEYS else 'number'}, got {v!r}")
            t[k] = int(v) if k in INT_KEYS else float(v)
    if args.bins:
        t["bins"] = args.bins
    for a, b in (("psi_warn", "psi_alert"), ("ks_warn", "ks_alert"), ("missing_warn", "missing_alert"),
                 ("accuracy_drop_warn", "accuracy_drop_alert"), ("mae_increase_warn", "mae_increase_alert")):
        if t[a] > t[b]:
            raise ValueError(f"config {a} ({t[a]}) must not exceed {b} ({t[b]})")
    if t["bins"] < 2 or t["categorical_top_n"] < 1:
        raise ValueError("bins must be at least 2 and categorical_top_n at least 1")
    bcols, brows = load_csv(args.baseline)
    ccols, crows = load_csv(args.current)
    skip = {c.strip() for c in (args.exclude or "").split(",") if c.strip()} | {args.label_col}
    for col in (args.prediction_col, args.label_col):
        if col and (col not in bcols or col not in ccols):
            raise ValueError(f"column '{col}' is not in both CSVs")
    features = [analyze_feature(c, [r[c] for r in brows], [r[c] for r in crows], t)
                for c in bcols if c in ccols and c not in skip]
    dropped = [{"feature": c, "status": "ALERT", "note": "column missing from current data", "psi": None,
                "flags": ["missing"],
                "missing_rate": {"baseline": 0, "current": 1, "change": 1}}
               for c in bcols if c not in ccols and c not in skip]
    features += dropped
    report: Dict[str, Any] = {"baseline_rows": len(brows), "current_rows": len(crows), "thresholds": t,
                              "features": features, "new_columns": [c for c in ccols if c not in bcols]}
    if args.prediction_col and args.label_col:
        report["performance"] = analyze_performance(brows, crows, args.prediction_col, args.label_col, t)
    statuses = [f["status"] for f in features] + [report.get("performance", {}).get("status", "OK")]
    report["summary"] = {lv: statuses.count(lv) for lv in LEVELS}
    report["status"] = worst(*statuses)
    if args.output:
        out = Path(args.output)
        files = {"drift_report.json": json.dumps(report, indent=2) + "\n",
                 "alert_rules.yaml": alert_rules(report, args.model_name, t)}
        existing = [n for n in files if (out / n).exists()]
        if existing and not args.force:
            raise FileExistsError(f"{out} already has {', '.join(existing)}; pass --force to overwrite")
        out.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (out / name).write_text(text, encoding="utf-8")
        report["written"] = [str(out / n) for n in files]
    return report


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as a readable table."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Drift report: baseline {report['baseline_rows']} rows, current {report['current_rows']} rows")
    print(f"{'feature':<20} {'type':<12} {'PSI':>7} {'KS D':>7} {'KS p':>9} {'miss chg':>9}  status")
    for f in report["features"]:
        ks = f.get("ks") or {}
        fmt_n = lambda v, spec: format(v, spec) if isinstance(v, (int, float)) else "-"
        print(f"{f['feature']:<20} {f.get('type', '-'):<12} {fmt_n(f.get('psi'), '7.4f'):>7} "
              f"{fmt_n(ks.get('statistic'), '7.4f'):>7} {fmt_n(ks.get('p_value'), '9.4g'):>9} "
              f"{f['missing_rate']['change']:>+9.3f}  {f['status']}")
    for f in report["features"]:
        for note in (f.get("note"), f.get("psi_note"), (f.get("ks") or {}).get("note")):
            if note:
                print(f"  note: {f['feature']}: {note}")
    perf = report.get("performance")
    if perf:
        print(f"Performance: {perf.get('metric', '-')} baseline {perf.get('baseline')} -> current "
              f"{perf.get('current')}  {perf['status']}" + (f" ({perf['note']})" if "note" in perf else ""))
    if report["new_columns"]:
        print(f"New columns in current (not checked): {', '.join(report['new_columns'])}")
    s = report["summary"]
    print(f"Overall: {report['status']} (OK {s['OK']}, WARN {s['WARN']}, ALERT {s['ALERT']})")
    for path in report.get("written", []):
        print(f"wrote {path}")


def main() -> None:
    """Parse arguments, run the analysis and exit with the gate code."""
    ap = argparse.ArgumentParser(description="Feature, prediction and performance drift between a baseline "
                                 "and a current CSV (PSI, KS, missing rate, accuracy/MAE).")
    ap.add_argument("--baseline", "-b", help="reference CSV (training or a stable production window)")
    ap.add_argument("--current", "-c", help="CSV to compare against the baseline")
    ap.add_argument("--prediction-col", help="model output column (also checked for prediction drift)")
    ap.add_argument("--label-col", help="ground-truth column; with --prediction-col enables performance drift")
    ap.add_argument("--exclude", help="comma-separated columns to skip (ids, timestamps)")
    ap.add_argument("--bins", type=int, help="quantile bins for numeric PSI (default 10)")
    ap.add_argument("--config", help="JSON file overriding thresholds (see --example)")
    ap.add_argument("--output", "-o", help="directory for drift_report.json and alert_rules.yaml")
    ap.add_argument("--model-name", default="model", help="model label used in alert rules (default model)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files in --output")
    ap.add_argument("--fail-on", choices=["alert", "warn", "never"], default="alert",
                    help="exit 1 when the overall status reaches this level (default alert)")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="report format (default text)")
    ap.add_argument("--example", action="store_true", help="print a sample threshold config and exit")
    args = ap.parse_args()
    if args.example:
        print(json.dumps(DEFAULTS, indent=2))
        return
    if not args.baseline or not args.current:
        ap.error("--baseline and --current are required (or use --example)")
    if args.bins is not None and args.bins < 2:
        ap.error("--bins must be at least 2")
    if not MODEL_RE.fullmatch(args.model_name):
        ap.error("--model-name must be 1-63 characters of letters, digits, '.', '_' or '-'")
    try:
        report = run(args)
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: config is not valid JSON ({exc.msg} at line {exc.lineno})", file=sys.stderr)
        sys.exit(2)
    except (ValueError, TypeError, AttributeError, KeyError, csv.Error, UnicodeDecodeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    gate = {"alert": ["ALERT"], "warn": ["WARN", "ALERT"], "never": []}[args.fail_on]
    sys.exit(1 if report["status"] in gate else 0)


if __name__ == "__main__":
    main()
