#!/usr/bin/env python3
"""
Slop Content Checks — the markup and copy layer of ai_slop_detector.py.

Landing-page template structure (centered hero, 3-up feature grid, 3-tier pricing,
avatar testimonials, hero > features > testimonials > pricing > CTA order) and stock copy
(generic CTAs, buzzword density, placeholder text). Run alone to debug one layer.

Usage:
    python slop_content_checks.py --input page.html
    python slop_content_checks.py --input page.html --css styles.css --format json

Exit codes: 0 no findings, 1 findings, 2 missing or unreadable file.
"""

import argparse
import importlib.util as _ilu
import json
import os
import re
import sys


def _sibling(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_vis = _sibling("slop_visual_checks")
SlopFinding = _vis.SlopFinding
find_line_number = _vis.find_line_number
load_page = _vis.load_page
P = _vis.P

GENERIC_HERO_PATTERNS = P["generic_hero"]
HERO_STRUCTURE_INDICATORS = P["hero_structure_indicators"]
THREE_COLUMN_PATTERNS = P["three_column"]
FEATURE_GRID_PATTERN = re.compile(P["feature_grid_block"], re.DOTALL | re.IGNORECASE)
PRICING_TABLE_PATTERNS = P["pricing_table"]
TESTIMONIAL_PATTERNS = P["testimonial"]
GENERIC_CTA_PHRASES = P["generic_cta"]
BUZZWORDS = P["buzzwords"]
LOREM_PATTERNS = P["placeholder_text"]
TEMPLATE_SECTION_ORDER = P["template_section_order"]


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

    if any(re.search(pattern, combined, re.IGNORECASE) for pattern in THREE_COLUMN_PATTERNS):
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


def run_checks(html_content: str, css_content: str) -> list[SlopFinding]:
    """Content checks alone, in report order."""
    return (detect_generic_hero(html_content) + detect_three_column_grids(html_content, css_content)
            + detect_pricing_tables(html_content) + detect_testimonial_layouts(html_content)
            + detect_template_ordering(html_content) + detect_generic_copy(html_content)
            + detect_lorem_ipsum(html_content))


def main():
    parser = argparse.ArgumentParser(
        description="Slop Content Checks — template structure and stock copy in one page",
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
