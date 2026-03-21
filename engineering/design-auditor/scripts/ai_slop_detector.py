#!/usr/bin/env python3
"""
AI Slop Detector — Analyzes HTML/CSS for AI-generated UI patterns.

Detects generic gradients, stock patterns, template layouts, inconsistent
spacing, meaningless decorative elements, and generic copy patterns.
Each finding includes a confidence score (0.0-1.0).

Usage:
    python ai_slop_detector.py --input page.html
    python ai_slop_detector.py --input page.html --css styles.css
    python ai_slop_detector.py --input page.html --css styles.css --threshold 0.6
    python ai_slop_detector.py --input page.html --format text
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any

# ── Pattern Definitions ──────────────────────────────────────────────────────

GRADIENT_SLOP_COLORS = [
    (r"#[89a-f]{2}[0-5]{2}[f]{2}", r"#[0-5]{2}[89a-f]{2}[f]{2}"),  # purple-to-blue variants
    (r"rgb\(\s*1[2-9]\d", r"rgb\(\s*[0-6]\d"),  # pink-to-blue range
]

STOCK_GRADIENT_PATTERNS = [
    r"linear-gradient\s*\(\s*(?:to\s+(?:right|bottom|bottom\s+right)|1[23]\d\s*deg|45\s*deg)",
    r"linear-gradient\s*\([^)]*(?:#[68-9a-f]{3,6}|purple|violet|indigo)[^)]*(?:#[0-6][0-9a-f]{5}|blue|cyan|teal)",
    r"linear-gradient\s*\([^)]*(?:pink|#f[0-9a-f]{2}[0-5])[^)]*(?:orange|#f[89a-f]{2}[0-9a-f]{2})",
    r"background:\s*linear-gradient[^;]*,\s*linear-gradient",  # stacked gradients
]

GENERIC_HERO_PATTERNS = [
    r"<(?:section|div)[^>]*class=\"[^\"]*hero[^\"]*\"",
    r"<(?:section|div)[^>]*(?:id|class)=\"[^\"]*(?:hero|banner|jumbotron)[^\"]*\"",
]

HERO_STRUCTURE_INDICATORS = [
    r"text-(?:center|align:\s*center)",
    r"(?:max-width|margin):\s*(?:auto|0\s+auto)",
    r"<h1[^>]*>[^<]{10,80}</h1>\s*<p[^>]*>[^<]{20,200}</p>\s*<(?:a|button)",
]

THREE_COLUMN_PATTERNS = [
    r"grid-template-columns:\s*repeat\(\s*3\s*,",
    r"class=\"[^\"]*(?:col-(?:md-|lg-)?4|grid-cols-3|three-col)",
    r"flex(?:-wrap)?[^;]*;\s*(?:[^}]*width:\s*(?:33|calc\(100%\s*/\s*3))",
]

FEATURE_GRID_PATTERN = re.compile(
    r"<div[^>]*>\s*(?:<(?:svg|img|i|span)[^>]*(?:icon|svg|fa-)[^>]*>.*?</(?:svg|img|i|span)>|<(?:svg|img|i|span)[^>]*/?>)\s*"
    r"<h[2-4][^>]*>[^<]+</h[2-4]>\s*<p[^>]*>[^<]+</p>\s*</div>",
    re.DOTALL | re.IGNORECASE,
)

SHADOW_OVERUSE_PATTERN = r"box-shadow\s*:"
BLUR_OVERUSE_PATTERN = r"backdrop-filter\s*:\s*blur"
BORDER_RADIUS_LARGE = r"border-radius\s*:\s*(\d+)"

PRICING_TABLE_PATTERNS = [
    r"class=\"[^\"]*(?:pricing|price|plan)[^\"]*\"",
    r"(?:popular|recommended|best\s*value|most\s*popular)",
    r"\$\s*\d+\s*(?:/\s*mo|per\s*month|/month)",
]

TESTIMONIAL_PATTERNS = [
    r"class=\"[^\"]*(?:testimonial|review|quote)[^\"]*\"",
    r"<(?:img|div)[^>]*(?:avatar|profile|headshot|rounded-full|border-radius:\s*50%)",
    r"<blockquote|<q\b",
]

GENERIC_CTA_PHRASES = [
    r"\bget\s+started\b",
    r"\blearn\s+more\b",
    r"\btry\s+(?:it\s+)?free\b",
    r"\bsign\s+up\s+(?:now|today|free)\b",
    r"\bstart\s+(?:your\s+)?(?:free\s+)?trial\b",
    r"\bjoin\s+(?:now|today|us)\b",
    r"\bbook\s+a\s+demo\b",
    r"\bschedule\s+a\s+(?:call|demo)\b",
    r"\bcontact\s+(?:us|sales)\b",
]

BUZZWORDS = [
    r"\bseamless(?:ly)?\b",
    r"\bpowerful\b",
    r"\brevolutionar(?:y|ize)\b",
    r"\bnext[\s-]gen(?:eration)?\b",
    r"\bcutting[\s-]edge\b",
    r"\binnovative\b",
    r"\btransform(?:ative)?\b",
    r"\bunlock\b",
    r"\bleverage\b",
    r"\bsupercharge\b",
    r"\bstreamline\b",
    r"\bempower\b",
    r"\bgame[\s-]chang(?:er|ing)\b",
    r"\bworld[\s-]class\b",
    r"\bstate[\s-]of[\s-]the[\s-]art\b",
    r"\bfrictionless\b",
    r"\brobust\b",
    r"\bscalable\b",
    r"\bholistic\b",
    r"\bsynergy\b",
]

LOREM_PATTERNS = [
    r"\blorem\s+ipsum\b",
    r"\bdolor\s+sit\s+amet\b",
    r"\bconsectetur\s+adipiscing\b",
    r"\bsed\s+do\s+eiusmod\b",
    r"\but\s+labore\s+et\s+dolore\b",
    r"\bplaceholder\b",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bXXX\b",
]

TEMPLATE_SECTION_ORDER = [
    "hero",
    "feature",
    "testimonial",
    "pricing",
    "cta",
    "footer",
]

ICON_STYLE_PATTERNS = {
    "fontawesome": r"fa-[a-z]",
    "material": r"material-icons|mat-icon",
    "heroicons": r"heroicon",
    "feather": r"feather-",
    "lucide": r"lucide-",
    "phosphor": r"ph-",
    "tabler": r"tabler-icon|ti-",
    "bootstrap": r"bi-",
    "ionicons": r"ion-",
    "outlined_svg": r"stroke-width|stroke=\"|fill=\"none\"",
    "filled_svg": r"fill=\"(?!none)[^\"]+\"[^>]*(?!stroke)",
}


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


def detect_generic_hero(html_content: str) -> list[SlopFinding]:
    """Detect generic hero section patterns."""
    findings = []
    for pattern in GENERIC_HERO_PATTERNS:
        for match in re.finditer(pattern, html_content, re.IGNORECASE):
            hero_region = html_content[match.start():match.start() + 2000]
            indicator_count = 0
            for indicator in HERO_STRUCTURE_INDICATORS:
                if re.search(indicator, hero_region, re.IGNORECASE | re.DOTALL):
                    indicator_count += 1

            if indicator_count >= 2:
                line = find_line_number(html_content, match.start())
                confidence = min(0.9, 0.5 + indicator_count * 0.15)
                findings.append(SlopFinding(
                    pattern_type="structural_hero",
                    description="Generic hero section — centered heading + subtitle + CTA button over full-width background",
                    confidence=confidence,
                    evidence=match.group(0).strip()[:150],
                    line=line,
                    remediation="Add unique visual elements, asymmetric layout, or product-specific imagery. "
                                "Break the centered-text-over-gradient pattern.",
                ))
    return findings


def detect_three_column_grids(html_content: str, css_content: str) -> list[SlopFinding]:
    """Detect cookie-cutter 3-column feature grids."""
    findings = []
    combined = html_content + "\n" + css_content

    has_three_col = False
    for pattern in THREE_COLUMN_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            has_three_col = True
            break

    if has_three_col:
        feature_blocks = list(FEATURE_GRID_PATTERN.finditer(html_content))
        if len(feature_blocks) == 3:
            line = find_line_number(html_content, feature_blocks[0].start())
            findings.append(SlopFinding(
                pattern_type="structural_grid",
                description="3-column feature grid with icon + heading + paragraph — extremely common AI pattern",
                confidence=0.75,
                evidence="3 identical icon+heading+paragraph blocks in 3-column grid",
                line=line,
                remediation="Vary the layout: use 2 or 4 columns, add images, use cards with different sizes, "
                            "or break the rigid grid with a featured/highlighted item.",
            ))
        elif len(feature_blocks) >= 3:
            line = find_line_number(html_content, feature_blocks[0].start())
            findings.append(SlopFinding(
                pattern_type="structural_grid",
                description="Repetitive feature blocks in grid layout — suggests template generation",
                confidence=0.5,
                evidence=f"{len(feature_blocks)} identical feature blocks detected",
                line=line,
                remediation="Add visual variety: different block sizes, images, or interactive elements.",
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


def detect_pricing_tables(html_content: str) -> list[SlopFinding]:
    """Detect cookie-cutter pricing table layouts."""
    findings = []
    pricing_indicators = 0
    first_match_pos = len(html_content)

    for pattern in PRICING_TABLE_PATTERNS:
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        if matches:
            pricing_indicators += 1
            first_match_pos = min(first_match_pos, matches[0].start())

    if pricing_indicators >= 2:
        # Check for 3-tier structure
        price_matches = re.findall(r"\$\s*\d+", html_content)
        confidence = 0.5
        if len(price_matches) == 3:
            confidence = 0.75
        if re.search(r"(?:popular|recommended|best\s*value)", html_content, re.IGNORECASE):
            confidence += 0.1

        line = find_line_number(html_content, first_match_pos)
        findings.append(SlopFinding(
            pattern_type="structural_pricing",
            description="Cookie-cutter pricing table — standard tier layout with highlighted recommendation",
            confidence=min(0.9, confidence),
            evidence=f"{len(price_matches)} price points found with {pricing_indicators} pricing indicators",
            line=line,
            remediation="Differentiate with unique layout: toggle pricing, slider, comparison table, "
                        "or custom illustrations per tier.",
        ))

    return findings


def detect_testimonial_layouts(html_content: str) -> list[SlopFinding]:
    """Detect generic testimonial patterns."""
    findings = []
    testimonial_indicators = 0
    first_pos = len(html_content)

    for pattern in TESTIMONIAL_PATTERNS:
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        if matches:
            testimonial_indicators += 1
            first_pos = min(first_pos, matches[0].start())

    if testimonial_indicators >= 2:
        line = find_line_number(html_content, first_pos)
        findings.append(SlopFinding(
            pattern_type="structural_testimonial",
            description="Generic testimonial layout — circular avatar + quote + attribution pattern",
            confidence=0.6,
            evidence=f"{testimonial_indicators} testimonial layout indicators found",
            line=line,
            remediation="Add specificity: use real photos, include company logos, link to case studies, "
                        "or use video testimonials.",
        ))

    return findings


def detect_generic_copy(html_content: str) -> list[SlopFinding]:
    """Detect generic CTA phrases and buzzword density."""
    findings = []
    text_content = re.sub(r"<[^>]+>", " ", html_content)
    text_content = re.sub(r"\s+", " ", text_content)

    # Generic CTAs
    cta_count = 0
    for pattern in GENERIC_CTA_PHRASES:
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        cta_count += len(matches)

    if cta_count >= 3:
        findings.append(SlopFinding(
            pattern_type="copy_cta",
            description=f"Generic CTA phrases — {cta_count} instances of stock call-to-action text",
            confidence=min(0.8, 0.4 + cta_count * 0.1),
            evidence=f"{cta_count} generic CTAs found",
            remediation="Replace with specific, value-driven CTAs: 'Start analyzing data' instead of 'Get Started', "
                        "'See the 14-day results' instead of 'Learn More'.",
        ))

    # Buzzword density
    word_count = len(text_content.split())
    buzzword_count = 0
    for pattern in BUZZWORDS:
        buzzword_count += len(re.findall(pattern, text_content, re.IGNORECASE))

    if word_count > 50:
        density = buzzword_count / word_count * 100
        if density > 2.0:
            findings.append(SlopFinding(
                pattern_type="copy_buzzwords",
                description=f"High buzzword density — {buzzword_count} buzzwords in {word_count} words ({density:.1f}%)",
                confidence=min(0.8, 0.3 + density * 0.1),
                evidence=f"Buzzword density: {density:.1f}%",
                remediation="Replace buzzwords with specific, measurable claims. "
                            "'Reduces build time by 40%' beats 'powerful and seamless'.",
            ))

    return findings


def detect_lorem_ipsum(html_content: str) -> list[SlopFinding]:
    """Detect lorem ipsum and placeholder text."""
    findings = []
    for pattern in LOREM_PATTERNS:
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        for match in matches:
            line = find_line_number(html_content, match.start())
            findings.append(SlopFinding(
                pattern_type="copy_placeholder",
                description=f"Placeholder text detected: '{match.group(0).strip()}'",
                confidence=0.95,
                evidence=match.group(0).strip(),
                line=line,
                remediation="Replace with real content or clearly mark as draft with a visible indicator.",
            ))
    return findings


def detect_template_ordering(html_content: str) -> list[SlopFinding]:
    """Detect predictable template section ordering."""
    findings = []
    section_positions = {}

    for section in TEMPLATE_SECTION_ORDER:
        pattern = rf"class=\"[^\"]*{section}[^\"]*\"|id=\"[^\"]*{section}[^\"]*\""
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            section_positions[section] = match.start()

    if len(section_positions) >= 4:
        ordered = sorted(section_positions.keys(), key=lambda s: section_positions[s])
        # Check if order matches template order
        expected_order = [s for s in TEMPLATE_SECTION_ORDER if s in section_positions]
        if ordered == expected_order:
            findings.append(SlopFinding(
                pattern_type="structural_ordering",
                description=f"Template section ordering detected — {' > '.join(ordered)}",
                confidence=0.6,
                evidence=f"Sections appear in standard template order: {' > '.join(ordered)}",
                remediation="Reorder sections based on user needs and content strategy. "
                            "Consider starting with the problem, not the product.",
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


def compute_slop_grade(findings: list[SlopFinding], threshold: float) -> str:
    """Compute overall AI Slop Grade based on findings."""
    if not findings:
        return "A"

    high_confidence = [f for f in findings if f.confidence >= threshold]
    count = len(high_confidence)

    if count == 0:
        return "A"
    elif count <= 2:
        return "B"
    elif count <= 5:
        return "C"
    elif count <= 8:
        return "D"
    else:
        return "F"


def analyze(html_content: str, css_content: str, threshold: float) -> dict:
    """Run all detection passes and produce a report."""
    all_findings: list[SlopFinding] = []

    # Visual patterns (CSS-focused)
    all_findings.extend(detect_stock_gradients(css_content))
    all_findings.extend(detect_shadow_overuse(css_content))
    all_findings.extend(detect_large_border_radius(css_content))

    # Structural patterns (HTML-focused)
    all_findings.extend(detect_generic_hero(html_content))
    all_findings.extend(detect_three_column_grids(html_content, css_content))
    all_findings.extend(detect_pricing_tables(html_content))
    all_findings.extend(detect_testimonial_layouts(html_content))
    all_findings.extend(detect_template_ordering(html_content))

    # Copy patterns
    all_findings.extend(detect_generic_copy(html_content))
    all_findings.extend(detect_lorem_ipsum(html_content))

    # Consistency patterns
    all_findings.extend(detect_icon_inconsistency(html_content, css_content))

    # Filter by threshold
    above_threshold = [f for f in all_findings if f.confidence >= threshold]
    below_threshold = [f for f in all_findings if f.confidence < threshold]

    grade = compute_slop_grade(all_findings, threshold)

    # Group by type
    by_type = {}
    for f in all_findings:
        cat = f.pattern_type.split("_")[0]
        if cat not in by_type:
            by_type[cat] = []
        by_type[cat].append(f.to_dict())

    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "ai_slop_detector.py",
            "version": "2.0.0",
            "threshold": threshold,
        },
        "grade": grade,
        "summary": {
            "total_patterns": len(all_findings),
            "above_threshold": len(above_threshold),
            "below_threshold": len(below_threshold),
            "by_category": {cat: len(items) for cat, items in by_type.items()},
        },
        "findings": [f.to_dict() for f in sorted(all_findings, key=lambda x: -x.confidence)],
        "findings_by_category": by_type,
    }


def format_text_report(report: dict) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("AI SLOP DETECTION REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append(f"Threshold: {report['metadata']['threshold']}")
    lines.append("")

    lines.append(f"AI Slop Grade: {report['grade']}")
    lines.append("")

    s = report["summary"]
    lines.append(f"Total patterns detected: {s['total_patterns']}")
    lines.append(f"  Above threshold: {s['above_threshold']}")
    lines.append(f"  Below threshold: {s['below_threshold']}")
    lines.append("")

    if s["by_category"]:
        lines.append("By Category:")
        category_labels = {
            "visual": "Visual Patterns",
            "structural": "Structural Patterns",
            "copy": "Copy Patterns",
        }
        for cat, count in s["by_category"].items():
            label = category_labels.get(cat, cat.title())
            lines.append(f"  {label}: {count}")
        lines.append("")

    if report["findings"]:
        lines.append("FINDINGS (sorted by confidence)")
        lines.append("-" * 60)
        for f in report["findings"]:
            conf_bar = "#" * int(f["confidence"] * 10)
            lines.append(f"\n  [{f['confidence']:.2f}] {conf_bar}")
            lines.append(f"  Type: {f['pattern_type']}")
            lines.append(f"  {f['description']}")
            if f.get("evidence"):
                lines.append(f"  Evidence: {f['evidence']}")
            if f.get("line"):
                lines.append(f"  Line: {f['line']}")
            if f.get("remediation"):
                lines.append(f"  Fix: {f['remediation']}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def read_file(path: str) -> str:
    """Read a file, return empty string if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Cannot read {path} as text", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AI Slop Detector — Analyze HTML/CSS for AI-generated UI patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input page.html
  %(prog)s --input page.html --css styles.css --threshold 0.6
  %(prog)s --input page.html --format text
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to HTML file to analyze")
    parser.add_argument("--css", "-c", help="Path to CSS file (optional, will also extract inline styles from HTML)")
    parser.add_argument("--threshold", "-t", type=float, default=0.5, help="Confidence threshold (0.0-1.0, default: 0.5)")
    parser.add_argument("--output", "-o", help="Path to write report JSON (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json", help="Output format (default: json)")

    args = parser.parse_args()

    # Validate threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("Error: Threshold must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)

    # Read files
    html_content = read_file(args.input)

    css_content = ""
    if args.css:
        css_content = read_file(args.css)

    # Also extract inline and embedded styles from HTML
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html_content, re.DOTALL | re.IGNORECASE)
    inline_styles = re.findall(r"style=\"([^\"]+)\"", html_content, re.IGNORECASE)
    css_content += "\n".join(style_blocks) + "\n" + "\n".join(inline_styles)

    # Analyze
    report = analyze(html_content, css_content, args.threshold)

    # Output
    if args.format == "text":
        output = format_text_report(report)
    else:
        output = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
