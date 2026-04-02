#!/usr/bin/env python3
"""Score SKILL.md files against the skill authoring standard.

Evaluates skills across five categories (frontmatter, structure, quality,
size, tools) and assigns letter grades.  Supports single-skill, domain,
or full-repo scoring with JSON, table, and summary output formats.

Usage:
    python scripts/skill_quality_scorer.py engineering/senior-backend
    python scripts/skill_quality_scorer.py --all
    python scripts/skill_quality_scorer.py --domain engineering
    python scripts/skill_quality_scorer.py --all --format json
    python scripts/skill_quality_scorer.py --all --format summary
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

DOMAINS = [
    "business-growth",
    "c-level-advisor",
    "data-analytics",
    "engineering",
    "finance",
    "hr-operations",
    "marketing",
    "product-team",
    "project-management",
    "ra-qm-team",
    "sales-success",
]

GRADE_THRESHOLDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")]

# ANSI colour helpers
_USE_COLOR = True


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c("32", t)


def yellow(t: str) -> str:
    return _c("33", t)


def red(t: str) -> str:
    return _c("31", t)


def bold(t: str) -> str:
    return _c("1", t)


def cyan(t: str) -> str:
    return _c("36", t)


def grade_color(grade: str, text: str) -> str:
    if grade == "A":
        return green(text)
    if grade == "B":
        return cyan(text)
    if grade == "C":
        return yellow(text)
    return red(text)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def find_skill_dirs(path: Path) -> list[Path]:
    """Return skill directories that contain a SKILL.md."""
    results = []
    if not path.is_dir():
        return results
    for child in sorted(path.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            results.append(child)
    return results


def resolve_skill_path(spec: str) -> Path | None:
    """Resolve a user-provided skill spec like 'engineering/senior-backend'."""
    candidate = REPO_ROOT / spec
    if candidate.is_dir() and (candidate / "SKILL.md").exists():
        return candidate
    # Try adding domain prefix search
    for domain in DOMAINS:
        candidate = REPO_ROOT / domain / spec
        if candidate.is_dir() and (candidate / "SKILL.md").exists():
            return candidate
    return None


def collect_skills(args) -> list[Path]:
    """Collect skill directories based on CLI arguments."""
    if args.all:
        skills = []
        for domain in DOMAINS:
            skills.extend(find_skill_dirs(REPO_ROOT / domain))
        return skills
    if args.domain:
        domain_path = REPO_ROOT / args.domain
        if not domain_path.is_dir():
            print(red(f"Domain not found: {args.domain}"), file=sys.stderr)
            sys.exit(1)
        return find_skill_dirs(domain_path)
    if args.skill:
        path = resolve_skill_path(args.skill)
        if path is None:
            print(red(f"Skill not found: {args.skill}"), file=sys.stderr)
            sys.exit(1)
        return [path]
    print(red("Provide a skill path, --domain, or --all"), file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML frontmatter parser (no PyYAML dependency)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    data: dict = {}
    current_key = None
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Top-level key: value
        match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if match and not line.startswith(" "):
            current_key = match.group(1)
            val = match.group(2).strip()
            if val == ">":
                data[current_key] = ""
            elif val:
                data[current_key] = val
            else:
                data[current_key] = {}
            continue
        # Nested key under metadata
        nested = re.match(r"^\s+(\w[\w-]*):\s*(.*)", line)
        if nested and current_key:
            if not isinstance(data.get(current_key), dict):
                data[current_key] = {}
            data[current_key][nested.group(1)] = nested.group(2).strip()
            continue
        # Continuation of multi-line description
        if current_key and isinstance(data.get(current_key), str):
            data[current_key] += " " + stripped
    return data


# ---------------------------------------------------------------------------
# Scoring functions — each returns (points, max_points, details)
# ---------------------------------------------------------------------------


def score_frontmatter(text: str, fm: dict) -> tuple[int, int, list[str]]:
    """Frontmatter: 20 pts."""
    pts = 0
    details = []

    # Has frontmatter at all (4 pts)
    if fm:
        pts += 4
        details.append("+ Has YAML frontmatter (4)")
    else:
        details.append("- Missing YAML frontmatter (0/4)")
        return pts, 20, details

    # Has name field (4 pts)
    if fm.get("name"):
        pts += 4
        details.append("+ Has name field (4)")
    else:
        details.append("- Missing name field (0/4)")

    # Has description field (4 pts)
    desc = fm.get("description", "")
    if desc:
        pts += 4
        details.append("+ Has description field (4)")
    else:
        details.append("- Missing description field (0/4)")

    # Has license (2 pts)
    if fm.get("license"):
        pts += 2
        details.append("+ Has license field (2)")
    else:
        details.append("- Missing license field (0/2)")

    # Has metadata block (2 pts)
    if isinstance(fm.get("metadata"), dict) and fm["metadata"]:
        pts += 2
        details.append("+ Has metadata block (2)")
    else:
        details.append("- Missing metadata block (0/2)")

    # Description contains trigger clause (4 pts)
    desc_lower = str(desc).lower()
    if "use when" in desc_lower or "should be used when" in desc_lower:
        pts += 4
        details.append("+ Description has trigger clause (4)")
    else:
        details.append("- Description missing trigger clause (0/4)")

    return pts, 20, details


def score_structure(text: str) -> tuple[int, int, list[str]]:
    """Structure: 20 pts."""
    pts = 0
    details = []
    checks = [
        ("Quick Start", 4),
        ("Tools Overview", 4),
        ("Workflow", 4),
        ("Anti-Pattern", 4),
        ("Reference Documentation", 4),
    ]
    text_lower = text.lower()
    for label, weight in checks:
        # Accept as header or in text
        pattern = label.lower().replace("-", "[-\\s]?")
        if re.search(pattern, text_lower):
            pts += weight
            details.append(f"+ Has {label} section ({weight})")
        else:
            details.append(f"- Missing {label} section (0/{weight})")
    return pts, 20, details


def score_quality(text: str) -> tuple[int, int, list[str]]:
    """Quality: 20 pts."""
    pts = 0
    details = []

    # Third-person agent voice (5 pts)
    if re.search(r"\bthe agent\b", text, re.IGNORECASE):
        pts += 5
        details.append("+ Uses agent voice (5)")
    else:
        details.append("- Missing agent voice 'The agent...' (0/5)")

    # Numbered workflow steps (5 pts)
    numbered = re.findall(r"^\s*\d+\.\s+", text, re.MULTILINE)
    if len(numbered) >= 3:
        pts += 5
        details.append(f"+ Has numbered steps ({len(numbered)} found) (5)")
    else:
        details.append(f"- Few numbered steps ({len(numbered)} found) (0/5)")

    # Validation checkpoints (5 pts)
    validation_terms = [
        r"validation checkpoint",
        r"quality gate",
        r"verify that",
        r"checklist",
        r"must pass",
        r"validate",
    ]
    found_val = sum(1 for v in validation_terms if re.search(v, text, re.IGNORECASE))
    if found_val >= 2:
        pts += 5
        details.append(f"+ Has validation checkpoints ({found_val} terms) (5)")
    elif found_val == 1:
        pts += 3
        details.append(f"~ Partial validation ({found_val} term) (3/5)")
    else:
        details.append("- No validation checkpoints (0/5)")

    # Concrete examples / code blocks (5 pts)
    code_blocks = text.count("```")
    if code_blocks >= 6:
        pts += 5
        details.append(f"+ Has code blocks ({code_blocks // 2} blocks) (5)")
    elif code_blocks >= 2:
        pts += 3
        details.append(f"~ Few code blocks ({code_blocks // 2}) (3/5)")
    else:
        details.append("- No code blocks (0/5)")

    return pts, 20, details


def score_size(text: str) -> tuple[int, int, list[str]]:
    """Size: 20 pts."""
    pts = 0
    details = []
    lines = text.count("\n") + 1
    words = len(text.split())

    # Lines: under 500 = 10, under 600 = 5, over 600 = 0
    if lines <= 500:
        pts += 10
        details.append(f"+ Under 500 lines ({lines}) (10)")
    elif lines <= 600:
        pts += 5
        details.append(f"~ {lines} lines (between 500-600) (5/10)")
    else:
        details.append(f"- Over 600 lines ({lines}) (0/10)")

    # Words: under 3000 = 10, under 4000 = 5, over 4000 = 0
    if words <= 3000:
        pts += 10
        details.append(f"+ Under 3000 words ({words}) (10)")
    elif words <= 4000:
        pts += 5
        details.append(f"~ {words} words (between 3000-4000) (5/10)")
    else:
        details.append(f"- Over 4000 words ({words}) (0/10)")

    return pts, 20, details


def score_tools(skill_dir: Path) -> tuple[int, int, list[str]]:
    """Tools: 20 pts."""
    pts = 0
    details = []
    scripts_dir = skill_dir / "scripts"

    # Has scripts/ directory (5 pts)
    if not scripts_dir.is_dir():
        details.append("- No scripts/ directory (0/20)")
        return 0, 20, details

    py_files = sorted(scripts_dir.glob("*.py"))
    if not py_files:
        details.append("- scripts/ directory has no .py files (0/20)")
        return 0, 20, details

    pts += 5
    details.append(f"+ Has scripts/ directory with {len(py_files)} file(s) (5)")

    # Check each script for argparse, compile, and --help
    argparse_count = 0
    compile_count = 0
    help_count = 0

    for pyf in py_files:
        content = pyf.read_text(errors="replace")

        # Argparse check
        if "import argparse" in content or "from argparse" in content:
            argparse_count += 1

        # Compile check
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(pyf)],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                compile_count += 1
        except (subprocess.TimeoutExpired, OSError):
            pass

        # Help check
        try:
            result = subprocess.run(
                [sys.executable, str(pyf), "--help"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                help_count += 1
        except (subprocess.TimeoutExpired, OSError):
            pass

    total = len(py_files)

    # Argparse (5 pts)
    if argparse_count == total:
        pts += 5
        details.append(f"+ All scripts use argparse ({argparse_count}/{total}) (5)")
    elif argparse_count > 0:
        partial = round(5 * argparse_count / total)
        pts += partial
        details.append(f"~ Some scripts use argparse ({argparse_count}/{total}) ({partial}/5)")
    else:
        details.append(f"- No scripts use argparse (0/{total}) (0/5)")

    # Compile (5 pts)
    if compile_count == total:
        pts += 5
        details.append(f"+ All scripts compile ({compile_count}/{total}) (5)")
    elif compile_count > 0:
        partial = round(5 * compile_count / total)
        pts += partial
        details.append(f"~ Some scripts compile ({compile_count}/{total}) ({partial}/5)")
    else:
        details.append(f"- No scripts compile (0/{total}) (0/5)")

    # Help flag (5 pts)
    if help_count == total:
        pts += 5
        details.append(f"+ All scripts support --help ({help_count}/{total}) (5)")
    elif help_count > 0:
        partial = round(5 * help_count / total)
        pts += partial
        details.append(f"~ Some scripts support --help ({help_count}/{total}) ({partial}/5)")
    else:
        details.append(f"- No scripts support --help (0/{total}) (0/5)")

    return pts, 20, details


# ---------------------------------------------------------------------------
# Main scoring
# ---------------------------------------------------------------------------


def letter_grade(score: int) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def score_skill(skill_dir: Path) -> dict:
    """Score a single skill and return structured results."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(errors="replace")
    fm = parse_frontmatter(text)

    categories = {}
    total_pts = 0
    total_max = 0

    for name, fn in [
        ("Frontmatter", lambda: score_frontmatter(text, fm)),
        ("Structure", lambda: score_structure(text)),
        ("Quality", lambda: score_quality(text)),
        ("Size", lambda: score_size(text)),
        ("Tools", lambda: score_tools(skill_dir)),
    ]:
        pts, mx, details = fn()
        categories[name] = {"points": pts, "max": mx, "details": details}
        total_pts += pts
        total_max += mx

    grade = letter_grade(total_pts)
    # Relative path for display
    try:
        rel = skill_dir.relative_to(REPO_ROOT)
    except ValueError:
        rel = skill_dir
    return {
        "skill": str(rel),
        "score": total_pts,
        "max": total_max,
        "grade": grade,
        "categories": categories,
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def print_table(results: list[dict]) -> None:
    """Print a compact table of results."""
    print()
    header = f"{'Skill':<50} {'Score':>5}  {'Grade':>5}  {'FM':>3} {'ST':>3} {'QL':>3} {'SZ':>3} {'TL':>3}"
    print(bold(header))
    print("-" * len(header))
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        cats = r["categories"]
        g = r["grade"]
        score_str = grade_color(g, f"{r['score']:>3}")
        grade_str = grade_color(g, f"  {g:>1}  ")
        fm = cats["Frontmatter"]["points"]
        st = cats["Structure"]["points"]
        ql = cats["Quality"]["points"]
        sz = cats["Size"]["points"]
        tl = cats["Tools"]["points"]
        print(f"{r['skill']:<50} {score_str}  {grade_str}  {fm:>3} {st:>3} {ql:>3} {sz:>3} {tl:>3}")

    print()
    _print_summary_stats(results)


def print_detail(results: list[dict]) -> None:
    """Print detailed breakdown for each skill."""
    for r in results:
        g = r["grade"]
        print()
        print(bold(f"{'=' * 60}"))
        print(bold(f"  {r['skill']}"))
        print(bold(f"  Score: ") + grade_color(g, f"{r['score']}/{r['max']} ({g})"))
        print(bold(f"{'=' * 60}"))
        for cat_name, cat in r["categories"].items():
            print(f"\n  {bold(cat_name)} ({cat['points']}/{cat['max']})")
            for d in cat["details"]:
                if d.startswith("+"):
                    print(f"    {green(d)}")
                elif d.startswith("~"):
                    print(f"    {yellow(d)}")
                else:
                    print(f"    {red(d)}")

    if len(results) > 1:
        print()
        _print_summary_stats(results)


def _print_summary_stats(results: list[dict]) -> None:
    """Print aggregate stats."""
    scores = [r["score"] for r in results]
    avg = sum(scores) / len(scores) if scores else 0
    grade_counts: dict[str, int] = {}
    for r in results:
        grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1

    print(bold("Summary"))
    print(f"  Skills scored: {len(results)}")
    print(f"  Average score: {avg:.1f}/100 ({letter_grade(int(avg))})")
    print(f"  Grade distribution: ", end="")
    parts = []
    for g in ["A", "B", "C", "D", "F"]:
        if grade_counts.get(g, 0) > 0:
            parts.append(f"{g}={grade_counts[g]}")
    print(", ".join(parts))

    # Skills needing improvement
    needs_work = [r for r in results if r["score"] < 70]
    if needs_work:
        print()
        print(yellow(f"  Skills needing improvement (score < 70): {len(needs_work)}"))
        for r in sorted(needs_work, key=lambda x: x["score"]):
            print(f"    {red(r['grade'])} {r['score']:>3}  {r['skill']}")
    print()


def print_summary(results: list[dict]) -> None:
    """Print only averages and grade distribution."""
    print()
    _print_summary_stats(results)


def print_json(results: list[dict]) -> None:
    """Print results as JSON."""
    # Strip ANSI-unsafe data — already clean dicts
    scores = [r["score"] for r in results]
    avg = sum(scores) / len(scores) if scores else 0
    output = {
        "summary": {
            "total_skills": len(results),
            "average_score": round(avg, 1),
            "average_grade": letter_grade(int(avg)),
        },
        "skills": results,
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Score SKILL.md files against the skill authoring standard."
    )
    p.add_argument("skill", nargs="?", help="Skill path (e.g., engineering/senior-backend)")
    p.add_argument("--all", action="store_true", help="Score every skill in the repo")
    p.add_argument("--domain", help="Score all skills in a domain (e.g., engineering)")
    p.add_argument(
        "--format",
        choices=["table", "detail", "json", "summary"],
        default="detail",
        help="Output format (default: detail for single, table for multiple)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return p


def main() -> None:
    global _USE_COLOR
    parser = build_parser()
    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        _USE_COLOR = False

    skill_dirs = collect_skills(args)
    if not skill_dirs:
        print(red("No skills found."), file=sys.stderr)
        sys.exit(1)

    results = [score_skill(d) for d in skill_dirs]

    fmt = args.format
    # Default: detail for single, table for multiple
    if fmt == "detail" and len(results) > 1 and args.format == "detail":
        fmt = "table"

    if fmt == "json":
        print_json(results)
    elif fmt == "summary":
        print_summary(results)
    elif fmt == "table":
        print_table(results)
    else:
        print_detail(results)


if __name__ == "__main__":
    main()
