#!/usr/bin/env python3
"""Check the text-bearing colour pairs of a design_token_generator.py tokens JSON
against WCAG 2.x contrast, and name the primary shade to use when the brand colour fails.

Usage:
    python3 token_contrast_checker.py --tokens ../assets/sample_tokens.json
    python3 token_contrast_checker.py --tokens tokens.json --target AAA --format json
    python3 design_token_generator.py "#FF6B6B" playful json | python3 token_contrast_checker.py --tokens -
    python3 token_contrast_checker.py --tokens t.json --pair surface.background:primary.600 \\
        --pair primary.DEFAULT:surface.background:3      # focus ring, non-text 3:1

Pairs checked (normal-size text, so 4.5:1 for AA, 7:1 for AAA):
    body text      surface.foreground on surface.background
    muted text     neutral.500 on surface.background
    link text      primary.DEFAULT on surface.background
    button label   surface.background on primary.DEFAULT (white label on a brand fill)
    <semantic>     semantic.<name>.contrast on semantic.<name>.base
    --pair FG:BG[:MIN]  extra pairs a component adds; FG/BG are #RRGGBB or a path under
                   colors (primary.600); MIN overrides the target (3 for non-text or large text)
Exit codes: 0 every pair passes, 1 at least one pair fails, 2 unreadable or incomplete input.
"""

import argparse
import json
import re
import sys
from typing import Dict, List

TARGETS = {"AA": 4.5, "AAA": 7.0}
HEX6 = re.compile(r"#[0-9a-fA-F]{6}")


class CheckError(Exception):
    """Unusable input; exits 2."""


def luminance(hex_color: str) -> float:
    """WCAG 2.x relative luminance of #RRGGBB."""
    h = hex_color.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def pick(colors: Dict, path: str) -> str:
    """Colour at a dotted path under tokens.colors, validated as #RRGGBB."""
    node = colors
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise CheckError(f"tokens missing colors.{path}")
        node = node[part]
    if not isinstance(node, str) or not HEX6.fullmatch(node.strip()):
        raise CheckError(f"colors.{path} is not a #RRGGBB colour: {node!r}")
    return node.strip()


def load(path: str) -> Dict:
    """Tokens JSON from a file or '-' (stdin)."""
    try:
        if path == "-":
            text = sys.stdin.read()
        else:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        data = json.loads(text)
    except (OSError, ValueError) as exc:
        raise CheckError(f"cannot read tokens JSON ({path}): {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("colors"), dict):
        raise CheckError("input has no 'colors' object; pass the generator's json output")
    return data


def resolve(colors: Dict, ref: str) -> str:
    """A #RRGGBB literal or a dotted path under colors."""
    ref = ref.strip()
    if HEX6.fullmatch(ref):
        return ref
    if ref.startswith("#"):
        raise CheckError(f"colour '{ref}' is not #RRGGBB")
    return pick(colors, ref)


def parse_extra(colors: Dict, specs: List[str], need: float) -> List[tuple]:
    """--pair FG:BG[:MIN] specs to (label, fg, bg, min) tuples."""
    out = []
    for spec in specs:
        parts = spec.split(":")
        if len(parts) not in (2, 3):
            raise CheckError(f"--pair must be FG:BG or FG:BG:MIN, got '{spec}'")
        try:
            minimum = float(parts[2]) if len(parts) == 3 else need
        except ValueError as exc:
            raise CheckError(f"--pair minimum must be a number, got '{parts[2]}'") from exc
        if not 1.0 <= minimum <= 21.0:
            raise CheckError(f"--pair minimum must be between 1 and 21, got {minimum}")
        out.append((f"{parts[0]} on {parts[1]}", resolve(colors, parts[0]),
                    resolve(colors, parts[1]), minimum))
    return out


def check(tokens: Dict, target: str, extra: List[str] = ()) -> Dict:
    """All pair results, failures, and a suggested primary shade."""
    colors, need = tokens["colors"], TARGETS[target]
    bg = pick(colors, "surface.background")
    pairs = [
        ("body text", pick(colors, "surface.foreground"), bg),
        ("muted text", pick(colors, "neutral.500"), bg),
        ("link text", pick(colors, "primary.DEFAULT"), bg),
        ("button label", bg, pick(colors, "primary.DEFAULT")),
    ]
    for name in sorted(colors.get("semantic", {})):
        pairs.append((f"{name} label", pick(colors, f"semantic.{name}.contrast"),
                      pick(colors, f"semantic.{name}.base")))
    if len(pairs) == 4:
        raise CheckError("tokens have no colors.semantic entries")
    pairs = [(p, fg, b, need) for p, fg, b in pairs] + parse_extra(colors, list(extra), need)
    rows = [{"pair": p, "fg": fg, "bg": b, "ratio": round(ratio(fg, b), 2), "min": m,
             "pass": ratio(fg, b) >= m} for p, fg, b, m in pairs]
    suggestion = None
    if any(not r["pass"] for r in rows if r["pair"] in ("link text", "button label")):
        steps = sorted((k for k in colors["primary"] if k.isdigit()), key=int)
        for step in steps:
            shade = pick(colors, f"primary.{step}")
            if ratio(shade, bg) >= need:
                suggestion = {"shade": f"primary.{step}", "hex": shade,
                              "ratio": round(ratio(shade, bg), 2)}
                break
    failed = [r["pair"] for r in rows if not r["pass"]]
    return {"target": target, "min_ratio": need, "pairs": rows, "failed": failed,
            "primary_suggestion": suggestion, "verdict": "FAIL" if failed else "PASS"}


def as_text(result: Dict) -> str:
    """Human-readable report."""
    out = [f"Contrast check, WCAG {result['target']} ({result['min_ratio']}:1 normal text)", ""]
    for r in result["pairs"]:
        mark = "pass" if r["pass"] else "FAIL"
        floor = "" if r["min"] == result["min_ratio"] else f"  (min {r['min']:g}:1)"
        out.append(f"  {mark}  {r['pair']:<14} {r['fg']} on {r['bg']}  {r['ratio']:.2f}:1{floor}")
    sug = result["primary_suggestion"]
    if sug:
        out += ["", f"Brand colour fails as text/fill. Use {sug['shade']} ({sug['hex']}, "
                f"{sug['ratio']:.2f}:1) for links and button fills; keep the brand hex for "
                "large or decorative use."]
    elif any(p in result["failed"] for p in ("link text", "button label")):
        out += ["", "No primary shade reaches the target on this background; pick a darker brand tone."]
    out += ["", f"Verdict: {result['verdict']} ({len(result['failed'])} of {len(result['pairs'])} pairs fail)"]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WCAG contrast check for a generated tokens JSON.",
        epilog="Exit codes: 0 all pairs pass, 1 a pair fails, 2 unreadable or incomplete input.")
    parser.add_argument("--tokens", required=True, help="tokens JSON from design_token_generator.py, or - for stdin")
    parser.add_argument("--target", choices=sorted(TARGETS), default="AA", help="WCAG level (default AA)")
    parser.add_argument("--pair", action="append", default=[], metavar="FG:BG[:MIN]",
                        help="extra pair to check; colours are #RRGGBB or paths like primary.600 (repeatable)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default text)")
    args = parser.parse_args()
    try:
        result = check(load(args.tokens), args.target, args.pair)
    except CheckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.format == "json" else as_text(result))
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
