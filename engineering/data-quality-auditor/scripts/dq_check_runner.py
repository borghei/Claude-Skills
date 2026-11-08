#!/usr/bin/env python3
"""
dq_check_runner.py — Run a DQ check suite against tabular data from CSV / JSON.

Stdlib only. Reads a check definition YAML + data file; emits pass/fail per check.
For live DB queries, integrate with your DB driver (out of scope for stdlib-only).

Check types: not_null, unique, accepted_values, matches_regex, between,
row_count_between, freshness, length_between, reference_exists.

Output: Markdown or JSON. Per-check status + actionable message.

Usage:
    python3 dq_check_runner.py --data orders.csv --checks orders_dq.yaml
    python3 dq_check_runner.py --data events.json --checks events_dq.yaml --format json
    python3 dq_check_runner.py --profile --data orders.csv

Checks file: YAML (block or flow lists) or JSON, with a top-level `checks:` list.
Exit codes: 0 all checks pass, 1 a check failed or errored, 2 bad input
(missing/unreadable file, unsupported format, no checks loaded).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


# Minimal YAML parser (same as other scripts)
def parse_yaml(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, line[indent:]))
    result, _ = _parse_block(lines, 0, 0)
    return result if isinstance(result, dict) else {}


def _parse_block(lines, idx, indent):
    if idx >= len(lines):
        return None, idx
    first_indent = lines[idx][0]
    if first_indent < indent:
        return None, idx
    first_line = lines[idx][1]
    if first_line.startswith("- "):
        return _parse_seq(lines, idx, first_indent)
    return _parse_map(lines, idx, first_indent)


def _parse_map(lines, idx, indent):
    out: dict[str, Any] = {}
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            idx += 1
            continue
        if ":" not in content:
            idx += 1
            continue
        key, _, rest = content.partition(":")
        key = key.strip().strip('"').strip("'")
        rest = rest.strip()
        if rest:
            out[key] = _scalar(rest)
            idx += 1
        else:
            idx += 1
            if idx < len(lines) and lines[idx][0] > indent:
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out[key] = value if value is not None else {}
            else:
                out[key] = {}
    return out, idx


def _parse_seq(lines, idx, indent):
    out: list[Any] = []
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if not content.startswith("- "):
            break
        rest = content[2:].strip()
        if not rest:
            idx += 1
            if idx < len(lines) and lines[idx][0] > indent:
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out.append(value if value is not None else {})
            else:
                out.append(None)
        elif ":" in rest:
            synth = [(indent + 2, rest)]
            j = idx + 1
            while j < len(lines) and lines[j][0] > indent:
                synth.append(lines[j])
                j += 1
            value, _ = _parse_map(synth, 0, indent + 2)
            out.append(value)
            idx = j
        else:
            out.append(_scalar(rest))
            idx += 1
    return out, idx


def _scalar(s: str):
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):  # YAML flow list: [a, b, "c"]
        return [_scalar(x) for x in s[1:-1].split(",") if x.strip()]
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "~", ""):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


# --- Data loading ---

def load_data(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif suffix == ".json":
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return [data]
    else:
        raise ValueError(f"Unsupported data format: {suffix}")


# --- Profile ---

def profile_data(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"row_count": 0, "columns": {}}
    columns: dict[str, dict[str, Any]] = {}
    keys = list(rows[0].keys())
    for k in keys:
        col_values = [r.get(k) for r in rows]
        non_null = [v for v in col_values if v not in (None, "", "null")]
        col = {
            "non_null_count": len(non_null),
            "null_count": len(col_values) - len(non_null),
            "null_rate": (len(col_values) - len(non_null)) / len(col_values) if col_values else 0,
            "distinct_count": len(set(map(str, non_null))),
            "sample_values": list({str(v) for v in non_null[:50]})[:5],
        }
        # numeric stats if possible
        try:
            numeric = [float(v) for v in non_null]
            col["min"] = min(numeric) if numeric else None
            col["max"] = max(numeric) if numeric else None
            col["mean"] = sum(numeric) / len(numeric) if numeric else None
        except (ValueError, TypeError):
            pass
        columns[k] = col
    return {"row_count": len(rows), "columns": columns}


# --- Checks ---

@dataclass
class CheckResult:
    check_id: str
    check_type: str
    column: str
    status: str  # pass / fail / warn / error
    value: Any
    threshold: Any
    message: str


def run_check(check: dict[str, Any], rows: list[dict[str, Any]]) -> CheckResult:
    cid = str(check.get("id") or check.get("name") or "")
    ctype = check.get("type", "")
    col = check.get("column", "")
    threshold = check.get("threshold")
    try:
        if ctype == "not_null":
            return _check_not_null(cid, col, rows, threshold)
        if ctype == "unique":
            return _check_unique(cid, col, rows)
        if ctype == "accepted_values":
            return _check_accepted_values(cid, col, rows, check.get("values", []))
        if ctype == "matches_regex":
            return _check_regex(cid, col, rows, check.get("regex", ".*"))
        if ctype == "between":
            return _check_between(cid, col, rows, check.get("min"), check.get("max"))
        if ctype == "row_count_between":
            return _check_row_count(cid, rows, check.get("min"), check.get("max"))
        if ctype == "freshness":
            return _check_freshness(cid, col, rows, check.get("max_age_min", 60), check.get("now"))
        if ctype == "length_between":
            return _check_length(cid, col, rows, check.get("min_len", 0), check.get("max_len", 10000))
        if ctype == "reference_exists":
            return _check_reference(cid, col, rows, check.get("reference_values", []))
        return CheckResult(cid, ctype, col, "error", None, None, f"Unknown check type: {ctype}")
    except Exception as e:
        return CheckResult(cid, ctype, col, "error", None, None, f"Exception: {e}")


def _check_not_null(cid: str, col: str, rows: list, threshold: float | None) -> CheckResult:
    if threshold is None:
        threshold = 0.0
    n_total = len(rows)
    if n_total == 0:
        return CheckResult(cid, "not_null", col, "pass", 0, threshold, "Empty table")
    n_null = sum(1 for r in rows if r.get(col) in (None, "", "null"))
    rate = n_null / n_total
    status = "pass" if rate <= threshold else "fail"
    return CheckResult(cid, "not_null", col, status, rate, threshold,
                       f"Null rate {rate:.4f} (threshold ≤ {threshold})")


def _check_unique(cid: str, col: str, rows: list) -> CheckResult:
    values = [str(r.get(col, "")) for r in rows]
    cnt = Counter(values)
    dupes = {v: c for v, c in cnt.items() if c > 1}
    status = "pass" if not dupes else "fail"
    return CheckResult(cid, "unique", col, status, len(dupes), 0,
                       f"{len(dupes)} duplicate values found" if dupes else "All unique")


def _check_accepted_values(cid: str, col: str, rows: list, accepted: list) -> CheckResult:
    accepted_set = set(map(str, accepted))
    invalid = [r.get(col) for r in rows if str(r.get(col, "")) not in accepted_set]
    status = "pass" if not invalid else "fail"
    return CheckResult(cid, "accepted_values", col, status, len(invalid), 0,
                       f"{len(invalid)} values not in accepted set")


def _check_regex(cid: str, col: str, rows: list, pattern: str) -> CheckResult:
    rx = re.compile(pattern)
    invalid = [r.get(col) for r in rows if not rx.match(str(r.get(col, "")))]
    status = "pass" if not invalid else "fail"
    return CheckResult(cid, "matches_regex", col, status, len(invalid), 0,
                       f"{len(invalid)} values don't match pattern")


def _check_between(cid: str, col: str, rows: list, min_v, max_v) -> CheckResult:
    out_of_range = 0
    for r in rows:
        try:
            v = float(r.get(col, ""))
            if (min_v is not None and v < min_v) or (max_v is not None and v > max_v):
                out_of_range += 1
        except (ValueError, TypeError):
            out_of_range += 1
    status = "pass" if not out_of_range else "fail"
    return CheckResult(cid, "between", col, status, out_of_range, 0,
                       f"{out_of_range} values outside [{min_v}, {max_v}]")


def _check_row_count(cid: str, rows: list, min_v, max_v) -> CheckResult:
    n = len(rows)
    bad = (min_v is not None and n < min_v) or (max_v is not None and n > max_v)
    return CheckResult(cid, "row_count_between", "", "fail" if bad else "pass", n, f"[{min_v}, {max_v}]",
                       f"Row count {n} {'outside expected range' if bad else 'in range'}")


def _check_freshness(cid: str, col: str, rows: list, max_age_min: int, now_iso: str | None) -> CheckResult:
    now = datetime.now(timezone.utc) if not now_iso else datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    max_ts = None
    for r in rows:
        v = r.get(col)
        if not v:
            continue
        try:
            if isinstance(v, (int, float)):
                ts = datetime.fromtimestamp(v / 1000 if v > 10**11 else v, tz=timezone.utc)
            else:
                ts = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            if not max_ts or ts > max_ts:
                max_ts = ts
        except ValueError:
            continue
    if not max_ts:
        return CheckResult(cid, "freshness", col, "error", None, max_age_min, "No valid timestamps found")
    age_min = (now - max_ts).total_seconds() / 60
    status = "pass" if age_min <= max_age_min else "fail"
    return CheckResult(cid, "freshness", col, status, age_min, max_age_min,
                       f"Max ts age {age_min:.1f}min (threshold ≤ {max_age_min}min)")


def _check_length(cid: str, col: str, rows: list, min_len: int, max_len: int) -> CheckResult:
    out_of_range = sum(1 for r in rows if not (min_len <= len(str(r.get(col, ""))) <= max_len))
    status = "pass" if not out_of_range else "fail"
    return CheckResult(cid, "length_between", col, status, out_of_range, 0,
                       f"{out_of_range} values outside length range")


def _check_reference(cid: str, col: str, rows: list, ref_values: list) -> CheckResult:
    ref_set = set(map(str, ref_values))
    missing = sum(1 for r in rows if str(r.get(col, "")) not in ref_set)
    status = "pass" if not missing else "fail"
    return CheckResult(cid, "reference_exists", col, status, missing, 0,
                       f"{missing} values don't have referenced match")


# --- Output ---

def render_markdown(results: list[CheckResult], profile: dict[str, Any] | None) -> str:
    out = ["# DQ Check Results", ""]
    if profile:
        out.append("## Profile")
        out.append("")
        out.append(f"**Row count:** {profile['row_count']}")
        out.append("")
        out.append("| Column | Non-null | Null rate | Distinct | Sample |")
        out.append("|--------|----------|-----------|----------|--------|")
        for col, info in profile.get("columns", {}).items():
            sample = ", ".join(str(s) for s in info.get("sample_values", []))[:60]
            out.append(f"| {col} | {info['non_null_count']} | {info['null_rate']:.3f} | {info['distinct_count']} | {sample} |")
        out.append("")
    if results:
        n = Counter(r.status for r in results)
        out += ["## Check Summary", "", f"- **Total**: {len(results)}", f"- **Passed**: {n['pass']}",
                f"- **Failed**: {n['fail']}", f"- **Errored**: {n['error']}", ""]
        out.append("## Check Details")
        out.append("")
        out.append("| ID | Type | Column | Status | Message |")
        out.append("|----|------|--------|--------|---------|")
        for r in results:
            emoji = {"pass": "✓", "fail": "✗", "warn": "!", "error": "?"}.get(r.status, "?")
            out.append(f"| {r.check_id} | {r.check_type} | {r.column} | {emoji} {r.status} | {r.message[:80]} |")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run DQ checks against tabular data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--data", help="Path to data file (CSV or JSON)")
    p.add_argument("--checks", help="Path to checks YAML")
    p.add_argument("--profile", action="store_true", help="Output dataset profile")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    if args.data:
        try:
            rows = load_data(Path(args.data))
        except (OSError, ValueError, json.JSONDecodeError) as e:
            print(f"error loading data: {e}", file=sys.stderr)
            return 2

    profile = profile_data(rows) if args.profile else None
    results: list[CheckResult] = []
    if args.checks:
        try:
            text = Path(args.checks).read_text()
            checks_doc = json.loads(text) if args.checks.lower().endswith(".json") else parse_yaml(text)
        except (OSError, ValueError) as e:
            print(f"error loading checks: {e}", file=sys.stderr)
            return 2
        checks = checks_doc.get("checks") if isinstance(checks_doc, dict) else None
        if not isinstance(checks, list) or not any(isinstance(c, dict) for c in checks):
            print(f"error: no checks loaded from {args.checks} (expected a top-level 'checks' list)", file=sys.stderr)
            return 2
        for idx, check in enumerate(c for c in checks if isinstance(c, dict)):
            check.setdefault("id", check.get("name") or f"check_{idx + 1}")
            results.append(run_check(check, rows))
    elif not args.profile:
        print("error: pass --checks <file> and/or --profile", file=sys.stderr)
        return 2

    if args.format == "json":
        out = json.dumps(
            {"profile": profile, "results": [asdict(r) for r in results]},
            indent=2,
            default=str,
        )
    else:
        out = render_markdown(results, profile)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if any(r.status in ("fail", "error") for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
