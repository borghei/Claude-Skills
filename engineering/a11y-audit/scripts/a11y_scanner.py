#!/usr/bin/env python3
"""
Accessibility Scanner - Scan HTML files for WCAG 2.1 violations.

Checks for missing alt text, heading hierarchy, form labels, ARIA usage,
link text quality, language attributes, and landmark regions.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple


@dataclass
class Finding:
    """An accessibility finding."""
    severity: str  # critical (A), warning (AA), info (AAA)
    wcag_level: str  # A, AA, AAA
    criterion: str  # e.g., "1.1.1"
    file: str
    line: int
    element: str
    message: str
    recommendation: str


class A11yHTMLParser(HTMLParser):
    """HTML parser that collects accessibility-relevant information."""

    GENERIC_LINK_TEXT = {
        "click here", "here", "read more", "more", "link", "learn more",
        "click", "this", "go", "start",
    }

    LANDMARK_ELEMENTS = {"header", "nav", "main", "aside", "footer", "section", "article"}
    FORM_INPUT_TYPES = {"text", "email", "password", "search", "tel", "url", "number", "date", "file"}

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.findings: List[Finding] = []
        self.heading_levels: List[Tuple[int, int]] = []  # (level, line)
        self.has_lang = False
        self.has_main = False
        self.has_h1 = False
        self.current_tag = ""
        self.current_attrs: Dict[str, Optional[str]] = {}
        self.tag_stack: List[str] = []
        self.label_for_ids: Set[str] = set()
        self.input_ids: List[Tuple[str, int]] = []  # (id, line)
        self.inputs_with_aria_label: Set[str] = set()
        self._in_label = False
        self._label_has_input = False
        self._current_data = ""
        self._in_a = False
        self._a_line = 0
        self._a_text = ""
        self._a_has_aria = False

    def handle_starttag(self, tag: str, attrs: list):
        tag = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}
        line = self.getpos()[0]

        self.tag_stack.append(tag)

        # Check html lang attribute
        if tag == "html":
            if "lang" in attr_dict and attr_dict["lang"]:
                self.has_lang = True
            else:
                self.findings.append(Finding(
                    severity="critical", wcag_level="A", criterion="3.1.1",
                    file=self.filename, line=line, element="<html>",
                    message="Missing or empty 'lang' attribute on <html> element.",
                    recommendation='Add lang attribute: <html lang="en">',
                ))

        # Check images for alt text
        if tag == "img":
            role = attr_dict.get("role", "")
            if role == "presentation" or attr_dict.get("aria-hidden") == "true":
                pass  # Decorative, skip
            elif "alt" not in attr_dict:
                self.findings.append(Finding(
                    severity="critical", wcag_level="A", criterion="1.1.1",
                    file=self.filename, line=line, element=f'<img src="{attr_dict.get("src", "")}">',
                    message="Image missing 'alt' attribute.",
                    recommendation="Add descriptive alt text, or alt='' for decorative images.",
                ))
            elif attr_dict["alt"] == "" and role != "presentation":
                # Empty alt without presentation role - could be intentional
                pass

        # Track headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.heading_levels.append((level, line))
            if level == 1:
                self.has_h1 = True

        # Track landmarks
        if tag == "main" or attr_dict.get("role") == "main":
            self.has_main = True

        # Track form labels
        if tag == "label":
            self._in_label = True
            self._label_has_input = False
            for_id = attr_dict.get("for", "")
            if for_id:
                self.label_for_ids.add(for_id)

        # Track form inputs
        if tag == "input":
            input_type = attr_dict.get("type", "text").lower()
            if input_type in self.FORM_INPUT_TYPES:
                input_id = attr_dict.get("id", "")
                has_aria = "aria-label" in attr_dict or "aria-labelledby" in attr_dict
                has_title = "title" in attr_dict
                if input_id:
                    self.input_ids.append((input_id, line))
                if has_aria:
                    if input_id:
                        self.inputs_with_aria_label.add(input_id)
                elif not input_id and not self._in_label and not has_title:
                    self.findings.append(Finding(
                        severity="critical", wcag_level="A", criterion="1.3.1",
                        file=self.filename, line=line,
                        element=f'<input type="{input_type}">',
                        message="Form input has no associated label, aria-label, or title.",
                        recommendation="Add a <label for='id'>, aria-label, or wrap input in <label>.",
                    ))
                if self._in_label:
                    self._label_has_input = True

        if tag == "textarea" or tag == "select":
            input_id = attr_dict.get("id", "")
            if input_id:
                self.input_ids.append((input_id, line))
            if "aria-label" in attr_dict or "aria-labelledby" in attr_dict:
                if input_id:
                    self.inputs_with_aria_label.add(input_id)

        # Track anchor tags for link text
        if tag == "a":
            self._in_a = True
            self._a_line = line
            self._a_text = ""
            self._a_has_aria = "aria-label" in attr_dict

        # Check tabindex
        tabindex = attr_dict.get("tabindex", "")
        if tabindex:
            try:
                idx = int(tabindex)
                if idx > 0:
                    self.findings.append(Finding(
                        severity="warning", wcag_level="AA", criterion="2.4.3",
                        file=self.filename, line=line, element=f"<{tag} tabindex=\"{idx}\">",
                        message=f"Positive tabindex ({idx}) disrupts natural tab order.",
                        recommendation="Use tabindex='0' for focusable or tabindex='-1' for programmatic focus.",
                    ))
            except ValueError:
                pass

        # Check for autoplaying media
        if tag in ("video", "audio"):
            if "autoplay" in attr_dict:
                self.findings.append(Finding(
                    severity="critical", wcag_level="A", criterion="1.4.2",
                    file=self.filename, line=line, element=f"<{tag} autoplay>",
                    message="Auto-playing media without user control.",
                    recommendation="Remove autoplay or add controls and muted attributes.",
                ))

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag == "label":
            self._in_label = False

        if tag == "a" and self._in_a:
            self._in_a = False
            text = self._a_text.strip().lower()
            if text and text in self.GENERIC_LINK_TEXT and not self._a_has_aria:
                self.findings.append(Finding(
                    severity="warning", wcag_level="AA", criterion="2.4.4",
                    file=self.filename, line=self._a_line,
                    element=f'<a>...{self._a_text.strip()}...</a>',
                    message=f"Generic link text '{self._a_text.strip()}' is not descriptive.",
                    recommendation="Use descriptive link text that explains the destination.",
                ))

    def handle_data(self, data: str):
        if self._in_a:
            self._a_text += data

    def finalize(self):
        """Run post-parse checks."""
        self._check_heading_hierarchy()
        self._check_unlabeled_inputs()
        self._check_missing_landmarks()

    def _check_heading_hierarchy(self):
        """Check heading levels are sequential."""
        if not self.heading_levels:
            return

        prev_level = 0
        for level, line in self.heading_levels:
            if level > prev_level + 1 and prev_level > 0:
                self.findings.append(Finding(
                    severity="warning", wcag_level="AA", criterion="1.3.1",
                    file=self.filename, line=line, element=f"<h{level}>",
                    message=f"Heading level skipped: h{prev_level} to h{level}.",
                    recommendation=f"Use h{prev_level + 1} instead, or restructure heading hierarchy.",
                ))
            prev_level = level

        if not self.has_h1:
            self.findings.append(Finding(
                severity="warning", wcag_level="AA", criterion="1.3.1",
                file=self.filename, line=0, element="(document)",
                message="No <h1> element found in page.",
                recommendation="Add exactly one <h1> element for the page title.",
            ))

    def _check_unlabeled_inputs(self):
        """Check for inputs without matching labels."""
        for input_id, line in self.input_ids:
            if input_id not in self.label_for_ids and input_id not in self.inputs_with_aria_label:
                self.findings.append(Finding(
                    severity="critical", wcag_level="A", criterion="1.3.1",
                    file=self.filename, line=line,
                    element=f'<input id="{input_id}">',
                    message=f"Input '{input_id}' has no matching <label for='{input_id}'>.",
                    recommendation=f'Add <label for="{input_id}">Label text</label> or aria-label.',
                ))

    def _check_missing_landmarks(self):
        """Check for missing landmark regions."""
        if not self.has_main:
            self.findings.append(Finding(
                severity="info", wcag_level="AAA", criterion="1.3.1",
                file=self.filename, line=0, element="(document)",
                message="No <main> landmark found.",
                recommendation="Wrap primary content in <main> element.",
            ))


def scan_file(filepath: Path) -> List[Finding]:
    """Scan a single HTML file."""
    content = filepath.read_text(errors="replace")
    parser = A11yHTMLParser(str(filepath))
    try:
        parser.feed(content)
    except Exception:
        pass
    parser.finalize()
    return parser.findings


def format_text(all_findings: Dict[str, List[Finding]]) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("ACCESSIBILITY SCAN REPORT (WCAG 2.1)")
    lines.append("=" * 60)

    total = sum(len(f) for f in all_findings.values())
    lines.append(f"\nFiles scanned: {len(all_findings)}")
    lines.append(f"Total findings: {total}")

    for filepath, findings in all_findings.items():
        if not findings:
            continue
        lines.append(f"\n--- {filepath} ---")
        critical = [f for f in findings if f.severity == "critical"]
        warnings = [f for f in findings if f.severity == "warning"]
        info = [f for f in findings if f.severity == "info"]

        for sev, group in [("CRITICAL [Level A]", critical),
                           ("WARNING [Level AA]", warnings),
                           ("INFO [Level AAA]", info)]:
            if not group:
                continue
            lines.append(f"\n  [{sev}]")
            for f in group:
                loc = f"line {f.line}" if f.line > 0 else "global"
                lines.append(f"    WCAG {f.criterion} ({loc}): {f.message}")
                lines.append(f"      Element: {f.element}")
                lines.append(f"      Fix: {f.recommendation}")

    if total == 0:
        lines.append("\nNo accessibility issues found.")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json(all_findings: Dict[str, List[Finding]]) -> str:
    """Format as JSON."""
    total_findings = []
    for filepath, findings in all_findings.items():
        for f in findings:
            total_findings.append(asdict(f))

    return json.dumps({
        "files_scanned": len(all_findings),
        "findings": total_findings,
        "summary": {
            "total": len(total_findings),
            "critical_a": sum(1 for f in total_findings if f["severity"] == "critical"),
            "warning_aa": sum(1 for f in total_findings if f["severity"] == "warning"),
            "info_aaa": sum(1 for f in total_findings if f["severity"] == "info"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Scan HTML files for WCAG 2.1 accessibility violations."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Path to a single HTML file")
    group.add_argument("--dir", "-d", help="Path to directory of HTML files")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--level", choices=["A", "AA", "AAA"], default="AAA",
                       help="Minimum WCAG level to report")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any finding at level")
    args = parser.parse_args()

    level_map = {"A": {"critical"}, "AA": {"critical", "warning"}, "AAA": {"critical", "warning", "info"}}
    include_severities = level_map[args.level]

    all_findings: Dict[str, List[Finding]] = {}

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(2)
        findings = scan_file(path)
        all_findings[str(path)] = [f for f in findings if f.severity in include_severities]
    else:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f"Error: Not a directory: {args.dir}", file=sys.stderr)
            sys.exit(2)
        for root, _, files in os.walk(dir_path):
            for fname in files:
                if fname.endswith((".html", ".htm")):
                    filepath = Path(root) / fname
                    findings = scan_file(filepath)
                    filtered = [f for f in findings if f.severity in include_severities]
                    all_findings[str(filepath)] = filtered

    if args.format == "json":
        print(format_json(all_findings))
    else:
        print(format_text(all_findings))

    total = sum(len(f) for f in all_findings.values())
    if args.strict and total > 0:
        sys.exit(1)
    elif any(f.severity == "critical" for findings in all_findings.values() for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
