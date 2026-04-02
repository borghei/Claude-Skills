#!/usr/bin/env python3
"""
Form Automation Builder - Generate form automation scripts from HTML analysis.

Parses HTML forms, identifies field types and validation requirements, and generates
ready-to-use automation scripts with proper field handling and submission logic.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from html.parser import HTMLParser
import textwrap


@dataclass
class FormField:
    """Represents a form field."""
    name: str
    field_type: str  # text, email, password, select, checkbox, radio, textarea, file, hidden, date, number
    label: Optional[str] = None
    required: bool = False
    placeholder: Optional[str] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    options: List[str] = field(default_factory=list)  # for select/radio
    default_value: Optional[str] = None


@dataclass
class FormInfo:
    """Represents an HTML form."""
    action: str = ""
    method: str = "GET"
    enctype: str = "application/x-www-form-urlencoded"
    form_id: Optional[str] = None
    fields: List[FormField] = field(default_factory=list)
    has_csrf: bool = False
    csrf_field_name: Optional[str] = None
    has_captcha: bool = False


class FormHTMLParser(HTMLParser):
    """Parse HTML to extract form structure."""

    def __init__(self):
        super().__init__()
        self.forms: List[FormInfo] = []
        self.current_form: Optional[FormInfo] = None
        self.current_select_name: Optional[str] = None
        self.current_select_options: List[str] = []
        self.current_label_for: Optional[str] = None
        self.current_label_text: str = ""
        self.in_label = False
        self.in_select = False
        self.in_option = False
        self.current_option_value: Optional[str] = None
        self.labels: Dict[str, str] = {}
        self.in_textarea = False
        self.current_textarea_name: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k: v for k, v in attrs if v is not None}

        if tag == "form":
            self.current_form = FormInfo(
                action=attr_dict.get("action", ""),
                method=attr_dict.get("method", "GET").upper(),
                enctype=attr_dict.get("enctype", "application/x-www-form-urlencoded"),
                form_id=attr_dict.get("id"),
            )

        elif tag == "input" and self.current_form is not None:
            input_type = attr_dict.get("type", "text").lower()
            name = attr_dict.get("name", "")
            if not name:
                return

            # Check for CSRF tokens
            if any(tok in name.lower() for tok in ["csrf", "_token", "authenticity_token", "__requestverificationtoken"]):
                self.current_form.has_csrf = True
                self.current_form.csrf_field_name = name
                self.current_form.fields.append(FormField(
                    name=name, field_type="hidden", default_value=attr_dict.get("value", "")
                ))
                return

            # Check for CAPTCHA
            if any(tok in name.lower() for tok in ["captcha", "recaptcha", "hcaptcha"]):
                self.current_form.has_captcha = True
                return

            ff = FormField(
                name=name,
                field_type=input_type,
                required="required" in {k for k, _ in attrs},
                placeholder=attr_dict.get("placeholder"),
                pattern=attr_dict.get("pattern"),
                default_value=attr_dict.get("value"),
            )
            if attr_dict.get("minlength"):
                try:
                    ff.min_length = int(attr_dict["minlength"])
                except ValueError:
                    pass
            if attr_dict.get("maxlength"):
                try:
                    ff.max_length = int(attr_dict["maxlength"])
                except ValueError:
                    pass
            self.current_form.fields.append(ff)

        elif tag == "select" and self.current_form is not None:
            self.in_select = True
            self.current_select_name = attr_dict.get("name", "")
            self.current_select_options = []

        elif tag == "option" and self.in_select:
            self.in_option = True
            self.current_option_value = attr_dict.get("value", "")

        elif tag == "textarea" and self.current_form is not None:
            self.in_textarea = True
            self.current_textarea_name = attr_dict.get("name", "")

        elif tag == "label":
            self.in_label = True
            self.current_label_for = attr_dict.get("for")
            self.current_label_text = ""

    def handle_data(self, data: str):
        if self.in_label:
            self.current_label_text += data.strip()
        if self.in_option:
            text = data.strip()
            if text and self.current_option_value is not None:
                self.current_select_options.append(self.current_option_value or text)

    def handle_endtag(self, tag: str):
        if tag == "form" and self.current_form is not None:
            # Apply collected labels
            for f in self.current_form.fields:
                if f.name in self.labels:
                    f.label = self.labels[f.name]
            self.forms.append(self.current_form)
            self.current_form = None
            self.labels = {}

        elif tag == "select" and self.in_select and self.current_form is not None:
            self.current_form.fields.append(FormField(
                name=self.current_select_name or "",
                field_type="select",
                options=self.current_select_options,
            ))
            self.in_select = False

        elif tag == "option":
            self.in_option = False
            self.current_option_value = None

        elif tag == "textarea" and self.in_textarea and self.current_form is not None:
            self.current_form.fields.append(FormField(
                name=self.current_textarea_name or "",
                field_type="textarea",
            ))
            self.in_textarea = False

        elif tag == "label" and self.in_label:
            self.in_label = False
            if self.current_label_for:
                self.labels[self.current_label_for] = self.current_label_text


def parse_html(html_content: str) -> List[FormInfo]:
    """Parse HTML content and extract form information."""
    parser = FormHTMLParser()
    parser.feed(html_content)
    return parser.forms


def generate_requests_script(form: FormInfo, base_url: str) -> str:
    """Generate a Python requests-based automation script."""
    lines = []
    lines.append('#!/usr/bin/env python3')
    lines.append('"""Auto-generated form automation script using requests."""')
    lines.append('')
    lines.append('import requests')
    lines.append('import time')
    lines.append('import random')
    lines.append('')
    lines.append('')
    lines.append('def submit_form(session=None):')
    lines.append('    """Submit the form with the configured data."""')
    lines.append('    if session is None:')
    lines.append('        session = requests.Session()')
    lines.append('')
    lines.append('    # Configure headers')
    lines.append('    session.headers.update({')
    lines.append('        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",')
    lines.append('        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",')
    lines.append('        "Accept-Language": "en-US,en;q=0.9",')
    lines.append('    })')
    lines.append('')

    if form.has_csrf:
        lines.append(f'    # Fetch CSRF token from form page')
        action_url = form.action if form.action.startswith("http") else f"{base_url}{form.action}"
        lines.append(f'    page = session.get("{action_url}")')
        lines.append(f'    # TODO: Extract CSRF token "{form.csrf_field_name}" from page.text')
        lines.append(f'    csrf_token = ""  # Extract from HTML')
        lines.append('')

    lines.append('    # Form data')
    lines.append('    data = {')

    for f in form.fields:
        if f.field_type == "hidden":
            if form.has_csrf and f.name == form.csrf_field_name:
                lines.append(f'        "{f.name}": csrf_token,')
            else:
                lines.append(f'        "{f.name}": "{f.default_value or ""}",')
        elif f.field_type == "select":
            opts = f.options[:3] if f.options else ["option1"]
            lines.append(f'        "{f.name}": "{opts[0]}",  # Options: {opts}')
        elif f.field_type == "checkbox":
            lines.append(f'        "{f.name}": "on",  # checkbox')
        elif f.field_type == "file":
            continue  # handled separately
        else:
            label = f.label or f.name
            req = " (REQUIRED)" if f.required else ""
            lines.append(f'        "{f.name}": "",  # {f.field_type}: {label}{req}')

    lines.append('    }')
    lines.append('')

    # Handle file uploads
    file_fields = [f for f in form.fields if f.field_type == "file"]
    if file_fields:
        lines.append('    # File uploads')
        lines.append('    files = {')
        for f in file_fields:
            lines.append(f'        "{f.name}": ("filename.ext", open("path/to/file", "rb"), "application/octet-stream"),')
        lines.append('    }')
        lines.append('')

    action = form.action if form.action.startswith("http") else f"{base_url}{form.action}"
    method = form.method.lower()

    lines.append(f'    # Submit form ({form.method} {form.action})')
    lines.append(f'    time.sleep(random.uniform(1.0, 3.0))  # Human-like delay')

    if file_fields:
        lines.append(f'    response = session.{method}("{action}", data=data, files=files)')
    else:
        lines.append(f'    response = session.{method}("{action}", data=data)')

    lines.append('')
    lines.append('    print(f"Status: {response.status_code}")')
    lines.append('    return response')
    lines.append('')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    submit_form()')

    return "\n".join(lines)


def generate_analysis(forms: List[FormInfo]) -> Dict:
    """Generate analysis summary of discovered forms."""
    analysis = {
        "total_forms": len(forms),
        "forms": [],
    }
    for i, form in enumerate(forms):
        form_info = {
            "index": i,
            "action": form.action,
            "method": form.method,
            "enctype": form.enctype,
            "total_fields": len(form.fields),
            "required_fields": sum(1 for f in form.fields if f.required),
            "has_csrf": form.has_csrf,
            "has_captcha": form.has_captcha,
            "has_file_upload": any(f.field_type == "file" for f in form.fields),
            "field_types": {},
            "fields": [asdict(f) for f in form.fields],
        }
        for f in form.fields:
            form_info["field_types"][f.field_type] = form_info["field_types"].get(f.field_type, 0) + 1
        analysis["forms"].append(form_info)
    return analysis


def format_human(analysis: Dict, script: Optional[str]) -> str:
    """Format for human output."""
    lines = []
    lines.append("=" * 60)
    lines.append("FORM AUTOMATION ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"Total forms found: {analysis['total_forms']}")
    lines.append("")

    for form in analysis["forms"]:
        lines.append(f"Form #{form['index']}: {form['method']} {form['action']}")
        lines.append(f"  Fields: {form['total_fields']} ({form['required_fields']} required)")
        lines.append(f"  CSRF: {'Yes' if form['has_csrf'] else 'No'}")
        lines.append(f"  CAPTCHA: {'Yes (manual intervention needed)' if form['has_captcha'] else 'No'}")
        lines.append(f"  File Upload: {'Yes' if form['has_file_upload'] else 'No'}")
        lines.append(f"  Field Types: {form['field_types']}")
        lines.append("")
        for f in form["fields"]:
            req = "*" if f.get("required") else " "
            lines.append(f"  {req} [{f['field_type']:10s}] {f['name']}")
        lines.append("")

    if script:
        lines.append("-" * 60)
        lines.append("GENERATED SCRIPT:")
        lines.append("-" * 60)
        lines.append(script)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Form Automation Builder - Generate form automation scripts from HTML"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html-file", help="Path to HTML file containing forms")
    group.add_argument("--url", help="Base URL (used with --html-file for resolving relative actions)")
    parser.add_argument("--output", help="Write generated script to file")
    parser.add_argument("--form-index", type=int, default=0,
                        help="Index of form to generate script for (default: 0)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")
    parser.add_argument("--base-url", default="https://example.com",
                        help="Base URL for resolving relative form actions")

    args = parser.parse_args()

    if args.html_file:
        path = Path(args.html_file)
        if not path.exists():
            print(f"Error: File not found: {args.html_file}", file=sys.stderr)
            sys.exit(1)
        html_content = path.read_text(encoding="utf-8", errors="ignore")
        base_url = args.base_url
    else:
        print("Error: --url requires fetching which is not supported. Use --html-file instead.", file=sys.stderr)
        print("Save the HTML page locally first, then use --html-file.", file=sys.stderr)
        sys.exit(1)

    forms = parse_html(html_content)
    if not forms:
        print("No forms found in the HTML content.", file=sys.stderr)
        sys.exit(1)

    analysis = generate_analysis(forms)

    script = None
    if args.form_index < len(forms):
        script = generate_requests_script(forms[args.form_index], base_url)
        if args.output:
            Path(args.output).write_text(script)
            print(f"Script written to: {args.output}")

    if args.format == "json":
        output = json.dumps(analysis, indent=2)
    else:
        output = format_human(analysis, script)

    print(output)


if __name__ == "__main__":
    main()
