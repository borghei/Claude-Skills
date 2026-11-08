#!/usr/bin/env python3
"""
Frontend Project Scaffolder

Generates a complete Next.js/React project structure with TypeScript,
Tailwind CSS, and best practice configurations. Every file body lives in
assets/templates/scaffold/ (manifest.json maps paths to template files),
so templates can be edited without touching this script.

Usage:
    python frontend_scaffolder.py my-app --template nextjs
    python frontend_scaffolder.py dashboard --template react --features auth,api
    python frontend_scaffolder.py landing --template nextjs --dry-run --format json

Exit codes: 0 ok, 2 bad input (target exists, unknown feature, unwritable path,
missing or broken template assets).
"""

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "templates" / "scaffold"


def load_manifest(template_dir: Path = TEMPLATE_DIR) -> Dict:
    """Load the scaffold manifest (templates, features, content and config file maps)."""
    with open(template_dir / "manifest.json", encoding="utf-8") as f:
        return json.load(f)


def read_template(rel_path: str, template_dir: Path = TEMPLATE_DIR) -> str:
    """Read one template file relative to the scaffold template folder."""
    return (template_dir / rel_path).read_text(encoding="utf-8")


try:
    MANIFEST = load_manifest()
except (OSError, json.JSONDecodeError) as _exc:
    print(f"error: cannot load scaffold templates from {TEMPLATE_DIR}: {_exc}", file=sys.stderr)
    sys.exit(2)

TEMPLATES: Dict = MANIFEST["templates"]
FEATURES: Dict = MANIFEST["features"]


def file_content(key: str, default: Optional[str] = "", template: str = "") -> Optional[str]:
    """Return the body for a content key, or ``default`` when the key has no template.

    Keys listed in the manifest's ``use_client`` get the directive in the nextjs
    template only; Vite has no Server Components, so it never needs one.
    """
    rel = MANIFEST["contents"].get(key)
    if rel is None:
        return default
    body = read_template(rel)
    if template == "nextjs" and key in MANIFEST.get("use_client", []):
        body = "'use client';\n\n" + body
    return body


def feature_spec(feature: str, template: str) -> Dict:
    """Return the per-template part of a feature (files, deps, scripts, notes)."""
    return FEATURES[feature].get(template, {})


def generate_structure(base_path: Path, structure: Dict, dry_run: bool = False) -> List[str]:
    """Generate directory structure recursively."""
    created_files = []
    for name, content in structure.items():
        current_path = base_path / name

        if isinstance(content, dict):  # a directory
            if not dry_run:
                current_path.mkdir(parents=True, exist_ok=True)
            created_files.extend(generate_structure(current_path, content, dry_run))
        else:  # a file
            if not dry_run:
                current_path.parent.mkdir(parents=True, exist_ok=True)
                current_path.write_text(file_content(content, ""))
            created_files.append(str(current_path))
    return created_files


def generate_config_files(project_path: Path, template: str, project_name: str,
                          features: List[str], dry_run: bool = False) -> List[str]:
    """Generate configuration files."""
    created_files = []
    config_templates = get_config_templates(project_name, template, features)
    template_config = TEMPLATES[template]
    for config_file in template_config["config_files"]:
        file_path = project_path / config_file
        if config_file in config_templates:
            if not dry_run:
                file_path.write_text(config_templates[config_file])
            created_files.append(str(file_path))
    return created_files


def get_config_templates(name: str, template: str, features: List[str]) -> Dict[str, str]:
    """Get configuration file contents."""
    package = copy.deepcopy(MANIFEST["package"][template])

    # Feature scripts and dependencies are appended, in the order the features were given
    for feature in features:
        if feature in FEATURES:
            spec = feature_spec(feature, template)
            for field in ("scripts", "dependencies", "devDependencies"):
                package[field].update(spec.get(field, {}))

    package_json = {"name": name, "version": "0.1.0", "private": True}
    for field in ("type", "scripts", "dependencies", "devDependencies"):
        if field in package:
            package_json[field] = package[field]

    configs = {"package.json": json.dumps(package_json, indent=2)}
    placeholder = MANIFEST["name_placeholder"]
    for config_file, rel in MANIFEST["configs"][template].items():
        configs[config_file] = read_template(rel).replace(placeholder, name)
    return configs


def scaffold_project(
    name: str,
    output_dir: Path,
    template: str = "nextjs",
    features: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict:
    """Scaffold a complete frontend project."""
    features = features or []
    project_path = output_dir / name
    # npm package names (unscoped): lowercase, URL-safe, no leading dot/underscore, <= 214 chars.
    # The same rule keeps the project folder inside --dir: no "/", "\\" or "..".
    if not (len(name) <= 214 and re.fullmatch(r"[a-z0-9~-][a-z0-9._~-]*", name)):
        return {"error": f"invalid project name {name!r}: use a lowercase npm package name "
                         "(letters, digits, '-', '.', '_', '~'; no spaces or slashes)"}
    if project_path.resolve().parent != output_dir.resolve():
        return {"error": f"project path escapes --dir: {project_path}"}

    if project_path.exists() and not dry_run:
        return {"error": f"Directory already exists: {project_path}"}

    template_config = TEMPLATES.get(template)
    if not template_config:
        return {"error": f"Unknown template: {template}"}

    created_files = []
    notes: List[str] = []

    if not dry_run:
        project_path.mkdir(parents=True, exist_ok=True)

    created_files.extend(
        generate_structure(project_path, template_config["structure"], dry_run)
    )

    created_files.extend(
        generate_config_files(project_path, template, name, features, dry_run)
    )

    # Add feature files
    for feature in features:
        if feature in FEATURES:
            spec = feature_spec(feature, template)
            for file_path, content_key in spec.get("files", {}).items():
                full_path = project_path / file_path
                if not dry_run:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    content = file_content(content_key, f"// TODO: Implement {content_key}", template)
                    full_path.write_text(content)
                created_files.append(str(full_path))
            notes.extend(n for n in spec.get("notes", []) if n not in notes)

    return {
        "name": name,
        "template": template,
        "template_name": template_config["name"],
        "features": features,
        "path": str(project_path),
        "files_created": len(created_files),
        "files": created_files,
        "notes": notes,
        "next_steps": [
            f"cd {name}",
            "npm install",
            "npm run dev",
        ],
    }


def print_result(result: Dict) -> None:
    """Print scaffolding result."""
    print(f"\n{'='*60}")
    print(f"Project Scaffolded: {result['name']}")
    print(f"{'='*60}")
    print(f"Template: {result['template_name']}")
    print(f"Location: {result['path']}")
    print(f"Files Created: {result['files_created']}")

    if result["features"]:
        print(f"Features: {', '.join(result['features'])}")

    if result["notes"]:
        print("\nNotes:")
        for note in result["notes"]:
            print(f"  - {note}")

    print("\nNext Steps:")
    for step in result["next_steps"]:
        print(f"  $ {step}")

    print(f"{'='*60}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Scaffold a frontend project with best practices"
    )
    parser.add_argument("name", nargs="?",
                        help="Project name, a lowercase npm package name (optional with --list-*)")
    parser.add_argument("--dir", "-d", default=".",
                        help="Output directory (default: current directory)")
    parser.add_argument("--template", "-t", choices=list(TEMPLATES.keys()), default="nextjs",
                        help="Project template (default: nextjs)")
    parser.add_argument("--features", "-f",
                        help="Comma-separated features to add (auth,api,forms,testing,storybook)")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--list-features", action="store_true", help="List available features")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be created without creating files")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Shorthand for --format json")
    return parser


def main():
    args = build_parser().parse_args()

    if args.list_templates:
        print("\nAvailable Templates:")
        for key, template in TEMPLATES.items():
            print(f"  {key}: {template['name']}")
            print(f"    {template['description']}")
        return

    if args.list_features:
        print("\nAvailable Features:")
        for key, feature in FEATURES.items():
            print(f"  {key}: {feature['description']}")
            for template in TEMPLATES:
                spec = feature.get(template, {})
                deps = ", ".join([*spec.get("dependencies", {}), *spec.get("devDependencies", {})])
                if deps:
                    print(f"    Adds ({template}): {deps}")
        return

    if not args.name:
        build_parser().error("the following arguments are required: name")

    features = []
    if args.features:
        features = [f.strip() for f in args.features.split(",")]
        invalid = [f for f in features if f not in FEATURES]
        if invalid:
            print(f"error: unknown features: {', '.join(invalid)} "
                  f"(valid: {', '.join(FEATURES.keys())})", file=sys.stderr)
            sys.exit(2)

    try:
        result = scaffold_project(
            name=args.name,
            output_dir=Path(args.dir),
            template=args.template,
            features=features,
            dry_run=args.dry_run,
        )
    except OSError as exc:
        print(f"error: cannot write project: {exc}", file=sys.stderr)
        sys.exit(2)
    if result.get("error"):
        print(f"error: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if args.json or args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
