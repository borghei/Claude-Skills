#!/usr/bin/env python3
"""Design Token Generator: a full token system (colour, type, spacing, sizing, borders,
shadows, motion, breakpoints, z-index) from one brand colour and a style preset.

Usage:
    python3 design_token_generator.py [brand_color] [style] [output]
    python3 design_token_generator.py "#0066CC" modern json > tokens.json
    python3 design_token_generator.py "#8B4513" classic css
    python3 design_token_generator.py "#FF6B6B" playful scss
    python3 design_token_generator.py "#0066CC" --format text      # summary

brand_color  #RRGGBB or #RGB (default #0066CC)
style        modern | classic | playful (default modern)
output       json | css | scss | summary (default json)
--format     text | json | css | scss; overrides output (text = summary)

Primary and secondary scales are computed from the brand colour; everything else comes
from ../references/token-presets.json. Semantic `contrast` is the first of white,
neutral-900, black that reaches 4.5:1 on the base colour.
Check the result with token_contrast_checker.py.
Exit codes: 0 tokens written, 2 bad colour, unknown style or unreadable presets.
"""

import argparse
import colorsys
import json
import os
import re
import sys
from typing import Dict, List, Tuple

PRESETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "references", "token-presets.json")
STYLES = ("modern", "classic", "playful")
HEX_RE = re.compile(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})")


class TokenInputError(Exception):
    """Unusable input or bundled data; exits 2."""


def load_presets(path: str = PRESETS_PATH) -> Dict:
    """Bundled preset data."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        raise TokenInputError(f"presets unreadable ({path}): {exc}") from exc


def normalise_hex(value: str) -> str:
    """'#RRGGBB' as given (case kept); '#RGB' and a missing '#' are expanded/added."""
    match = HEX_RE.fullmatch(value.strip())
    if not match:
        raise TokenInputError(f"brand colour must be a hex colour like #0066CC, got '{value}'")
    digits = match.group(1)
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits).upper()
    return "#" + digits


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.x relative luminance of #RRGGBB."""
    h = hex_color.lstrip("#")
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    chans = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def contrast_ratio(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two #RRGGBB colours."""
    la, lb = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class DesignTokenGenerator:
    """Generate a design token system from a brand colour and style preset."""

    def __init__(self, presets: Dict = None):
        self.presets = presets if presets is not None else load_presets()
        self.base_unit = self.presets["base_unit"]  # 8pt grid
        self.type_scale_ratio = self.presets["type_scale_ratio"]  # major third
        self.base_font_size = self.presets["base_font_size"]

    def generate_complete_system(self, brand_color: str = "#0066CC", style: str = "modern") -> Dict:
        """All token categories, in a stable order."""
        meta = self.presets["meta"]
        return {
            "meta": {"version": meta["version"], "style": style, "generated": meta["generated"]},
            "colors": self.generate_color_palette(brand_color),
            "typography": self.generate_typography_system(style),
            "spacing": self.generate_spacing_system(),
            "sizing": self.generate_sizing_tokens(),
            "borders": self.generate_border_tokens(style),
            "shadows": self.generate_shadow_tokens(style),
            "animation": self.generate_animation_tokens(),
            "breakpoints": self.generate_breakpoints(),
            "z-index": self.generate_z_index_scale(),
        }

    def generate_color_palette(self, brand_color: str) -> Dict:
        """Primary and complementary secondary scales plus fixed neutral/semantic/surface."""
        semantic = {}
        for name, shades in self.presets["semantic"].items():
            semantic[name] = dict(shades, contrast=self._label_colour(shades["base"]))
        return {
            "primary": self._generate_color_scale(brand_color, "primary"),
            "secondary": self._generate_color_scale(self._adjust_hue(brand_color, 180), "secondary"),
            "neutral": self._generate_neutral_scale(),
            "semantic": semantic,
            "surface": dict(self.presets["surface"]),
        }

    def _label_colour(self, base: str) -> str:
        """First candidate reaching 4.5:1 on base, else the highest-contrast one."""
        candidates = self.presets["contrast_candidates"]
        for cand in candidates:
            if contrast_ratio(cand, base) >= 4.5:
                return cand
        return max(candidates, key=lambda c: contrast_ratio(c, base))

    def _generate_color_scale(self, base_color: str, name: str) -> Dict:
        """10-step scale 50-900: 500-900 in HSV (V scales down), 50-400 tint 500 toward white."""
        h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in self._hex_to_rgb(base_color)])
        scale = {}
        for step in (500, 600, 700, 800, 900):
            new_v = v * (1 - (step - 500) / 500)
            new_s = s * (0.3 + 0.7 * (step / 900))
            new_rgb = colorsys.hsv_to_rgb(h, new_s, new_v)
            scale[str(step)] = self._rgb_to_hex([int(c * 255) for c in new_rgb])
        mid = self._hex_to_rgb(scale["500"])
        for step, white in self.presets["light_tint_mix"].items():
            scale[step] = self._rgb_to_hex([round(c + (255 - c) * white) for c in mid])
        scale = {k: scale[k] for k in ("50", "100", "200", "300", "400", "500", "600", "700", "800", "900")}
        scale["DEFAULT"] = base_color
        return scale

    def _generate_neutral_scale(self) -> Dict:
        """Fixed neutral grey scale."""
        return dict(self.presets["neutral"])

    def generate_typography_system(self, style: str) -> Dict:
        """Families per style, modular size scale, weights, line heights, text styles."""
        p = self.presets
        return {
            "fontFamily": dict(p["font_families"].get(style, p["font_families"]["modern"])),
            "fontSize": self._generate_type_scale(),
            "fontWeight": dict(p["fontWeight"]),
            "lineHeight": dict(p["lineHeight"]),
            "letterSpacing": dict(p["letterSpacing"]),
            "textStyles": self._generate_text_styles(),
        }

    def _generate_type_scale(self) -> Dict:
        """Modular scale around the base size, rounded to whole pixels."""
        sizes = self.presets["type_scale_steps"]
        base = sizes.index("base")
        scale = {}
        for i, size in enumerate(sizes):
            if i == base:
                scale[size] = f"{self.base_font_size}px"
            elif i < base:
                scale[size] = f"{round(self.base_font_size / self.type_scale_ratio ** (base - i))}px"
            else:
                scale[size] = f"{round(self.base_font_size * self.type_scale_ratio ** (i - base))}px"
        return scale

    def _generate_text_styles(self) -> Dict:
        """Pre-composed h1-h6, body, small, caption."""
        return json.loads(json.dumps(self.presets["textStyles"]))

    def generate_spacing_system(self) -> Dict:
        """Numeric 8pt-grid scale plus semantic aliases (xs-3xl)."""
        spacing = {str(i): f"{int(self.base_unit * m)}px"
                   for i, m in enumerate(self.presets["spacing_multipliers"])}
        spacing.update({k: spacing[ref] for k, ref in self.presets["spacing_semantic"].items()})
        return spacing

    def generate_sizing_tokens(self) -> Dict:
        """Containers and component sizes."""
        return json.loads(json.dumps(self.presets["sizing"]))

    def generate_border_tokens(self, style: str) -> Dict:
        """Radius per style and border widths."""
        radius = self.presets["radius"]
        return {"radius": dict(radius.get(style, radius["modern"])),
                "width": dict(self.presets["border_width"])}

    def generate_shadow_tokens(self, style: str) -> Dict:
        """Shadow set per style; styles without their own set use modern."""
        shadows = self.presets["shadows"]
        return dict(shadows.get(style, shadows["modern"]))

    def generate_animation_tokens(self) -> Dict:
        """Durations, easings, keyframes."""
        return json.loads(json.dumps(self.presets["animation"]))

    def generate_breakpoints(self) -> Dict:
        """Responsive breakpoints xs-2xl."""
        return dict(self.presets["breakpoints"])

    def generate_z_index_scale(self) -> Dict:
        """Layering scale."""
        return dict(self.presets["z-index"])

    def export_tokens(self, tokens: Dict, format: str = "json") -> str:
        """Serialise as json, css (custom properties) or scss (variables)."""
        if format == "css":
            return self._export_as_css(tokens)
        if format == "scss":
            return self._export_as_scss(tokens)
        return json.dumps(tokens, indent=2)

    @staticmethod
    def _flatten(obj: Dict, prefix: str = "") -> List[Tuple[str, object]]:
        """Nested dict to (dash-joined-name, value) pairs, in order."""
        pairs = []
        for key, value in obj.items():
            name = f"{prefix}-{key}" if prefix else str(key)
            if isinstance(value, dict):
                pairs.extend(DesignTokenGenerator._flatten(value, name))
            else:
                pairs.append((name, value))
        return pairs

    def _export_as_css(self, tokens: Dict) -> str:
        """CSS custom properties on :root."""
        lines = [":root {"] + [f"  --{n}: {v};" for n, v in self._flatten(tokens)] + ["}"]
        return "\n".join(lines)

    def _export_as_scss(self, tokens: Dict) -> str:
        """SCSS variables, same names as the CSS export."""
        return "\n".join(f"${n}: {v};" for n, v in self._flatten(tokens))

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Hex to RGB."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: List[int]) -> str:
        """RGB to lower-case hex."""
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _adjust_hue(self, hex_color: str, degrees: int) -> str:
        """Rotate hue in HSV."""
        h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in self._hex_to_rgb(hex_color)])
        new_rgb = colorsys.hsv_to_rgb((h + degrees / 360) % 1, s, v)
        return self._rgb_to_hex([int(c * 255) for c in new_rgb])


def summary(tokens: Dict, style: str, brand_color: str) -> str:
    """Short human-readable overview."""
    return "\n".join([
        "=" * 60, "DESIGN SYSTEM TOKENS", "=" * 60,
        f"\n🎨 Style: {style}", f"🎨 Brand Color: {brand_color}", "\n📊 Generated Tokens:",
        f"  • Colors: {len(tokens['colors'])} palettes",
        f"  • Typography: {len(tokens['typography'])} categories",
        f"  • Spacing: {len(tokens['spacing'])} values",
        f"  • Shadows: {len(tokens['shadows'])} styles",
        f"  • Breakpoints: {len(tokens['breakpoints'])} sizes",
        "\n💾 Export formats available: json, css, scss",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a design-token system from a brand colour and style preset.",
        epilog="Exit codes: 0 written, 2 bad colour, unknown style or unreadable presets.")
    parser.add_argument("brand_color", nargs="?", default="#0066CC", help="brand colour, #RRGGBB or #RGB (default #0066CC)")
    parser.add_argument("style", nargs="?", default="modern", choices=STYLES, help="style preset (default modern)")
    parser.add_argument("output", nargs="?", default="json", choices=["json", "css", "scss", "summary"],
                        help="output format (default json)")
    parser.add_argument("--format", choices=["text", "json", "css", "scss"],
                        help="overrides the positional output; text prints the summary")
    args = parser.parse_args()
    output = {"text": "summary"}.get(args.format, args.format) if args.format else args.output
    try:
        brand_color = normalise_hex(args.brand_color)
        generator = DesignTokenGenerator()
        tokens = generator.generate_complete_system(brand_color, args.style)
    except TokenInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if output == "summary":
        print(summary(tokens, args.style, brand_color))
    else:
        print(generator.export_tokens(tokens, output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
