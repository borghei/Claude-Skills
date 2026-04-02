#!/usr/bin/env python3
"""Integration test runner for all Python tools across the skills repo.

Runs five checks against every Python script found in skills' scripts/
directories: compile, help flag, import audit, argparse presence, and
format flag support.

Usage:
    python scripts/integration_test_runner.py
    python scripts/integration_test_runner.py --domain engineering
    python scripts/integration_test_runner.py --skill engineering/senior-backend
    python scripts/integration_test_runner.py -v
    python scripts/integration_test_runner.py --format json
"""

import argparse
import importlib.util
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

# Known standard library top-level module names (Python 3.10+).
# We include the most common ones; anything not here gets flagged.
_STDLIB_NAMES: set[str] | None = None


def _get_stdlib_names() -> set[str]:
    global _STDLIB_NAMES
    if _STDLIB_NAMES is not None:
        return _STDLIB_NAMES
    # Python 3.10+ has sys.stdlib_module_names
    if hasattr(sys, "stdlib_module_names"):
        _STDLIB_NAMES = set(sys.stdlib_module_names)
        return _STDLIB_NAMES
    # Fallback: comprehensive list for 3.8/3.9
    _STDLIB_NAMES = {
        "__future__", "_thread", "abc", "aifc", "argparse", "array", "ast",
        "asynchat", "asyncio", "asyncore", "atexit", "audioop", "base64",
        "bdb", "binascii", "binhex", "bisect", "builtins", "bz2",
        "calendar", "cgi", "cgitb", "chunk", "cmath", "cmd", "code",
        "codecs", "codeop", "collections", "colorsys", "compileall",
        "concurrent", "configparser", "contextlib", "contextvars", "copy",
        "copyreg", "cProfile", "crypt", "csv", "ctypes", "curses",
        "dataclasses", "datetime", "dbm", "decimal", "difflib", "dis",
        "distutils", "doctest", "email", "encodings", "enum", "errno",
        "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch",
        "formatter", "fractions", "ftplib", "functools", "gc", "getopt",
        "getpass", "gettext", "glob", "grp", "gzip", "hashlib", "heapq",
        "hmac", "html", "http", "idlelib", "imaplib", "imghdr", "imp",
        "importlib", "inspect", "io", "ipaddress", "itertools", "json",
        "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
        "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
        "modulefinder", "multiprocessing", "netrc", "nis", "nntplib",
        "numbers", "operator", "optparse", "os", "ossaudiodev", "parser",
        "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil",
        "platform", "plistlib", "poplib", "posix", "posixpath", "pprint",
        "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr",
        "pydoc", "queue", "quopri", "random", "re", "readline", "reprlib",
        "resource", "rlcompleter", "runpy", "sched", "secrets", "select",
        "selectors", "shelve", "shlex", "shutil", "signal", "site",
        "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd",
        "sqlite3", "sre_compile", "sre_constants", "sre_parse", "ssl",
        "stat", "statistics", "string", "stringprep", "struct",
        "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog",
        "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test",
        "textwrap", "threading", "time", "timeit", "tkinter", "token",
        "tokenize", "tomllib", "trace", "traceback", "tracemalloc",
        "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
        "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave",
        "weakref", "webbrowser", "winreg", "winsound", "wsgiref",
        "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport",
        "zlib", "zoneinfo", "_ast", "_collections_abc", "_io",
        "typing_extensions",  # commonly bundled
    }
    return _STDLIB_NAMES

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


def dim(t: str) -> str:
    return _c("2", t)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def find_scripts(path: Path) -> list[Path]:
    """Find all .py files under scripts/ directories in skill folders."""
    results = []
    if not path.is_dir():
        return results
    for skill_dir in sorted(path.iterdir()):
        if not skill_dir.is_dir():
            continue
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            results.extend(sorted(scripts_dir.glob("*.py")))
    return results


def collect_scripts(args) -> list[Path]:
    """Collect Python scripts based on CLI arguments."""
    scripts: list[Path] = []
    if args.skill:
        # Resolve skill path
        candidate = REPO_ROOT / args.skill
        if not candidate.is_dir():
            for d in DOMAINS:
                candidate = REPO_ROOT / d / args.skill
                if candidate.is_dir():
                    break
        scripts_dir = candidate / "scripts"
        if scripts_dir.is_dir():
            scripts = sorted(scripts_dir.glob("*.py"))
        if not scripts:
            print(red(f"No scripts found for skill: {args.skill}"), file=sys.stderr)
            sys.exit(1)
        return scripts
    if args.domain:
        domain_path = REPO_ROOT / args.domain
        if not domain_path.is_dir():
            print(red(f"Domain not found: {args.domain}"), file=sys.stderr)
            sys.exit(1)
        return find_scripts(domain_path)
    # All domains
    for domain in DOMAINS:
        scripts.extend(find_scripts(REPO_ROOT / domain))
    return scripts


# ---------------------------------------------------------------------------
# Test checks
# ---------------------------------------------------------------------------


def check_compile(script: Path) -> tuple[bool, str]:
    """Test 1: python -m py_compile succeeds."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, "compiles OK"
        return False, f"compile error: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'unknown'}"
    except subprocess.TimeoutExpired:
        return False, "compile timed out"
    except OSError as e:
        return False, f"OS error: {e}"


def check_help(script: Path) -> tuple[bool, str]:
    """Test 2: python script.py --help returns exit code 0."""
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, "--help OK"
        return False, f"--help exited with code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"
    except OSError as e:
        return False, f"OS error: {e}"


def check_imports(script: Path) -> tuple[bool, str]:
    """Test 3: Only standard library imports."""
    try:
        content = script.read_text(errors="replace")
    except OSError:
        return False, "cannot read file"

    stdlib = _get_stdlib_names()
    non_stdlib = []

    for line in content.splitlines():
        line = line.strip()
        # import X, from X import ...
        m = re.match(r"^import\s+([\w.]+)", line)
        if m:
            top = m.group(1).split(".")[0]
            if top not in stdlib:
                non_stdlib.append(top)
            continue
        m = re.match(r"^from\s+([\w.]+)\s+import", line)
        if m:
            top = m.group(1).split(".")[0]
            if top not in stdlib:
                non_stdlib.append(top)

    if non_stdlib:
        unique = sorted(set(non_stdlib))
        return False, f"non-stdlib imports: {', '.join(unique)}"
    return True, "stdlib only"


def check_argparse(script: Path) -> tuple[bool, str]:
    """Test 4: File contains argparse import."""
    try:
        content = script.read_text(errors="replace")
    except OSError:
        return False, "cannot read file"

    if "import argparse" in content or "from argparse" in content:
        return True, "uses argparse"
    return False, "no argparse import"


def check_format_flag(script: Path) -> tuple[bool, str]:
    """Test 5: File supports --format flag."""
    try:
        content = script.read_text(errors="replace")
    except OSError:
        return False, "cannot read file"

    # Look for --format in argparse add_argument calls or similar
    if re.search(r"['\"]--format['\"]", content):
        return True, "supports --format"
    if re.search(r"add_argument\([^)]*format", content):
        return True, "supports format arg"
    return False, "no --format flag"


ALL_CHECKS = [
    ("compile", check_compile),
    ("help", check_help),
    ("imports", check_imports),
    ("argparse", check_argparse),
    ("format_flag", check_format_flag),
]


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------


def run_tests(scripts: list[Path], verbose: bool) -> list[dict]:
    """Run all checks on all scripts. Returns list of result dicts."""
    results = []
    for script in scripts:
        try:
            rel = script.relative_to(REPO_ROOT)
        except ValueError:
            rel = script

        checks = {}
        all_pass = True
        for check_name, check_fn in ALL_CHECKS:
            passed, message = check_fn(script)
            checks[check_name] = {"passed": passed, "message": message}
            if not passed:
                all_pass = False

        result = {
            "script": str(rel),
            "passed": all_pass,
            "checks": checks,
        }
        results.append(result)

        # Print progress
        if verbose:
            status = green("PASS") if all_pass else red("FAIL")
            print(f"  {status}  {rel}")
            for cn, cv in checks.items():
                icon = green("ok") if cv["passed"] else red("FAIL")
                print(f"         {icon}  {cn}: {cv['message']}")
        else:
            status = green(".") if all_pass else red("F")
            print(status, end="", flush=True)

    if not verbose:
        print()  # newline after dots

    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def print_results(results: list[dict], verbose: bool) -> None:
    """Print human-readable summary."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    print()
    print(bold(f"Results: {passed}/{total} scripts passed all checks"))
    print()

    # Per-check summary
    for check_name, _ in ALL_CHECKS:
        count = sum(1 for r in results if r["checks"][check_name]["passed"])
        pct = (count / total * 100) if total else 0
        color_fn = green if count == total else (yellow if pct >= 80 else red)
        print(f"  {check_name:<15} {color_fn(f'{count}/{total}'):>12}  ({pct:.0f}%)")

    # List failures
    failures = [r for r in results if not r["passed"]]
    if failures:
        print()
        print(red(bold(f"Failures ({len(failures)}):")))
        for r in failures:
            failed_checks = [
                cn for cn, cv in r["checks"].items() if not cv["passed"]
            ]
            reasons = [
                f"{cn}: {r['checks'][cn]['message']}" for cn in failed_checks
            ]
            print(f"  {red('FAIL')}  {r['script']}")
            for reason in reasons:
                print(f"         {dim(reason)}")

    print()
    if failed > 0:
        print(red(f"Exit code: 1 ({failed} failure(s))"))
    else:
        print(green("All checks passed."))


def print_json_results(results: list[dict]) -> None:
    """Print results as JSON."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    check_summary = {}
    for check_name, _ in ALL_CHECKS:
        count = sum(1 for r in results if r["checks"][check_name]["passed"])
        check_summary[check_name] = {"passed": count, "total": total}

    output = {
        "summary": {
            "total_scripts": total,
            "passed": passed,
            "failed": total - passed,
        },
        "check_summary": check_summary,
        "scripts": results,
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Integration test runner for all Python tools across the skills repo."
    )
    p.add_argument("--skill", help="Test scripts for a specific skill (e.g., engineering/senior-backend)")
    p.add_argument("--domain", help="Test all scripts in a domain (e.g., engineering)")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output per script")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return p


def main() -> None:
    global _USE_COLOR
    parser = build_parser()
    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        _USE_COLOR = False

    scripts = collect_scripts(args)
    if not scripts:
        print(red("No Python scripts found.") if _USE_COLOR else "No Python scripts found.", file=sys.stderr)
        sys.exit(1)

    print(bold(f"Testing {len(scripts)} Python scripts..."))
    print()

    results = run_tests(scripts, args.verbose)

    if args.format == "json":
        print_json_results(results)
    else:
        print_results(results, args.verbose)

    # Exit code
    if any(not r["passed"] for r in results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
