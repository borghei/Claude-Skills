#!/usr/bin/env python3
"""
Theme Builder — compile a design-token JSON file into a single inlinable CSS
bundle with light/dark theming via CSS custom properties.

The bundle is self-contained: no @import, no web fonts, no external assets.
It is meant to be pasted into a <style> block of a standalone HTML document.

Usage:
    python3 theme_builder.py --input tokens.json
    python3 theme_builder.py --input tokens.json --out theme.css --format text
    python3 theme_builder.py --input tokens.json --format css > theme.css
    python3 theme_builder.py --input tokens.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HEX_CHARS = set("0123456789abcdefABCDEF")


def load_tokens(path: Path) -> Dict[str, Any]:
    """Load and minimally validate a token JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: token file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    if not isinstance(data, dict):
        raise SystemExit("error: token file must contain a JSON object at the top level")
    for key in ("typography", "spacing", "palette", "roles"):
        if key not in data:
            raise SystemExit(f"error: token file is missing required key '{key}'")
    return data


def resolve_color(value: str, palette: Dict[str, Dict[str, str]]) -> str:
    """Resolve a role value ('ramp.step' or a literal hex) to a hex string."""
    value = str(value).strip()
    if value.startswith("#"):
        body = value[1:]
        if len(body) in (3, 6) and all(c in HEX_CHARS for c in body):
            return value.lower()
        raise SystemExit(f"error: '{value}' is not a valid hex color")
    if "." not in value:
        raise SystemExit(f"error: role value '{value}' must be 'ramp.step' or a hex color")
    ramp, step = value.split(".", 1)
    if ramp not in palette:
        raise SystemExit(f"error: role references unknown palette ramp '{ramp}'")
    if step not in palette[ramp]:
        raise SystemExit(f"error: ramp '{ramp}' has no step '{step}'")
    return str(palette[ramp][step]).lower()


def type_scale(typography: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Compute px sizes for each named step of a modular type scale.

    The step named 'base' anchors the scale at base_px; steps before it are
    divided by the ratio, steps after are multiplied.
    """
    base = float(typography.get("base_px", 16))
    ratio = float(typography.get("ratio", 1.25))
    steps: List[str] = list(typography.get("steps", ["sm", "base", "lg"]))
    if "base" not in steps:
        raise SystemExit("error: typography.steps must include a step named 'base'")
    if ratio <= 1:
        raise SystemExit("error: typography.ratio must be greater than 1")
    anchor = steps.index("base")
    return [(name, round(base * (ratio ** (i - anchor)), 2)) for i, name in enumerate(steps)]


def spacing_scale(spacing: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Compute px values for each multiple of the spacing base unit."""
    base = float(spacing.get("base_px", 8))
    out: List[Tuple[str, float]] = []
    for step in spacing.get("steps", [0, 1, 2, 4]):
        name = str(step).replace(".", "_")
        out.append((name, round(base * float(step), 2)))
    return out


def build_css(tokens: Dict[str, Any]) -> str:
    """Render the full themed CSS bundle from resolved tokens."""
    typo = tokens["typography"]
    palette = tokens["palette"]
    roles = tokens["roles"]
    fonts = typo.get("fonts", {})
    lines: List[str] = [f"/* theme: {tokens.get('name', 'untitled')} */", ":root {"]

    for name, px in type_scale(typo):
        lines.append(f"  --font-size-{name}: {px}px;")
    for name, px in spacing_scale(tokens["spacing"]):
        lines.append(f"  --space-{name}: {px}px;")
    for name, value in tokens.get("radius", {}).items():
        lines.append(f"  --radius-{name}: {value};")
    lines.append(f"  --measure: {typo.get('measure_ch', 72)}ch;")
    lines.append(f"  --line-height-body: {typo.get('line_height_body', 1.6)};")
    lines.append(f"  --line-height-heading: {typo.get('line_height_heading', 1.2)};")
    for slot in ("body", "heading", "mono"):
        if slot in fonts:
            lines.append(f"  --font-{slot}: {fonts[slot]};")
    for role, value in roles.get("light", {}).items():
        lines.append(f"  --color-{role}: {resolve_color(value, palette)};")
    lines.append("  color-scheme: light dark;")
    lines.append("}")

    dark = "".join(
        f"\n  --color-{role}: {resolve_color(value, palette)};"
        for role, value in roles.get("dark", {}).items()
    )
    lines.append("")
    lines.append("@media (prefers-color-scheme: dark) {")
    lines.append("  :root {" + dark + "\n  }")
    lines.append("}")
    lines.append("")
    lines.append(':root[data-theme="dark"] {' + dark + "\n}")
    lines.append("")
    lines.append(':root[data-theme="light"] {')
    for role, value in roles.get("light", {}).items():
        lines.append(f"  --color-{role}: {resolve_color(value, palette)};")
    lines.append("}")
    lines.append(BASE_RULES)
    return "\n".join(lines)


BASE_RULES = """
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  padding: var(--space-4) var(--space-3);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: var(--font-body, serif);
  font-size: var(--font-size-base);
  line-height: var(--line-height-body);
}
main { max-width: var(--measure); margin: 0 auto; }
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading, sans-serif);
  line-height: var(--line-height-heading);
  margin: var(--space-4) 0 var(--space-2);
  text-wrap: balance;
}
h1 { font-size: var(--font-size-3xl); }
h2 { font-size: var(--font-size-xl); }
h3 { font-size: var(--font-size-lg); }
p, ul, ol, table, figure, blockquote, pre { margin: 0 0 var(--space-2); }
a { color: var(--color-link); }
small, .muted { color: var(--color-text-muted); font-size: var(--font-size-sm); }
hr { border: 0; border-top: 1px solid var(--color-border); margin: var(--space-4) 0; }
blockquote {
  border-left: 3px solid var(--color-accent);
  padding-left: var(--space-2);
  color: var(--color-text-muted);
}
code, pre { font-family: var(--font-mono, monospace); font-size: var(--font-size-sm); }
pre {
  background: var(--color-code-surface);
  color: var(--color-code-text);
  padding: var(--space-2);
  border-radius: var(--radius-md, 6px);
  overflow-x: auto;
}
code { background: var(--color-code-surface); padding: 0 0.25em; border-radius: var(--radius-sm, 3px); }
pre code { background: none; padding: 0; }
img { max-width: 100%; height: auto; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: var(--font-size-sm); }
th, td { border-bottom: 1px solid var(--color-border); padding: var(--space-1) var(--space-1_5, 8px); text-align: left; }
th { font-family: var(--font-heading, sans-serif); }
figure figcaption { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.callout-warn { border-left: 3px solid var(--color-warn); padding-left: var(--space-2); }
.callout-danger { border-left: 3px solid var(--color-danger); padding-left: var(--space-2); }
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
"""


def summarize(tokens: Dict[str, Any], css: str) -> Dict[str, Any]:
    """Build a machine-readable summary of what the bundle contains."""
    return {
        "theme": tokens.get("name", "untitled"),
        "type_steps": {n: px for n, px in type_scale(tokens["typography"])},
        "spacing_steps": {n: px for n, px in spacing_scale(tokens["spacing"])},
        "ramps": {k: len(v) for k, v in tokens["palette"].items()},
        "roles_light": len(tokens["roles"].get("light", {})),
        "roles_dark": len(tokens["roles"].get("dark", {})),
        "css_bytes": len(css.encode("utf-8")),
        "css_lines": css.count("\n") + 1,
    }


def output(summary: Dict[str, Any], css: str, fmt: str, out_path: Path) -> None:
    """Emit the requested representation to stdout."""
    if fmt == "css":
        print(css)
        return
    if fmt == "json":
        print(json.dumps(summary, indent=2))
        return
    print(f"Theme: {summary['theme']}")
    print(f"  type steps    : {len(summary['type_steps'])} "
          f"({min(summary['type_steps'].values())}px - {max(summary['type_steps'].values())}px)")
    print(f"  spacing steps : {len(summary['spacing_steps'])}")
    print(f"  color ramps   : {len(summary['ramps'])} "
          f"({sum(summary['ramps'].values())} stops)")
    print(f"  roles         : {summary['roles_light']} light / {summary['roles_dark']} dark")
    print(f"  bundle        : {summary['css_bytes']} bytes, {summary['css_lines']} lines")
    if out_path:
        print(f"  written to    : {out_path}")
    else:
        print("  (use --out PATH to write the CSS, or --format css to print it)")


def main() -> None:
    """Parse arguments, build the theme, and report."""
    parser = argparse.ArgumentParser(
        description="Compile design tokens into a single inlinable themed CSS bundle.")
    parser.add_argument("--input", required=True,
                        help="path to the design-token JSON file")
    parser.add_argument("--out",
                        help="write the generated CSS bundle to this path")
    parser.add_argument("--format", choices=["text", "json", "css"], default="text",
                        help="stdout format: text summary (default), json summary, or raw css")
    args = parser.parse_args()

    try:
        tokens = load_tokens(Path(args.input))
        css = build_css(tokens)
        out_path = Path(args.out) if args.out else None
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(css, encoding="utf-8")
        output(summarize(tokens, css), css, args.format, out_path)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not write output ({exc})", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: theme build failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
