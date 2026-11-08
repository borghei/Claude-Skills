#!/usr/bin/env python3
"""Product brief -> design-system spec (direction, palette, type, tokens, rules, charts, page patterns, motion).
Usage: design_recommender.py --brief brief.json [--format json] | --product "...". Exit: 0 consistent, 1 conflicts, 2 bad input.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REF = Path(__file__).resolve().parent.parent / "references"
FILES = {"products": "product-types.json", "directions": "directions.json", "palettes": "palettes.json", "motion": "motion.json",
         "pairings": "type-pairings.json", "rules": "ux-rules.json", "charts": "charts.json", "stacks": "stacks.json",
         "presets": "token-presets.json", "patterns": "page-patterns.json", "modifiers": "brief-modifiers.json"}
SEV = {"critical": 0, "high": 1, "medium": 2, "low": 3}
ENUMS = {"platform": {"web", "mobile", "both"}, "mode": {"light", "dark", "both", "auto"}, "contrast_target": {"AA", "AAA"},
         "density": {"compact", "comfortable", "spacious"}, "motion": {"calm", "standard", "expressive"}}
NON_LATIN = re.compile(r"[\u0590-\u08ff\u0900-\u0dff\u0e00-\u0e7f\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
KNOWN = set(ENUMS) | {"product", "audience", "product_type", "brand_color", "stack", "mood", "direction", "data_questions", "must_avoid", "pairing"}
STOP = {"a", "an", "and", "the", "for", "of", "to", "in", "on", "with", "or", "is", "our", "we", "app", "that", "by", "at"}


class BriefError(Exception):
    """Unusable input or bundled data; exits 2."""


def load(kind: str) -> Any:
    """Rows (or the presets object) of one bundled reference file."""
    try:
        return json.loads((REF / FILES[kind]).read_text(encoding="utf-8"))[kind]
    except (OSError, ValueError, KeyError) as exc:
        raise BriefError(f"bundled data {FILES[kind]} unreadable: {exc}") from exc


def index(kind: str) -> Dict[str, Dict[str, Any]]:
    """Bundled rows keyed by id."""
    return {r["id"]: r for r in load(kind)}


def lum(v: str) -> float:
    """WCAG 2.x relative luminance."""
    c = [int(v[1 + i:3 + i], 16) / 255 for i in (0, 2, 4)]  # #RRGGBB; brand colours are normalised in validate()
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio, 2 decimals."""
    return round((max(lum(a), lum(b)) + 0.05) / (min(lum(a), lum(b)) + 0.05), 2)


def words(text: str) -> set:
    """Lower-case word stems without stopwords."""
    ws = [w[:-3] + "y" if len(w) > 4 and w.endswith("ies") else w for w in re.findall(r"[a-z0-9]+", text.lower().replace("color", "colour").replace("gray", "grey")) if w not in STOP]
    ws = [w[:-2] if len(w) > 4 and re.search(r"(ch|sh|x|ss)es$", w) else w for w in ws]
    return {w[:-3] if len(w) > 5 and w.endswith("ing") else (w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w) for w in ws}


def has_cue(cues: List[str], text: str) -> bool:
    """True when any cue phrase appears as whole words (a trailing plural s is allowed)."""
    return any(re.search(r"(?<![a-z0-9-])" + re.escape(c.lower()) + r"s?(?![a-z0-9])", text) for c in cues)


def score(query: str, phrases: List[str], extra: str = "") -> int:
    """+3 per whole phrase in the query, +1 per shared word stem."""
    q = " " + " ".join(re.findall(r"[a-z0-9]+", query.lower())) + " "
    hits = sum(3 for p in phrases if " " + " ".join(re.findall(r"[a-z0-9]+", p.lower())) + " " in q)
    return hits + len(words(query) & words(" ".join(phrases) + " " + extra))


def finding(level: str, code: str, message: str, rule: str = "") -> Dict[str, str]:
    """One finding record."""
    return {"level": level, "code": code, "message": message, **({"rule": rule} if rule else {})}


def validate(brief: Any) -> Dict[str, Any]:
    """Check brief shape, types and ids."""
    if not isinstance(brief, dict) or not isinstance(brief.get("product"), str) or not brief["product"].strip():
        raise BriefError("brief must be a JSON object whose product is one sentence describing the product")
    brief = {k: v for k, v in brief.items() if v is not None}  # null means "not given"
    for key, allowed in ENUMS.items():
        if key in brief and not (isinstance(brief[key], str) and brief[key] in allowed):
            raise BriefError(f"brief.{key} must be one of {sorted(allowed)}, got {brief[key]!r}")
    for key in ("data_questions", "must_avoid", "mood", "audience", "stack", "product_type", "brand_color", "direction", "pairing"):
        want_list, v = key in ("data_questions", "must_avoid", "mood"), brief.get(key)
        if v is not None and not ((isinstance(v, list) and all(isinstance(x, str) for x in v)) if want_list else isinstance(v, str)):
            raise BriefError(f"brief.{key} must be {'a list of strings' if want_list else 'a string'}")
    if "brand_color" in brief and not re.fullmatch(r"#(?:[0-9a-fA-F]{3}){1,2}", brief["brand_color"].strip()):
        raise BriefError(f"brief.brand_color must be a hex colour like #1F4FD1, got {brief['brand_color']!r}")
    if "brand_color" in brief:
        v = brief["brand_color"].strip().lstrip("#")
        brief["brand_color"] = "#" + ("".join(c * 2 for c in v) if len(v) == 3 else v).upper()
    for key, kind in (("direction", "directions"), ("product_type", "products"), ("pairing", "pairings")):
        if brief.get(key) and brief[key] not in index(kind):
            raise BriefError(f"unknown {key} {brief[key]!r}; see references/{FILES[kind]}")
    return brief


def match_product(brief: Dict[str, Any], text: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Best product type plus the top three candidates."""
    if brief.get("product_type"):
        return index("products")[brief["product_type"]], [{"id": brief["product_type"], "score": "explicit"}]
    ranked = sorted(((score(text, p["keywords"], p["name"]), score(text, p["keywords"]), p) for p in load("products")),
                    key=lambda s: (-s[0], -s[1]))
    return ranked[0][2], [{"id": p["id"], "score": s} for s, _, p in ranked[:3]]


def pick_direction(product: Dict[str, Any], mode: str, avoid: List[str], prefer: List[str], mood: str, out: List) -> Dict:
    """First usable direction: explicit/modifier preference, then the product pair ordered by mood fit."""
    idx, avoid = index("directions"), [a.lower() for a in avoid]
    pair, fit = [product["direction"], product["alt"]], lambda d: score(mood, idx[d]["signatures"] + idx[d]["best_for"], idx[d]["summary"])
    if mood and fit(pair[1]) > fit(pair[0]):
        pair.reverse()
        out.append(finding("info", "direction-mood", f"mood words fit {pair[0]} better than {pair[1]}"))
    for did in dict.fromkeys(prefer + pair):
        d = idx[did]
        if not (any(a in (d["id"], d["name"].lower()) for a in avoid) or
                (mode in ("light", "both") and d["light"] == "no") or (mode in ("dark", "both") and d["dark"] == "no")):
            if did not in prefer and did != pair[0]:
                out.append(finding("warn", "direction-swapped", f"{pair[0]} excluded or cannot do {mode} mode; using {did}"))
            elif did in prefer and d["a11y_risk"] == "high":
                out.append(finding("warn", "direction-risk", f"{did} carries high accessibility risk: {d['pitfalls'][0]}", "A11Y-01"))
            return d
    out.append(finding("fail", "direction-conflict", f"{', '.join(dict.fromkeys(prefer + pair))} are all excluded or cannot render {mode} mode"))
    return idx[product["direction"]]


def apply_modifiers(brief: Dict[str, Any], text: str, out: List) -> Tuple[Dict[str, str], List[str]]:
    """Defaults changed by brief cues (landing, density, motion, mode, direction), plus extra avoid items."""
    sets, avoid = {}, []  # type: Dict[str, str], List[str]
    for m in (m for m in load("modifiers") if has_cue(m["cues"], text)):
        applied = {k: v for k, v in m["set"].items() if k not in brief and k not in sets}
        sets, avoid = {**sets, **applied}, avoid + m.get("avoid", [])
        out.append(finding("info", f"modifier-{m['id']}", m["note"] + (f" (sets {applied})" if applied else "")))
    return sets, avoid


def checks(roles: Dict[str, str], target: str) -> List[Dict[str, Any]]:
    """The eleven contrast pairs every palette mode must pass."""
    t = 7.0 if target == "AAA" else 4.5
    pairs = [("fg", "bg", t), ("fg", "surface", t), ("muted_fg", "bg", t), ("muted_fg", "surface", t),
             ("on_primary", "primary", 4.5), ("on_accent", "accent", 4.5), ("on_danger", "danger", 4.5),
             ("primary", "bg", 3.0), ("focus", "bg", 3.0), ("danger", "bg", 4.5), ("success", "bg", 4.5)]
    return [{"pair": f"{a}/{b}", "ratio": (r := contrast(roles[a], roles[b])), "min": m, "pass": r >= m} for a, b, m in pairs]


def with_brand(pal: Dict[str, Any], brand: str, modes: List[str], out: List) -> Dict[str, Any]:
    """Brand colour in the primary role, adjusted per mode to 4.5:1 on the background."""
    pal, rgb = json.loads(json.dumps(pal)), [int(brand[i:i + 2], 16) for i in (1, 3, 5)]
    for mode in modes:  # blend toward black (light bg) or white (dark bg) in 2% steps until 4.5:1
        r, toward = pal[mode], (0, 0, 0) if lum(pal[mode]["bg"]) > 0.18 else (255, 255, 255)
        cands = ["#" + "".join(f"{round(x + (y - x) * st / 100):02X}" for x, y in zip(rgb, toward)) for st in range(0, 101, 2)]
        primary = next(c for c in cands + ["#000000" if toward == (0, 0, 0) else "#FFFFFF"] if contrast(c, r["bg"]) >= 4.5 or c == cands[-1])
        if primary != brand:
            out.append(finding("warn", "brand-adjusted", f"{mode}: brand {brand} is {contrast(brand, r['bg'])}:1 on {r['bg']}; "
                               f"use {primary} for text and controls, keep the original for large decoration only", "A11Y-03"))
        r["primary"], r["focus"], dark_text = primary, primary, r["fg"] if mode == "light" else r["bg"]
        r["on_primary"] = "#FFFFFF" if contrast(primary, "#FFFFFF") >= contrast(primary, dark_text) else dark_text
    pal["id"] += "+brand"
    return pal


def pick_palette(product: Dict[str, Any], brief: Dict[str, Any], modes: List[str], out: List) -> Tuple[Dict, Dict]:
    """First candidate palette whose required modes all pass the target."""
    idx, target = index("palettes"), brief.get("contrast_target", "AA")
    for pid in product["palettes"] + (["highcontrast"] if target == "AAA" else []):
        pal = with_brand(idx[pid], brief["brand_color"], modes, out) if brief.get("brand_color") else idx[pid]
        res = {m: checks(pal[m], target) for m in modes}
        if all(c["pass"] for m in modes for c in res[m]):
            if pid not in product["palettes"]:
                out.append(finding("warn", "palette-fallback", f"no default palette reaches {target}; fell back to {pid}", "A11Y-01"))
            return pal, res
    out.append(finding("fail", "palette-contrast", f"no candidate palette passes {target} in {'/'.join(modes)} mode", "A11Y-01"))
    return idx[product["palettes"][0]], {m: checks(idx[product["palettes"][0]][m], target) for m in modes}


def pick_charts(product: Dict[str, Any], questions: List[str], out: List) -> List[Dict[str, Any]]:
    """Map each data question to a chart rule, or fall back to the product defaults."""
    charts = load("charts")
    if not questions:
        return [dict(c, matched_from="product default") for c in charts if c["id"] in product["charts"]]
    picked = [(q,) + max(((score(q, c["keywords"], c["question"]), c) for c in charts), key=lambda s: s[0]) for q in questions]
    out += [finding("warn", "chart-unmatched", f"no chart rule matches {q!r}; describe the question in plain words")
            for q, sc, _ in picked if sc < 2]
    return [dict(c, matched_from=q) for q, sc, c in picked if sc >= 2]


def pick_stack(name: str, platform: str, out: List) -> Dict[str, Any]:
    """Stack notes; fail when the stack cannot run on the brief's platform."""
    name = name.lower().strip()
    s = next((s for s in load("stacks") if name and (name in (s["id"], s["name"].lower()) or name in s["keywords"])), {})
    if s and platform != "both" and s["platform"] != platform:
        out.append(finding("fail", "stack-platform", f"stack {s['name']} runs on {s['platform']} but the brief targets {platform}"))
    elif name and not s:
        out.append(finding("warn", "stack-unknown", f"no notes for stack {name!r}; tokens still apply"))
    return s


def recommend(brief: Dict[str, Any], rule_limit: int = 15) -> Dict[str, Any]:
    """Build the spec dict from a validated brief."""
    out, presets, pats = [], load("presets"), index("patterns")  # type: List[Dict[str, str]], Dict, Dict
    cues = presets["audience_cues"]
    text = " ".join([brief["product"], brief.get("audience", "")] + brief.get("mood", [])).lower()
    product, candidates = match_product(brief, text)
    guess = ", ".join(f"{c['id']}={c['score']}" for c in candidates)
    if candidates[0]["score"] == 0:
        out.append(finding("fail", "no-match", "no product type matches the brief" + (" (it is not in English; keyword matching is English-only)"
                           if NON_LATIN.search(text) or re.search(r"[\u00c0-\u024f]", text) else "") + "; set product_type explicitly"))
    elif candidates[0]["score"] == 1 or (len(candidates) > 1 and candidates[0]["score"] == candidates[1]["score"]):
        out.append(finding("warn", "weak-match", f"product type is a guess ({guess}); set product_type explicitly"))
    out += [finding("warn", "unknown-field", f"brief field {k!r} is not used; see the brief table in references/design-decision-guide.md")
            for k in brief if k not in KNOWN]
    mods, extra_avoid = apply_modifiers(brief, text, out)
    platform, questions = brief.get("platform", "web"), brief.get("data_questions", [])
    mode = mods.get("mode", product["mode"]) if brief.get("mode", "auto") == "auto" else brief["mode"]
    modes = ["light", "dark"] if mode == "both" else [mode]
    prefer = [x for x in (brief.get("direction"), mods.get("direction")) if x]
    direction = pick_direction(product, mode, brief.get("must_avoid", []), prefer, " ".join(brief.get("mood", [])), out)
    density, motion = (brief.get(k, mods.get(k, product[k])) for k in ("density", "motion"))
    for cond, f in ((motion == "expressive" and has_cue(cues["motion_sensitive"], text), ("fail", "motion-audience",
                     "expressive motion for a motion-sensitive audience; use calm and honour reduced motion", "MOT-01")),
                    (density == "spacious" and len(questions) >= 4, ("warn", "density-data",
                     f"spacious density with {len(questions)} data views; expect scrolling, consider comfortable")),
                    (density == "compact" and platform in ("mobile", "both"), ("warn", "density-touch",
                     "compact spacing on touch: keep hit areas at 44pt even when rows are tight", "TCH-01"))):
        out += [finding(*f)] if cond else []
    palette, pal_checks = pick_palette(product, brief, modes, out)
    low_vision = has_cue(cues["low_vision"], text)
    pid, reason = ((brief["pairing"], "set in the brief") if brief.get("pairing")
                   else ("global-scripts", "brief mentions or is written in non-Latin or RTL scripts")
                   if has_cue(cues["multi_script"], text) or NON_LATIN.search(text)
                   else ("hyperlegible", "brief mentions low-vision or older readers") if low_vision
                   else (product["pairings"][0], "product default") if direction["id"] == product["direction"]
                   else (direction["pairing"], f"follows the {direction['name']} direction"))
    pair, ratio, base = index("pairings")[pid], (1.2 if density == "compact" else direction["type_ratio"]), (18 if low_vision else 16)
    scale = sorted({round(base * ratio ** i) for i in range(-2, 6) if base * ratio ** i >= 11.5})
    prio = product["priorities"]
    rules = [r for r in load("rules") if (platform == "both" or r["platform"] in ("all", platform))
             and (r["severity"] == "critical" or (r["category"] in prio and r["severity"] in ("high", "medium")))]
    rules.sort(key=lambda r: (SEV[r["severity"]], prio.index(r["category"]) if r["category"] in prio else 9))
    mo, tier = presets["motion"][motion], ["calm", "standard", "expressive"].index(motion)
    out = [f for i, f in enumerate(out) if f not in out[:i]]
    tokens = {"contrast_target": brief.get("contrast_target", "AA"), "modes": modes, "color": {m: palette[m] for m in modes},
              "font": {"families": sorted({pair["display"], pair["body"], pair["mono"]}), "base_size": base,
                       "line_height": 1.5, "heading_line_height": 1.2, "scale": scale},
              "space": presets["spacing"][density], "radius": dict(direction["radius"], full=9999),
              "elevation": presets["elevation"][direction["elevation"]],
              "motion": {"durations_ms": mo["durations_ms"], "easing": mo["easing"], "reduced_motion": True},
              "touch_target": mods.get("touch_target", 44 if platform == "web" else 48), "focus": {"width": 2, "offset": 2},
              "icon": {"sizes": [16, 20, 24], "stroke": 1.5 if direction["elevation"] in ("flat", "soft") else 2}}
    return {"brief": brief, "product_type": {"id": product["id"], "name": product["name"], "candidates": candidates},
            "mode": mode, "platform": platform, "density": density, "motion_tier": motion, "motion_notes": mo["movement"],
            "direction": direction, "palette": dict({k: palette[k] for k in ("id", "name", "summary")}, checks=pal_checks),
            "typography": {k: pair[k] for k in ("display", "body", "mono", "fallback", "why")} | {"reason": reason, "ratio": ratio},
            "tokens": tokens, "ux_rules": rules[:rule_limit], "charts": pick_charts(product, questions, out),
            "page_patterns": {"landing": pats.get(mods.get("landing") or product.get("landing") or ""),
                              "screens": [pats[x] for x in product.get("screens", []) if x in pats]},
            "motion_map": [{k: v for k, v in m.items() if k != "keywords"} | {"ms": m["ms"][tier]}
                           for m in load("motion") if m["ms"][tier] is not None],
            "stack": pick_stack(brief.get("stack", ""), platform, out), "avoid": product["avoid"] + extra_avoid + direction["pitfalls"], "risks": product["risks"],
            "findings": out, "verdict": "CONFLICTS" if any(f["level"] == "fail" for f in out) else "CONSISTENT"}


def summary(s: Dict[str, Any]) -> str:
    """Short terminal summary; spec_renderer.py --format text prints the long form."""
    t, ty = s["tokens"], s["typography"]
    return "\n".join([f"DESIGN SPEC  {s['verdict']}  {s['product_type']['name']} ({s['product_type']['id']})",
            f"  {s['direction']['name']} | palette {s['palette']['id']} ({', '.join(t['color'])}) | "
            f"{ty['display']} / {ty['body']} {t['font']['base_size']}px x{ty['ratio']} | {s['density']} | {s['motion_tier']}",
            f"  rules {', '.join(r['id'] for r in s['ux_rules'])}", f"  charts {'; '.join(c['best'] for c in s['charts']) or 'none'}",
            f"  landing {(s['page_patterns']['landing'] or {}).get('id', 'none')} | screens "
            f"{', '.join(x['id'] for x in s['page_patterns']['screens']) or 'none'}", "FINDINGS" + ("" if s["findings"] else "  none")]
                     + [f"  [{f['level']}] {f['code']}: {f['message']}" for f in s["findings"]])


def main() -> None:
    """Parse arguments, build the spec, print it, exit with the contract code."""
    ap = argparse.ArgumentParser(description="Recommend a design-system spec from a product brief.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--brief", help="brief JSON file (see assets/sample_brief.json)")
    src.add_argument("--product", help="one-sentence product description (quick mode, other fields default)")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format (default text)")
    ap.add_argument("--rules", type=int, default=15, help="maximum UX rules to include (default 15)")
    args = ap.parse_args()
    try:
        try:
            brief = json.loads(Path(args.brief).read_text(encoding="utf-8")) if args.brief else {"product": args.product}
        except (OSError, ValueError) as exc:
            raise BriefError(f"cannot read {args.brief} as JSON: {getattr(exc, 'strerror', None) or exc}") from exc
        spec = recommend(validate(brief), max(1, args.rules))
    except BriefError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(spec, indent=2) if args.format == "json" else summary(spec))
    sys.exit(1 if spec["verdict"] == "CONFLICTS" else 0)


if __name__ == "__main__":
    main()
