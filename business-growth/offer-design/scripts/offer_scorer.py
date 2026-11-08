#!/usr/bin/env python3
"""
offer_scorer.py — Score an offer before it goes in front of buyers: its
perceived value, whether every buyer obstacle is answered, whether each
component earns its place, whether the guarantee is affordable, and whether the
urgency is real.

The offer is described as the buyer's obstacles on the way to the result they
want, and the components that remove them. Each component has a value to the
buyer and a cost to deliver. The tool reports:

  value score   0-100 from four drivers: size of the outcome, the buyer's
                belief they will get it, time to the result, effort asked
                score = 100 * (outcome/10 * belief/10) * (1 - 0.6 * friction)
                friction = mean(time penalty, effort/10);
                time penalty = log(1 + days) / log(366), capped at 1
  stack ratio   total buyer value of all components / price
  coverage      share of listed obstacles answered by at least one component
  efficiency    buyer value / delivery cost per component
  contribution  price - core cost - component costs - expected guarantee cost

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 offer_scorer.py --input offer.json
    python3 offer_scorer.py --input offer.json --format json

Exit codes: 0 no fail finding, 1 at least one fail finding, 2 bad input.

Input schema (see assets/sample_offer.json):
{
  "offer_name": str, "currency": str, "price": float, "core_unit_cost": float,
  "drivers": {"outcome": 1-10, "belief": 1-10, "days_to_result": int, "effort": 1-10},
  "proof": [str],
  "obstacles": [{"id": str, "text": str}],
  "components": [{"name": str, "kind": "core"|"bonus", "solves": [obstacle ids],
                  "buyer_value": float, "delivery_cost": float}],
  "guarantee": {"type": "none"|"conditional"|"unconditional"|"outcome",
                "terms": str, "expected_claim_rate": 0-1},
  "urgency": {"type": "none"|"deadline"|"capacity"|"cohort"|"seasonal",
              "reason": str, "verifiable": bool},
  "headline": str
}
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

GUARANTEES = ("none", "conditional", "unconditional", "outcome")
URGENCY = ("none", "deadline", "capacity", "cohort", "seasonal")
STACK_TARGET = 3.0          # buyers should see at least 3x the price in value
EFFICIENCY_TRIM = 3.0       # a component worth under 3x its cost is a trim candidate
COVERAGE_FAIL = 0.6
MARGIN_WARN = 0.20
HEADLINE_MAX_WORDS = 12


class InputError(ValueError):
    """Raised when the offer file is structurally unusable."""


def _score(value: Any, name: str) -> float:
    """Validate a 1-10 driver score."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 1 <= value <= 10:
        raise InputError(f"drivers.{name} must be a number from 1 to 10")
    return float(value)


def load(offer: Any) -> dict[str, Any]:
    """Validate the offer and return it with normalised fields."""
    if not isinstance(offer, dict):
        raise InputError("offer must be a JSON object")
    for key in ("price", "core_unit_cost"):
        v = offer.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            raise InputError(f"{key} must be a non-negative number")
    if offer["price"] == 0:
        raise InputError("price must be above zero")
    d = offer.get("drivers")
    if not isinstance(d, dict):
        raise InputError("drivers block is required")
    days = d.get("days_to_result")
    if isinstance(days, bool) or not isinstance(days, (int, float)) or days < 0:
        raise InputError("drivers.days_to_result must be a non-negative number")
    offer["drivers"] = {"outcome": _score(d.get("outcome"), "outcome"),
                        "belief": _score(d.get("belief"), "belief"),
                        "effort": _score(d.get("effort"), "effort"), "days_to_result": float(days)}
    obstacles = offer.get("obstacles")
    if not isinstance(obstacles, list) or not all(isinstance(o, dict) and "id" in o for o in obstacles):
        raise InputError("obstacles must be a list of {id, text}")
    comps = offer.get("components")
    if not isinstance(comps, list) or not comps:
        raise InputError("components must be a non-empty list")
    for i, c in enumerate(comps):
        if not isinstance(c, dict) or "name" not in c:
            raise InputError(f"components[{i}] needs a name")
        for key in ("buyer_value", "delivery_cost"):
            if isinstance(c.get(key), bool) or not isinstance(c.get(key), (int, float)) or c[key] < 0:
                raise InputError(f"components[{i}].{key} must be a non-negative number")
        if not isinstance(c.get("solves", []), list):
            raise InputError(f"components[{i}].solves must be a list of obstacle ids")
    g = offer.setdefault("guarantee", {"type": "none"})
    if not isinstance(g, dict):
        raise InputError('guarantee must be an object such as {"type": "none"}')
    if g.get("type") not in GUARANTEES:
        raise InputError(f"guarantee.type must be one of {GUARANTEES}")
    rate = g.get("expected_claim_rate", 0)
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
        raise InputError("guarantee.expected_claim_rate must be between 0 and 1")
    u = offer.setdefault("urgency", {"type": "none"})
    if not isinstance(u, dict):
        raise InputError('urgency must be an object such as {"type": "none"}')
    if u.get("type") not in URGENCY:
        raise InputError(f"urgency.type must be one of {URGENCY}")
    offer.setdefault("proof", [])
    return offer


def value_score(d: dict[str, float]) -> float:
    """Combine the four drivers into a 0-100 perceived value score."""
    time_penalty = min(1.0, math.log1p(d["days_to_result"]) / math.log(366))
    friction = (time_penalty + d["effort"] / 10) / 2
    return round(100 * (d["outcome"] / 10) * (d["belief"] / 10) * (1 - 0.6 * friction), 1)


def analyse(o: dict[str, Any]) -> dict[str, Any]:
    """Score the offer and collect findings."""
    findings: list[dict[str, str]] = []

    def add(sev: str, msg: str) -> None:
        findings.append({"severity": sev, "message": msg})

    price, comps = float(o["price"]), o["components"]
    ids = {ob["id"] for ob in o["obstacles"]}
    solved = {s for c in comps for s in c.get("solves", []) if s in ids}
    unknown = sorted({s for c in comps for s in c.get("solves", [])} - ids)
    coverage = len(solved) / len(ids) if ids else 0.0
    stack_value = sum(c["buyer_value"] for c in comps)
    ratio = stack_value / price
    rows = []
    for c in comps:
        eff = c["buyer_value"] / c["delivery_cost"] if c["delivery_cost"] else math.inf
        rows.append({"name": c["name"], "kind": c.get("kind", "core"),
                     "solves": c.get("solves", []), "buyer_value": c["buyer_value"],
                     "delivery_cost": c["delivery_cost"],
                     "efficiency": None if math.isinf(eff) else round(eff, 1)})
        if not c.get("solves"):
            add("warn", f"'{c['name']}' answers no listed obstacle; filler lowers perceived value")
        if eff < EFFICIENCY_TRIM:
            add("warn", f"'{c['name']}' returns {eff:.1f}x its cost in buyer value; trim or rework it")
    g, u = o["guarantee"], o["urgency"]
    delivery = float(o["core_unit_cost"]) + sum(c["delivery_cost"] for c in comps)
    claim_cost = price * float(g.get("expected_claim_rate", 0)) if g["type"] != "none" else 0.0
    contribution = price - delivery - claim_cost
    margin = contribution / price

    if g["type"] != "none" and "expected_claim_rate" not in g:
        add("warn", "guarantee has no expected_claim_rate; its cost is counted as zero until you estimate one")
    if not ids:
        add("fail", "no buyer obstacles listed; an offer is built from the obstacles it removes")
    elif coverage < COVERAGE_FAIL:
        add("fail", f"only {coverage:.0%} of buyer obstacles are answered")
    for ob in o["obstacles"]:
        if ob["id"] not in solved:
            add("warn", f"obstacle {ob['id']} unanswered: {ob.get('text', '')}")
    if unknown:
        add("warn", f"components refer to unknown obstacle ids {unknown}")
    if ratio < 1:
        add("fail", f"stack value {stack_value:,.0f} is below the price {price:,.0f}")
    elif ratio < STACK_TARGET:
        add("warn", f"stack value is {ratio:.1f}x price; aim for {STACK_TARGET:.0f}x or more")
    if contribution <= 0:
        add("fail", f"each sale loses {-contribution:,.2f} after delivery and expected guarantee claims")
    elif margin < MARGIN_WARN:
        add("warn", f"contribution after guarantee is {margin:.0%} of price")
    if g["type"] == "none" and o["drivers"]["belief"] < 7:
        add("warn", "belief is low and there is no guarantee; risk reversal would lift it")
    if g["type"] != "none" and not str(g.get("terms", "")).strip():
        add("fail", "guarantee has no written terms")
    if u["type"] != "none":
        if not str(u.get("reason", "")).strip():
            add("fail", "urgency has no stated reason")
        if not u.get("verifiable"):
            add("fail", f"{u['type']} urgency is not verifiable; fake scarcity destroys trust")
    if o["drivers"]["belief"] >= 8 and len(o["proof"]) < 2:
        add("warn", "belief scored 8+ with fewer than 2 proof items; the score is not earned")
    words = len(str(o.get("headline", "")).split())
    if words == 0:
        add("warn", "no headline; name the offer by the outcome it delivers")
    elif words > HEADLINE_MAX_WORDS:
        add("warn", f"headline is {words} words; keep it under {HEADLINE_MAX_WORDS}")

    weakest = min(("outcome", "belief"), key=lambda k: o["drivers"][k])
    if o["drivers"]["effort"] >= 7 or o["drivers"]["days_to_result"] > 90:
        lever = "cut effort or time to first result"
    else:
        lever = f"raise {weakest}"
    return {
        "offer_name": o.get("offer_name", "unnamed"), "currency": o.get("currency", ""),
        "price": price, "value_score": value_score(o["drivers"]), "best_lever": lever,
        "stack_value": round(stack_value, 2), "stack_ratio": round(ratio, 2),
        "obstacle_coverage": round(coverage, 3), "components": rows,
        "delivery_cost": round(delivery, 2), "expected_guarantee_cost": round(claim_cost, 2),
        "contribution": round(contribution, 2), "contribution_margin": round(margin, 3),
        "findings": findings, "fail_count": sum(1 for f in findings if f["severity"] == "fail"),
    }


def render_text(r: dict[str, Any]) -> str:
    """Render the scorecard for a person."""
    cur = r["currency"]
    lines = [f"Offer scorecard — {r['offer_name']}",
             f"Value score: {r['value_score']}/100   best lever: {r['best_lever']}",
             f"Price {r['price']:,.2f} {cur}   stack value {r['stack_value']:,.0f} "
             f"({r['stack_ratio']:.1f}x)   obstacle coverage {r['obstacle_coverage']:.0%}",
             f"Delivery cost {r['delivery_cost']:,.2f}   expected guarantee cost "
             f"{r['expected_guarantee_cost']:,.2f}   contribution {r['contribution']:,.2f} "
             f"({r['contribution_margin']:.0%})", "",
             f"  {'COMPONENT':<34} {'KIND':<6} {'VALUE':>8} {'COST':>8} {'EFF':>6}  SOLVES"]
    for c in r["components"]:
        eff = "inf" if c["efficiency"] is None else f"{c['efficiency']:.1f}x"
        lines.append(f"  {c['name'][:34]:<34} {c['kind']:<6} {c['buyer_value']:>8,.0f} "
                     f"{c['delivery_cost']:>8,.2f} {eff:>6}  {','.join(c['solves']) or '-'}")
    lines += ["", f"Findings: {r['fail_count']} fail, {len(r['findings']) - r['fail_count']} warn"]
    lines += [f"  [{f['severity'].upper():4}] {f['message']}" for f in r["findings"]]
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Score an offer's value, obstacle coverage, guarantee cost and urgency.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--input", required=True, help="Offer JSON file")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()
    try:
        offer = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(load(offer))
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    except (InputError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    return 1 if report["fail_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
