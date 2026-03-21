#!/usr/bin/env python3
"""Validate a project's development setup completeness.

Checks for README, .env.example, Makefile/scripts, required tools,
CI config, and other setup hygiene indicators. Produces a scored
report with pass/warn/fail verdicts and actionable recommendations.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Each check: (id, name, description, severity)
# severity: "critical" (blocks setup), "recommended", "nice-to-have"


def _file_exists(root, *candidates):
    """Return the first matching file path or None."""
    for c in candidates:
        if (Path(root) / c).exists():
            return c
    return None


def _glob_any(root, pattern):
    """Return True if any file matches the glob pattern."""
    return bool(list(Path(root).glob(pattern)))


def _file_has_content(root, filename, min_lines=3):
    """Check if a file exists and has meaningful content."""
    target = Path(root) / filename
    if not target.exists():
        return False
    try:
        lines = [l.strip() for l in open(target, errors="ignore") if l.strip()]
        return len(lines) >= min_lines
    except (OSError, PermissionError):
        return False


def _detect_package_scripts(root):
    """Extract script names from package.json if present."""
    pkg_path = Path(root) / "package.json"
    if not pkg_path.exists():
        return []
    try:
        import json as _json
        data = _json.loads(pkg_path.read_text(errors="ignore"))
        return list(data.get("scripts", {}).keys())
    except (ValueError, OSError):
        return []


def _check_tool_available(tool_name):
    """Check if a CLI tool is available on PATH."""
    return shutil.which(tool_name) is not None


def run_checks(root):
    """Run all setup validation checks and return results."""
    root = str(Path(root).resolve())
    results = []

    # 1. README exists and has content
    readme = _file_exists(root, "README.md", "README.rst", "README.txt", "README")
    results.append({
        "id": "readme",
        "name": "README documentation",
        "severity": "critical",
        "status": "pass" if readme and _file_has_content(root, readme) else (
            "warn" if readme else "fail"
        ),
        "found": readme,
        "recommendation": (
            None if readme and _file_has_content(root, readme)
            else "README exists but is too short" if readme
            else "Add a README.md with project overview, setup steps, and usage examples"
        ),
    })

    # 2. Environment variable template
    env_file = _file_exists(root, ".env.example", ".env.sample", ".env.template", ".env.defaults")
    results.append({
        "id": "env_template",
        "name": "Environment variable template",
        "severity": "critical",
        "status": "pass" if env_file else "fail",
        "found": env_file,
        "recommendation": (
            None if env_file
            else "Add .env.example listing all required environment variables with descriptions"
        ),
    })

    # 3. .env not committed (check .gitignore)
    gitignore_path = Path(root) / ".gitignore"
    env_ignored = False
    if gitignore_path.exists():
        try:
            content = gitignore_path.read_text(errors="ignore")
            env_ignored = any(
                line.strip() in (".env", ".env*", ".env.*", ".env.local")
                for line in content.splitlines()
            )
        except OSError:
            pass
    env_committed = (Path(root) / ".env").exists()
    results.append({
        "id": "env_gitignore",
        "name": ".env excluded from version control",
        "severity": "critical",
        "status": "pass" if env_ignored and not env_committed else (
            "fail" if env_committed and not env_ignored else "warn"
        ),
        "found": ".gitignore has .env pattern" if env_ignored else None,
        "recommendation": (
            None if env_ignored and not env_committed
            else "SECURITY: .env file is committed! Add .env to .gitignore and remove from tracking"
            if env_committed and not env_ignored
            else "Add .env to .gitignore to prevent accidental secret commits"
        ),
    })

    # 4. Build / task runner
    makefile = _file_exists(root, "Makefile", "justfile", "Taskfile.yml")
    pkg_scripts = _detect_package_scripts(root)
    has_runner = makefile is not None or len(pkg_scripts) > 0
    results.append({
        "id": "task_runner",
        "name": "Build/task runner configured",
        "severity": "recommended",
        "status": "pass" if has_runner else "warn",
        "found": makefile or (f"package.json scripts: {', '.join(pkg_scripts[:5])}" if pkg_scripts else None),
        "recommendation": (
            None if has_runner
            else "Add a Makefile or package.json scripts for common tasks (build, test, lint, dev)"
        ),
    })

    # 5. Lock file present
    lock = _file_exists(
        root, "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
        "Pipfile.lock", "poetry.lock", "uv.lock",
        "go.sum", "Cargo.lock", "Gemfile.lock", "composer.lock",
    )
    results.append({
        "id": "lockfile",
        "name": "Dependency lock file",
        "severity": "recommended",
        "status": "pass" if lock else "warn",
        "found": lock,
        "recommendation": (
            None if lock
            else "Commit a dependency lock file to ensure reproducible builds"
        ),
    })

    # 6. CI/CD configuration
    ci_found = None
    if (Path(root) / ".github" / "workflows").is_dir():
        workflows = list((Path(root) / ".github" / "workflows").glob("*.yml")) + \
                    list((Path(root) / ".github" / "workflows").glob("*.yaml"))
        if workflows:
            ci_found = f".github/workflows/ ({len(workflows)} workflow(s))"
    if not ci_found:
        ci_file = _file_exists(root, ".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml",
                               "bitbucket-pipelines.yml", ".travis.yml")
        if ci_file:
            ci_found = ci_file
    results.append({
        "id": "ci_config",
        "name": "CI/CD configuration",
        "severity": "recommended",
        "status": "pass" if ci_found else "warn",
        "found": ci_found,
        "recommendation": (
            None if ci_found
            else "Add CI/CD configuration to automate testing and deployment"
        ),
    })

    # 7. Linting / formatting config
    lint_config = _file_exists(
        root, ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        "eslint.config.js", "eslint.config.mjs",
        ".prettierrc", ".prettierrc.json", "prettier.config.js",
        "biome.json", "biome.jsonc",
        ".flake8", ".pylintrc", "pyproject.toml", "setup.cfg",
        ".rubocop.yml", ".golangci.yml",
    )
    results.append({
        "id": "linter",
        "name": "Linting/formatting configuration",
        "severity": "recommended",
        "status": "pass" if lint_config else "warn",
        "found": lint_config,
        "recommendation": (
            None if lint_config
            else "Add linter/formatter config for consistent code style"
        ),
    })

    # 8. Tests exist
    has_tests = (
        _glob_any(root, "**/*.test.*") or
        _glob_any(root, "**/*.spec.*") or
        _glob_any(root, "**/test_*.py") or
        _glob_any(root, "**/tests/**/*.py") or
        _glob_any(root, "tests/") or
        _glob_any(root, "test/") or
        _glob_any(root, "__tests__/")
    )
    results.append({
        "id": "tests",
        "name": "Test suite present",
        "severity": "recommended",
        "status": "pass" if has_tests else "warn",
        "found": "Test files detected" if has_tests else None,
        "recommendation": (
            None if has_tests
            else "Add tests to verify setup correctness and prevent regressions"
        ),
    })

    # 9. Contributing guide
    contrib = _file_exists(root, "CONTRIBUTING.md", "CONTRIBUTING", "docs/CONTRIBUTING.md")
    results.append({
        "id": "contributing",
        "name": "Contributing guidelines",
        "severity": "nice-to-have",
        "status": "pass" if contrib else "warn",
        "found": contrib,
        "recommendation": (
            None if contrib
            else "Add CONTRIBUTING.md with PR process, coding standards, and review expectations"
        ),
    })

    # 10. License
    lic = _file_exists(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING")
    results.append({
        "id": "license",
        "name": "License file",
        "severity": "nice-to-have",
        "status": "pass" if lic else "warn",
        "found": lic,
        "recommendation": (
            None if lic
            else "Add a LICENSE file to clarify usage and contribution terms"
        ),
    })

    # 11. Docker setup (if Dockerfile exists, check docker-compose too)
    dockerfile = _file_exists(root, "Dockerfile")
    compose = _file_exists(root, "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
    if dockerfile:
        results.append({
            "id": "docker_compose",
            "name": "Docker Compose for local infra",
            "severity": "recommended",
            "status": "pass" if compose else "warn",
            "found": compose,
            "recommendation": (
                None if compose
                else "Dockerfile found but no docker-compose. Add docker-compose.yml for local infrastructure"
            ),
        })

    # 12. Editor config
    editor = _file_exists(root, ".editorconfig")
    results.append({
        "id": "editorconfig",
        "name": "EditorConfig for consistent formatting",
        "severity": "nice-to-have",
        "status": "pass" if editor else "warn",
        "found": editor,
        "recommendation": (
            None if editor
            else "Add .editorconfig for consistent indentation across editors"
        ),
    })

    return results


def compute_score(results):
    """Compute an overall setup health score."""
    weights = {"critical": 3, "recommended": 2, "nice-to-have": 1}
    total = 0
    earned = 0
    for r in results:
        w = weights.get(r["severity"], 1)
        total += w
        if r["status"] == "pass":
            earned += w
        elif r["status"] == "warn":
            earned += w * 0.5
    return round((earned / total) * 100) if total > 0 else 0


def format_human(results, score, project_path):
    """Format results as human-readable text."""
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  SETUP VALIDATION: {Path(project_path).name}")
    lines.append(f"{'=' * 60}")
    lines.append(f"\nProject: {project_path}")
    lines.append(f"Score:   {score}/100\n")

    status_icons = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}
    severity_order = {"critical": 0, "recommended": 1, "nice-to-have": 2}
    sorted_results = sorted(results, key=lambda r: (severity_order.get(r["severity"], 9), r["status"] != "fail"))

    for r in sorted_results:
        icon = status_icons.get(r["status"], "[????]")
        lines.append(f"  {icon}  {r['name']} ({r['severity']})")
        if r["found"]:
            lines.append(f"         Found: {r['found']}")
        if r["recommendation"]:
            lines.append(f"         -> {r['recommendation']}")
        lines.append("")

    pass_count = sum(1 for r in results if r["status"] == "pass")
    warn_count = sum(1 for r in results if r["status"] == "warn")
    fail_count = sum(1 for r in results if r["status"] == "fail")
    lines.append(f"--- Summary ---")
    lines.append(f"  Passed: {pass_count}  |  Warnings: {warn_count}  |  Failed: {fail_count}")
    lines.append(f"  Health Score: {score}/100")

    if score >= 80:
        lines.append("\n  Verdict: Setup is well-configured for onboarding.")
    elif score >= 50:
        lines.append("\n  Verdict: Setup needs improvement. Address failed checks first.")
    else:
        lines.append("\n  Verdict: Setup has significant gaps. New developers will struggle.")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a project's development setup completeness.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s /path/to/project\n"
            "  %(prog)s . --json\n"
            "  %(prog)s ~/my-app --json | jq '.results[] | select(.status==\"fail\")'\n"
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Project directory to validate (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of human-readable format",
    )
    args = parser.parse_args()

    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    results = run_checks(str(target))
    score = compute_score(results)

    if args.json_output:
        output = {
            "project_name": target.name,
            "project_path": str(target),
            "score": score,
            "total_checks": len(results),
            "passed": sum(1 for r in results if r["status"] == "pass"),
            "warnings": sum(1 for r in results if r["status"] == "warn"),
            "failed": sum(1 for r in results if r["status"] == "fail"),
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, score, str(target)))


if __name__ == "__main__":
    main()
