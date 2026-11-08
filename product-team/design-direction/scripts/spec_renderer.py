#!/usr/bin/env python3
"""Render a design-direction spec (the recommender's JSON) as a markdown design-system
document, a CSS custom-property theme, or a bare tokens JSON file.

Usage:
  python3 design_recommender.py --brief brief.json --format json > spec.json
  python3 spec_renderer.py --spec spec.json --format markdown > DESIGN-SPEC.md
  python3 spec_renderer.py --spec spec.json --format css > theme.css
  python3 spec_renderer.py --spec spec.json --format json > tokens.json
  python3 spec_renderer.py --spec spec.json --format text

Exit codes: 0 rendered from a consistent spec, 1 rendered but the spec carries
conflicts (a banner says so), 2 unreadable or not a recommender spec.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

BLOCKERS = ("components use role tokens only, no raw hex",
            "text over images and translucent panels measured at 4.5:1 over the busiest area",
            "visible focus ring on every interactive element; keyboard order follows visual order",
            "touch targets at the spec minimum, icon buttons included",
            "shipped theme re-checked with the token checker (exit 0)")
REQUIRED = ("brief", "product_type", "direction", "palette", "typography", "tokens", "ux_rules", "findings", "verdict")


class SpecError(Exception):
    """Input is not a usable spec; exits 2."""


def table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    """Markdown table lines."""
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    return out + ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]


def findings_block(spec: Dict[str, Any]) -> List[str]:
    """Findings as bullets, or a clean note."""
    if not spec["findings"]:
        return ["- None. The brief, direction, palette and tokens agree."]
    return [f"- **{f['level'].upper()}** `{f['code']}`: {f['message']}" + (f" (rule {f['rule']})" if f.get("rule") else "")
            for f in spec["findings"]]


def markdown(spec: Dict[str, Any]) -> str:
    """Full design-system document."""
    d, t, tok = spec["direction"], spec["typography"], spec["tokens"]
    lines = [f"# Design System Spec: {spec['brief']['product']}", ""]
    if spec["verdict"] != "CONSISTENT":
        lines += ["> **This spec has unresolved conflicts.** Fix the brief and re-run before building.", ""]
    lines += [f"**Verdict:** {spec['verdict']}  ",
              f"**Product type:** {spec['product_type']['name']} (`{spec['product_type']['id']}`)  ",
              f"**Platform:** {spec.get('platform')}  **Mode:** {spec.get('mode')}  **Density:** {spec.get('density')}  "
              f"**Motion:** {spec.get('motion_tier')}", "", "## Findings", ""] + findings_block(spec)
    lines += ["", f"## Direction: {d['name']}", "", d["summary"], "", "**Signatures:**"] + [f"- {s}" for s in d["signatures"]]
    lines += ["", f"**Best for:** {', '.join(d['best_for'])}  ", f"**Avoid when:** {'; '.join(d['avoid_when'])}  ",
              f"**Accessibility risk:** {d['a11y_risk']}  **Performance cost:** {d['perf_cost']}"]
    lines += ["", f"## Colour: {spec['palette']['name']} (`{spec['palette']['id']}`)", "", spec["palette"]["summary"], ""]
    for mode, roles in tok["color"].items():
        lines += [f"### {mode.title()} mode", ""]
        lines += table(["Role", "Value", "CSS variable"], [[k, f"`{v}`", f"`--{k.replace('_', '-')}`"] for k, v in roles.items()])
        lines += ["", "Computed contrast (WCAG 2.x):", ""]
        lines += table(["Pair", "Ratio", "Minimum", "Result"],
                       [[c["pair"], f"{c['ratio']}:1", f"{c['min']}:1", "pass" if c["pass"] else "FAIL"]
                        for c in spec["palette"]["checks"].get(mode, [])])
        lines.append("")
    lines += ["## Typography", ""]
    lines += table(["Role", "Family"], [["Display", t["display"]], ["Body", t["body"]], ["Mono", t["mono"]], ["Fallback", t["fallback"]]])
    lines += ["", f"Why: {t['why']} Chosen because: {t['reason']}.", "",
              f"Scale (ratio {t['ratio']}, base {tok['font']['base_size']}px): " + ", ".join(f"{s}px" for s in tok["font"]["scale"]),
              f"Line height: body {tok['font']['line_height']}, headings {tok['font'].get('heading_line_height', 1.2)}", ""]
    lines += ["## Spacing, radius, elevation, motion", "",
              f"- Spacing scale (px): {', '.join(str(s) for s in tok['space'])}",
              "- Radius (px): " + ", ".join(f"{k} {v}" for k, v in tok["radius"].items()),
              "- Elevation: " + " / ".join(f"`{e}`" for e in tok["elevation"]),
              f"- Motion: {', '.join(str(x) for x in tok['motion']['durations_ms'])} ms, easing `{tok['motion']['easing']}`; "
              f"{spec.get('motion_notes', '')}",
              "- Reduced motion: remove movement; keep opacity changes under 150ms",
              f"- Touch target: {tok['touch_target']}px minimum; focus ring {tok['focus']['width']}px, offset {tok['focus']['offset']}px",
              f"- Icons: sizes {', '.join(str(x) for x in tok.get('icon', {}).get('sizes', []))} px, stroke "
              f"{tok.get('icon', {}).get('stroke', 'n/a')}; one family, one style per level",
              ""]
    lines += pattern_section(spec) + motion_section(spec) + ["## UX rules to review first", ""]
    lines += table(["ID", "Severity", "Rule", "How to check"], [[r["id"], r["severity"], r["rule"], r["check"]] for r in spec["ux_rules"]])
    if spec.get("charts"):
        lines += ["", "## Charts", ""]
        lines += table(["Question", "Use", "Avoid when", "Accessible fallback"],
                       [[c["matched_from"], c["best"], c["avoid_when"], c["a11y"]] for c in spec["charts"]])
    if spec.get("stack"):
        lines += ["", f"## Stack notes: {spec['stack']['name']}", ""] + [f"- {n}" for n in spec["stack"]["notes"]]
    lines += ["", "## Avoid", ""] + [f"- {a}" for a in spec.get("avoid", [])]
    lines += ["", "## Product risks to design for", ""] + [f"- {r}" for r in spec.get("risks", [])]
    lines += ["", "## Before delivery", "", "Run `references/pre-delivery-checklist.md` on the built interface. "
              "Critical lines that block delivery here:", ""] + [f"- [ ] {c}" for c in BLOCKERS]
    return "\n".join(lines) + "\n"


def pattern_section(spec: Dict[str, Any]) -> List[str]:
    """Landing pattern and in-product screen patterns, when the spec carries them."""
    pp = spec.get("page_patterns") or {}
    out = []
    for p in ([pp["landing"]] if pp.get("landing") else []) + pp.get("screens", []):
        out += [f"### {'Landing' if p['kind'] == 'landing' else 'Screen'}: {p['name']} (`{p['id']}`)", ""]
        out += [f"{i}. {sec}" for i, sec in enumerate(p["sections"], 1)]
        out += ["", f"- Primary action: {p['cta']}", f"- Evidence on the page: {p['proof']}", f"- Not when: {p['avoid_when']}", ""]
    return ["## Page patterns", ""] + out if out else []


def motion_section(spec: Dict[str, Any]) -> List[str]:
    """Per-interaction motion table for the spec's tier."""
    rows = [[m["name"], f"{m['ms']}ms", m["easing"], ", ".join(m["animate"]), m["reduced"], m["rule"]] for m in spec.get("motion_map", [])]
    if not rows:
        return []
    return [f"## Motion by interaction ({spec.get('motion_tier')})", ""] + table(
        ["Interaction", "Duration", "Easing", "Animate only", "Reduced motion", "Rule"], rows) + [""]


def css_block(selector: str, roles: Dict[str, str], indent: str = "") -> List[str]:
    """One selector block of colour custom properties."""
    return [f"{indent}{selector} {{"] + [f"{indent}  --{k.replace('_', '-')}: {v};" for k, v in roles.items()] + [f"{indent}}}"]


def css(spec: Dict[str, Any]) -> str:
    """CSS theme: light roles on :root, dark under the media query and a data-theme override."""
    tok = spec["tokens"]
    colours = tok["color"]
    first = "light" if "light" in colours else next(iter(colours))
    t = spec["typography"]
    out = [f"/* Theme generated from the design-direction spec for: {str(spec['brief']['product']).replace('*/', '* /')} */",
           f"/* Verdict: {spec['verdict']}. Contrast target {tok['contrast_target']}. */", ":root {"]
    out += [f"  color-scheme: {' '.join(colours)};"] + [f"  --{k.replace('_', '-')}: {v};" for k, v in colours[first].items()]
    out += [f"  --font-display: \"{t['display']}\", {t['fallback'].split(' / ')[0]};",
            f"  --font-body: \"{t['body']}\", {t['fallback'].split(' / ')[-1]};",
            f"  --font-mono: \"{t['mono']}\", ui-monospace, monospace;",
            f"  --font-size-base: {tok['font']['base_size']}px;", f"  --line-height-body: {tok['font']['line_height']};"]
    out += [f"  --font-size-{i}: {s}px;" for i, s in enumerate(tok["font"]["scale"])]
    out += [f"  --space-{i}: {s}px;" for i, s in enumerate(tok["space"], 1)]
    out += [f"  --radius-{k}: {v}px;" for k, v in tok["radius"].items()]
    out += [f"  --elevation-{i}: {e};" for i, e in enumerate(tok["elevation"])]
    names = ("fast", "base", "slow")
    out += [f"  --duration-{names[i] if i < 3 else i}: {d}ms;" for i, d in enumerate(tok["motion"]["durations_ms"])]
    out += [f"  --easing-standard: {tok['motion']['easing']};", f"  --touch-target: {tok['touch_target']}px;",
            f"  --focus-width: {tok['focus']['width']}px;", f"  --focus-offset: {tok['focus']['offset']}px;"]
    out += [f"  --icon-{n}: {v}px;" for n, v in zip(("sm", "md", "lg"), tok.get("icon", {}).get("sizes", []))]
    out += [f"  --icon-stroke: {tok['icon']['stroke']};"] if tok.get("icon") else []
    out += ["}", ""]
    if "dark" in colours and first != "dark":
        out += ["@media (prefers-color-scheme: dark) {"] + css_block(':root:not([data-theme="light"])', colours["dark"], "  ") + ["}", ""]
        out += css_block(':root[data-theme="dark"]', colours["dark"]) + [""]
    out += ["@media (prefers-reduced-motion: reduce) {", "  :root { --duration-fast: 0ms; --duration-base: 0ms; --duration-slow: 0ms; }",
            "  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;",
            "    transition-duration: 0.01ms !important; scroll-behavior: auto !important; }", "}", "",
            ":focus-visible { outline: var(--focus-width) solid var(--focus); outline-offset: var(--focus-offset); }"]
    return "\n".join(out) + "\n"


def text(spec: Dict[str, Any]) -> str:
    """Long-form terminal summary with the tightest contrast pair per mode."""
    tok, ty = spec["tokens"], spec["typography"]
    tight = {m: min(c, key=lambda x: x["ratio"] / x["min"]) for m, c in spec["palette"]["checks"].items() if c}
    rows = [("verdict", spec["verdict"]), ("product type", f"{spec['product_type']['name']} ({spec['product_type']['id']})"),
            ("direction", f"{spec['direction']['name']}: {spec['direction']['summary']}"),
            ("palette", f"{spec['palette']['name']} ({spec['palette']['id']}), modes {', '.join(tok['color'])}"),
            ("type", f"{ty['display']} / {ty['body']} / {ty['mono']}; base {tok['font']['base_size']}px, ratio {ty['ratio']}, "
                     f"scale {tok['font']['scale']} ({ty['reason']})"),
            ("spacing", f"{spec.get('density')} {tok['space']}"), ("radius", str(tok["radius"])),
            ("motion", f"{spec.get('motion_tier')} {tok['motion']['durations_ms']} ms, reduced motion honoured"),
            ("touch / focus", f"{tok['touch_target']}px / {tok['focus']['width']}px ring"),
            ("tightest pair", "; ".join(f"{m} {c['pair']} {c['ratio']}:1 (min {c['min']})" for m, c in tight.items())),
            ("rules", ", ".join(r["id"] for r in spec["ux_rules"])),
            ("charts", "; ".join(f"{c['matched_from']} -> {c['best']}" for c in spec.get("charts", [])) or "none"),
            ("patterns", ", ".join(p["id"] for p in [(spec.get("page_patterns") or {}).get("landing") or {}]
                                   + (spec.get("page_patterns") or {}).get("screens", []) if p) or "none"),
            ("stack", (spec.get("stack") or {}).get("name", "not set"))]
    out = [f"  {k:14} {v}" for k, v in rows]
    out += ["  findings       " + ("none" if not spec["findings"] else "")]
    out += [f"    [{f['level']}] {f['code']}: {f['message']}" for f in spec["findings"]]
    return "DESIGN SPEC\n" + "\n".join(out) + "\n"


def load_spec(path: str) -> Dict[str, Any]:
    """Read and shape-check a recommender spec."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise SpecError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except ValueError as exc:
        raise SpecError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecError("spec must be a JSON object produced by design_recommender.py --format json")
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise SpecError(f"not a recommender spec; missing keys: {', '.join(missing)}")
    if not isinstance(data["tokens"].get("color"), dict) or not data["tokens"]["color"]:
        raise SpecError("spec tokens carry no colour modes")
    for mode, roles in data["tokens"]["color"].items():
        if not isinstance(roles, dict) or any(r not in roles for r in ("bg", "fg", "primary", "focus")):
            raise SpecError(f"tokens.color.{mode} must hold at least bg, fg, primary and focus")
        bad = [k for k, v in roles.items() if not (isinstance(v, str) and re.fullmatch(r"#(?:[0-9a-fA-F]{3}){1,2}", v))]
        if bad:
            raise SpecError(f"tokens.color.{mode}: non-hex values for {', '.join(bad)}")
    for key in ("touch_target", "focus", "font", "space", "radius", "motion", "contrast_target"):
        if data["tokens"].get(key) in (None, "", [], {}):
            raise SpecError(f"tokens.{key} is missing; regenerate the spec with design_recommender.py")
    if not isinstance(data["palette"], dict):
        raise SpecError("spec.palette must be an object")
    return data


def main() -> None:
    """Parse arguments, render, exit with the contract code."""
    ap = argparse.ArgumentParser(description="Render a design-direction spec as markdown, CSS or tokens JSON.")
    ap.add_argument("--spec", required=True, help="spec JSON from design_recommender.py --format json")
    ap.add_argument("--format", choices=["markdown", "css", "json", "text"], default="markdown",
                    help="markdown document, CSS theme, bare tokens JSON for design_spec_checker.py, or text summary")
    args = ap.parse_args()
    try:
        spec = load_spec(args.spec)
        rendered = {"markdown": markdown, "css": css, "text": text}.get(args.format)
        output = rendered(spec) if rendered else json.dumps(spec["tokens"], indent=2) + "\n"
    except SpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except (KeyError, TypeError, AttributeError, ValueError, ZeroDivisionError, IndexError) as exc:
        print(f"error: spec is missing or mis-typed field {exc}; regenerate it with design_recommender.py", file=sys.stderr)
        sys.exit(2)
    sys.stdout.write(output)
    sys.exit(0 if spec["verdict"] == "CONSISTENT" else 1)


if __name__ == "__main__":
    main()
