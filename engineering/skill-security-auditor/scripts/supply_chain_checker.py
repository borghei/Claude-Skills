#!/usr/bin/env python3
"""
Supply Chain Checker - Detect typosquatting and dependency risks.

Scans Python imports, requirements*.txt and package.json for typosquatting
risks (Python names), unpinned versions, and inline pip/npm install commands
in scripts.

Uses Levenshtein distance against a curated list of popular PyPI packages
to flag suspicious package names. It does not check pinned versions against
vulnerability advisories: run pip-audit, npm audit or OSV-Scanner for that.

Exit codes: 0 PASS or WARN, 1 FAIL, 2 target does not exist.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Set, Tuple


# ---------------------------------------------------------------------------
# Popular PyPI packages (top ~80 by download count)
# ---------------------------------------------------------------------------

POPULAR_PACKAGES: List[str] = [
    "requests", "urllib3", "boto3", "botocore", "setuptools", "pip",
    "certifi", "charset-normalizer", "idna", "numpy", "typing-extensions",
    "packaging", "six", "python-dateutil", "pyyaml", "s3transfer",
    "cryptography", "cffi", "jmespath", "pyasn1", "attrs", "click",
    "importlib-metadata", "pycparser", "tomli", "platformdirs", "wheel",
    "filelock", "colorama", "markupsafe", "jinja2", "zipp", "pyparsing",
    "pytz", "pillow", "pandas", "aiohttp", "grpcio", "scipy",
    "protobuf", "wrapt", "flask", "django", "sqlalchemy", "psycopg2",
    "redis", "celery", "pytest", "coverage", "tox", "flake8",
    "black", "mypy", "isort", "pylint", "httpx", "fastapi", "uvicorn",
    "pydantic", "starlette", "gunicorn", "paramiko", "fabric",
    "beautifulsoup4", "lxml", "scrapy", "selenium", "playwright",
    "matplotlib", "scikit-learn", "tensorflow", "torch", "transformers",
    "openai", "langchain", "anthropic", "docker", "kubernetes",
    "google-cloud-storage", "azure-storage-blob", "aws-cdk-lib",
    "pygments", "rich", "typer", "argparse", "pathlib", "dataclasses",
]

# Known typosquatting examples (package -> what it impersonates)
KNOWN_TYPOSQUATS: Dict[str, str] = {
    "reqeusts": "requests",
    "requets": "requests",
    "reqests": "requests",
    "request": "requests",
    "requestes": "requests",
    "colourma": "colorama",
    "colourama": "colorama",
    "numppy": "numpy",
    "numpay": "numpy",
    "pandsa": "pandas",
    "pandaas": "pandas",
    "flassk": "flask",
    "flaask": "flask",
    "djano": "django",
    "djnago": "django",
    "scikitlearn": "scikit-learn",
    "beautifulsoup": "beautifulsoup4",
    "python-opencv": "opencv-python",
    "python3-dateutil": "python-dateutil",
    "pipsqlalchemy": "sqlalchemy",
    "httx": "httpx",
    "fasttapi": "fastapi",
    "pyaml": "pyyaml",
    "pycryptography": "cryptography",
}


@dataclass
class Finding:
    severity: str
    category: str
    file: str
    line: int
    package: str
    detail: str
    fix: str


@dataclass
class CheckReport:
    target: str
    files_scanned: int
    packages_checked: int
    total_findings: int
    critical_count: int
    high_count: int
    info_count: int
    verdict: str
    findings: List[Dict] = field(default_factory=list)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def normalize_package_name(name: str) -> str:
    """Normalize package name for comparison (PEP 503)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def check_typosquatting(package: str) -> Tuple[bool, str]:
    """Check if a package name is a potential typosquat."""
    normalized = normalize_package_name(package)

    # Standard-library modules (urllib, json, ...) are never typosquats of PyPI packages
    if package.split(".")[0] in getattr(sys, "stdlib_module_names", ()):
        return False, ""

    # Check known typosquats first
    if normalized in KNOWN_TYPOSQUATS:
        return True, KNOWN_TYPOSQUATS[normalized]

    # Check Levenshtein distance against popular packages
    for popular in POPULAR_PACKAGES:
        pop_normalized = normalize_package_name(popular)
        if normalized == pop_normalized:
            return False, ""
        dist = levenshtein_distance(normalized, pop_normalized)
        # Flag if edit distance is 1-2 for packages with 4+ chars
        if len(normalized) >= 4 and 1 <= dist <= 2:
            return True, popular

    return False, ""


def extract_imports_from_python(filepath: str) -> List[Tuple[int, str]]:
    """Extract imported package names from a Python file."""
    results: List[Tuple[int, str]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line_num, line in enumerate(fh, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue

                # import package / import package.submodule
                m = re.match(r"^import\s+([\w.]+)", stripped)
                if m:
                    top_level = m.group(1).split(".")[0]
                    results.append((line_num, top_level))

                # from package import ...
                m = re.match(r"^from\s+([\w.]+)\s+import", stripped)
                if m:
                    top_level = m.group(1).split(".")[0]
                    results.append((line_num, top_level))
    except OSError:
        pass
    return results


def extract_deps_from_requirements(filepath: str) -> List[Tuple[int, str, bool]]:
    """Extract packages from requirements.txt. Returns (line, name, is_pinned)."""
    results: List[Tuple[int, str, bool]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line_num, line in enumerate(fh, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                    continue
                # Parse: package==1.0, package>=1.0, package~=1.0, package
                m = re.match(r"^([A-Za-z0-9_.-]+)\s*(==|>=|<=|~=|!=|>|<|;|\[|$)", stripped)
                if m:
                    pkg_name = m.group(1)
                    operator = m.group(2)
                    is_pinned = operator == "=="
                    results.append((line_num, pkg_name, is_pinned))
    except OSError:
        pass
    return results


def extract_deps_from_package_json(filepath: str) -> List[Tuple[int, str, bool]]:
    """Extract (line, name, is_pinned) from package.json dependency blocks."""
    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return []
    results: List[Tuple[int, str, bool]] = []
    lines = text.splitlines()
    for block in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, spec in (data.get(block) or {}).items():
            line = next((i for i, l in enumerate(lines, 1) if f'"{name}"' in l), 0)
            pinned = bool(re.match(r"^\d+\.\d+\.\d+", str(spec)))  # ^, ~, *, ranges, tags are not pins
            results.append((line, name, pinned))
    return results


def scan_for_pip_install(filepath: str) -> List[Tuple[int, str]]:
    """Scan a file for inline pip/pip3/npm install commands."""
    results: List[Tuple[int, str]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line_num, line in enumerate(fh, start=1):
                if re.search(r"(pip3?|python3?\s+-m\s+pip|npm|yarn|pnpm)\s+(install|add|i)\b", line):
                    results.append((line_num, line.strip()))
    except OSError:
        pass
    return results


def is_requirements(name: str) -> bool:
    return name.startswith("requirements") and name.endswith(".txt")


def collect_files(target: str) -> Tuple[List[str], List[str], List[str]]:
    """Collect Python files, dependency manifests, and all script files."""
    target_path = Path(target)
    py_files: List[str] = []
    req_files: List[str] = []
    script_files: List[str] = []

    if target_path.is_file():
        s = str(target_path)
        if s.endswith(".py"):
            py_files.append(s)
            script_files.append(s)
        elif is_requirements(target_path.name) or target_path.name == "package.json":
            req_files.append(s)
        return py_files, req_files, script_files

    if target_path.is_dir():
        for p in sorted(target_path.rglob("*")):
            if p.is_file():
                s = str(p)
                if s.endswith(".py"):
                    py_files.append(s)
                    script_files.append(s)
                elif s.endswith(".sh"):
                    script_files.append(s)
                elif (is_requirements(p.name) or p.name == "package.json") and "node_modules" not in p.parts:
                    req_files.append(s)

    return py_files, req_files, script_files


def run_check(target: str, strict: bool) -> CheckReport:
    """Run the full supply chain check."""
    py_files, req_files, script_files = collect_files(target)
    findings: List[Finding] = []
    checked_packages: Set[str] = set()
    typo_checked: Set[str] = set()

    # 1. Check imports in Python files for typosquatting
    for pf in py_files:
        imports = extract_imports_from_python(pf)
        for line_num, pkg in imports:
            if pkg in checked_packages:
                continue
            checked_packages.add(pkg)
            is_typo, real_pkg = check_typosquatting(pkg)
            if is_typo:
                findings.append(Finding(
                    severity="HIGH",
                    category="TYPOSQUAT",
                    file=pf,
                    line=line_num,
                    package=pkg,
                    detail=f"Package '{pkg}' looks like a typosquat of '{real_pkg}'",
                    fix=f"Verify the package name. Did you mean '{real_pkg}'?",
                ))

    # 2. Check requirements files
    for rf in req_files:
        is_npm = rf.endswith("package.json")
        deps = extract_deps_from_package_json(rf) if is_npm else extract_deps_from_requirements(rf)
        for line_num, pkg, is_pinned in deps:
            declared = f"npm:{pkg}" if is_npm else pkg
            # Typosquatting check (the reference list is PyPI, so Python manifests only)
            if declared not in checked_packages:
                checked_packages.add(declared)
            if not is_npm and pkg not in typo_checked:
                typo_checked.add(pkg)
                is_typo, real_pkg = check_typosquatting(pkg)
                if is_typo:
                    findings.append(Finding(
                        severity="CRITICAL",
                        category="TYPOSQUAT",
                        file=rf,
                        line=line_num,
                        package=pkg,
                        detail=f"Dependency '{pkg}' looks like a typosquat of '{real_pkg}'",
                        fix=f"Replace with the correct package name: '{real_pkg}'",
                    ))

            # Unpinned version check
            if not is_pinned:
                findings.append(Finding(
                    severity="INFO",
                    category="UNPINNED",
                    file=rf,
                    line=line_num,
                    package=pkg,
                    detail=f"Dependency '{pkg}' is not pinned to an exact version",
                    fix=(f'Pin to an exact version ("{pkg}": "x.y.z") and commit the lockfile' if is_npm
                         else f"Pin to a specific version: {pkg}==<version>"),
                ))

    # 3. Scan scripts for inline pip install commands
    for sf in script_files:
        pip_cmds = scan_for_pip_install(sf)
        for line_num, line_text in pip_cmds:
            findings.append(Finding(
                severity="HIGH",
                category="INLINE-INSTALL",
                file=sf,
                line=line_num,
                package="pip",
                detail=f"Inline package installation found: {line_text[:60]}",
                fix="Declare dependencies in requirements.txt / package.json instead of installing inline",
            ))

    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    high = sum(1 for f in findings if f.severity == "HIGH")
    info = sum(1 for f in findings if f.severity == "INFO")

    if critical > 0:
        verdict = "FAIL"
    elif high > 0:
        verdict = "FAIL" if strict else "WARN"
    else:
        verdict = "PASS"

    total_files = len(set(py_files + req_files + script_files))

    return CheckReport(
        target=target,
        files_scanned=total_files,
        packages_checked=len(checked_packages),
        total_findings=len(findings),
        critical_count=critical,
        high_count=high,
        info_count=info,
        verdict=verdict,
        findings=[asdict(f) for f in findings],
    )


def format_human_readable(report: CheckReport) -> str:
    """Format the report for human-readable terminal output."""
    lines = [
        "",
        "+" + "=" * 55 + "+",
        "|  SUPPLY CHAIN CHECK REPORT" + " " * 28 + "|",
        f"|  Target: {report.target[:44]:<44} |",
        f"|  Files scanned: {report.files_scanned:<37} |",
        f"|  Packages checked: {report.packages_checked:<34} |",
        f"|  Verdict: {report.verdict:<43} |",
        "+" + "=" * 55 + "+",
        f"|  CRITICAL: {report.critical_count}  |  HIGH: {report.high_count}  |  INFO: {report.info_count}",
        "+" + "=" * 55 + "+",
        "",
    ]

    if not report.findings:
        lines.append("  No supply chain issues found.")
        lines.append("")
        return "\n".join(lines)

    for f in report.findings:
        lines.append(f"{f['severity']} [{f['category']}] {f['file']}:{f['line']}")
        lines.append(f"  Package: {f['package']}")
        lines.append(f"  Detail: {f['detail']}")
        lines.append(f"  Fix: {f['fix']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check for typosquatting risks in import statements and "
                    "dependency declarations. Validates requirements.txt for "
                    "unpinned versions and detects inline pip install commands.",
        epilog="Examples:\n"
               "  %(prog)s scripts/\n"
               "  %(prog)s requirements.txt\n"
               "  %(prog)s . --strict --json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        help="File or directory to check (scans .py and requirements.txt files)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Strict mode: any HIGH finding upgrades verdict to FAIL",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="json_output",
        help="Output results as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    if not os.path.exists(target):
        print(f"Error: target '{args.target}' does not exist.", file=sys.stderr)
        sys.exit(2)

    report = run_check(target, args.strict)

    if args.json_output:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_human_readable(report))

    sys.exit(1 if report.verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
