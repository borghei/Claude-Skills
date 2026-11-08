#!/usr/bin/env python3
"""Extract design tokens from a CSS theme's custom properties into the tokens JSON shape
that design_spec_checker.py audits. Static parsing only, no browser.

Light values come from blocks outside any dark context; dark values from blocks whose
selector or at-rule prelude mentions "dark" (":not(...)" ignored), layered over the light
values as the cascade does. Nested rules and @layer/@media/@theme are followed; var()
chains and fallbacks are resolved. Colours: hex, rgb()/hsl() (either syntax), bare
"H S% L%" triplets, oklch()/oklab(), white/black, color-mix(in srgb, ...); translucent
roles are composited over the mode's background. "color-scheme: light" (or "dark") alone
marks a deliberate single-mode theme; "dark" alone moves undecorated blocks to dark.

Usage:
  python3 css_token_extractor.py --css theme.css --format json > tokens.json
  python3 css_token_extractor.py --css base.css dark.css      # :root split across files
Exit codes: 0 complete (bg/fg/primary per mode, both modes or a declared single mode,
spacing, radius, base size, every colour role understood), 1 gaps that leave the audit
partial, 2 unreadable file or no custom properties at all.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_ROLES = ("bg", "fg", "primary")
ROLE_ALIASES = {role: names.split() for role, names in (  # earlier aliases win: "muted-foreground" beats "muted"
    ("bg", "bg background page surface-page canvas"), ("surface", "surface card panel surface-1"),
    ("fg", "fg foreground text text-primary on-bg body"), ("muted_fg", "muted-fg muted-foreground text-muted text-secondary fg-muted muted"),
    ("primary", "primary brand action"), ("on_primary", "on-primary primary-foreground primary-fg on-brand"),
    ("accent", "accent secondary cta"), ("on_accent", "on-accent accent-foreground accent-fg"), ("border", "border line divider"),
    ("focus", "focus ring focus-ring outline"), ("danger", "danger destructive error critical"),
    ("on_danger", "on-danger destructive-foreground danger-fg on-error"), ("success", "success positive"))}
DECL_RE = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);?")
SCHEME_RE = re.compile(r"(?<![\w-])color-scheme\s*:\s*([^;]+)", re.I)
NUM_RE = re.compile(r"^(-?[0-9.]+)\s*(px|rem|em|ms|s)?$")
VAR_RE = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)\s*(?:,\s*((?:[^()]|\([^()]*\))*))?\)")
TRIPLET_RE = re.compile(r"^(-?[0-9.]+)(?:deg)?\s+([0-9.]+)%\s+([0-9.]+)%\s*(?:/\s*([0-9.]+%?))?$")
NAMED = {"white": (255, 255, 255, 1.0), "black": (0, 0, 0, 1.0), "transparent": (0, 0, 0, 0.0)}
RGBA = Tuple[float, float, float, float]
NUMERIC = [(r"^(space|spacing|gap|size-space)(-|$)", "space"), (r"^(radius|rounded|corner)", "radius"),
           (r"^(duration|motion-duration|transition-duration)", "duration"),
           (r"^(font-size-base|text-base|font-size-body|body-size)$", "base_size"),
           (r"^(line-height-body|leading-body|line-height-base|leading-normal)$", "line_height"),
           (r"^(font-size|text)-", "scale"), (r"^font-(family-)?(display|heading|body|sans|serif|mono|ui|base)$", "family"),
           (r"^(touch-target|tap-target|hit-target)$", "touch_target"),
           (r"^(focus-width|focus-ring-width|ring-width|outline-width)$", "focus")]


def _blocks(css: str) -> List[Tuple[str, str]]:
    """(context, declarations) pairs; context joins every enclosing prelude. Declarations
    before and after a nested rule stay with their own block."""
    out: List[Tuple[str, str]] = []
    stack: List[str] = []
    buf = ""
    for ch in re.sub(r"/\*.*?\*/", "", css, flags=re.S):
        if ch == "{":
            decls, _, prelude = buf.rpartition(";")
            if stack and decls.strip():
                out.append((" | ".join(stack), decls + ";"))
            stack.append(prelude.strip().lower())
            buf = ""
        elif ch == "}":
            if stack:
                if buf.strip():
                    out.append((" | ".join(stack), buf))
                stack.pop()
            buf = ""
        else:
            buf += ch
    return out


def _mode_of(context: str, root_mode: str) -> str:
    """dark / light for a block context; undecorated blocks belong to root_mode."""
    c = re.sub(r":not\((?:[^()]|\([^()]*\))*\)", "", context)
    if re.search(r"\bdark\b", c):
        return "dark"
    return "light" if re.search(r"\blight\b", c) else root_mode


def _tok(t: str, pct: float = 1.0) -> float:
    """One colour component: percentages scale to pct, angles become degrees."""
    t = t.strip().lower()
    if t == "none":
        return 0.0
    if t.endswith("%"):
        return float(t[:-1]) / 100 * pct
    for unit, f in (("deg", 1.0), ("grad", 0.9), ("rad", 180 / math.pi), ("turn", 360.0)):
        if t.endswith(unit):
            return float(t[: -len(unit)]) * f
    return float(t)


def _hsl(h: float, s: float, light: float) -> Tuple[float, float, float]:
    """HSL (degrees, 0-1, 0-1) to 0-255 sRGB."""
    def f(n: float) -> float:
        k = (n + h / 30) % 12
        return 255 * (light - s * min(light, 1 - light) * max(-1, min(k - 3, 9 - k, 1)))
    return f(0), f(8), f(4)


def _oklab(lightness: float, a: float, b: float) -> Tuple[float, float, float]:
    """OKLab to 0-255 sRGB, clamped to the sRGB gamut."""
    l_, m_, s_ = (lightness + 0.3963377774 * a + 0.2158037573 * b, lightness - 0.1055613458 * a - 0.0638541728 * b,
                  lightness - 0.0894841775 * a - 1.2914855480 * b)
    lc, mc, sc = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (4.0767416621 * lc - 3.3077115913 * mc + 0.2309699292 * sc, -1.2684380046 * lc + 2.6097574011 * mc - 0.3413193965 * sc,
           -0.0041960863 * lc - 0.7034186147 * mc + 1.7076147010 * sc)
    gam = [12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055 for x in (max(0.0, min(1.0, v)) for v in lin)]
    return gam[0] * 255, gam[1] * 255, gam[2] * 255


def _split_top(s: str) -> List[str]:
    """Split on commas outside parentheses."""
    marks = [i for i, depth in ((i, s[:i].count("(") - s[:i].count(")")) for i, ch in enumerate(s) if ch == ",") if depth == 0]
    return [s[a + 1:b] for a, b in zip([-1] + marks, marks + [len(s)])]


def parse_colour(value: str) -> Optional[RGBA]:
    """A CSS colour as (r, g, b, alpha) with channels 0-255, or None if unsupported."""
    v = value.strip().lower()
    try:
        if v in NAMED:
            return NAMED[v]
        if re.fullmatch(r"#[0-9a-f]{3,8}", v) and len(v) in (4, 5, 7, 9):
            h = v[1:] if len(v) > 5 else "".join(c * 2 for c in v[1:])
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255 if len(h) == 8 else 1.0)
        m = TRIPLET_RE.match(v)
        if m:
            return _hsl(float(m.group(1)), float(m.group(2)) / 100, float(m.group(3)) / 100) + (_tok(m.group(4)) if m.group(4) else 1.0,)
        m = re.fullmatch(r"color-mix\(\s*in\s+srgb\s*,(.*)\)", v)
        if m:
            (c1, p1), (c2, p2) = [re.fullmatch(r"\s*(.*?)\s*(?:\s([0-9.]+)%)?\s*", part).groups() for part in _split_top(m.group(1))]
            a, b = parse_colour(c1), parse_colour(c2)
            w = float(p1) / 100 if p1 else (1 - float(p2) / 100 if p2 else 0.5)
            return None if a is None or b is None else tuple(x * w + y * (1 - w) for x, y in zip(a, b))  # type: ignore
        m = re.fullmatch(r"(rgba?|hsla?|oklch|oklab)\((.*)\)", v)
        if not m:
            return None
        main, _, alpha = m.group(2).replace(",", " ").partition("/")
        t = main.split()
        if len(t) == 4 and not alpha:
            t, alpha = t[:3], t[3]
        if len(t) != 3:
            return None
        al = max(0.0, min(1.0, _tok(alpha))) if alpha.strip() else 1.0
        fn = m.group(1)
        if fn.startswith("rgb"):
            return (_tok(t[0], 255), _tok(t[1], 255), _tok(t[2], 255), al)
        if fn.startswith("hsl"):
            return _hsl(_tok(t[0]), float(t[1].rstrip("%")) / 100, float(t[2].rstrip("%")) / 100) + (al,)
        lightness = _tok(t[0])
        if fn == "oklch":
            c, hue = _tok(t[1], 0.4), math.radians(_tok(t[2]))
            return _oklab(lightness, c * math.cos(hue), c * math.sin(hue)) + (al,)
        return _oklab(lightness, _tok(t[1], 0.4), _tok(t[2], 0.4)) + (al,)
    except (ValueError, AttributeError, TypeError, ZeroDivisionError):
        return None


def _hex(c: RGBA) -> str:
    """Opaque channels to upper-case #RRGGBB."""
    return "#" + "".join(f"{max(0, min(255, round(x))):02X}" for x in c[:3])


def _number(value: str, unit_default: str = "px") -> Optional[float]:
    """Parse '16px', '1rem', '.2s', '200ms' or a bare number into px or ms."""
    m = NUM_RE.match(value.strip())
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2) or unit_default
    return {"rem": n * 16, "em": n * 16, "s": n * 1000}.get(unit, n)


def parse_css(css: str, root_mode: str = "auto") -> Dict[str, Any]:
    """Return a tokens dict (colour roles per mode plus numeric scales) from CSS text."""
    blocks = [(c, b) for c, b in _blocks(css) if "prefers-reduced-motion" not in c]  # overrides, not theme values
    schemes = [(c, set(re.findall(r"light|dark", v.lower()))) for c, b in blocks for v in SCHEME_RE.findall(b)]
    if root_mode == "auto":
        root_mode = "dark" if any(s == {"dark"} and _mode_of(c, "x") == "x" for c, s in schemes) else "light"
    props: Dict[str, Dict[str, str]] = {"light": {}, "dark": {}}
    for context, body in blocks:
        for name, value in DECL_RE.findall(body):
            props[_mode_of(context, root_mode)][name.lower()] = re.sub(r"\s*!important\s*$", "", value.strip(), flags=re.I)
    has_dark = bool(props["dark"])
    props["dark"] = {**props["light"], **props["dark"]} if props["light"] and has_dark else props["dark"]

    def resolve(value: str, mode: str, depth: int = 0) -> str:
        """Substitute var(--x, fallback) from the same mode until nothing changes."""
        new = VAR_RE.sub(lambda m: props[mode].get(m.group(1).lower()) or (m.group(2) or m.group(0)).strip(), value)
        return resolve(new, mode, depth + 1) if new != value and depth < 10 else new

    tokens: Dict[str, Any] = {"color": {}, "font": {"families": [], "scale": []}, "space": [], "radius": {}, "motion": {
        "durations_ms": [], "reduced_motion": "prefers-reduced-motion" in re.sub(r"/\*.*?\*/", "", css, flags=re.S)}}
    tokens.update({"modes": d} if (d := sorted(set().union(*(s for _, s in schemes)))) else {})
    unresolved, notes = [], []
    for mode in [m for m in ("light", "dark") if props[m] and (m == "light" or has_dark)]:
        names = {re.sub(r"^(color|colour|clr|c)-", "", n): n for n in props[mode]}
        raw = {role: props[mode][names[a]] for role, aliases in ROLE_ALIASES.items() for a in reversed(aliases) if a in names}
        parsed = {role: (resolve(v, mode), parse_colour(resolve(v, mode))) for role, v in raw.items()}
        bg = parsed.get("bg", ("", None))[1]
        base = (255.0, 255.0, 255.0) if mode == "light" else (0.0, 0.0, 0.0)
        bg_rgb = tuple(c * bg[3] + o * (1 - bg[3]) for c, o in zip(bg[:3], base)) if bg else base
        roles: Dict[str, str] = {}
        for role, (text, c) in parsed.items():
            if c is None:
                unresolved.append(f"{mode}: {role} = {text[:60]}")
                continue
            if c[3] < 1:
                over = base if role == "bg" else bg_rgb
                c = tuple(x * c[3] + o * (1 - c[3]) for x, o in zip(c[:3], over)) + (1.0,)
                notes.append(f"{mode}: {role} is translucent; composited over {'the page' if role == 'bg' else 'bg'}")
            roles[role] = text.upper() if re.fullmatch(r"#[0-9a-fA-F]{6}", text) else _hex(c)
        if roles:
            tokens["color"][mode] = roles
    families = set()
    num_mode = "light" if props["light"] else "dark"  # a dark-only theme keeps its scales in the dark block
    for name, raw_value in props[num_mode].items():
        value, font = resolve(raw_value, num_mode), tokens["font"]
        kind = next((k for pat, k in NUMERIC if re.match(pat, name)), None)
        n = _number(value, "ms" if kind == "duration" else "" if kind == "line_height" else "px")
        if kind == "family":
            families.add(value.split(",")[0].strip().strip("'\""))
        elif n is None or kind is None:
            continue
        elif kind in ("space", "scale", "duration"):
            (tokens["space"] if kind == "space" else font["scale"] if kind == "scale" else tokens["motion"]["durations_ms"]).append(n)
        elif kind == "radius":
            tokens["radius"][name] = n
        elif kind in ("base_size", "line_height"):
            font[kind] = n
        else:
            tokens[kind] = {"width": n} if kind == "focus" else n
    tokens["font"]["families"] = sorted(families)
    tokens["space"] = sorted(set(tokens["space"]))
    if tokens["font"].get("base_size"):
        tokens["font"]["scale"].append(tokens["font"]["base_size"])
    tokens["font"]["scale"] = sorted(set(tokens["font"]["scale"]))
    tokens["extraction"] = {"unresolved": unresolved, "notes": notes}
    return tokens


def gaps(tokens: Dict[str, Any]) -> List[str]:
    """What the audit will not be able to check."""
    out = []
    if not tokens["color"]:
        out.append("no colour roles recognised (names are matched after stripping a color- prefix)")
    for mode, roles in tokens["color"].items():
        missing = [r for r in REQUIRED_ROLES if r not in roles]
        if missing:
            out.append(f"{mode}: missing required colour roles {', '.join(missing)}")
    single = tokens.get("modes") in (["light"], ["dark"])
    if tokens["color"] and "dark" not in tokens["color"] and not single:
        out.append("no dark-mode block (prefers-color-scheme: dark, [data-theme=dark] or .dark); "
                   "declare color-scheme: light if the product is light-only")
    out += [f"colour value not understood, role skipped: {u}" for u in tokens["extraction"]["unresolved"]]
    return out + [msg for ok, msg in ((tokens["space"], "no spacing tokens (--space-* or --spacing)"),
                                      (tokens["radius"], "no radius tokens (--radius-*)"),
                                      (tokens["font"].get("base_size"), "no base font size (--font-size-base or --text-base)")) if not ok]


def main() -> None:
    """Parse arguments, extract tokens, print them, exit with the contract code."""
    ap = argparse.ArgumentParser(description="Extract design tokens from CSS custom properties.")
    ap.add_argument("--css", required=True, nargs="+", help="one or more CSS files, read in order (later files override)")
    ap.add_argument("--target", choices=["AA", "AAA"], default="AA", help="contrast target written into the tokens")
    ap.add_argument("--root-mode", choices=["auto", "light", "dark"], default="auto",
                    help="mode of blocks with no light/dark marker (auto: dark only when color-scheme says dark)")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format (json feeds the checker)")
    args = ap.parse_args()
    try:
        text = "\n".join(Path(p).read_text(encoding="utf-8") for p in args.css)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {getattr(exc, 'filename', None) or ', '.join(args.css)}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not DECL_RE.search(re.sub(r"/\*.*?\*/", "", text, flags=re.S)):
        print(f"error: no CSS custom properties (--name: value) found in {', '.join(args.css)}", file=sys.stderr)
        sys.exit(2)
    tokens = dict(parse_css(text, args.root_mode), contrast_target=args.target)
    problems = gaps(tokens)  # any gap means the audit downstream would be partial
    if args.format == "json":
        print(json.dumps(tokens, indent=2))
    else:
        print(f"CSS TOKENS  {', '.join(args.css)}  declared modes: {', '.join(tokens.get('modes', [])) or 'not declared'}")
        for mode, roles in tokens["color"].items():
            print(f"  {mode:6} {len(roles)} roles: " + ", ".join(f"{k} {v}" for k, v in roles.items()))
        print(f"  fonts  {', '.join(tokens['font']['families']) or 'none'}; base {tokens['font'].get('base_size', '-')}; "
              f"scale {tokens['font']['scale']}")
        print(f"  space  {tokens['space']}")
        print(f"  radius {sorted(tokens['radius'].values())}")
        print(f"  motion {tokens['motion']['durations_ms']} ms; reduced-motion block: {tokens['motion']['reduced_motion']}")
        print("\n".join([f"  [note] {n}" for n in tokens["extraction"]["notes"]] + [f"  [gap] {p}" for p in problems]))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
