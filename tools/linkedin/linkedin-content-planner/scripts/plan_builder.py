#!/usr/bin/env python3
"""Turn a pillar, cadence and format-mix config into a dated publishing plan.

Reads a JSON config (pillars with target shares, posting weekdays, a format
mix, limits), lays posts onto calendar dates so pillars and formats are spread
evenly, optionally binds each slot to a ready entry from a story bank file,
and flags imbalance. Produces a plan to act on by hand; it does not post,
schedule or contact any service.

Usage:
    python3 plan_builder.py --input plan_config.json
    python3 plan_builder.py --input plan_config.json --format json
    python3 plan_builder.py --input plan_config.json \
        --story-bank story_bank.json --fail-on error

Exit codes:
    0  plan built (and no flag reached the --fail-on level)
    1  gate failed: a flag at or above --fail-on exists
    2  bad input: file missing, not JSON, or config invalid
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plan_rules import (  # noqa: E402
    DEFAULT_LIMITS, PILLAR_SETS, SEVERITY_RANK, WEEKDAYS, check_plan,
    deficit_pick, largest_remainder, percent)


def fail(message: str) -> NoReturn:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def read_json(path: Path, what: str) -> Any:
    """Read a JSON file, exiting with guidance when it is missing or malformed."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {what} {path}: {getattr(exc, 'strerror', None) or exc}")
    except json.JSONDecodeError as exc:
        fail(f"{what} {path} is not valid JSON (line {exc.lineno}, column "
             f"{exc.colno}): {exc.msg}")


def weekday_list(config: Dict[str, Any], key: str, required: bool) -> List[int]:
    """Validate a list of weekday names and return their indexes (mon=0)."""
    raw = config.get(key, [])
    if not isinstance(raw, list) or (required and not raw):
        fail(f"'{key}' must be a non-empty list of weekdays such as "
             '["tue", "thu"].')
    days = [str(d).strip().lower()[:3] for d in raw]
    unknown = [str(r) for r, d in zip(raw, days) if d not in WEEKDAYS]
    if unknown:
        fail(f"'{key}' contains unknown weekday(s): {', '.join(unknown)}. "
             f"Use {', '.join(WEEKDAYS)}.")
    return sorted({WEEKDAYS.index(d) for d in days})


def share_items(raw: Any, key: str) -> List[Dict[str, Any]]:
    """Validate a list of {name, share} objects whose shares sum to 100."""
    if not isinstance(raw, list) or not raw or any(not isinstance(i, dict) for i in raw):
        fail(f"'{key}' must be a non-empty list of objects with 'name' and 'share'.")
    names = [str(i.get("name", "")).strip() for i in raw]
    if any(not n for n in names) or len(set(names)) != len(names):
        fail(f"every item in '{key}' needs a unique, non-empty 'name'.")
    for item in raw:
        if isinstance(item.get("share"), bool) or not isinstance(
                item.get("share"), (int, float)) or item["share"] <= 0:
            fail(f"'{key}' item '{item.get('name')}' needs a 'share' above 0.")
    total = sum(i["share"] for i in raw)
    if abs(total - 100) > 0.5:
        fail(f"'{key}' shares sum to {total:g}, not 100. Adjust the shares; "
             "the planner will not guess which one to change.")
    return raw


def load_config(path: Path) -> Dict[str, Any]:
    """Load the plan config and normalise it into a validated dictionary."""
    config = read_json(path, "plan config")
    if not isinstance(config, dict):
        fail("the plan config must be a JSON object. See "
             "assets/sample_plan_config.json for the expected shape.")
    try:
        start = date.fromisoformat(str(config.get("start_date")))
    except ValueError:
        fail(f"'start_date' must be YYYY-MM-DD, got '{config.get('start_date')}'.")
    weeks = config.get("weeks", 1)
    if isinstance(weeks, bool) or not isinstance(weeks, int) or not 1 <= weeks <= 13:
        fail("'weeks' must be a whole number from 1 to 13.")
    pillars = config.get("pillars")
    if pillars is None and config.get("pillar_set") is not None:
        if config["pillar_set"] not in PILLAR_SETS:
            fail(f"'pillar_set' must be one of: {', '.join(PILLAR_SETS)}.")
        pillars = [dict(p) for p in PILLAR_SETS[config["pillar_set"]]]
    skip: List[date] = []
    for raw in config.get("skip_dates", []) or []:
        try:
            skip.append(date.fromisoformat(str(raw)))
        except ValueError:
            fail(f"'skip_dates' entry '{raw}' is not a YYYY-MM-DD date.")
    limits = dict(DEFAULT_LIMITS)
    for key, value in (config.get("limits") or {}).items():
        if key not in DEFAULT_LIMITS or isinstance(value, bool) or not isinstance(
                value, (int, float)) or value < 0:
            fail(f"'limits.{key}' is not a known limit with a non-negative "
                 f"number. Known limits: {', '.join(DEFAULT_LIMITS)}.")
        limits[key] = value
    return {
        "owner": str(config.get("owner", "unknown")), "start": start, "weeks": weeks,
        "posting": weekday_list(config, "posting_weekdays", True),
        "conversation": weekday_list(config, "conversation_weekdays", False),
        "pillars": share_items(pillars, "pillars"),
        "formats": share_items(config.get("formats") or [{"name": "text", "share": 100}],
                               "formats"),
        "skip": skip, "limits": limits,
    }


def build_calendar(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Lay posting and conversation days onto dates, dropping skip dates."""
    slots: List[Dict[str, Any]] = []
    talk, skipped = [], 0
    for offset in range(cfg["weeks"] * 7):
        day = cfg["start"] + timedelta(days=offset)
        row = {"date": day.isoformat(), "weekday": WEEKDAYS[day.weekday()],
               "week": offset // 7 + 1}
        if day.weekday() in cfg["posting"]:
            if day in cfg["skip"]:
                skipped += 1
            else:
                slots.append(row)
        elif day.weekday() in cfg["conversation"] and day not in cfg["skip"]:
            talk.append(row)
    if not slots:
        fail("the config produces no posting slots. Check 'posting_weekdays', "
             "'weeks' and 'skip_dates'.")
    return {"slots": slots, "conversation": talk, "skipped": skipped}


def allocate(slots: List[Dict[str, Any]], cfg: Dict[str, Any]) -> List[int]:
    """Assign a pillar, format and ask to every slot; return format quotas."""
    pillars, formats, limits = cfg["pillars"], cfg["formats"], cfg["limits"]
    total = len(slots)
    p_quota = largest_remainder([p["share"] for p in pillars], total)
    f_quota = largest_remainder([f["share"] for f in formats], total)
    p_given, f_given = [0] * len(pillars), [0] * len(formats)
    promo_in_week: Dict[int, int] = {}
    made_in_week: Dict[int, int] = {}
    previous: Optional[int] = None
    for position, slot in enumerate(slots, start=1):
        week = slot["week"]
        open_pillars = [i for i, p in enumerate(pillars) if not (
            p.get("promotional")
            and promo_in_week.get(week, 0) >= limits["max_promotional_per_week"])]
        pick = deficit_pick(p_quota, p_given, position, total, open_pillars, previous)
        if pick is None:
            pick = deficit_pick(p_quota, p_given, position, total) or 0
        pillar = pillars[pick]
        p_given[pick] += 1
        previous = pick
        if pillar.get("promotional"):
            promo_in_week[week] = promo_in_week.get(week, 0) + 1
        wanted = pillar.get("formats") or [f["name"] for f in formats]
        fits = [i for i, f in enumerate(formats) if f["name"] in wanted]
        if not fits:
            fail(f"pillar '{pillar['name']}' allows formats {wanted}, none of "
                 "which appear under 'formats'.")
        roomy = [i for i in fits if not (
            formats[i].get("produced")
            and made_in_week.get(week, 0) >= limits["max_produced_per_week"])]
        choice = deficit_pick(f_quota, f_given, position, total, roomy)
        if choice is None:
            choice = (roomy or fits)[0]
        f_given[choice] += 1
        if formats[choice].get("produced"):
            made_in_week[week] = made_in_week.get(week, 0) + 1
        slot.update({"pillar": pillar["name"], "format": formats[choice]["name"],
                     "ask": str(pillar.get("ask", "reply")),
                     "promotional": bool(pillar.get("promotional")),
                     "entry_id": None, "entry_title": None})
    return f_quota


def attach_bank(slots: List[Dict[str, Any]], path: Path) -> None:
    """Bind each slot to a ready story bank entry for its pillar, unused first."""
    bank = read_json(path, "story bank")
    if not isinstance(bank, dict) or not isinstance(bank.get("entries"), list):
        fail(f"{path} is not a story bank: expected a JSON object with an "
             "'entries' array.")
    ready = [e for e in bank["entries"]
             if isinstance(e, dict) and e.get("status") == "ready"]
    ready.sort(key=lambda e: bool(e.get("used_in")))
    taken: set = set()
    for slot in slots:
        for index, entry in enumerate(ready):
            if index not in taken and slot["pillar"] in (entry.get("pillars") or []):
                taken.add(index)
                slot["entry_id"], slot["entry_title"] = entry.get("id"), entry.get("title")
                break


def build(cfg: Dict[str, Any], bank_path: Optional[Path]) -> Dict[str, Any]:
    """Build the full plan report: calendar, mix table and flags."""
    calendar = build_calendar(cfg)
    slots = calendar["slots"]
    format_targets = allocate(slots, cfg)
    if bank_path:
        attach_bank(slots, bank_path)
    flags = check_plan({
        "slots": slots, "limits": cfg["limits"], "pillars": cfg["pillars"],
        "formats": cfg["formats"], "weeks": cfg["weeks"],
        "format_targets": format_targets, "skipped": calendar["skipped"],
        "conversation_weekdays": cfg["conversation"],
        "bank_supplied": bank_path is not None})
    per = {p["name"]: sum(1 for s in slots if s["pillar"] == p["name"]) for p in cfg["pillars"]}
    mix = [{"pillar": p["name"], "target_share": p["share"], "posts": per[p["name"]],
            "planned_share": percent(per[p["name"]], len(slots))} for p in cfg["pillars"]]
    return {
        "owner": cfg["owner"], "start_date": cfg["start"].isoformat(),
        "end_date": (cfg["start"] + timedelta(days=cfg["weeks"] * 7 - 1)).isoformat(),
        "weeks": cfg["weeks"], "posts": len(slots), "limits": cfg["limits"],
        "pillar_mix": mix,
        "format_mix": {f["name"]: sum(1 for s in slots if s["format"] == f["name"])
                       for f in cfg["formats"]},
        "counts": {s: sum(1 for f in flags if f["severity"] == s) for s in SEVERITY_RANK},
        "slots": slots, "conversation_days": calendar["conversation"], "flags": flags,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the plan as JSON or as a week-by-week text calendar."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Publishing plan: {report['owner']}  {report['start_date']} to "
          f"{report['end_date']}  ({report['posts']} posts, {report['weeks']} weeks)"
          f"\n{'=' * 78}")
    rows = [dict(s, kind="post") for s in report["slots"]] + [
        dict(c, kind="talk") for c in report["conversation_days"]]
    rows.sort(key=lambda r: r["date"])
    week = 0
    for row in rows:
        if row["week"] != week:
            week = row["week"]
            print(f"Week {week}")
        if row["kind"] == "talk":
            print(f"  {row['weekday']} {row['date']}  conversation block")
            continue
        source = (f"{row['entry_id']} {row['entry_title']}" if row["entry_id"]
                  else "no source entry")
        print(f"  {row['weekday']} {row['date']}  POST  {row['pillar']:<14}"
              f"{row['format']:<10}ask={row['ask']:<8} {source}")
    print("-" * 78 + f"\n{'Pillar':<16}{'target':>8}{'planned':>9}{'posts':>7}")
    for item in report["pillar_mix"]:
        print(f"{item['pillar']:<16}{item['target_share']:>7g}%"
              f"{item['planned_share']:>8g}%{item['posts']:>7}")
    print("Formats: " + ", ".join(f"{k} x{v}" for k, v in report["format_mix"].items()))
    print("-" * 78 + "\nFlags: " + ", ".join(f"{n} {s}" for s, n in report["counts"].items()))
    for item in report["flags"]:
        print(f"[{item['severity'].upper():<5}] {item['id']}  {item['where']}: "
              f"{item['title']}\n        evidence: {item['evidence']}"
              f"\n        do: {item['action']}")


def main() -> None:
    """Parse arguments, build the plan, print it, apply the gate."""
    parser = argparse.ArgumentParser(
        description="Turn a pillar, cadence and format-mix config into a dated "
                    "publishing plan and flag imbalance.",
        epilog="Exit codes: 0 plan built, 1 a flag reached --fail-on, 2 bad input.")
    parser.add_argument("--input", required=True,
                        help="Path to the plan config JSON.")
    parser.add_argument("--story-bank", default=None,
                        help="Optional story bank JSON; binds slots to ready entries.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["error", "warn"], default=None,
                        help="Exit 1 if any flag at or above this level exists.")
    args = parser.parse_args()
    try:
        report = build(load_config(Path(args.input)),
                       Path(args.story_bank) if args.story_bank else None)
    except (AttributeError, KeyError, TypeError) as exc:
        fail(f"the config or story bank has a field of the wrong type ({exc}). Compare it "
             "with assets/plan_config_template.json.")
    output(report, args.format)
    if args.fail_on and any(SEVERITY_RANK[f["severity"]] <= SEVERITY_RANK[args.fail_on]
                            for f in report["flags"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
