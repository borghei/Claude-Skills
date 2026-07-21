#!/usr/bin/env python3
"""
Token Linter — structural audit of a design-token JSON file before it is
compiled into CSS. Catches the drift that makes a theme feel inconsistent:
off-scale spacing, non-monotonic color ramps, roles missing from one mode,
orphaned palette stops, and naming that will not survive a rename.

Usage:
    python3 token_linter.py --input tokens.json
    python3 token_linter.py --input tokens.json --format json
    python3 token_linter.py --input tokens.json --max-severity warning
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
ROLE_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def load_tokens(path: Path) -> Dict[str, Any]:
    """Load a design-token JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: token file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """Convert #rgb or #rrggbb to an (r, g, b) tuple of 0-255 integers."""
    body = str(value).lstrip("#")
    if len(body) == 3:
        body = "".join(c * 2 for c in body)
    if len(body) != 6:
        raise ValueError(f"'{value}' is not a 3- or 6-digit hex color")
    return int(body[0:2], 16), int(body[2:4], 16), int(body[4:6], 16)


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Compute WCAG relative luminance for an sRGB triple."""
    channels: List[float] = []
    for raw in rgb:
        c = raw / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def finding(severity: str, code: str, message: str, fix: str) -> Dict[str, str]:
    """Build a single lint finding record."""
    return {"severity": severity, "code": code, "message": message, "fix": fix}


def check_typography(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate the modular type scale definition."""
    out: List[Dict[str, str]] = []
    typo = tokens.get("typography")
    if not isinstance(typo, dict):
        return [finding("error", "TYPO_MISSING", "no 'typography' block",
                        "add typography with base_px, ratio, and steps")]
    ratio = float(typo.get("ratio", 0))
    if not 1.05 <= ratio <= 1.7:
        out.append(finding("error", "TYPO_RATIO",
                           f"type ratio {ratio} is outside the usable 1.05-1.7 range",
                           "use 1.2 (minor third) for dense docs, 1.25 for reports, 1.333 for decks"))
    base = float(typo.get("base_px", 0))
    if base < 16:
        out.append(finding("warning", "TYPO_BASE",
                           f"base font size {base}px is below the 16px readable minimum",
                           "set typography.base_px to 16-18 for body copy"))
    steps = typo.get("steps", [])
    if "base" not in steps:
        out.append(finding("error", "TYPO_ANCHOR", "type scale has no step named 'base'",
                           "add 'base' to typography.steps to anchor the scale"))
    measure = float(typo.get("measure_ch", 0))
    if measure and not 55 <= measure <= 85:
        out.append(finding("warning", "TYPO_MEASURE",
                           f"line measure {measure}ch is outside the 55-85ch comfort band",
                           "set typography.measure_ch to 66-75 for long-form documents"))
    return out


def check_spacing(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate that every spacing step is a clean multiple of the base unit."""
    out: List[Dict[str, str]] = []
    spacing = tokens.get("spacing", {})
    base = float(spacing.get("base_px", 0))
    if base not in (4.0, 8.0):
        out.append(finding("warning", "SPACE_BASE",
                           f"spacing base is {base}px; 4px or 8px grids compose best",
                           "set spacing.base_px to 8 (or 4 for dense UI-like documents)"))
    steps = [float(s) for s in spacing.get("steps", [])]
    if steps != sorted(steps):
        out.append(finding("error", "SPACE_ORDER", "spacing steps are not in ascending order",
                           "sort spacing.steps ascending so the scale reads predictably"))
    for step in steps:
        if step and (step * 2) % 1 != 0:
            out.append(finding("warning", "SPACE_FRACTION",
                               f"spacing step {step} is not a half-unit multiple",
                               "keep steps at whole or half multiples of the base unit"))
    return out


def check_ramps(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate that each color ramp darkens monotonically as its step rises."""
    out: List[Dict[str, str]] = []
    for ramp, stops in tokens.get("palette", {}).items():
        if len(stops) < 2:
            out.append(finding("warning", "RAMP_THIN", f"ramp '{ramp}' has {len(stops)} stop(s)",
                               "a ramp needs at least a light and a dark stop to theme both modes"))
            continue
        try:
            ordered = sorted(stops.items(), key=lambda kv: float(kv[0]))
        except ValueError:
            out.append(finding("error", "RAMP_KEYS", f"ramp '{ramp}' has non-numeric step keys",
                               "name ramp stops numerically (50, 100, ... 900)"))
            continue
        lums: List[float] = []
        for name, value in ordered:
            try:
                lums.append(relative_luminance(hex_to_rgb(value)))
            except ValueError as exc:
                out.append(finding("error", "RAMP_HEX", f"ramp '{ramp}.{name}': {exc}",
                                   "use #rgb or #rrggbb hex values"))
                lums.append(0.0)
        for i in range(1, len(lums)):
            if lums[i] > lums[i - 1]:
                out.append(finding("error", "RAMP_ORDER",
                                   f"ramp '{ramp}' brightens from {ordered[i-1][0]} to {ordered[i][0]}",
                                   "higher step numbers must be darker; swap the two hex values"))
                break
    return out


def check_roles(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate role naming, mode parity, and palette references."""
    out: List[Dict[str, str]] = []
    roles = tokens.get("roles", {})
    palette = tokens.get("palette", {})
    modes = list(roles)
    if "light" not in modes or "dark" not in modes:
        out.append(finding("error", "ROLE_MODES", f"roles define modes {modes}",
                           "define both a 'light' and a 'dark' role map"))
    for required in ("surface", "text", "border", "link"):
        for mode in modes:
            if required not in roles[mode]:
                out.append(finding("error", "ROLE_REQUIRED",
                                   f"'{mode}' mode is missing the '{required}' role",
                                   f"add a '{required}' entry to roles.{mode}"))
    if len(modes) == 2:
        a, b = modes
        for missing in set(roles[a]) ^ set(roles[b]):
            out.append(finding("error", "ROLE_PARITY",
                               f"role '{missing}' exists in only one mode",
                               "every role must be defined in both modes or theming will fall back"))
    used: set = set()
    for mode, role_map in roles.items():
        for name, value in role_map.items():
            if not ROLE_NAME_RE.match(name):
                out.append(finding("warning", "ROLE_NAME",
                                   f"role '{name}' is not lowercase-kebab-case",
                                   "rename to kebab-case so it maps cleanly to --color-<name>"))
            if isinstance(value, str) and "." in value and not value.startswith("#"):
                used.add(value)
                ramp, step = value.split(".", 1)
                if ramp not in palette or step not in palette.get(ramp, {}):
                    out.append(finding("error", "ROLE_REF",
                                       f"roles.{mode}.{name} points at missing '{value}'",
                                       "add the stop to the palette or repoint the role"))
            elif isinstance(value, str) and value.startswith("#"):
                out.append(finding("warning", "ROLE_LITERAL",
                                   f"roles.{mode}.{name} uses a literal hex",
                                   "point roles at palette stops so a ramp edit propagates"))
    for ramp, stops in palette.items():
        for step in stops:
            if f"{ramp}.{step}" not in used:
                out.append(finding("info", "PALETTE_ORPHAN",
                                   f"palette stop '{ramp}.{step}' is not used by any role",
                                   "delete it or bind it to a role; unused stops invite ad-hoc use"))
    return out


def lint(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Run every check and return the combined findings."""
    return (check_typography(tokens) + check_spacing(tokens)
            + check_ramps(tokens) + check_roles(tokens))


def output(findings: List[Dict[str, str]], threshold: str, fmt: str) -> int:
    """Print findings and return the count at or above the gate threshold."""
    limit = SEVERITY_ORDER[threshold]
    blocking = [f for f in findings if SEVERITY_ORDER[f["severity"]] >= limit]
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    if fmt == "json":
        print(json.dumps({
            "gate": "fail" if blocking else "pass",
            "threshold": threshold,
            "counts": counts,
            "findings": findings,
        }, indent=2))
        return len(blocking)
    print(f"Token lint - {counts['error']} error, {counts['warning']} warning, "
          f"{counts['info']} info\n")
    for sev in ("error", "warning", "info"):
        for f in [x for x in findings if x["severity"] == sev]:
            print(f"  [{sev.upper():<7}] {f['code']}: {f['message']}")
            print(f"            fix: {f['fix']}")
    if not findings:
        print("  no findings - token file is clean")
    print(f"\nGATE ({threshold}+): {'FAIL' if blocking else 'PASS'}")
    return len(blocking)


def main() -> None:
    """Parse arguments, lint the token file, and exit non-zero on failure."""
    parser = argparse.ArgumentParser(
        description="Lint a design-token JSON file for scale, ramp, and role consistency.")
    parser.add_argument("--input", required=True, help="path to the design-token JSON file")
    parser.add_argument("--max-severity", choices=["info", "warning", "error"],
                        default="error", dest="threshold",
                        help="lowest severity that fails the gate (default: error)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--no-gate", action="store_true",
                        help="always exit 0, even when findings block (report-only mode)")
    args = parser.parse_args()

    try:
        findings = lint(load_tokens(Path(args.input)))
        blocking = output(findings, args.threshold, args.format)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: token lint failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)
    if blocking and not args.no_gate:
        sys.exit(2)  # 2 = gate failed (1 is reserved for tool errors)


if __name__ == "__main__":
    main()
