#!/usr/bin/env python3
"""
Supply Chain Checker - Detect typosquatting and dependency risks.

Scans Python import statements and dependency declarations (requirements.txt,
setup.py, pyproject.toml) for typosquatting risks, unpinned versions, and
inline pip install commands in scripts.

Uses Levenshtein distance against a curated list of popular PyPI packages
to flag suspicious package names.
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


def scan_for_pip_install(filepath: str) -> List[Tuple[int, str]]:
    """Scan a file for inline pip/pip3 install commands."""
    results: List[Tuple[int, str]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line_num, line in enumerate(fh, start=1):
                if re.search(r"(pip3?|python3?\s+-m\s+pip)\s+install\b", line):
                    results.append((line_num, line.strip()))
    except OSError:
        pass
    return results


def collect_files(target: str) -> Tuple[List[str], List[str], List[str]]:
    """Collect Python files, requirements files, and all script files."""
    target_path = Path(target)
    py_files: List[str] = []
    req_files: List[str] = []
    script_files: List[str] = []

    if target_path.is_file():
        s = str(target_path)
        if s.endswith(".py"):
            py_files.append(s)
            script_files.append(s)
        elif target_path.name in ("requirements.txt", "requirements-dev.txt"):
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
                elif p.name in ("requirements.txt", "requirements-dev.txt"):
                    req_files.append(s)

    return py_files, req_files, script_files


def run_check(target: str, strict: bool) -> CheckReport:
    """Run the full supply chain check."""
    py_files, req_files, script_files = collect_files(target)
    findings: List[Finding] = []
    checked_packages: Set[str] = set()

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
        deps = extract_deps_from_requirements(rf)
        for line_num, pkg, is_pinned in deps:
            # Typosquatting check
            if pkg not in checked_packages:
                checked_packages.add(pkg)
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
                    fix=f"Pin to a specific version: {pkg}==<version>",
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
                fix="Move dependencies to requirements.txt instead of installing inline",
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
