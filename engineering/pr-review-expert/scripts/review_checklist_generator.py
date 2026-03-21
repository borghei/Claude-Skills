#!/usr/bin/env python3
"""Generate PR review checklists based on changed file types and patterns.

Reads a list of changed file paths (from git diff --name-only or stdin) and
produces a tailored review checklist. Checklist items are selected based on
which file categories appear in the change set: API routes, database files,
frontend components, config, tests, infrastructure, etc.

Usage:
    git diff --name-only main...HEAD | python review_checklist_generator.py
    python review_checklist_generator.py --files src/auth.ts src/db/migrate.sql
    python review_checklist_generator.py --diff-file /tmp/pr-123.diff --json
"""

import argparse
import json
import re
import sys
from collections import OrderedDict
from typing import Dict, List, Set, Tuple


# --- File category classifiers ---

FILE_CATEGORIES: List[Tuple[str, str, List[str]]] = [
    # (category_name, description, [regex patterns])
    ("api", "API Routes & Endpoints", [
        r"(routes?|controllers?|handlers?|endpoints?|api)/",
        r"\.(controller|handler|route)\.(ts|js|py|go|rb)$",
    ]),
    ("database", "Database & Migrations", [
        r"migrations?/", r"schemas?/", r"models?/",
        r"\.sql$", r"(prisma|drizzle|knex|sequelize|typeorm)",
        r"(alembic|flyway|liquibase)",
    ]),
    ("auth", "Authentication & Authorization", [
        r"auth/", r"(login|signup|session|oauth|jwt|rbac|permission)",
        r"middleware.*(auth|token|session)",
    ]),
    ("frontend", "Frontend Components & UI", [
        r"\.(tsx|jsx|vue|svelte)$",
        r"components?/", r"pages?/", r"views?/",
        r"styles?/", r"\.(css|scss|less|styled)$",
    ]),
    ("test", "Tests & Test Infrastructure", [
        r"\.(test|spec)\.", r"__tests__/", r"tests?/",
        r"(jest|vitest|pytest|mocha|cypress|playwright)",
        r"fixtures?/", r"factories/", r"mocks?/",
    ]),
    ("config", "Configuration Files", [
        r"\.(ya?ml|json|toml|ini|cfg|conf|env)$",
        r"(Makefile|Rakefile|Taskfile)",
        r"\.(eslint|prettier|babel|webpack|vite|tsconfig)",
        r"requirements.*\.txt$", r"package\.json$",
        r"(go\.mod|Cargo\.toml|pom\.xml|build\.gradle)",
    ]),
    ("infra", "Infrastructure & DevOps", [
        r"(docker|Docker)", r"k8s/", r"kubernetes/",
        r"terraform/", r"\.tf$", r"ansible/",
        r"helm/", r"pulumi/", r"cloudformation",
        r"\.github/(workflows|actions)/", r"(ci|cd)/",
        r"(Jenkinsfile|\.gitlab-ci)",
    ]),
    ("security", "Security-Sensitive Code", [
        r"(crypto|encrypt|decrypt|hash|sign|verify)/",
        r"(payment|billing|checkout|stripe|paypal)",
        r"(secrets?|credentials?|certs?)/",
        r"(cors|csp|helmet|sanitiz)",
    ]),
    ("shared_lib", "Shared Libraries & Utilities", [
        r"(lib|libs|shared|common|utils?|helpers?|packages?)/",
        r"(types|interfaces|contracts)/",
    ]),
    ("docs", "Documentation", [
        r"\.(md|mdx|rst|adoc|txt)$",
        r"(docs?|documentation)/",
        r"(README|CHANGELOG|CONTRIBUTING|LICENSE)",
    ]),
    ("deps", "Dependencies", [
        r"(package-lock|yarn\.lock|pnpm-lock|Gemfile\.lock|Pipfile\.lock|poetry\.lock)",
        r"(go\.sum|Cargo\.lock|composer\.lock)",
        r"(requirements.*\.txt|package\.json|Gemfile|Pipfile)$",
    ]),
]

# --- Checklist items per category ---

CHECKLIST_ITEMS: Dict[str, List[Tuple[str, str]]] = {
    "always": [
        ("scope", "PR title accurately describes the change"),
        ("scope", "PR description explains WHY, not just WHAT"),
        ("scope", "No unrelated changes included (scope creep)"),
        ("scope", "Linked ticket/issue exists and matches scope"),
    ],
    "api": [
        ("breaking", "No API endpoints removed without deprecation period"),
        ("breaking", "No required fields added to existing request/response schemas"),
        ("security", "Auth/authorization middleware applied to all new endpoints"),
        ("security", "Input validation present on all new parameters"),
        ("security", "Rate limiting considered for public endpoints"),
        ("security", "CORS configured correctly for new endpoints"),
        ("testing", "Integration tests cover new/modified endpoints"),
        ("testing", "Error response codes tested (400, 401, 403, 404, 500)"),
        ("docs", "API documentation updated (OpenAPI/Swagger if applicable)"),
        ("perf", "Pagination added for list endpoints returning unbounded data"),
    ],
    "database": [
        ("breaking", "Migration is reversible (has rollback/down method)"),
        ("breaking", "No destructive operations (DROP TABLE/COLUMN) without migration plan"),
        ("breaking", "NOT NULL columns include a default value or two-phase migration"),
        ("perf", "Indexes added for new query patterns"),
        ("perf", "No unbounded queries without LIMIT"),
        ("security", "Parameterized queries used (no string interpolation in SQL)"),
        ("testing", "Migration tested against production-like data volume"),
        ("data", "Data backfill strategy documented if needed"),
    ],
    "auth": [
        ("security", "No auth bypass patterns (skip, noauth, TODO)"),
        ("security", "Session/token expiration configured correctly"),
        ("security", "Failed login attempts are rate-limited"),
        ("security", "Sensitive data not exposed in error messages or logs"),
        ("security", "Password hashing uses bcrypt/argon2 (not MD5/SHA1)"),
        ("testing", "Auth edge cases tested (expired token, revoked session, role escalation)"),
        ("testing", "Both positive and negative auth paths have test coverage"),
    ],
    "frontend": [
        ("security", "No XSS vectors (innerHTML, dangerouslySetInnerHTML)"),
        ("security", "User input sanitized before rendering"),
        ("a11y", "Accessibility attributes present (aria-*, alt text, semantic HTML)"),
        ("perf", "No unnecessary re-renders or missing memoization"),
        ("perf", "Images and assets optimized"),
        ("ux", "Loading and error states handled"),
        ("ux", "Responsive design verified"),
        ("testing", "Component tests cover user interactions"),
    ],
    "test": [
        ("quality", "Test names clearly describe what they verify"),
        ("quality", "Edge cases covered (empty, null, boundary values)"),
        ("quality", "Error paths tested (not just happy path)"),
        ("quality", "No tests deleted without clear justification"),
        ("quality", "Test fixtures do not contain real secrets or PII"),
        ("quality", "Flaky test patterns avoided (timeouts, sleep, order dependency)"),
    ],
    "config": [
        ("breaking", "New environment variables documented in .env.example"),
        ("breaking", "Removed config values verified as unused in all environments"),
        ("security", "No secrets or credentials in config files"),
        ("ops", "Config changes are backward-compatible with rolling deploys"),
        ("ops", "Feature flags used for risky config changes"),
    ],
    "infra": [
        ("security", "No secrets in Dockerfiles or CI configs"),
        ("security", "Container images use specific version tags (not :latest)"),
        ("security", "Least privilege applied to IAM/RBAC changes"),
        ("ops", "Resource limits defined (CPU, memory)"),
        ("ops", "Health checks configured"),
        ("ops", "Rollback procedure documented for infrastructure changes"),
        ("testing", "Infrastructure changes tested in staging first"),
    ],
    "security": [
        ("security", "No hardcoded secrets, API keys, or credentials"),
        ("security", "Encryption algorithms are current (AES-256, SHA-256+)"),
        ("security", "Sensitive data encrypted at rest and in transit"),
        ("security", "Audit logging added for security-relevant operations"),
        ("testing", "Security-critical paths have near-100% test coverage"),
        ("compliance", "Changes reviewed against relevant compliance requirements"),
    ],
    "shared_lib": [
        ("breaking", "Backward-compatible for all consumers"),
        ("breaking", "Version bump follows semver"),
        ("blast_radius", "All downstream consumers identified and checked"),
        ("blast_radius", "Cross-service dependencies verified"),
        ("testing", "Shared code has comprehensive unit tests"),
        ("docs", "Public API documented with usage examples"),
    ],
    "docs": [
        ("quality", "Documentation matches actual code behavior"),
        ("quality", "Code examples are tested or verified"),
        ("quality", "Links are valid and not broken"),
    ],
    "deps": [
        ("security", "New dependencies checked for known CVEs"),
        ("security", "Dependencies are actively maintained (not abandoned)"),
        ("perf", "Bundle size impact assessed for frontend dependencies"),
        ("ops", "Lock file committed alongside dependency changes"),
        ("license", "New dependency licenses compatible with project license"),
    ],
}


def classify_files(file_paths: List[str]) -> Dict[str, List[str]]:
    """Classify each file path into zero or more categories."""
    categories: Dict[str, List[str]] = {}
    for path in file_paths:
        matched = False
        for cat_name, _, patterns in FILE_CATEGORIES:
            for pattern in patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    categories.setdefault(cat_name, []).append(path)
                    matched = True
                    break
        if not matched:
            categories.setdefault("other", []).append(path)
    return categories


def get_category_label(cat_name: str) -> str:
    """Get human-readable label for a category."""
    for name, label, _ in FILE_CATEGORIES:
        if name == cat_name:
            return label
    return cat_name.replace("_", " ").title()


def build_checklist(categories: Dict[str, List[str]]) -> OrderedDict:
    """Build a tailored checklist based on detected categories."""
    checklist = OrderedDict()

    # Always include base items
    checklist["Scope & Context"] = [
        {"check": item[1], "tag": item[0]} for item in CHECKLIST_ITEMS["always"]
    ]

    # Add category-specific items
    for cat_name in categories:
        if cat_name in CHECKLIST_ITEMS:
            section_label = get_category_label(cat_name)
            items = [
                {"check": item[1], "tag": item[0]}
                for item in CHECKLIST_ITEMS[cat_name]
            ]
            checklist[section_label] = items

    return checklist


def extract_files_from_diff(diff_text: str) -> List[str]:
    """Extract file paths from unified diff format."""
    files = []
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            if match:
                files.append(match.group(1))
    return files


def generate_report(file_paths: List[str]) -> Dict:
    """Generate the full checklist report."""
    categories = classify_files(file_paths)
    checklist = build_checklist(categories)

    total_items = sum(len(items) for items in checklist.values())

    category_summary = {}
    for cat_name, files in sorted(categories.items()):
        category_summary[cat_name] = {
            "label": get_category_label(cat_name),
            "file_count": len(files),
            "files": files,
        }

    return {
        "total_files": len(file_paths),
        "categories_detected": list(categories.keys()),
        "total_checklist_items": total_items,
        "category_summary": category_summary,
        "checklist": {k: v for k, v in checklist.items()},
    }


def format_human(result: Dict) -> str:
    """Format the checklist report for human reading."""
    lines = []
    lines.append("=" * 60)
    lines.append("  PR REVIEW CHECKLIST")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Files Analyzed:      {result['total_files']}")
    lines.append(f"Categories Detected: {', '.join(result['categories_detected'])}")
    lines.append(f"Checklist Items:     {result['total_checklist_items']}")
    lines.append("")

    # Category summary
    lines.append("File Categories:")
    for cat_name, info in result["category_summary"].items():
        lines.append(f"  [{info['label']}] ({info['file_count']} files)")
        for f in info["files"][:5]:
            lines.append(f"    - {f}")
        if info["file_count"] > 5:
            lines.append(f"    ... and {info['file_count'] - 5} more")
    lines.append("")

    # Checklist
    lines.append("-" * 60)
    lines.append("CHECKLIST")
    lines.append("-" * 60)

    for section, items in result["checklist"].items():
        lines.append("")
        lines.append(f"### {section}")
        for item in items:
            lines.append(f"  [ ] [{item['tag']}] {item['check']}")

    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Total: {result['total_checklist_items']} items to verify")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate PR review checklists based on changed file types and patterns.",
        epilog="Example: git diff --name-only main...HEAD | python review_checklist_generator.py",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--files", "-f",
        nargs="+",
        help="List of changed file paths to analyze.",
    )
    group.add_argument(
        "--diff-file", "-d",
        help="Path to a unified diff file (extracts file paths from diff headers).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    if args.files:
        file_paths = args.files
    elif args.diff_file:
        try:
            with open(args.diff_file, "r", encoding="utf-8", errors="replace") as fh:
                diff_text = fh.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.diff_file}", file=sys.stderr)
            sys.exit(1)
        file_paths = extract_files_from_diff(diff_text)
    else:
        if sys.stdin.isatty():
            print("Reading file paths from stdin (one per line)...", file=sys.stderr)
        file_paths = [line.strip() for line in sys.stdin if line.strip()]

    if not file_paths:
        print("Error: No file paths provided.", file=sys.stderr)
        sys.exit(1)

    result = generate_report(file_paths)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
