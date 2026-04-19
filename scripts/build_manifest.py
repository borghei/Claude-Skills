#!/usr/bin/env python3
"""Generate cli/skills.json from all SKILL.md files in the repo.

Walks domain directories, parses YAML frontmatter from each SKILL.md, measures
the skill folder size and file list, and writes a single JSON manifest that the
`npx claude-skills` CLI uses for list/search/info/add commands.

Standard library only. No external deps.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "cli" / "skills.json"

DOMAINS = [
    "engineering",
    "marketing",
    "c-level-advisor",
    "ra-qm-team",
    "business-growth",
    "legal",
    "project-management",
    "product-team",
    "data-analytics",
    "sales-success",
    "hr-operations",
    "finance",
]


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML-frontmatter parser covering the observed SKILL.md shapes.

    Handles: scalar key:value, multi-line `>` folded scalars, nested metadata:
    block with indented key:value pairs, and inline JSON-style arrays.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    lines = block.split("\n")

    result: dict = {}
    nested_key: str | None = None
    folded_key: str | None = None
    folded_parts: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        if folded_key is not None:
            if line.startswith("  ") and not re.match(r"^\s*\w+:", line):
                folded_parts.append(line.strip())
                i += 1
                continue
            target = result if nested_key is None else result.setdefault(nested_key, {})
            target[folded_key] = " ".join(folded_parts).strip()
            folded_key = None
            folded_parts = []

        if not stripped:
            i += 1
            continue

        m_nested_start = re.match(r"^(\w[\w-]*):\s*$", stripped)
        if m_nested_start and not line.startswith("  "):
            nested_key = m_nested_start.group(1)
            result.setdefault(nested_key, {})
            i += 1
            continue

        m_kv = re.match(r"^(\s*)(\w[\w-]*):\s*(.*)$", line)
        if m_kv:
            indent, key, value = m_kv.groups()
            if indent == "":
                nested_key = None
            target = result if nested_key is None else result.setdefault(nested_key, {})

            if value in ("", ">", "|"):
                if value in (">", "|"):
                    folded_key = key
                    folded_parts = []
                elif nested_key is None:
                    nested_key = key
                    result.setdefault(nested_key, {})
                i += 1
                continue

            target[key] = _parse_scalar(value.strip())
        i += 1

    if folded_key is not None:
        target = result if nested_key is None else result.setdefault(nested_key, {})
        target[folded_key] = " ".join(folded_parts).strip()

    return result


def _parse_scalar(value: str):
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


SKIP_DIRS = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", ".git"}
SKIP_FILE_SUFFIXES = (".pyc", ".pyo", ".DS_Store")


def walk_skill_dir(skill_dir: Path) -> tuple[list[str], int]:
    """Return relative file paths and total size in bytes for a skill folder.

    Skips build artifacts and hidden directories that aren't in git.
    """
    files: list[str] = []
    total = 0
    for root, dirs, filenames in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname.startswith(".") or fname.endswith(SKIP_FILE_SUFFIXES):
                continue
            p = Path(root) / fname
            rel = p.relative_to(skill_dir).as_posix()
            files.append(rel)
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return sorted(files), total


def build_skill_entry(domain: str, skill_dir: Path) -> dict | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None

    fm = parse_frontmatter(text)
    metadata = fm.get("metadata", {}) if isinstance(fm.get("metadata"), dict) else {}

    name = fm.get("name") or skill_dir.name
    description = fm.get("description", "")
    if isinstance(description, str):
        description = re.sub(r"\s+", " ", description).strip()
    else:
        description = ""

    tags = metadata.get("tags") or fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    files, size_bytes = walk_skill_dir(skill_dir)

    return {
        "name": name,
        "domain": domain,
        "description": description,
        "tags": tags,
        "version": metadata.get("version", "1.0.0"),
        "updated": metadata.get("updated", ""),
        "author": metadata.get("author", ""),
        "path": f"{domain}/{skill_dir.name}",
        "files": files,
        "size_bytes": size_bytes,
        "has_scripts": "scripts" in {f.split("/", 1)[0] for f in files},
        "has_references": "references" in {f.split("/", 1)[0] for f in files},
        "has_assets": "assets" in {f.split("/", 1)[0] for f in files},
    }


def main(argv: list[str]) -> int:
    skills: list[dict] = []
    for domain in DOMAINS:
        domain_dir = REPO_ROOT / domain
        if not domain_dir.is_dir():
            continue
        for skill_dir in sorted(domain_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            entry = build_skill_entry(domain, skill_dir)
            if entry is not None:
                skills.append(entry)

    manifest = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skill_count": len(skills),
        "domain_count": len({s["domain"] for s in skills}),
        "skills": skills,
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"  skills: {manifest['skill_count']}")
    print(f"  domains: {manifest['domain_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
