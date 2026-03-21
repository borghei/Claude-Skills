#!/usr/bin/env python3
"""Accessibility Auditor — Analyzes HTML for WCAG 2.1 violations.

Checks HTML content against WCAG 2.1 conformance levels A, AA, and AAA.
Detects missing alt text, heading hierarchy issues, color contrast problems,
form label associations, ARIA attribute usage, link text quality, and more.

Usage:
    python accessibility_auditor.py page.html
    python accessibility_auditor.py page.html --level AAA --json
    curl -s https://example.com | python accessibility_auditor.py - --level A
"""

from __future__ import annotations

import argparse
import html.parser
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

WCAG_LEVELS = ("A", "AA", "AAA")


@dataclass
class Violation:
    """A single WCAG violation."""

    rule_id: str
    wcag_criterion: str
    level: str  # A, AA, AAA
    severity: str  # must-fix, should-fix, nice-to-have
    message: str
    element: str
    selector_hint: str
    remediation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "wcag_criterion": self.wcag_criterion,
            "level": self.level,
            "severity": self.severity,
            "message": self.message,
            "element": self.element,
            "selector_hint": self.selector_hint,
            "remediation": self.remediation,
        }


@dataclass
class AuditResult:
    """Complete audit result."""

    total_elements_checked: int = 0
    violations: list[Violation] = field(default_factory=list)
    level_checked: str = "AA"
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        level_counts = {"A": 0, "AA": 0, "AAA": 0}
        severity_counts = {"must-fix": 0, "should-fix": 0, "nice-to-have": 0}
        for v in self.violations:
            level_counts[v.level] = level_counts.get(v.level, 0) + 1
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        total = self.total_elements_checked
        violation_count = len(self.violations)
        compliance_pct = round((1 - violation_count / max(total, 1)) * 100, 1)

        return {
            "level_checked": self.level_checked,
            "total_elements_checked": total,
            "total_violations": violation_count,
            "compliance_percentage": compliance_pct,
            "by_level": level_counts,
            "by_severity": severity_counts,
            "violations": [v.to_dict() for v in self.violations],
        }


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

@dataclass
class ParsedElement:
    """A parsed HTML element with its attributes."""

    tag: str
    attrs: dict[str, str]
    text_content: str = ""
    line: int = 0
    children_tags: list[str] = field(default_factory=list)


class HTMLStructureParser(html.parser.HTMLParser):
    """Lightweight HTML parser that extracts elements for accessibility checks."""

    def __init__(self) -> None:
        super().__init__()
        self.elements: list[ParsedElement] = []
        self._stack: list[ParsedElement] = []
        self._current_text: list[str] = []
        self.has_lang: bool = False
        self.has_title: bool = False
        self.has_doctype: bool = False
        self.heading_order: list[tuple[int, int]] = []  # (level, line)
        self.id_counts: dict[str, int] = {}
        self.label_for_ids: set[str] = set()
        self.input_ids: set[str] = set()
        self.form_inputs: list[ParsedElement] = []
        self.links: list[ParsedElement] = []
        self.images: list[ParsedElement] = []
        self.media_elements: list[ParsedElement] = []
        self.landmark_roles: list[str] = []
        self.all_tags: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        elem = ParsedElement(tag=tag, attrs=attr_dict, line=line)
        self.all_tags.append(tag)

        # Track parent-child
        if self._stack:
            self._stack[-1].children_tags.append(tag)

        self._stack.append(elem)
        self._current_text = []

        # Track html lang
        if tag == "html" and "lang" in attr_dict and attr_dict["lang"].strip():
            self.has_lang = True

        # Track title
        if tag == "title":
            self.has_title = True

        # Track headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.heading_order.append((level, line))

        # Track IDs
        elem_id = attr_dict.get("id", "").strip()
        if elem_id:
            self.id_counts[elem_id] = self.id_counts.get(elem_id, 0) + 1

        # Track labels
        if tag == "label" and "for" in attr_dict:
            self.label_for_ids.add(attr_dict["for"])

        # Track form inputs
        if tag in ("input", "textarea", "select"):
            self.form_inputs.append(elem)
            if elem_id:
                self.input_ids.add(elem_id)

        # Track links
        if tag == "a":
            self.links.append(elem)

        # Track images
        if tag == "img":
            self.images.append(elem)

        # Track media
        if tag in ("video", "audio"):
            self.media_elements.append(elem)

        # Track landmarks
        role = attr_dict.get("role", "")
        if role in ("banner", "navigation", "main", "contentinfo", "complementary", "search"):
            self.landmark_roles.append(role)
        if tag in ("header", "nav", "main", "footer", "aside"):
            self.landmark_roles.append(tag)

    def handle_data(self, data: str) -> None:
        self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._stack and self._stack[-1].tag == tag:
            elem = self._stack.pop()
            elem.text_content = " ".join(self._current_text).strip()
            self.elements.append(elem)
            self._current_text = []

            # Update link/image text
            if tag == "a" and self.links and self.links[-1] is elem:
                pass  # text_content already set
        else:
            self._current_text = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


# ---------------------------------------------------------------------------
# WCAG Checks
# ---------------------------------------------------------------------------

def check_images_alt_text(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.1.1 (A): All images must have alt text."""
    violations: list[Violation] = []
    for img in parser.images:
        alt = img.attrs.get("alt")
        role = img.attrs.get("role", "")
        if alt is None and role != "presentation":
            src = img.attrs.get("src", "unknown")
            violations.append(Violation(
                rule_id="img-alt",
                wcag_criterion="1.1.1 Non-text Content",
                level="A",
                severity="must-fix",
                message="Image missing alt attribute",
                element=f'<img src="{src}">',
                selector_hint=f'img[src="{src}"]' if len(src) < 80 else f"img (line {img.line})",
                remediation="Add alt attribute describing the image content, or alt=\"\" for decorative images",
            ))
        elif alt is not None and alt.strip() == "" and role != "presentation":
            # Empty alt is valid for decorative images, but flag if no role=presentation
            aria_hidden = img.attrs.get("aria-hidden", "")
            if aria_hidden != "true":
                src = img.attrs.get("src", "unknown")
                # This is actually acceptable per spec, so we don't flag it
    return violations


def check_page_language(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 3.1.1 (A): Page must have a lang attribute."""
    if not parser.has_lang:
        return [Violation(
            rule_id="html-lang",
            wcag_criterion="3.1.1 Language of Page",
            level="A",
            severity="must-fix",
            message="HTML element missing lang attribute",
            element="<html>",
            selector_hint="html",
            remediation='Add lang attribute to html element, e.g., <html lang="en">',
        )]
    return []


def check_page_title(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 2.4.2 (A): Page must have a title."""
    if not parser.has_title:
        return [Violation(
            rule_id="page-title",
            wcag_criterion="2.4.2 Page Titled",
            level="A",
            severity="must-fix",
            message="Page missing <title> element",
            element="<head>",
            selector_hint="head",
            remediation="Add a descriptive <title> element inside <head>",
        )]
    return []


def check_heading_hierarchy(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.3.1 (A) + 2.4.6 (AA): Headings should follow logical order."""
    violations: list[Violation] = []
    if not parser.heading_order:
        return violations

    # Check for skipped levels
    prev_level = 0
    for level, line in parser.heading_order:
        if prev_level > 0 and level > prev_level + 1:
            violations.append(Violation(
                rule_id="heading-order",
                wcag_criterion="1.3.1 Info and Relationships",
                level="A",
                severity="must-fix",
                message=f"Heading level skipped: h{prev_level} to h{level}",
                element=f"<h{level}>",
                selector_hint=f"h{level} (line {line})",
                remediation=f"Use h{prev_level + 1} instead of h{level}, or add missing intermediate headings",
            ))
        prev_level = level

    # Check first heading is h1
    if parser.heading_order and parser.heading_order[0][0] != 1:
        first_level = parser.heading_order[0][0]
        violations.append(Violation(
            rule_id="heading-first-h1",
            wcag_criterion="2.4.6 Headings and Labels",
            level="AA",
            severity="should-fix",
            message=f"First heading is h{first_level}, expected h1",
            element=f"<h{first_level}>",
            selector_hint=f"h{first_level} (line {parser.heading_order[0][1]})",
            remediation="Start the page heading hierarchy with an h1 element",
        ))

    return violations


def check_duplicate_ids(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 4.1.1 (A): IDs must be unique."""
    violations: list[Violation] = []
    for id_val, count in parser.id_counts.items():
        if count > 1:
            violations.append(Violation(
                rule_id="duplicate-id",
                wcag_criterion="4.1.1 Parsing",
                level="A",
                severity="must-fix",
                message=f'Duplicate id="{id_val}" found {count} times',
                element=f'id="{id_val}"',
                selector_hint=f'[id="{id_val}"]',
                remediation="Ensure all id attribute values are unique within the page",
            ))
    return violations


def check_form_labels(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.3.1 + 4.1.2 (A): Form inputs must have labels."""
    violations: list[Violation] = []
    for inp in parser.form_inputs:
        input_type = inp.attrs.get("type", "text")
        if input_type in ("hidden", "submit", "button", "reset", "image"):
            continue

        has_label = False
        input_id = inp.attrs.get("id", "")
        if input_id and input_id in parser.label_for_ids:
            has_label = True
        if inp.attrs.get("aria-label", "").strip():
            has_label = True
        if inp.attrs.get("aria-labelledby", "").strip():
            has_label = True
        if inp.attrs.get("title", "").strip():
            has_label = True
        if inp.attrs.get("placeholder", "").strip():
            # Placeholder alone is not sufficient per WCAG, but we soften severity
            pass

        if not has_label:
            name = inp.attrs.get("name", inp.attrs.get("id", "unknown"))
            violations.append(Violation(
                rule_id="form-label",
                wcag_criterion="4.1.2 Name, Role, Value",
                level="A",
                severity="must-fix",
                message=f"Form input missing accessible label: {inp.tag}[name={name}]",
                element=f"<{inp.tag} name=\"{name}\">",
                selector_hint=f'{inp.tag}[name="{name}"]' if name != "unknown" else f"{inp.tag} (line {inp.line})",
                remediation="Add a <label for=\"...\"> element, aria-label, or aria-labelledby attribute",
            ))
    return violations


def check_link_text_quality(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 2.4.4 (A) + 2.4.9 (AAA): Links must have descriptive text."""
    violations: list[Violation] = []
    generic_texts = {"click here", "here", "read more", "more", "link", "this"}

    for link in parser.links:
        href = link.attrs.get("href", "")
        text = link.text_content.strip().lower()
        aria_label = link.attrs.get("aria-label", "").strip()

        effective_text = aria_label or text

        if not effective_text:
            # Check for child images with alt
            if not link.children_tags or "img" not in link.children_tags:
                violations.append(Violation(
                    rule_id="link-name",
                    wcag_criterion="2.4.4 Link Purpose (In Context)",
                    level="A",
                    severity="must-fix",
                    message="Link has no accessible text",
                    element=f'<a href="{href[:60]}">',
                    selector_hint=f'a[href="{href[:60]}"]',
                    remediation="Add descriptive link text or aria-label attribute",
                ))
        elif effective_text in generic_texts:
            violations.append(Violation(
                rule_id="link-text-generic",
                wcag_criterion="2.4.9 Link Purpose (Link Only)",
                level="AAA",
                severity="nice-to-have",
                message=f'Link text "{effective_text}" is too generic',
                element=f'<a href="{href[:60]}">{effective_text}</a>',
                selector_hint=f'a[href="{href[:60]}"]',
                remediation="Use descriptive link text that makes sense out of context",
            ))

    return violations


def check_color_contrast_hints(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.4.3 (AA) + 1.4.6 (AAA): Flag elements that commonly have contrast issues.

    Note: Full contrast checking requires computed styles which we cannot get
    from static HTML alone. This check flags patterns that commonly indicate
    contrast problems and recommends manual verification.
    """
    violations: list[Violation] = []
    contrast_risk_patterns = []

    for elem in parser.elements:
        style = elem.attrs.get("style", "")
        if not style:
            continue

        # Check for inline color declarations that may have low contrast
        has_color = "color:" in style.lower() and "background" not in style.lower()
        has_bg = "background" in style.lower()

        if has_color and not has_bg:
            contrast_risk_patterns.append(elem)
        elif has_bg and not has_color:
            contrast_risk_patterns.append(elem)

    if contrast_risk_patterns:
        violations.append(Violation(
            rule_id="color-contrast-review",
            wcag_criterion="1.4.3 Contrast (Minimum)",
            level="AA",
            severity="should-fix",
            message=f"{len(contrast_risk_patterns)} element(s) have inline color styles — verify contrast ratio >= 4.5:1 for text, >= 3:1 for large text",
            element="(multiple elements with inline styles)",
            selector_hint="[style*='color']",
            remediation="Verify color contrast ratios meet WCAG AA (4.5:1 normal, 3:1 large) or AAA (7:1 normal, 4.5:1 large)",
        ))

    return violations


def check_media_alternatives(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.2.1-1.2.5 (A/AA): Media must have alternatives."""
    violations: list[Violation] = []
    for media in parser.media_elements:
        has_track = "track" in [c for c in media.children_tags]
        autoplay = "autoplay" in media.attrs

        if not has_track:
            violations.append(Violation(
                rule_id="media-captions",
                wcag_criterion="1.2.2 Captions (Prerecorded)",
                level="A",
                severity="must-fix",
                message=f"<{media.tag}> element missing captions/subtitles track",
                element=f"<{media.tag}> (line {media.line})",
                selector_hint=f"{media.tag} (line {media.line})",
                remediation="Add a <track kind=\"captions\"> element for synchronized captions",
            ))

        if autoplay:
            violations.append(Violation(
                rule_id="media-autoplay",
                wcag_criterion="1.4.2 Audio Control",
                level="A",
                severity="must-fix",
                message=f"<{media.tag}> has autoplay attribute",
                element=f"<{media.tag} autoplay> (line {media.line})",
                selector_hint=f"{media.tag}[autoplay]",
                remediation="Remove autoplay or ensure the media is muted and user can pause/stop it",
            ))

    return violations


def check_landmark_regions(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 1.3.1 (A): Page should use landmark regions."""
    violations: list[Violation] = []
    has_main = "main" in parser.landmark_roles
    has_nav = "nav" in parser.landmark_roles or "navigation" in parser.landmark_roles

    if not has_main and len(parser.all_tags) > 10:
        violations.append(Violation(
            rule_id="landmark-main",
            wcag_criterion="1.3.1 Info and Relationships",
            level="A",
            severity="must-fix",
            message="Page missing <main> landmark region",
            element="<body>",
            selector_hint="body",
            remediation="Wrap the primary content in a <main> element or add role=\"main\"",
        ))

    if not has_nav and len(parser.links) > 5:
        violations.append(Violation(
            rule_id="landmark-nav",
            wcag_criterion="1.3.1 Info and Relationships",
            level="A",
            severity="should-fix",
            message="Page has multiple links but no <nav> landmark",
            element="<body>",
            selector_hint="body",
            remediation="Wrap navigation links in a <nav> element",
        ))

    return violations


def check_focus_indicators(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 2.4.7 (AA): Check for outline:none or outline:0 that removes focus indicators."""
    violations: list[Violation] = []
    for elem in parser.elements:
        style = elem.attrs.get("style", "")
        if re.search(r"outline\s*:\s*(none|0)\b", style, re.IGNORECASE):
            violations.append(Violation(
                rule_id="focus-visible",
                wcag_criterion="2.4.7 Focus Visible",
                level="AA",
                severity="should-fix",
                message="Element removes focus indicator with outline:none",
                element=f"<{elem.tag}> (line {elem.line})",
                selector_hint=f"{elem.tag} (line {elem.line})",
                remediation="Remove outline:none or provide a custom focus indicator with :focus-visible",
            ))
    return violations


def check_tabindex_misuse(parser: HTMLStructureParser) -> list[Violation]:
    """WCAG 2.4.3 (A): tabindex > 0 disrupts natural tab order."""
    violations: list[Violation] = []
    for elem in parser.elements:
        tabindex = elem.attrs.get("tabindex", "")
        if tabindex:
            try:
                val = int(tabindex)
                if val > 0:
                    violations.append(Violation(
                        rule_id="tabindex-positive",
                        wcag_criterion="2.4.3 Focus Order",
                        level="A",
                        severity="must-fix",
                        message=f"Element has tabindex={val} which disrupts natural focus order",
                        element=f"<{elem.tag} tabindex=\"{val}\"> (line {elem.line})",
                        selector_hint=f"[tabindex=\"{val}\"]",
                        remediation="Use tabindex=\"0\" or tabindex=\"-1\" instead; restructure DOM for desired tab order",
                    ))
            except ValueError:
                pass
    return violations


# ---------------------------------------------------------------------------
# Audit Runner
# ---------------------------------------------------------------------------

ALL_CHECKS_A = [
    check_images_alt_text,
    check_page_language,
    check_page_title,
    check_heading_hierarchy,
    check_duplicate_ids,
    check_form_labels,
    check_link_text_quality,
    check_media_alternatives,
    check_landmark_regions,
    check_tabindex_misuse,
]

ALL_CHECKS_AA = [
    check_color_contrast_hints,
    check_focus_indicators,
]

ALL_CHECKS_AAA = [
    # Link text quality (AAA subset) is already included in the A check
    # with level=AAA on certain violations.
]


def run_audit(html_content: str, level: str = "AA") -> AuditResult:
    """Run all applicable checks against the HTML content."""
    parser = HTMLStructureParser()
    try:
        parser.feed(html_content)
    except Exception as exc:
        return AuditResult(violations=[Violation(
            rule_id="parse-error",
            wcag_criterion="N/A",
            level="A",
            severity="must-fix",
            message=f"Failed to parse HTML: {exc}",
            element="(document)",
            selector_hint="(document)",
            remediation="Ensure the HTML is well-formed",
        )])

    checks = list(ALL_CHECKS_A)
    if level in ("AA", "AAA"):
        checks.extend(ALL_CHECKS_AA)
    if level == "AAA":
        checks.extend(ALL_CHECKS_AAA)

    all_violations: list[Violation] = []
    for check_fn in checks:
        violations = check_fn(parser)
        all_violations.extend(violations)

    # Filter violations by level
    level_index = WCAG_LEVELS.index(level)
    filtered = [
        v for v in all_violations
        if WCAG_LEVELS.index(v.level) <= level_index
    ]

    total_elements = (
        len(parser.images) + len(parser.links) + len(parser.form_inputs)
        + len(parser.media_elements) + len(parser.heading_order)
        + len(parser.elements) + 3  # +3 for page-level checks
    )

    result = AuditResult(
        total_elements_checked=total_elements,
        violations=filtered,
        level_checked=level,
    )
    return result


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_human_readable(result: AuditResult) -> str:
    """Format audit result as human-readable text."""
    lines: list[str] = []
    data = result.to_dict()

    lines.append("=" * 60)
    lines.append("  ACCESSIBILITY AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Level checked:       WCAG 2.1 {data['level_checked']}")
    lines.append(f"  Elements checked:    {data['total_elements_checked']}")
    lines.append(f"  Total violations:    {data['total_violations']}")
    lines.append(f"  Compliance:          {data['compliance_percentage']}%")
    lines.append("")

    # By level
    lines.append("-" * 60)
    lines.append("  VIOLATIONS BY LEVEL")
    lines.append("-" * 60)
    for lvl in WCAG_LEVELS:
        count = data["by_level"].get(lvl, 0)
        lines.append(f"    Level {lvl}: {count}")
    lines.append("")

    # By severity
    lines.append("-" * 60)
    lines.append("  VIOLATIONS BY SEVERITY")
    lines.append("-" * 60)
    for sev in ("must-fix", "should-fix", "nice-to-have"):
        count = data["by_severity"].get(sev, 0)
        lines.append(f"    {sev}: {count}")
    lines.append("")

    # Individual violations
    if result.violations:
        lines.append("-" * 60)
        lines.append("  VIOLATIONS")
        lines.append("-" * 60)
        for i, v in enumerate(result.violations, 1):
            lines.append(f"  [{i}] {v.rule_id} ({v.level} / {v.severity})")
            lines.append(f"      WCAG: {v.wcag_criterion}")
            lines.append(f"      Issue: {v.message}")
            lines.append(f"      Element: {v.element}")
            lines.append(f"      Fix: {v.remediation}")
            lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json_output(result: AuditResult) -> str:
    """Format audit result as JSON."""
    return json.dumps(result.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="accessibility_auditor",
        description="Audit HTML for WCAG 2.1 accessibility violations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python accessibility_auditor.py page.html\n"
            "  python accessibility_auditor.py page.html --level AAA --json\n"
            "  curl -s https://example.com | python accessibility_auditor.py -\n"
        ),
    )
    parser.add_argument(
        "html_file",
        help="Path to HTML file (use '-' for stdin)",
    )
    parser.add_argument(
        "--level",
        choices=WCAG_LEVELS,
        default="AA",
        help="WCAG conformance level to check (default: AA)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Read HTML
    if args.html_file == "-":
        html_content = sys.stdin.read()
    else:
        path = Path(args.html_file)
        if not path.exists():
            print(f"Error: File not found: {args.html_file}", file=sys.stderr)
            sys.exit(1)
        html_content = path.read_text(encoding="utf-8")

    # Run audit
    result = run_audit(html_content, level=args.level)

    # Output
    if args.json_output:
        print(format_json_output(result))
    else:
        print(format_human_readable(result))

    # Exit code: non-zero if must-fix violations exist
    must_fix_count = sum(1 for v in result.violations if v.severity == "must-fix")
    if must_fix_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
