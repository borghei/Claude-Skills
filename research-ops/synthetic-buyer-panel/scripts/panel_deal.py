#!/usr/bin/env python3
"""
panel_deal.py — Deal a reproducible set of synthetic buyer cards from a target
customer profile and write one self-contained brief per buyer.

Segments and buying behaviours are allocated by exact quota (largest remainder),
so a 40-buyer panel with a 45% segment gets 18 buyers in it, not "about 18".
Income, age, context and the doubt each buyer starts with are then drawn with a
seeded random generator: the same profile, size and seed always give the same
cards. The tool never answers for a buyer; it only prepares the panel.

Before dealing, the profile is checked. A profile that would produce a
misleading panel (shares that do not add up, a vague target, a pitch with no
price, fewer than three objections) is reported and nothing is dealt.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 panel_deal.py --profile profile.json --n 40 --seed 7
    python3 panel_deal.py --profile profile.json --n 40 --out-dir panel/
    python3 panel_deal.py --profile profile.json --format json

Exit codes: 0 dealt, 1 profile fails a check, 2 bad input.

Profile schema (see assets/sample_customer_profile.json):
{
  "offer": str, "target": str, "currency": str, "age_range": [int, int],
  "price_unit": str (what the four price answers are for, e.g. "per litre"),
  "pitch": [str, ...],
  "segments":   [{"name": str, "share": float, "income": [int, int],
                  "age": [int, int] (optional, overrides age_range)}],
  "behaviours": [{"name": str, "share": float, "description": str}],
  "objections": [str, ...], "contexts": [str, ...]
}
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

SHARE_TOLERANCE = 0.02
HYPE_WORDS = ("best", "amazing", "revolutionary", "world-class", "guaranteed",
              "unbeatable", "perfect", "game-changing", "incredible")
REASON_CODES = ("price", "access", "trust", "need", "habit", "alternative", "other")

BRIEF = """# Buyer brief {id}

You are taking part in a buyer panel. Answer as the person described below and
only as that person. Do not try to be helpful to the seller.

## Who you are
- Age: {age}
- Group: {segment}, annual income about {income:,} {currency}
- How you buy: {behaviour} - {behaviour_how}
- Your week: {context}
- The doubt already in your head: "{doubt}"

## What you were shown
{pitch}

## How to answer
- Decide as this person would on an ordinary day, with their budget and habits.
  Most people pass on most offers; passing is a normal answer.
- Use only what the pitch says. Do not invent features, reviews or prices.
- Write your reason in your own plain words, one or two sentences.

Write exactly one JSON object and nothing else:

{{"buyer_id": "{id}", "decision": "buy" or "pass",
 "units_first_month": <whole number, 0 if pass>,
 "reason_code": one of {codes},
 "reason": "<your reason>", "main_objection": "<your biggest doubt>",
 "would_change_mind": "<the one thing that would flip your answer>",
 "price_points": {{"too_cheap": <n>, "bargain": <n>,
                  "getting_expensive": <n>, "too_expensive": <n>}}}}

The four price points answer: at what price would this seem so cheap you would
doubt it, a bargain, getting expensive but still possible, and too expensive to
consider. Give each as a number in {currency}, {price_unit}.
"""


class InputError(ValueError):
    """Raised when the profile is structurally unusable."""


def _require(profile: dict[str, Any], key: str, kind: type) -> Any:
    """Return a required field of the given type or raise InputError."""
    value = profile.get(key)
    if not isinstance(value, kind) or not value:
        raise InputError(f"profile needs a non-empty '{key}' ({kind.__name__})")
    return value


def check_profile(p: dict[str, Any], n: int) -> list[dict[str, str]]:
    """Return findings that would make the panel misleading."""
    out: list[dict[str, str]] = []

    def add(sev: str, msg: str) -> None:
        out.append({"severity": sev, "message": msg})

    for group in ("segments", "behaviours"):
        total = sum(float(x.get("share", 0)) for x in p[group])
        if abs(total - 1.0) > SHARE_TOLERANCE:
            add("fail", f"{group} shares sum to {total:.2f}, not 1.0")
    for group in ("segments", "behaviours"):
        names = [str(x.get("name")) for x in p[group]]
        if len(names) != len(set(names)):
            add("fail", f"{group} has duplicate names; each needs a distinct name")
    for seg in p["segments"]:
        lo, hi = seg["income"]
        if lo > hi:
            add("fail", f"segment '{seg['name']}' income range is reversed ({lo} > {hi})")
    if len(p["segments"]) < 2:
        add("warn", "only one segment: the panel cannot show who buys versus who passes")
    if len(p["objections"]) < 3:
        add("fail", f"only {len(p['objections'])} objections; list at least 3 real doubts")
    if len(p["target"].split()) < 5:
        add("fail", f"target '{p['target']}' is too vague; describe who, where and what they do now")
    pitch = " ".join(p["pitch"])
    if not re.search(r"\d(?![\d.,]*\s*%)", pitch):
        add("fail", "the pitch shows no price; buyers cannot answer price questions")
    hype = [w for w in HYPE_WORDS if re.search(rf"\b{re.escape(w)}\b", pitch.lower())]
    if hype:
        add("warn", f"pitch uses hype words {hype}; buyers should see what a real customer sees")
    if n < 20:
        add("warn", f"n={n}: fewer than 20 buyers gives segment rates too noisy to read")
    if n > 200:
        add("warn", f"n={n}: over 200 buyers costs a lot of runs for little extra signal")
    return out


def quotas(items: list[dict[str, Any]], n: int) -> list[str]:
    """Allocate n slots across items by share using the largest-remainder method."""
    total = sum(float(it["share"]) for it in items)
    if total <= 0:
        raise InputError("shares must add up to more than zero")
    # Normalise first: shares inside the tolerance band (e.g. 0.99 or 1.02) must still fill exactly n slots.
    raw = [(i, float(it["share"]) / total * n) for i, it in enumerate(items)]
    base = [int(v) for _, v in raw]
    left = n - sum(base)
    for i, _ in sorted(raw, key=lambda x: (-(x[1] - int(x[1])), items[x[0]]["name"], x[0]))[:left]:
        base[i] += 1
    slots = [items[i]["name"] for i in range(len(items)) for _ in range(base[i])]
    if len(slots) != n:
        raise InputError(f"could not allocate {n} slots across {len(items)} groups")
    return slots


def deal(p: dict[str, Any], n: int, seed: int) -> list[dict[str, Any]]:
    """Deal n buyer cards deterministically from the profile."""
    rng = random.Random(seed)
    segs = quotas(p["segments"], n)
    behs = quotas(p["behaviours"], n)
    rng.shuffle(behs)
    doubts = [p["objections"][i % len(p["objections"])] for i in range(n)]
    rng.shuffle(doubts)
    seg_by_name = {s["name"]: s for s in p["segments"]}
    beh_by_name = {b["name"]: b for b in p["behaviours"]}
    cards = []
    for i in range(n):
        seg = seg_by_name[segs[i]]
        lo, hi = seg["income"]
        lo_age, hi_age = seg.get("age", p["age_range"])
        cards.append({
            "id": f"B{i + 1:03d}", "segment": segs[i],
            "income": int(round(rng.uniform(lo, hi), -3)),
            "age": rng.randint(lo_age, hi_age), "behaviour": behs[i],
            "behaviour_how": beh_by_name[behs[i]].get("description", ""),
            "context": rng.choice(p["contexts"]) if p["contexts"] else "an ordinary week",
            "doubt": doubts[i],
        })
    return cards


def render_brief(card: dict[str, Any], p: dict[str, Any]) -> str:
    """Fill the fixed brief template for one buyer."""
    pitch = "\n".join(f"> {line}" for line in p["pitch"])
    return BRIEF.format(**card, currency=p.get("currency", "the pitch currency"), pitch=pitch,
                        price_unit=p.get("price_unit", "for the main item in the pitch"),
                        codes=" | ".join(REASON_CODES))


def load(path: str) -> dict[str, Any]:
    """Load and structurally validate the profile file."""
    try:
        p = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read profile: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"profile is not valid JSON: {exc}") from exc
    if not isinstance(p, dict):
        raise InputError("profile must be a JSON object")
    for key, kind in (("offer", str), ("target", str), ("pitch", list), ("segments", list),
                      ("behaviours", list), ("objections", list), ("age_range", list)):
        _require(p, key, kind)
    p.setdefault("contexts", [])
    for seg in p["segments"]:
        inc = seg.get("income") if isinstance(seg, dict) else None
        if not (isinstance(inc, list) and len(inc) == 2 and "name" in seg and "share" in seg):
            raise InputError("each segment needs name, share and income [low, high]")
    for beh in p["behaviours"]:
        if not isinstance(beh, dict) or "name" not in beh or "share" not in beh:
            raise InputError("each behaviour needs name and share")
    if len(p["age_range"]) != 2 or p["age_range"][0] > p["age_range"][1]:
        raise InputError("age_range must be [youngest, oldest]")
    return p


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deal reproducible synthetic buyer cards and briefs from a customer profile.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--profile", required=True, help="Customer profile JSON")
    parser.add_argument("--n", type=int, default=40, help="Number of buyers (default 40)")
    parser.add_argument("--seed", type=int, default=7, help="Random seed (default 7)")
    parser.add_argument("--out-dir", help="Write cards.json and one brief_<id>.md per buyer here")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()
    try:
        if args.n < 1:
            raise InputError("--n must be at least 1")
        profile = load(args.profile)
        findings = check_profile(profile, args.n)
        failed = any(f["severity"] == "fail" for f in findings)
        cards = [] if failed else deal(profile, args.n, args.seed)
        if args.out_dir and cards:
            out = Path(args.out_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / "cards.json").write_text(json.dumps(cards, indent=2), encoding="utf-8")
            for card in cards:
                (out / f"brief_{card['id']}.md").write_text(render_brief(card, profile), encoding="utf-8")
    except (InputError, TypeError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 2
    report = {"offer": profile["offer"], "n": args.n, "seed": args.seed,
              "dealt": len(cards), "findings": findings, "cards": cards}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Buyer panel — {profile['offer']}  (n={args.n}, seed={args.seed})")
        for f in findings:
            print(f"  [{f['severity'].upper():4}] {f['message']}")
        if failed:
            print("Nothing dealt: fix the failing checks in the profile first.")
        else:
            print(f"Dealt {len(cards)} cards.")
            for c in cards:
                print(f"  {c['id']}  {c['segment']:<22} {c['behaviour']:<20} age {c['age']:<3} "
                      f"income {c['income']:>7,}  doubt: {c['doubt']}")
            if args.out_dir:
                print(f"Wrote cards.json and {len(cards)} briefs to {args.out_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
