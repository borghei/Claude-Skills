#!/usr/bin/env python3
"""
CSS Declarations — the parsing layer of design_system_validator.py.

Loads a design-token file, walks CSS rule blocks into declarations (property, value,
line, selector), extracts the token-checkable values per category, and finds the closest
token for an off-system value. Categories and their regexes are read from
references/token-categories.json. Run alone to see what the validator reads from a file.

Usage:
    python css_declarations.py --input styles.css
    python css_declarations.py --input styles.css --category colors --format json

Exit codes: 0 parsed, 2 missing or unreadable file.
"""

import argparse
import json
import os
import re
import sys

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "token-categories.json")
with open(_DATA, "r", encoding="utf-8") as _f:
    _MODEL = json.load(_f)

# CSS properties grouped by token category, with the value-extraction regex for each
TOKEN_CATEGORIES = _MODEL["categories"]

# Values to skip during validation (CSS keywords, special values)
SKIP_VALUES = set(_MODEL["skip_values"])


def load_tokens(path: str) -> dict:
    """Load design tokens from JSON: {category: {name: value} or [values]}.

    Categories match references/token-categories.json (colors, spacing, font_sizes,
    font_families, font_weights, line_heights, border_radii, shadows, breakpoints,
    z_indices, transitions); see assets/sample_tokens.json.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Token file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in token file: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict):
        print("Error: Token file must be a JSON object keyed by category", file=sys.stderr)
        sys.exit(2)

    # Normalize: extract just the values into flat sets
    normalized = {}
    for category, tokens in data.items():
        if isinstance(tokens, dict):
            normalized[category] = set(str(v).strip().lower() for v in tokens.values())
        elif isinstance(tokens, list):
            normalized[category] = set(str(v).strip().lower() for v in tokens)
        else:
            normalized[category] = set()

    return normalized


def normalize_color(color: str) -> str:
    """Normalize color to lowercase hex for comparison."""
    color = color.strip().lower()
    if color.startswith("#"):
        # Expand 3-char hex to 6-char
        hex_val = color.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        return f"#{hex_val[:6]}"
    return color


def normalize_value(value: str) -> str:
    """Normalize a CSS value for comparison."""
    value = value.strip().lower()
    # Remove extra whitespace
    value = re.sub(r"\s+", " ", value)
    return value


def parse_css_declarations(css_content: str) -> list[dict]:
    """Parse CSS into declarations with file position info."""
    declarations = []
    # Remove comments
    css_clean = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

    # Walk rule blocks so one-line and minified rules ("a { x: 1; y: 2 }") yield
    # every declaration, each with the line it starts on.
    for block in re.finditer(r"([^{}]*)\{([^{}]*)\}", css_clean):
        selector = block.group(1).strip().split("\n")[-1].strip()
        offset = block.start(2)
        for decl in block.group(2).split(";"):
            prop_match = re.match(r"\s*([\w-]+)\s*:\s*(.+?)\s*$", decl, re.DOTALL)
            if prop_match:
                line_num = css_clean[:offset + len(decl) - len(decl.lstrip())].count("\n") + 1
                declarations.append({
                    "property": prop_match.group(1).strip().lower(),
                    "value": " ".join(prop_match.group(2).split()),
                    "line": line_num,
                    "selector": selector,
                    "raw": " ".join(decl.split()),
                })
            offset += len(decl) + 1

    # Also extract media query breakpoints
    for match in re.finditer(r"@media[^{]*\{", css_clean):
        bp_match = re.search(r"(?:min|max)-width\s*:\s*(\d+(?:\.\d+)?(?:px|rem|em))", match.group())
        if bp_match:
            line = css_clean[:match.start()].count("\n") + 1
            declarations.append({
                "property": "__media_query__",
                "value": bp_match.group(1),
                "line": line,
                "selector": "@media",
                "raw": match.group().strip(),
            })

    return declarations


def extract_values_from_declaration(decl: dict, category: str) -> list[dict]:
    """Extract token-checkable values from a CSS declaration."""
    prop = decl["property"]
    value = decl["value"]
    cat_config = TOKEN_CATEGORIES.get(category, {})
    properties = cat_config.get("properties", [])
    pattern = cat_config.get("extract_pattern", "")

    # Special case for media queries
    if category == "breakpoints" and prop == "__media_query__":
        return [{"value": normalize_value(value), "original": value, "context": decl}]

    # Check if property matches category
    if prop not in properties:
        return []

    # Extract values using pattern
    results = []
    if pattern:
        matches = re.findall(pattern, value, re.IGNORECASE)
        for m in matches:
            normalized = normalize_value(m)
            if normalized not in SKIP_VALUES:
                results.append({
                    "value": normalized,
                    "original": m,
                    "context": decl,
                })

    return results

def find_closest_token(value: str, token_values: set, category: str) -> str | None:
    """Find the closest matching token value."""
    if category == "colors":
        return _find_closest_color(value, token_values)
    elif category in ("spacing", "font_sizes", "border_radii"):
        return _find_closest_numeric(value, token_values)
    return None


def _parse_numeric_value(val: str) -> float | None:
    """Extract numeric part from a CSS value like '16px' or '1.5rem'."""
    match = re.match(r"(-?\d+(?:\.\d+)?)", val)
    if match:
        return float(match.group(1))
    return None


def _find_closest_numeric(value: str, token_values: set) -> str | None:
    """Find closest numeric token value; on a tie the smaller token wins (deterministic)."""
    target = _parse_numeric_value(value)
    if target is None:
        return None

    closest = None
    min_diff = float("inf")

    for tv in sorted(token_values, key=lambda t: (_parse_numeric_value(t) or 0.0, t)):
        tv_num = _parse_numeric_value(tv)
        if tv_num is not None:
            diff = abs(target - tv_num)
            if diff < min_diff:
                min_diff = diff
                closest = tv

    return closest


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    """Convert hex to RGB tuple."""
    hex_val = hex_color.lstrip("#").lower()
    if len(hex_val) == 3:
        hex_val = "".join(c * 2 for c in hex_val)
    if len(hex_val) != 6:
        return None
    try:
        return (int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16))
    except ValueError:
        return None


def _find_closest_color(value: str, token_values: set) -> str | None:
    """Find closest color token by Euclidean distance in RGB space (ties: lowest hex wins)."""
    target_rgb = _hex_to_rgb(value)
    if target_rgb is None:
        return None

    closest = None
    min_dist = float("inf")

    for tv in sorted(token_values):
        tv_rgb = _hex_to_rgb(tv)
        if tv_rgb is not None:
            dist = sum((a - b) ** 2 for a, b in zip(target_rgb, tv_rgb)) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = tv

    return closest


def collect_css_files(path: str, glob_pattern: str = "*.css") -> list[str]:
    """Collect CSS files from a path (file or directory)."""
    if os.path.isfile(path):
        return [path]

    if not os.path.isdir(path):
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(2)

    # Simple glob matching for *.css files
    files = []
    for root, dirs, filenames in os.walk(path):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "dist", "build", "vendor")]
        for fname in filenames:
            if glob_pattern == "*.css" and fname.endswith(".css"):
                files.append(os.path.join(root, fname))
            elif glob_pattern == "*.scss" and fname.endswith(".scss"):
                files.append(os.path.join(root, fname))
            elif glob_pattern == "*" and (fname.endswith(".css") or fname.endswith(".scss")):
                files.append(os.path.join(root, fname))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description="CSS Declarations — show the declarations and token values the validator reads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input styles.css
  %(prog)s --input styles.css --category colors --format json
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to one CSS file")
    parser.add_argument("--category", "-c", choices=list(TOKEN_CATEGORIES),
                        help="Only show values extracted for this token category")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            css = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error: Cannot read {args.input}: {e}", file=sys.stderr)
        sys.exit(2)

    rows = []
    for decl in parse_css_declarations(css):
        cats = [args.category] if args.category else list(TOKEN_CATEGORIES)
        values = {c: [v["value"] for v in extract_values_from_declaration(decl, c)] for c in cats}
        values = {c: v for c, v in values.items() if v}
        if args.category and not values:
            continue
        rows.append({"line": decl["line"], "selector": decl["selector"], "property": decl["property"],
                     "value": decl["value"], "token_values": values})

    if args.format == "json":
        print(json.dumps({"input": args.input, "declarations": rows}, indent=2))
    else:
        print(f"{len(rows)} declarations in {args.input}")
        for r in rows:
            found = "; ".join(f"{c}={', '.join(v)}" for c, v in r["token_values"].items())
            print(f"  {r['line']:>4}  {r['selector']} {{ {r['property']}: {r['value']} }}"
                  + (f"  -> {found}" if found else ""))


if __name__ == "__main__":
    main()
