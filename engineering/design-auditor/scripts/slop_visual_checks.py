#!/usr/bin/env python3
"""
Slop Visual Checks — the CSS-side layer of ai_slop_detector.py.

Stock gradients, shadow and backdrop-blur overuse, rounded-everything radii and mixed
icon sets. Also holds what both layers share: the pattern tables (loaded from
references/slop-patterns.json), the finding type and page loading. Run alone to debug
one layer; grading, threshold and the report belong to ai_slop_detector.py.

Usage:
    python slop_visual_checks.py --input page.html --css styles.css
    python slop_visual_checks.py --input page.html --format json

Exit codes: 0 no findings, 1 findings, 2 missing or unreadable file.
"""

import argparse
import json
import os
import re
import sys

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "slop-patterns.json")
with open(_DATA, "r", encoding="utf-8") as _f:
    P = json.load(_f)

STOCK_GRADIENT_PATTERNS = P["stock_gradient"]
SHADOW_OVERUSE_PATTERN = P["shadow"]
BLUR_OVERUSE_PATTERN = P["backdrop_blur"]
BORDER_RADIUS_LARGE = P["border_radius"]
ICON_STYLE_PATTERNS = P["icon_sets"]


class SlopFinding:
    """Represents a single slop detection finding."""

    def __init__(self, pattern_type: str, description: str, confidence: float,
                 evidence: str = "", line: int = 0, remediation: str = ""):
        self.pattern_type = pattern_type
        self.description = description
        self.confidence = min(1.0, max(0.0, confidence))
        self.evidence = evidence[:200] if evidence else ""
        self.line = line
        self.remediation = remediation

    def to_dict(self) -> dict:
        d = {
            "pattern_type": self.pattern_type,
            "description": self.description,
            "confidence": round(self.confidence, 2),
        }
        if self.evidence:
            d["evidence"] = self.evidence
        if self.line > 0:
            d["line"] = self.line
        if self.remediation:
            d["remediation"] = self.remediation
        return d


def find_line_number(content: str, match_start: int) -> int:
    """Get line number for a match position."""
    return content[:match_start].count("\n") + 1


def detect_stock_gradients(css_content: str) -> list[SlopFinding]:
    """Detect stock/trending gradient patterns."""
    findings = []
    for pattern in STOCK_GRADIENT_PATTERNS:
        for match in re.finditer(pattern, css_content, re.IGNORECASE):
            line = find_line_number(css_content, match.start())
            findings.append(SlopFinding(
                pattern_type="visual_gradient",
                description="Stock gradient pattern detected — trending color combination suggests AI generation",
                confidence=0.6,
                evidence=match.group(0).strip()[:150],
                line=line,
                remediation="Replace with brand-specific colors or intentional color palette. Use design tokens.",
            ))
    return findings


def detect_shadow_overuse(css_content: str) -> list[SlopFinding]:
    """Detect overuse of box-shadow."""
    findings = []
    shadow_matches = list(re.finditer(SHADOW_OVERUSE_PATTERN, css_content, re.IGNORECASE))
    # Count unique selectors with shadows (approximate by counting occurrences)
    total_rules = css_content.count("{")
    if total_rules > 0 and len(shadow_matches) > 0:
        ratio = len(shadow_matches) / max(total_rules, 1)
        if ratio > 0.4:
            findings.append(SlopFinding(
                pattern_type="visual_shadow",
                description=f"Shadow overuse — {len(shadow_matches)} box-shadow declarations across ~{total_rules} rules ({ratio:.0%})",
                confidence=min(0.8, 0.4 + ratio),
                evidence=f"{len(shadow_matches)} box-shadow properties found",
                remediation="Reserve shadows for elevation hierarchy. Use 2-3 shadow levels max in a design system.",
            ))

    blur_matches = list(re.finditer(BLUR_OVERUSE_PATTERN, css_content, re.IGNORECASE))
    if len(blur_matches) > 3:
        findings.append(SlopFinding(
            pattern_type="visual_blur",
            description=f"Backdrop blur overuse — {len(blur_matches)} backdrop-filter: blur declarations",
            confidence=min(0.7, 0.3 + len(blur_matches) * 0.1),
            evidence=f"{len(blur_matches)} backdrop-filter: blur properties",
            remediation="Use backdrop blur sparingly — only for overlays, modals, or frosted glass effects where justified.",
        ))

    return findings


def detect_large_border_radius(css_content: str) -> list[SlopFinding]:
    """Detect overuse of large border-radius values."""
    findings = []
    matches = re.finditer(BORDER_RADIUS_LARGE, css_content)
    large_count = 0
    total_count = 0
    for m in matches:
        total_count += 1
        val = int(m.group(1))
        if val >= 16:
            large_count += 1

    if total_count > 3 and large_count / max(total_count, 1) > 0.6:
        findings.append(SlopFinding(
            pattern_type="visual_radius",
            description=f"Rounded everything — {large_count}/{total_count} border-radius values are >= 16px",
            confidence=0.5,
            evidence=f"{large_count} large border-radius values detected",
            remediation="Establish a border-radius scale (e.g., 2px, 4px, 8px, 16px) and use intentionally.",
        ))

    return findings


def detect_icon_inconsistency(html_content: str, css_content: str) -> list[SlopFinding]:
    """Detect mixed icon sets suggesting AI assembly."""
    findings = []
    combined = html_content + "\n" + css_content
    detected_sets = []

    for icon_set, pattern in ICON_STYLE_PATTERNS.items():
        if re.search(pattern, combined, re.IGNORECASE):
            detected_sets.append(icon_set)

    # Check for outline vs filled SVG mix
    has_outlined = "outlined_svg" in detected_sets
    has_filled = "filled_svg" in detected_sets
    named_sets = [s for s in detected_sets if s not in ("outlined_svg", "filled_svg")]

    issues = []
    if len(named_sets) > 1:
        issues.append(f"multiple icon libraries ({', '.join(named_sets)})")
    if has_outlined and has_filled:
        issues.append("mixed outlined and filled SVG styles")

    if issues:
        findings.append(SlopFinding(
            pattern_type="visual_icons",
            description=f"Inconsistent icon styles — {'; '.join(issues)}",
            confidence=min(0.8, 0.4 + len(issues) * 0.2),
            evidence=f"Detected icon sources: {', '.join(detected_sets)}",
            remediation="Standardize on a single icon set with consistent weight and style. "
                        "Prefer a single library (e.g., Lucide, Phosphor) used consistently.",
        ))

    return findings


def read_file(path: str) -> str:
    """Read a text file; exit 2 when it is missing, a directory or not text."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"Error: Cannot read {path} as text", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"Error: Cannot read {path}: {e.strerror}", file=sys.stderr)
        sys.exit(2)


def load_page(html_path: str, css_path: str | None) -> tuple[str, str]:
    """Return (html, css): the CSS file plus every <style> block and inline style attribute."""
    html_content = read_file(html_path)
    css_content = read_file(css_path) if css_path else ""
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html_content, re.DOTALL | re.IGNORECASE)
    inline_styles = re.findall(r"style=\"([^\"]+)\"", html_content, re.IGNORECASE)
    css_content += "\n".join(style_blocks) + "\n" + "\n".join(inline_styles)
    return html_content, css_content


def run_checks(html_content: str, css_content: str) -> list[SlopFinding]:
    """Visual checks alone, in report order."""
    return (detect_stock_gradients(css_content) + detect_shadow_overuse(css_content)
            + detect_large_border_radius(css_content) + detect_icon_inconsistency(html_content, css_content))


def main():
    parser = argparse.ArgumentParser(
        description="Slop Visual Checks — gradients, shadows, blur, radii and icon sets in one page",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input page.html --css styles.css
  %(prog)s --input page.html --format json
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to HTML file to analyze")
    parser.add_argument("--css", "-c", help="Path to CSS file (inline and <style> CSS is read too)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    html_content, css_content = load_page(args.input, args.css)
    findings = sorted(run_checks(html_content, css_content), key=lambda x: -x.confidence)
    if args.format == "json":
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        print(f"{len(findings)} finding(s)")
        for f in findings:
            line = f" (line {f.line})" if f.line else ""
            print(f"  [{f.confidence:.2f}] {f.pattern_type}{line}: {f.description}")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
