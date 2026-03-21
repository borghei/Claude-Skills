#!/usr/bin/env python3
"""Validate .env files against .env.example — detect missing, extra, and suspicious vars.

Compares a target .env file against a reference .env.example to find:
  - Missing variables (in example but not in target)
  - Extra variables (in target but not in example)
  - Empty required variables
  - Secrets accidentally left in .env.example
  - Variables with placeholder/default values that should be customized

Usage:
    python env_validator.py .env.example .env
    python env_validator.py .env.example .env --strict --json
    python env_validator.py .env.example .env.staging --check-secrets
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Patterns that suggest a value is a real secret (not a placeholder)
SECRET_VALUE_PATTERNS = [
    (r"^AKIA[0-9A-Z]{16}$", "AWS Access Key ID"),
    (r"^sk_(live|test)_[0-9a-zA-Z]{24,}$", "Stripe Secret Key"),
    (r"^ghp_[0-9a-zA-Z]{36}$", "GitHub Personal Access Token"),
    (r"^glpat-[0-9a-zA-Z\-]{20,}$", "GitLab Personal Access Token"),
    (r"^SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}$", "SendGrid API Key"),
    (r"^xox[bpras]-[0-9a-zA-Z\-]{10,}$", "Slack Token"),
    (r"^whsec_[0-9a-zA-Z]{32,}$", "Stripe Webhook Secret"),
    (r"^-----BEGIN (RSA |EC )?PRIVATE KEY-----", "Private Key"),
    (r"^eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.", "JWT Token"),
]

# Variable names that typically hold secrets
SECRET_KEY_PATTERNS = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*ACCESS_KEY.*",
    r".*CREDENTIAL.*",
    r".*AUTH.*KEY.*",
]

# Placeholder values that indicate a var needs customization
PLACEHOLDER_PATTERNS = [
    r"^(changeme|CHANGEME|replace_me|REPLACE_ME|todo|TODO|xxx|XXX|your[_-].*here)$",
    r"^<.*>$",
    r"^\{\{.*\}\}$",
    r"^\$\{.*\}$",
]


def parse_env_file(filepath: str) -> dict:
    """Parse a .env file into a dict of {KEY: value}.

    Handles comments, blank lines, quoted values, and inline comments.
    Returns dict with keys mapped to their string values (empty string if unset).
    """
    variables = {}
    path = Path(filepath)
    if not path.exists():
        return variables

    with open(path, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            # Skip blanks and comments
            if not line or line.startswith("#"):
                continue
            # Must contain '='
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key or key.startswith("#"):
                continue
            # Strip inline comments (not inside quotes)
            value = value.strip()
            if value and value[0] in ('"', "'"):
                quote = value[0]
                end = value.find(quote, 1)
                if end != -1:
                    value = value[1:end]
            else:
                # Remove inline comment
                comment_match = re.search(r"\s+#\s", value)
                if comment_match:
                    value = value[: comment_match.start()]
                value = value.strip()
            variables[key] = value
    return variables


def is_secret_key(key: str) -> bool:
    """Check if a variable name looks like it holds a secret."""
    upper = key.upper()
    return any(re.match(p, upper) for p in SECRET_KEY_PATTERNS)


def detect_real_secret_value(value: str) -> str | None:
    """Return description if value matches a known secret format, else None."""
    for pattern, desc in SECRET_VALUE_PATTERNS:
        if re.search(pattern, value):
            return desc
    return None


def is_placeholder(value: str) -> bool:
    """Check if a value looks like a placeholder that needs customization."""
    return any(re.match(p, value, re.IGNORECASE) for p in PLACEHOLDER_PATTERNS)


def validate(
    reference_path: str,
    target_path: str,
    strict: bool = False,
    check_secrets: bool = False,
) -> dict:
    """Run all validation checks. Returns a results dict."""
    ref_vars = parse_env_file(reference_path)
    target_vars = parse_env_file(target_path)

    ref_keys = set(ref_vars.keys())
    target_keys = set(target_vars.keys())

    missing = sorted(ref_keys - target_keys)
    extra = sorted(target_keys - ref_keys)

    # Empty required vars (secret-looking keys with empty values)
    empty_required = []
    for key in sorted(ref_keys & target_keys):
        if is_secret_key(key) and not target_vars.get(key, ""):
            empty_required.append(key)

    # Placeholders that need customization
    placeholders = []
    for key in sorted(target_keys):
        val = target_vars[key]
        if val and is_placeholder(val):
            placeholders.append(key)

    # Secrets leaked into reference file (e.g., .env.example with real values)
    leaked_in_reference = []
    if check_secrets:
        for key, val in sorted(ref_vars.items()):
            if not val:
                continue
            secret_type = detect_real_secret_value(val)
            if secret_type:
                leaked_in_reference.append({"key": key, "type": secret_type})
            elif is_secret_key(key) and len(val) > 8 and not is_placeholder(val):
                # A secret-named key with a non-trivial, non-placeholder value
                leaked_in_reference.append({"key": key, "type": "potential secret value"})

    # Build issues list
    issues = []
    for key in missing:
        issues.append({"severity": "error", "type": "missing", "key": key,
                        "message": f"Variable '{key}' is in reference but missing from target"})
    for key in extra:
        sev = "error" if strict else "warning"
        issues.append({"severity": sev, "type": "extra", "key": key,
                        "message": f"Variable '{key}' is in target but not in reference"})
    for key in empty_required:
        issues.append({"severity": "error", "type": "empty_required", "key": key,
                        "message": f"Secret variable '{key}' is present but empty"})
    for key in placeholders:
        issues.append({"severity": "warning", "type": "placeholder", "key": key,
                        "message": f"Variable '{key}' still has a placeholder value"})
    for item in leaked_in_reference:
        issues.append({"severity": "error", "type": "leaked_secret", "key": item["key"],
                        "message": f"Reference file contains a {item['type']} in '{item['key']}'"})

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    return {
        "reference_file": reference_path,
        "target_file": target_path,
        "reference_count": len(ref_keys),
        "target_count": len(target_keys),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "passed": len(errors) == 0,
        "issues": issues,
    }


def print_human(results: dict) -> None:
    """Pretty-print validation results."""
    ref = results["reference_file"]
    tgt = results["target_file"]
    print(f"Env Validator: {ref} -> {tgt}")
    print(f"  Reference vars: {results['reference_count']}")
    print(f"  Target vars:    {results['target_count']}")
    print()

    if not results["issues"]:
        print("  All checks passed. No issues found.")
        return

    errors = [i for i in results["issues"] if i["severity"] == "error"]
    warnings = [i for i in results["issues"] if i["severity"] == "warning"]

    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for issue in errors:
            print(f"    [{issue['type'].upper()}] {issue['message']}")
        print()

    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for issue in warnings:
            print(f"    [{issue['type'].upper()}] {issue['message']}")
        print()

    status = "FAILED" if not results["passed"] else "PASSED (with warnings)"
    print(f"  Result: {status}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate .env files against .env.example. "
                    "Detects missing vars, extra vars, empty secrets, and leaked credentials.",
        epilog="Examples:\n"
               "  %(prog)s .env.example .env\n"
               "  %(prog)s .env.example .env --strict --json\n"
               "  %(prog)s .env.example .env.staging --check-secrets\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("reference", help="Reference file (e.g., .env.example)")
    parser.add_argument("target", help="Target file to validate (e.g., .env)")
    parser.add_argument("--strict", action="store_true",
                        help="Treat extra variables as errors instead of warnings")
    parser.add_argument("--check-secrets", action="store_true",
                        help="Check reference file for accidentally included real secrets")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")

    args = parser.parse_args()

    if not Path(args.reference).exists():
        print(f"Error: Reference file not found: {args.reference}", file=sys.stderr)
        return 2
    if not Path(args.target).exists():
        print(f"Error: Target file not found: {args.target}", file=sys.stderr)
        return 2

    results = validate(args.reference, args.target,
                       strict=args.strict, check_secrets=args.check_secrets)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print_human(results)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
