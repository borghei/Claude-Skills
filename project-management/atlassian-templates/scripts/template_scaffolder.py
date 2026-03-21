#!/usr/bin/env python3
"""Template Scaffolder - Generate Confluence/Jira template scaffolds from specs.

Reads a template specification and generates ready-to-deploy Confluence
storage format or Jira description markup.

Usage:
    python template_scaffolder.py --spec spec.json --format confluence
    python template_scaffolder.py --spec spec.json --format jira --json
    python template_scaffolder.py --example
"""

import argparse
import json
import sys


CONFLUENCE_SECTION_TEMPLATES = {
    "header_panel": '{panel:title=__TITLE__|borderColor=#0052cc}\n__CONTENT__\n{panel}\n',
    "info_block": '{info}\n__CONTENT__\n{info}\n',
    "warning_block": '{warning}\n__CONTENT__\n{warning}\n',
    "table": '| __HEADERS__ |\n| __SEPARATOR__ |\n| __ROWS__ |\n',
    "task_list": '{tasks}\n__ITEMS__\n{tasks}\n',
    "expand": '{expand:title=__TITLE__}\n__CONTENT__\n{expand}\n',
    "heading": 'h__LEVEL__. __TITLE__\n',
    "toc": '{toc:maxLevel=3}\n',
}


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def generate_confluence(spec: dict) -> str:
    """Generate Confluence storage format template."""
    name = spec.get("name", "Untitled Template")
    sections = spec.get("sections", [])
    metadata = spec.get("metadata", {})

    output = []

    # Header panel
    meta_lines = []
    for key, value in metadata.items():
        meta_lines.append(f"**{key}**: {value}")
    if meta_lines:
        panel = CONFLUENCE_SECTION_TEMPLATES["header_panel"]
        panel = panel.replace("__TITLE__", name)
        panel = panel.replace("__CONTENT__", "\n".join(meta_lines))
        output.append(panel)

    # TOC
    if spec.get("include_toc", True):
        output.append(CONFLUENCE_SECTION_TEMPLATES["toc"])

    # Sections
    for section in sections:
        sec_type = section.get("type", "heading")
        title = section.get("title", "Section")
        content = section.get("content", "[Add content here]")
        level = section.get("level", 2)

        if sec_type == "heading":
            heading = CONFLUENCE_SECTION_TEMPLATES["heading"]
            heading = heading.replace("__LEVEL__", str(level))
            heading = heading.replace("__TITLE__", title)
            output.append(heading)
            output.append(content + "\n")

        elif sec_type == "table":
            headers = section.get("headers", ["Column 1", "Column 2"])
            rows = section.get("rows", 3)
            heading = CONFLUENCE_SECTION_TEMPLATES["heading"].replace("__LEVEL__", str(level)).replace("__TITLE__", title)
            output.append(heading)
            header_row = " | ".join(headers)
            separator = " | ".join(["---"] * len(headers))
            row_template = " | ".join(["[Enter value]"] * len(headers))
            row_lines = "\n".join([f"| {row_template} |"] * rows)
            output.append(f"| {header_row} |\n| {separator} |\n{row_lines}\n")

        elif sec_type == "task_list":
            heading = CONFLUENCE_SECTION_TEMPLATES["heading"].replace("__LEVEL__", str(level)).replace("__TITLE__", title)
            output.append(heading)
            items = section.get("items", ["Task 1", "Task 2", "Task 3"])
            item_lines = "\n".join([f"- [ ] {item}" for item in items])
            tasks = CONFLUENCE_SECTION_TEMPLATES["task_list"].replace("__ITEMS__", item_lines)
            output.append(tasks)

        elif sec_type == "expand":
            expand = CONFLUENCE_SECTION_TEMPLATES["expand"]
            expand = expand.replace("__TITLE__", title)
            expand = expand.replace("__CONTENT__", content)
            output.append(expand)

        elif sec_type == "info":
            heading = CONFLUENCE_SECTION_TEMPLATES["heading"].replace("__LEVEL__", str(level)).replace("__TITLE__", title)
            output.append(heading)
            info = CONFLUENCE_SECTION_TEMPLATES["info_block"].replace("__CONTENT__", content)
            output.append(info)

    return "\n".join(output)


def generate_jira(spec: dict) -> str:
    """Generate Jira description template."""
    name = spec.get("name", "Untitled")
    sections = spec.get("sections", [])

    output = []
    for section in sections:
        title = section.get("title", "Section")
        content = section.get("content", "[Add details]")
        sec_type = section.get("type", "heading")

        output.append(f"## {title}")

        if sec_type == "table":
            headers = section.get("headers", ["Column 1", "Column 2"])
            output.append("| " + " | ".join(headers) + " |")
            output.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for _ in range(section.get("rows", 2)):
                output.append("| " + " | ".join([""] * len(headers)) + " |")
        elif sec_type == "task_list":
            items = section.get("items", ["Item 1", "Item 2"])
            for item in items:
                output.append(f"- [ ] {item}")
        else:
            output.append(content)

        output.append("")

    return "\n".join(output)


def scaffold_template(spec: dict, fmt: str) -> dict:
    if fmt == "confluence":
        content = generate_confluence(spec)
    else:
        content = generate_jira(spec)

    return {
        "name": spec.get("name", "Untitled"),
        "format": fmt,
        "section_count": len(spec.get("sections", [])),
        "content": content,
    }


def print_report(result: dict) -> None:
    print(f"\nTemplate Scaffold: {result['name']}")
    print(f"Format: {result['format']}  |  Sections: {result['section_count']}")
    print("=" * 60)
    print(result["content"])


def print_example() -> None:
    example = {
        "name": "Sprint Retrospective",
        "include_toc": True,
        "metadata": {
            "Sprint": "[Sprint Number]",
            "Date": "{date}",
            "Team": "[Team Name]",
            "Facilitator": "@facilitator",
        },
        "sections": [
            {"type": "heading", "title": "Sprint Overview", "level": 2, "content": "**Sprint Goal**: [Goal]\n**Velocity**: [X points]\n**Completed**: [X/Y stories]"},
            {"type": "heading", "title": "What Went Well", "level": 2, "content": "- [Positive item 1]\n- [Positive item 2]"},
            {"type": "heading", "title": "What Needs Improvement", "level": 2, "content": "- [Challenge 1]\n- [Challenge 2]"},
            {"type": "table", "title": "Improvement Ideas", "level": 2, "headers": ["Idea", "Votes", "Owner", "Target Sprint"], "rows": 3},
            {"type": "task_list", "title": "Action Items", "level": 2, "items": ["Action 1 - @owner - Due: [Date]", "Action 2 - @owner - Due: [Date]"]},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Generate Confluence/Jira template scaffolds.")
    parser.add_argument("--spec", type=str, help="Path to template spec JSON file")
    parser.add_argument("--format", choices=["confluence", "jira"], default="confluence", help="Output format")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example spec and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.spec:
        parser.error("--spec is required")

    spec = load_data(args.spec)
    result = scaffold_template(spec, args.format)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
