#!/usr/bin/env python3
"""Audit a design token file against the bundled UX rules (contrast, type, spacing,
radius, motion, touch target, focus ring).

Usage:
  python3 design_spec_checker.py --tokens assets/sample_tokens.json
  python3 design_spec_checker.py --tokens spec.json --target AAA --format json
  python3 css_token_extractor.py --css theme.css --format json | python3 design_spec_checker.py --tokens -
  python3 design_spec_checker.py --palettes            # self-check every bundled palette

Accepts a bare tokens JSON or the recommender's JSON output (reads its "tokens" block);
"-" reads stdin. CSS themes go through css_token_extractor.py first.
Exit codes: 0 no critical/high findings, 1 critical/high findings (or any finding with
--strict), 2 unreadable or unusable input.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REF = Path(__file__).resolve().parent.parent / "references"
SEV = {"critical": 0, "high": 1, "medium": 2, "low": 3}
REQUIRED_ROLES = ("bg", "fg", "primary")
RULES: Dict[str, Dict[str, Any]] = {}


class TokenError(Exception):
    """Unusable input or bundled data; exits 2."""


def load_ref(name: str, key: str) -> List[Dict[str, Any]]:
    """Rows of one bundled reference file."""
    try:
        return json.loads((REF / name).read_text(encoding="utf-8"))[key]
    except (OSError, ValueError, KeyError) as exc:
        raise TokenError(f"bundled data {name} unreadable: {exc}") from exc


def is_hex(v: Any) -> bool:
    """True for #RGB / #RRGGBB strings."""
    return isinstance(v, str) and bool(re.fullmatch(r"#(?:[0-9a-fA-F]{3}){1,2}", v.strip()))


def norm_hex(v: str) -> str:
    """Upper-case #RRGGBB."""
    v = v.strip().lstrip("#")
    return "#" + ("".join(c * 2 for c in v) if len(v) == 3 else v).upper()


def lum(v: str) -> float:
    """WCAG 2.x relative luminance."""
    h = norm_hex(v)[1:]
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio, 2 decimals."""
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return round((hi + 0.05) / (lo + 0.05), 2)


def _f(rule: str, message: str, mode: str = "", severity: str = "") -> Dict[str, Any]:
    """Finding tied to a UX rule; severity comes from the rule unless a missing token lowers it."""
    r = RULES[rule]
    return {"rule": rule, "severity": severity or r["severity"], "category": r["category"],
            "message": (f"[{mode}] " if mode else "") + message}


def check_colour(tokens: Dict[str, Any], target: str) -> List[Dict[str, Any]]:
    """Contrast and dark-mode checks for every colour mode present."""
    out: List[Dict[str, Any]] = []
    colours = tokens.get("color") or {}
    if not colours:
        return [_f("A11Y-01", "no colour roles found; cannot verify contrast")]
    declared = tokens.get("modes")
    if "dark" not in colours and not (isinstance(declared, list) and "dark" not in declared):
        out.append(_f("CLR-02", "no dark-mode roles defined; dark mode will be an inversion or missing "
                                "(declare \"modes\": [\"light\"] or color-scheme: light if light-only is deliberate)"))
    text_min = 7.0 if target == "AAA" else 4.5
    for mode, roles in colours.items():
        if not isinstance(roles, dict):
            raise TokenError(f"color.{mode} must be an object of role -> hex")
        bad = [k for k, v in roles.items() if not is_hex(v)]
        if bad:
            raise TokenError(f"color.{mode}: non-hex values for {', '.join(bad)}")
        missing = [r for r in REQUIRED_ROLES if r not in roles]
        if missing:
            out.append(_f("A11Y-01", f"missing required roles: {', '.join(missing)}", mode))
            continue
        pairs = [("A11Y-01", "fg", "bg", text_min), ("A11Y-01", "fg", "surface", text_min),
                 ("A11Y-02", "muted_fg", "bg", text_min), ("A11Y-02", "muted_fg", "surface", text_min),
                 ("A11Y-04", "on_primary", "primary", 4.5), ("A11Y-04", "on_accent", "accent", 4.5),
                 ("A11Y-04", "on_danger", "danger", 4.5), ("A11Y-03", "primary", "bg", 3.0),
                 ("A11Y-03", "focus", "bg", 3.0), ("CLR-05", "danger", "bg", 4.5), ("A11Y-01", "success", "bg", 4.5)]
        for rule, a, b, minimum in pairs:
            if a in roles and b in roles:
                ratio = contrast(roles[a], roles[b])
                if ratio < minimum:
                    out.append(_f(rule, f"{a} {roles[a]} on {b} {roles[b]} is {ratio}:1, needs {minimum}:1", mode))
        if mode == "dark" and norm_hex(roles["bg"]) == "#000000" and norm_hex(roles["fg"]) == "#FFFFFF":
            out.append(_f("CLR-03", "pure white on pure black; lift the background or soften the text", mode))
    return out


def check_type(font: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Base size, line height, family count and scale consistency."""
    out: List[Dict[str, Any]] = []
    base = font.get("base_size")
    if isinstance(base, (int, float)) and base < 16:
        out.append(_f("TYP-01", f"body size {base}px is under 16px"))
    scale = sorted(x for x in font.get("scale", []) if isinstance(x, (int, float)))
    if scale and scale[0] < 12:
        out.append(_f("TYP-01", f"smallest type step {scale[0]}px is under 12px"))
    lh = font.get("line_height")
    if isinstance(lh, (int, float)) and not 1.4 <= lh <= 1.7:
        out.append(_f("TYP-02", f"body line height {lh} is outside 1.4-1.7"))
    families = [f for f in font.get("families", []) if f not in ("system-ui", "ui-monospace")]
    if len(families) > 3:
        out.append(_f("PRF-03", f"{len(families)} font families ({', '.join(families)}); keep to two plus a mono"))
    for a, b in zip(scale, scale[1:]):
        ratio = b / a
        if ratio < 1.07 or ratio > 1.62:
            out.append(_f("TYP-04", f"type step {a}px -> {b}px is a {ratio:.2f}x jump (keep 1.07-1.62)"))
    return out


def check_layout(tokens: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Spacing grid, scale size, near-duplicates and radius count."""
    out: List[Dict[str, Any]] = []
    space = sorted(x for x in tokens.get("space", []) if isinstance(x, (int, float)) and x > 0)
    off = [x for x in space if x % 4 and x != 2]
    if off:
        out.append(_f("LAY-02", f"spacing values off the 4px grid: {', '.join(f'{x:g}' for x in off)}"))
    if len(space) > 12:
        out.append(_f("LAY-03", f"{len(space)} spacing steps; keep to 12 or fewer"))
    close = [(a, b) for a, b in zip(space, space[1:]) if a >= 8 and b / a < 1.2]
    if close:
        out.append(_f("LAY-03", "near-duplicate spacing steps: " + ", ".join(f"{a:g}/{b:g}" for a, b in close)))
    radius = tokens.get("radius", {})
    values = radius.values() if isinstance(radius, dict) else radius
    distinct = {v for v in values if isinstance(v, (int, float)) and 0 < v < 999}
    if len(distinct) > 4:
        out.append(_f("LAY-04", f"{len(distinct)} corner radii ({', '.join(f'{v:g}' for v in sorted(distinct))}); keep to four"))
    return out


def check_motion_touch(tokens: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Durations, reduced motion, touch target and focus ring."""
    out: List[Dict[str, Any]] = []
    motion = tokens.get("motion", {})
    durations = [d for d in motion.get("durations_ms", []) if isinstance(d, (int, float))]
    slow = [d for d in durations if d > 500]
    fast = [d for d in durations if 0 < d < 80]
    if slow:
        out.append(_f("MOT-02", f"durations over 500ms: {', '.join(f'{d:g}' for d in slow)}"))
    if fast:
        out.append(_f("MOT-02", f"durations under 80ms read as no transition: {', '.join(f'{d:g}' for d in fast)}"))
    if durations and not motion.get("reduced_motion"):
        out.append(_f("MOT-01", "motion tokens present but no reduced-motion handling declared"))
    touch = tokens.get("touch_target")
    if isinstance(touch, (int, float)) and touch < 44:
        out.append(_f("TCH-01", f"touch target {touch:g}px is under 44px" + (" and under the 24px WCAG minimum" if touch < 24 else ""),
                      severity="" if touch < 24 else "high"))
    elif touch is None:
        out.append(_f("TCH-01", "no touch_target token; hit areas are unspecified, measure them by hand", severity="medium"))
    focus = tokens.get("focus") or {}
    width = focus.get("width") if isinstance(focus, dict) else None
    if width is None:
        out.append(_f("A11Y-05", "no focus ring width token; check the focus style by hand", severity="medium"))
    elif width < 2:
        out.append(_f("A11Y-05", f"focus ring {width:g}px is thinner than 2px"))
    return out


def load_tokens(path: str) -> Dict[str, Any]:
    """Read tokens JSON (bare tokens or a recommender spec) from a file or stdin."""
    if path.lower().endswith(".css"):
        raise TokenError("CSS input: run css_token_extractor.py --css FILE --format json and pipe it here with --tokens -")
    try:
        raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
    except OSError as exc:
        raise TokenError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except ValueError as exc:
        raise TokenError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise TokenError("token JSON must be an object")
    tokens = data.get("tokens", data)
    if not isinstance(tokens, dict) or not any(k in tokens for k in ("color", "font", "space")):
        raise TokenError("no tokens found: expected color/font/space keys (or a 'tokens' block)")
    if "modes" in tokens and not (isinstance(tokens["modes"], list) and set(tokens["modes"]) <= {"light", "dark"} and tokens["modes"]):
        raise TokenError('tokens.modes must be a non-empty list drawn from "light" and "dark"')
    shapes = {"color": dict, "font": dict, "space": list, "radius": (dict, list), "motion": dict, "focus": dict}
    for key, kind in shapes.items():
        if key in tokens and not isinstance(tokens[key], kind):
            raise TokenError(f"tokens.{key} has the wrong type ({type(tokens[key]).__name__})")
    font, motion = tokens.get("font") or {}, tokens.get("motion") or {}
    numbers = [("space", tokens.get("space") or []), ("font.scale", font.get("scale") or []),
               ("motion.durations_ms", motion.get("durations_ms") or []),
               ("radius", list((tokens.get("radius") or {}).values()) if isinstance(tokens.get("radius"), dict) else tokens.get("radius") or [])]
    for name, values in numbers:
        if not isinstance(values, list) or not all(_num(v) and v >= 0 for v in values):
            raise TokenError(f"tokens.{name} must be a list of non-negative numbers")
    for name, v in (("font.base_size", font.get("base_size")), ("font.line_height", font.get("line_height")),
                    ("touch_target", tokens.get("touch_target")), ("focus.width", (tokens.get("focus") or {}).get("width"))):
        if v is not None and not (_num(v) and v > 0):
            raise TokenError(f"tokens.{name} must be a positive number")
    if not isinstance(font.get("families", []), list) or not all(isinstance(f, str) for f in font.get("families", [])):
        raise TokenError("tokens.font.families must be a list of strings")
    return tokens


def _num(v: Any) -> bool:
    """A finite int or float that is not a bool."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def audit(tokens: Dict[str, Any], target: str) -> Dict[str, Any]:
    """Run every check and summarise by severity."""
    findings = (check_colour(tokens, target) + check_type(tokens.get("font") or {})
                + check_layout(tokens) + check_motion_touch(tokens))
    findings.sort(key=lambda f: (SEV[f["severity"]], f["rule"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEV}
    return {"target": target, "modes": sorted((tokens.get("color") or {}).keys()), "counts": counts, "findings": findings,
            "passed": counts["critical"] == 0 and counts["high"] == 0}


def audit_palettes(target: str) -> Dict[str, Any]:
    """Self-check every bundled palette in both modes."""
    results = []
    for pal in load_ref("palettes.json", "palettes"):
        findings = check_colour({"color": {"light": pal["light"], "dark": pal["dark"]}}, target)
        results.append({"id": pal["id"], "findings": findings})
    failing = [r for r in results if r["findings"]]
    return {"target": target, "palettes": len(results), "failing": len(failing), "results": results,
            "passed": not failing}


def main() -> None:
    """Parse arguments, run the audit and exit with the contract code."""
    ap = argparse.ArgumentParser(description="Audit design tokens against the bundled UX rules.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--tokens", help="tokens JSON or recommender spec JSON; - reads stdin")
    src.add_argument("--palettes", action="store_true", help="self-check the bundled palettes")
    ap.add_argument("--target", choices=["AA", "AAA"], help="contrast target (default: file's contrast_target or AA)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding, not only critical/high")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        RULES.update({r["id"]: r for r in load_ref("ux-rules.json", "rules")})
        if args.palettes:
            report = audit_palettes(args.target or "AA")
        else:
            tokens = load_tokens(args.tokens)
            if tokens.get("contrast_target", "AA") not in ("AA", "AAA"):
                raise TokenError("contrast_target must be AA or AAA")
            report = audit(tokens, args.target or tokens.get("contrast_target", "AA"))
    except TokenError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except (TypeError, AttributeError, ValueError, ZeroDivisionError, KeyError) as exc:
        print(f"error: tokens file has an unexpected shape ({exc}); see references/design-decision-guide.md", file=sys.stderr)
        sys.exit(2)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif args.palettes:
        print(f"PALETTES  {report['palettes'] - report['failing']}/{report['palettes']} pass {report['target']}")
        for r in report["results"]:
            print(f"  {'ok  ' if not r['findings'] else 'FAIL'} {r['id']}" + "".join(f"\n       {f['message']}" for f in r["findings"]))
    else:
        c = report["counts"]
        print(f"TOKEN AUDIT  {'PASS' if report['passed'] else 'FAIL'}  target {report['target']}  modes {', '.join(report['modes']) or 'none'}")
        print(f"  critical {c['critical']}  high {c['high']}  medium {c['medium']}  low {c['low']}")
        for f in report["findings"]:
            print(f"  [{f['severity']:8}] {f['rule']}  {f['message']}")
        if not report["findings"]:
            print("  clean: every automated rule passed; review the manual rules in references/ux-rules.json")
    failed = not report["passed"] or (args.strict and not args.palettes and report["findings"])
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
