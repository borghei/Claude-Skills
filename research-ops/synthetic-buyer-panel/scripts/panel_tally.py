#!/usr/bin/env python3
"""
panel_tally.py — Validate and tally the answers from a synthetic buyer panel.

Reads the cards dealt by panel_deal.py and the answers each buyer agent wrote,
rejects answers that break the schema (unknown buyer, bad decision, price points
out of order), and reports the buy rate overall and by segment and behaviour,
why people pass, what would flip a no, and a price corridor from the four price
points. It also reports the panel's own reliability: coverage, invalid share,
answer diversity and an agreeableness warning.

The tally never fills in a missing answer. A buyer with no valid answer is
counted as missing and lowers coverage.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 panel_tally.py --cards cards.json --answers answers.json
    python3 panel_tally.py --cards cards.json --answers panel/answers/ --format json

--answers takes a JSON list of answer objects or a directory of *.json files,
one answer per file. --cards takes cards.json or the JSON report of panel_deal.py.

Exit codes: 0 panel is readable, 1 a reliability check fails, 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REASON_CODES = {"price", "access", "trust", "need", "habit", "alternative", "other"}
PRICE_KEYS = ("too_cheap", "bargain", "getting_expensive", "too_expensive")
MIN_VALID = 20
MAX_BAD_SHARE = 0.10
AGREEABLE_WARN = 0.60
DUPLICATE_WARN = 0.30
METHOD_NOTE = ("Simulated buyers from one language model. Rates are directional and "
               "lean agreeable: read the buy rate as a ceiling, not a forecast. Price "
               "corridor = median 'bargain' to median 'getting expensive'.")


class InputError(ValueError):
    """Raised when an input cannot be read at all."""


def _load_json(path: Path) -> Any:
    """Read one JSON file, mapping failures to InputError."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"{path} is not valid JSON: {exc}") from exc


def load_cards(path: str) -> dict[str, dict[str, Any]]:
    """Load cards from cards.json or a panel_deal.py JSON report."""
    data = _load_json(Path(path))
    if isinstance(data, dict):
        data = data.get("cards")
    if not isinstance(data, list) or not data:
        raise InputError("cards file holds no cards")
    if not all(isinstance(c, dict) and "id" in c for c in data):
        raise InputError("every card needs an id")
    return {c["id"]: c for c in data}


def load_answers(path: str) -> list[Any]:
    """Load answers from a JSON list or a directory of one-answer files."""
    p = Path(path)
    if p.is_dir():
        return [_load_json(f) for f in sorted(p.glob("*.json"))]
    data = _load_json(p)
    if not isinstance(data, list):
        raise InputError("answers file must hold a JSON list")
    return data


def validate(answer: Any, cards: dict[str, Any]) -> str | None:
    """Return the reason an answer is invalid, or None if it is usable."""
    if not isinstance(answer, dict):
        return "not a JSON object"
    bid = answer.get("buyer_id")
    if not isinstance(bid, (str, int)) or isinstance(bid, bool) or bid not in cards:
        return f"unknown buyer_id {answer.get('buyer_id')!r}"
    if answer.get("decision") not in ("buy", "pass"):
        return f"decision {answer.get('decision')!r} is not buy or pass"
    units = answer.get("units_first_month")
    if not isinstance(units, int) or isinstance(units, bool) or units < 0:
        return "units_first_month must be a whole number"
    if answer.get("reason_code") not in REASON_CODES:
        return f"reason_code {answer.get('reason_code')!r} unknown"
    for key in ("reason", "main_objection", "would_change_mind"):
        if not isinstance(answer.get(key), str) or not answer[key].strip():
            return f"{key} is empty"
    pp = answer.get("price_points")
    if not isinstance(pp, dict) or not all(isinstance(pp.get(k), (int, float)) for k in PRICE_KEYS):
        return "price_points needs four numbers"
    values = [pp[k] for k in PRICE_KEYS]
    if any(a > b for a, b in zip(values, values[1:])):
        return "price points out of order (too cheap <= bargain <= expensive <= too expensive)"
    return None


def _norm(text: str) -> str:
    """Normalise free text for counting repeats."""
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


def _rates(valid: list[dict[str, Any]], cards: dict[str, Any], field: str,
           overall: float) -> list[dict[str, Any]]:
    """Buy rate per value of a card field, with lift against the overall rate."""
    groups: dict[str, list[int]] = defaultdict(list)
    for a in valid:
        groups[cards[a["buyer_id"]][field]].append(1 if a["decision"] == "buy" else 0)
    rows = []
    for name, hits in sorted(groups.items()):
        rate = sum(hits) / len(hits)
        rows.append({"group": name, "n": len(hits), "buy_rate": round(rate, 3),
                     "lift_pts": round((rate - overall) * 100, 1)})
    return sorted(rows, key=lambda r: -r["buy_rate"])


def tally(cards: dict[str, Any], answers: list[Any]) -> dict[str, Any]:
    """Validate every answer and build the panel report."""
    valid, invalid, seen = [], [], set()
    for a in answers:
        problem = validate(a, cards)
        if problem is None and a["buyer_id"] in seen:
            problem = "duplicate answer for this buyer"
        if problem:
            invalid.append({"buyer_id": a.get("buyer_id") if isinstance(a, dict) else None,
                            "problem": problem})
        else:
            seen.add(a["buyer_id"])
            valid.append(a)
    missing = sorted(set(cards) - seen)
    n_valid = len(valid)
    buyers = [a for a in valid if a["decision"] == "buy"]
    passers = [a for a in valid if a["decision"] == "pass"]
    rate = len(buyers) / n_valid if n_valid else 0.0
    reasons = Counter(a["reason_code"] for a in passers)
    flips = Counter(_norm(a["would_change_mind"]) for a in passers)
    objections = Counter(_norm(a["main_objection"]) for a in valid)
    quotes: dict[str, str] = {}
    for a in passers:
        quotes.setdefault(a["reason_code"], a["reason"])
    corridor = {}
    if valid:
        for k in PRICE_KEYS:
            corridor[k] = round(statistics.median(a["price_points"][k] for a in valid), 2)
    texts = [_norm(a["reason"]) for a in valid]
    dup_share = (1 - len(set(texts)) / len(texts)) if texts else 0.0
    bad_share = (len(invalid) + len(missing)) / len(cards)

    findings: list[dict[str, str]] = []
    if n_valid < MIN_VALID:
        findings.append({"severity": "fail", "message":
                         f"only {n_valid} valid answers; at least {MIN_VALID} are needed to read rates"})
    if bad_share > MAX_BAD_SHARE:
        findings.append({"severity": "fail", "message":
                         f"{bad_share:.0%} of buyers have no valid answer; re-run them, never fill in"})
    if rate > AGREEABLE_WARN:
        findings.append({"severity": "warn", "message":
                         f"buy rate {rate:.0%} is suspiciously high; check the brief and the pitch for hype"})
    if dup_share > DUPLICATE_WARN:
        findings.append({"severity": "warn", "message":
                         f"{dup_share:.0%} of reasons are word-for-word repeats; buyers are not differentiated"})
    if n_valid and not passers:
        findings.append({"severity": "warn", "message": "nobody passed; the panel surfaced no objections"})
    return {
        "panel_size": len(cards), "valid": n_valid, "invalid": invalid, "missing": missing,
        "buy": len(buyers), "pass": len(passers), "buy_rate": round(rate, 3),
        "first_month_units_per_buyer": round(
            statistics.mean(a["units_first_month"] for a in buyers), 2) if buyers else 0.0,
        "by_segment": _rates(valid, cards, "segment", rate),
        "by_behaviour": _rates(valid, cards, "behaviour", rate),
        "pass_reasons": [{"code": c, "count": n, "example": quotes.get(c, "")}
                         for c, n in reasons.most_common()],
        "top_flips": [{"answer": t, "count": n} for t, n in flips.most_common(5)],
        "top_objections": [{"objection": t, "count": n} for t, n in objections.most_common(5)],
        "price_points_median": corridor,
        "price_corridor": [corridor.get("bargain"), corridor.get("getting_expensive")],
        "duplicate_reason_share": round(dup_share, 3),
        "findings": findings,
        "fail_count": sum(1 for f in findings if f["severity"] == "fail"),
        "method_note": METHOD_NOTE,
    }


def render_text(r: dict[str, Any]) -> str:
    """Render the tally for a person."""
    lines = [f"Panel tally: {r['buy']} buy / {r['pass']} pass of {r['valid']} valid "
             f"(panel {r['panel_size']}, {len(r['invalid'])} invalid, {len(r['missing'])} missing)",
             f"Buy rate: {r['buy_rate']:.0%} (ceiling, not forecast)   "
             f"first-month units per buyer: {r['first_month_units_per_buyer']}", ""]
    for title, key in (("By segment", "by_segment"), ("By behaviour", "by_behaviour")):
        lines.append(f"{title}:")
        lines += [f"  {row['group']:<26} n={row['n']:<3} buy {row['buy_rate']:>5.0%}  "
                  f"({row['lift_pts']:+.0f} pts)" for row in r[key]]
        lines.append("")
    lines.append("Why they pass:")
    lines += [f"  {p['code']:<12} {p['count']:>3}  e.g. \"{p['example']}\"" for p in r["pass_reasons"]]
    lines += ["", "What would flip a no:"]
    lines += [f"  {f['count']:>3}  {f['answer']}" for f in r["top_flips"]]
    pp = r["price_points_median"]
    if pp:
        lines += ["", "Median price points: " + ", ".join(f"{k} {v}" for k, v in pp.items()),
                  f"Price corridor: {r['price_corridor'][0]} to {r['price_corridor'][1]}"]
    if r["invalid"]:
        lines += ["", "Invalid answers:"]
        lines += [f"  {i['buyer_id']}: {i['problem']}" for i in r["invalid"]]
    lines += ["", f"Findings: {r['fail_count']} fail, {len(r['findings']) - r['fail_count']} warn"]
    lines += [f"  [{f['severity'].upper():4}] {f['message']}" for f in r["findings"]]
    lines += ["", f"Method: {r['method_note']}"]
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and tally synthetic buyer panel answers.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--cards", required=True, help="cards.json or panel_deal.py JSON report")
    parser.add_argument("--answers", required=True, help="JSON list of answers or a directory of answer files")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()
    try:
        report = tally(load_cards(args.cards), load_answers(args.answers))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    return 1 if report["fail_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
