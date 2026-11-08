#!/usr/bin/env python3
"""
React Component Generator

Generates React/Next.js component files with TypeScript, Tailwind CSS,
and optional test files following best practices.

Usage:
    python component_generator.py Button --dir src/components/ui
    python component_generator.py ProductCard --type client --with-test
    python component_generator.py UserProfile --type server --with-story --format json

Templates live in assets/templates/component/*.tmpl.
Exit codes: 0 ok, 2 bad input (unknown type, unwritable directory, missing templates).
"""

import argparse
import json
import sys
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "templates" / "component"
# Storybook 10 types come from the framework package the scaffolder installs
STORYBOOK_PACKAGES = {"next": "@storybook/nextjs-vite", "vite": "@storybook/react-vite"}
TEMPLATE_FILES = {
    "client": "client.tsx.tmpl",
    "server": "server.tsx.tmpl",
    "hook": "hook.ts.tmpl",
    "test": "test.tsx.tmpl",
    "story": "story.tsx.tmpl",
    "index": "index.ts.tmpl",
    "index_hook": "index_hook.ts.tmpl",
}


def load_templates(template_dir: Path = TEMPLATE_DIR) -> dict:
    """Load the str.format templates ({name} placeholder, doubled literal braces)."""
    return {key: (template_dir / fname).read_text(encoding="utf-8")
            for key, fname in TEMPLATE_FILES.items()}


try:
    TEMPLATES = load_templates()
except OSError as _exc:
    print(f"Error: cannot load component templates from {TEMPLATE_DIR}: {_exc}", file=sys.stderr)
    sys.exit(2)


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    # Handle kebab-case and snake_case
    words = name.replace('-', '_').replace(' ', '_').split('_')
    # Upper-case only the first letter so existing caps survive: ProductCard stays ProductCard
    return ''.join(word[:1].upper() + word[1:] for word in words if word)


def to_kebab_case(name: str) -> str:
    """Convert PascalCase to kebab-case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('-')
        result.append(char.lower())
    return ''.join(result)


def component_name(name: str, component_type: str) -> str:
    """PascalCase name; for hooks a leading 'use' is dropped so useThing -> Thing -> useThing."""
    pascal = to_pascal_case(name)
    if component_type == "hook" and len(pascal) > 3 and pascal.startswith("Use") and pascal[3].isupper():
        pascal = pascal[3:]
    return pascal


def generate_component(
    name: str,
    output_dir: Path,
    component_type: str = "client",
    with_test: bool = False,
    with_story: bool = False,
    with_index: bool = True,
    flat: bool = False,
    framework: str = "next",
    force: bool = False,
) -> dict:
    """Generate component files; refuses to overwrite existing files unless force."""
    pascal_name = component_name(name, component_type)
    component_dir = output_dir if flat else output_dir / pascal_name
    is_hook = component_type == "hook"

    # Plan every file first so nothing is written when one already exists
    planned = []
    if is_hook:
        planned.append((f"use{pascal_name}.ts", TEMPLATES["hook"].format(name=pascal_name)))
    else:
        planned.append((f"{pascal_name}.tsx", TEMPLATES[component_type].format(name=pascal_name)))
        if with_test:
            planned.append((f"{pascal_name}.test.tsx", TEMPLATES["test"].format(name=pascal_name)))
        if with_story:
            planned.append((f"{pascal_name}.stories.tsx", TEMPLATES["story"].format(
                name=pascal_name, storybook_pkg=STORYBOOK_PACKAGES[framework])))
    if with_index and not flat:
        planned.append(("index.ts", TEMPLATES["index_hook" if is_hook else "index"].format(name=pascal_name)))

    existing = [str(component_dir / fname) for fname, _ in planned if (component_dir / fname).exists()]
    if existing and not force:
        raise FileExistsError(f"refusing to overwrite {', '.join(existing)} (pass --force)")

    component_dir.mkdir(parents=True, exist_ok=True)
    files_created = []
    for fname, content in planned:
        (component_dir / fname).write_text(content)
        files_created.append(str(component_dir / fname))

    return {
        "name": pascal_name,
        "type": component_type,
        "directory": str(component_dir),
        "files": files_created,
    }


def print_result(result: dict, verbose: bool = False) -> None:
    """Print generation result."""
    print(f"\n{'='*50}")
    print(f"Component Generated: {result['name']}")
    print(f"{'='*50}")
    print(f"Type: {result['type']}")
    print(f"Directory: {result['directory']}")
    print(f"\nFiles created:")
    for file in result['files']:
        print(f"  - {file}")
    print(f"{'='*50}\n")

    # Print usage hint
    if result['type'] != 'hook':
        print("Usage:")
        print(f"  import {{ {result['name']} }} from '@/components/{result['name']}';")
        print(f"\n  <{result['name']}>Content</{result['name']}>")
    else:
        print("Usage:")
        print(f"  import {{ use{result['name']} }} from '@/hooks/use{result['name']}';")
        print(f"\n  const {{ isLoading, error }} = use{result['name']}();")


def main():
    parser = argparse.ArgumentParser(
        description="Generate React/Next.js components with TypeScript and Tailwind CSS"
    )
    parser.add_argument(
        "name",
        help="Component name (PascalCase or kebab-case)"
    )
    parser.add_argument(
        "--dir", "-d",
        default="src/components",
        help="Output directory (default: src/components)"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["client", "server", "hook"],
        default="client",
        help="Component type (default: client)"
    )
    parser.add_argument(
        "--with-test",
        action="store_true",
        help="Generate test file"
    )
    parser.add_argument(
        "--with-story",
        action="store_true",
        help="Generate Storybook story file"
    )
    parser.add_argument(
        "--framework",
        choices=sorted(STORYBOOK_PACKAGES),
        default="next",
        help="Framework for story imports: next (@storybook/nextjs-vite) or vite (@storybook/react-vite)"
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Skip generating index.ts file"
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Create files directly in output dir without subdirectory"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files that already exist (default: refuse, exit 2)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without creating files"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    output_dir = Path(args.dir)
    pascal_name = component_name(args.name, args.type)

    if args.dry_run and args.format == "json":
        print(json.dumps({
            "dry_run": True,
            "name": pascal_name,
            "type": args.type,
            "directory": str(output_dir / pascal_name if not args.flat else output_dir),
            "with_test": args.with_test,
            "with_story": args.with_story,
        }, indent=2))
        return

    if args.dry_run:
        print(f"\nDry run - would generate:")
        print(f"  Component: {pascal_name}")
        print(f"  Type: {args.type}")
        print(f"  Directory: {output_dir / pascal_name if not args.flat else output_dir}")
        print(f"  Test: {'Yes' if args.with_test else 'No'}")
        print(f"  Story: {'Yes' if args.with_story else 'No'}")
        return

    try:
        result = generate_component(
            name=args.name,
            output_dir=output_dir,
            component_type=args.type,
            with_test=args.with_test,
            with_story=args.with_story,
            with_index=not args.no_index,
            flat=args.flat,
            framework=args.framework,
            force=args.force,
        )
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print_result(result, args.verbose)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
