#!/usr/bin/env python3
"""Generate Playwright Page Object Model classes from HTML or selector lists.

Parses HTML files to extract interactive elements (inputs, buttons, links,
headings) and generates TypeScript Page Object classes following Playwright
best practices: semantic locators, user-intent methods, and proper typing.

Usage:
    python page_object_generator.py --html page.html --name LoginPage
    python page_object_generator.py --selectors selectors.txt --name DashboardPage
    python page_object_generator.py --html page.html --name LoginPage --json
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class ElementExtractor(HTMLParser):
    """Extract interactive elements from HTML for Page Object generation."""

    INTERACTIVE_TAGS = {"input", "button", "a", "select", "textarea", "form"}
    LANDMARK_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "nav", "main", "header", "footer"}

    def __init__(self):
        super().__init__()
        self.elements = []
        self._current_tag = None
        self._current_attrs = {}
        self._current_text = ""
        self._capture_text = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        tag_lower = tag.lower()

        if tag_lower in self.INTERACTIVE_TAGS or tag_lower in self.LANDMARK_TAGS:
            self._current_tag = tag_lower
            self._current_attrs = attr_dict
            self._current_text = ""
            self._capture_text = True

        if tag_lower == "input" or (tag_lower == "img"):
            # Self-closing: record immediately
            if tag_lower == "input":
                self._record_element(tag_lower, attr_dict, "")

    def handle_data(self, data):
        if self._capture_text:
            self._current_text += data.strip()

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == self._current_tag and self._capture_text:
            self._record_element(tag_lower, self._current_attrs, self._current_text)
            self._capture_text = False
            self._current_tag = None

    def _record_element(self, tag, attrs, text):
        element = {
            "tag": tag,
            "text": text,
            "id": attrs.get("id", ""),
            "name": attrs.get("name", ""),
            "type": attrs.get("type", ""),
            "role": attrs.get("role", ""),
            "aria_label": attrs.get("aria-label", ""),
            "placeholder": attrs.get("placeholder", ""),
            "data_testid": attrs.get("data-testid", ""),
            "href": attrs.get("href", ""),
            "class": attrs.get("class", ""),
            "for": attrs.get("for", ""),
            "label_text": attrs.get("aria-label", "") or attrs.get("placeholder", ""),
        }
        self.elements.append(element)


def parse_selector_file(filepath):
    """Parse a text file of selectors (one per line) into elements.

    Format per line: locator_type:value:property_name
    Examples:
        role:button:Submit:submitButton
        label:Email address:emailInput
        testid:nav-menu:navMenu
        text:Welcome back:welcomeText
    """
    elements = []
    content = Path(filepath).read_text(encoding="utf-8")
    for line_num, line in enumerate(content.strip().split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":")
        if len(parts) < 3:
            print(f"Warning: Line {line_num} skipped (format: type:value:propertyName): {line}", file=sys.stderr)
            continue
        loc_type = parts[0].strip().lower()
        value = parts[1].strip()
        prop_name = parts[2].strip()
        role_name = parts[3].strip() if len(parts) > 3 else ""
        elements.append({
            "locator_type": loc_type,
            "value": value,
            "property_name": prop_name,
            "role_name": role_name,
        })
    return elements


def to_camel_case(text):
    """Convert text to camelCase for property names."""
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    words = text.strip().split()
    if not words:
        return "element"
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def determine_locator(element):
    """Determine the best Playwright locator strategy for an element.

    Priority: getByRole > getByLabel > getByText > getByPlaceholder > getByTestId > CSS
    """
    tag = element.get("tag", "")
    text = element.get("text", "")
    aria_label = element.get("aria_label", "")
    placeholder = element.get("placeholder", "")
    data_testid = element.get("data_testid", "")
    el_type = element.get("type", "")
    el_id = element.get("id", "")
    el_name = element.get("name", "")
    role = element.get("role", "")

    # Determine ARIA role from tag
    role_map = {
        "button": "button",
        "a": "link",
        "h1": "heading",
        "h2": "heading",
        "h3": "heading",
        "h4": "heading",
        "h5": "heading",
        "h6": "heading",
        "nav": "navigation",
        "select": "combobox",
        "textarea": "textbox",
    }
    if el_type == "checkbox":
        inferred_role = "checkbox"
    elif el_type == "radio":
        inferred_role = "radio"
    elif tag == "input" and el_type in ("text", "email", "password", "search", "tel", "url", ""):
        inferred_role = "textbox"
    elif tag == "input" and el_type == "submit":
        inferred_role = "button"
    else:
        inferred_role = role or role_map.get(tag, "")

    display_name = aria_label or text

    # 1. getByRole (preferred)
    if inferred_role and display_name:
        return f"page.getByRole('{inferred_role}', {{ name: '{_escape(display_name)}' }})"
    if inferred_role and not display_name and tag in ("nav", "main", "header", "footer"):
        return f"page.getByRole('{inferred_role}')"

    # 2. getByLabel (form fields)
    if tag in ("input", "textarea", "select") and aria_label:
        return f"page.getByLabel('{_escape(aria_label)}')"

    # 3. getByText
    if text and tag not in ("input", "textarea", "select"):
        return f"page.getByText('{_escape(text)}')"

    # 4. getByPlaceholder
    if placeholder:
        return f"page.getByPlaceholder('{_escape(placeholder)}')"

    # 5. getByTestId
    if data_testid:
        return f"page.getByTestId('{_escape(data_testid)}')"

    # 6. CSS fallback
    if el_id:
        return f"page.locator('#{_escape(el_id)}')"
    if el_name:
        return f"page.locator('[name=\"{_escape(el_name)}\"]')"

    return f"page.locator('{tag}')"


def _escape(s):
    """Escape single quotes in strings for TypeScript output."""
    return s.replace("'", "\\'")


def generate_property_name(element, seen_names):
    """Generate a unique camelCase property name for an element."""
    tag = element.get("tag", "")
    text = element.get("text", "") or element.get("aria_label", "") or element.get("placeholder", "")
    data_testid = element.get("data_testid", "")
    el_name = element.get("name", "")
    el_id = element.get("id", "")

    base = text or data_testid or el_name or el_id or tag
    name = to_camel_case(base)

    # Add type suffix for clarity
    suffix_map = {"input": "Input", "button": "Button", "a": "Link", "select": "Select", "textarea": "TextArea"}
    tag_suffix = suffix_map.get(tag, "")
    if tag_suffix and not name.lower().endswith(tag_suffix.lower()):
        name = name + tag_suffix

    # Deduplicate
    original = name
    counter = 2
    while name in seen_names:
        name = f"{original}{counter}"
        counter += 1
    seen_names.add(name)
    return name


def generate_page_object(class_name, elements, page_path, source_type="html"):
    """Generate TypeScript Page Object class code."""
    lines = []
    seen_names = set()
    properties = []

    if source_type == "selectors":
        for el in elements:
            prop_name = el["property_name"]
            loc_type = el["locator_type"]
            value = el["value"]
            role_name = el.get("role_name", "")

            if loc_type == "role" and role_name:
                locator = f"page.getByRole('{value}', {{ name: '{_escape(role_name)}' }})"
            elif loc_type == "role":
                locator = f"page.getByRole('{value}')"
            elif loc_type == "label":
                locator = f"page.getByLabel('{_escape(value)}')"
            elif loc_type == "text":
                locator = f"page.getByText('{_escape(value)}')"
            elif loc_type == "placeholder":
                locator = f"page.getByPlaceholder('{_escape(value)}')"
            elif loc_type == "testid":
                locator = f"page.getByTestId('{_escape(value)}')"
            else:
                locator = f"page.locator('{_escape(value)}')"

            properties.append({"name": prop_name, "locator": locator})
    else:
        for el in elements:
            prop_name = generate_property_name(el, seen_names)
            locator = determine_locator(el)
            properties.append({"name": prop_name, "locator": locator})

    # Build TypeScript class
    lines.append(f"// {_filename_from_class(class_name)}")
    lines.append(f"import {{ type Page, type Locator, expect }} from '@playwright/test';")
    lines.append("")
    lines.append(f"export class {class_name} {{")
    lines.append(f"  readonly page: Page;")
    for prop in properties:
        lines.append(f"  readonly {prop['name']}: Locator;")

    lines.append("")
    lines.append(f"  constructor(page: Page) {{")
    lines.append(f"    this.page = page;")
    for prop in properties:
        lines.append(f"    this.{prop['name']} = {prop['locator']};")
    lines.append(f"  }}")

    # goto method
    lines.append("")
    lines.append(f"  async goto() {{")
    lines.append(f"    await this.page.goto('{page_path}');")
    lines.append(f"  }}")

    # expectLoaded method
    lines.append("")
    lines.append(f"  async expectLoaded() {{")
    if properties:
        lines.append(f"    await expect(this.{properties[0]['name']}).toBeVisible();")
    else:
        lines.append(f"    await expect(this.page).toHaveURL(/{page_path.replace('/', '\\\\/')}/);"  )
    lines.append(f"  }}")

    lines.append(f"}}")
    lines.append("")

    return "\n".join(lines), properties


def _filename_from_class(class_name):
    """Convert ClassName to class-name.page.ts."""
    name = re.sub(r"(?<!^)(?=[A-Z])", "-", class_name).lower()
    if not name.endswith("-page"):
        name += ".page"
    else:
        name = name.rsplit("-page", 1)[0] + ".page"
    return name + ".ts"


def format_human(class_name, code, properties, source):
    """Format output for human consumption."""
    output = []
    output.append("=" * 70)
    output.append("PAGE OBJECT GENERATOR")
    output.append("=" * 70)
    output.append("")
    output.append(f"  Class:      {class_name}")
    output.append(f"  Source:     {source}")
    output.append(f"  Properties: {len(properties)}")
    output.append(f"  File:       {_filename_from_class(class_name)}")
    output.append("")
    output.append("-" * 70)
    output.append("GENERATED CODE")
    output.append("-" * 70)
    output.append("")
    output.append(code)
    output.append("-" * 70)
    output.append("")
    output.append("LOCATOR STRATEGY BREAKDOWN")
    output.append("-" * 70)

    strategy_counts = {"getByRole": 0, "getByLabel": 0, "getByText": 0,
                       "getByPlaceholder": 0, "getByTestId": 0, "locator (CSS)": 0}
    for prop in properties:
        loc = prop["locator"]
        if "getByRole" in loc:
            strategy_counts["getByRole"] += 1
        elif "getByLabel" in loc:
            strategy_counts["getByLabel"] += 1
        elif "getByText" in loc:
            strategy_counts["getByText"] += 1
        elif "getByPlaceholder" in loc:
            strategy_counts["getByPlaceholder"] += 1
        elif "getByTestId" in loc:
            strategy_counts["getByTestId"] += 1
        else:
            strategy_counts["locator (CSS)"] += 1

    for strategy, count in strategy_counts.items():
        if count > 0:
            bar = "#" * count
            output.append(f"  {strategy:<20} {count:>3}  {bar}")

    css_count = strategy_counts["locator (CSS)"]
    total = len(properties) or 1
    if css_count > 0:
        output.append("")
        pct = css_count / total * 100
        output.append(f"  WARNING: {pct:.0f}% of locators use CSS fallback. Consider adding")
        output.append(f"  aria-label, role, or data-testid attributes to improve resilience.")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright Page Object Model classes from HTML or selector lists.",
        epilog="Example: python page_object_generator.py --html login.html --name LoginPage --route /login",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--html", help="Path to HTML file to extract elements from")
    source_group.add_argument("--selectors", help="Path to selector list file (type:value:name per line)")
    parser.add_argument("--name", required=True, help="Name for the generated Page Object class (e.g., LoginPage)")
    parser.add_argument("--route", default="/", help="Page route for goto() method (default: /)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()

    if args.html:
        source_path = Path(args.html)
        if not source_path.exists():
            print(f"Error: HTML file '{args.html}' not found.", file=sys.stderr)
            sys.exit(1)
        html_content = source_path.read_text(encoding="utf-8")
        extractor = ElementExtractor()
        extractor.feed(html_content)
        elements = extractor.elements
        if not elements:
            print("Warning: No interactive elements found in the HTML.", file=sys.stderr)
        code, properties = generate_page_object(args.name, elements, args.route, source_type="html")
        source = str(source_path)
    else:
        source_path = Path(args.selectors)
        if not source_path.exists():
            print(f"Error: Selector file '{args.selectors}' not found.", file=sys.stderr)
            sys.exit(1)
        elements = parse_selector_file(source_path)
        if not elements:
            print("Error: No valid selectors found in file.", file=sys.stderr)
            sys.exit(1)
        code, properties = generate_page_object(args.name, elements, args.route, source_type="selectors")
        source = str(source_path)

    if args.json_output:
        result = {
            "class_name": args.name,
            "filename": _filename_from_class(args.name),
            "route": args.route,
            "source": source,
            "properties_count": len(properties),
            "properties": properties,
            "code": code,
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_human(args.name, code, properties, source))


if __name__ == "__main__":
    main()
