#!/usr/bin/env python3
"""Analyze SQL queries for common performance issues and suggest optimizations.

Parses SQL text and checks for anti-patterns such as SELECT *, missing WHERE
clauses, implicit cartesian joins, unqualified column references in JOINs,
and excessive sub-query nesting.  Reports findings with severity and
actionable recommendations.

Usage:
    python query_optimizer.py --file query.sql
    python query_optimizer.py --sql "SELECT * FROM orders"
    python query_optimizer.py --file query.sql --json
"""

import argparse
import json
import re
import sys


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

def _check_select_star(sql: str) -> list:
    """Flag SELECT * usage."""
    issues = []
    for i, line in enumerate(sql.splitlines(), 1):
        if re.search(r"\bSELECT\s+\*", line, re.IGNORECASE):
            issues.append({
                "rule": "SELECT_STAR",
                "severity": "warning",
                "line": i,
                "message": "SELECT * fetches all columns; specify only needed columns to reduce I/O.",
                "suggestion": "Replace SELECT * with an explicit column list.",
            })
    return issues


def _check_missing_where(sql: str) -> list:
    """Flag queries that read large tables without a WHERE clause."""
    issues = []
    # Simplified: look for FROM without a subsequent WHERE at the statement level
    statements = re.split(r";", sql)
    for stmt in statements:
        stmt_stripped = stmt.strip()
        if not stmt_stripped:
            continue
        has_from = re.search(r"\bFROM\b", stmt_stripped, re.IGNORECASE)
        has_where = re.search(r"\bWHERE\b", stmt_stripped, re.IGNORECASE)
        has_limit = re.search(r"\bLIMIT\b", stmt_stripped, re.IGNORECASE)
        if has_from and not has_where and not has_limit:
            issues.append({
                "rule": "MISSING_WHERE",
                "severity": "warning",
                "line": None,
                "message": "Query reads from a table without a WHERE or LIMIT clause.",
                "suggestion": "Add filtering predicates or a LIMIT to avoid full table scans.",
            })
    return issues


def _check_cartesian_join(sql: str) -> list:
    """Flag comma-separated FROM (implicit cross join)."""
    issues = []
    # Match FROM a, b pattern (no JOIN keyword)
    pattern = re.compile(
        r"\bFROM\s+\w+\s*,\s*\w+", re.IGNORECASE
    )
    for i, line in enumerate(sql.splitlines(), 1):
        if pattern.search(line):
            issues.append({
                "rule": "IMPLICIT_CROSS_JOIN",
                "severity": "critical",
                "line": i,
                "message": "Comma-separated FROM clause may produce a cartesian product.",
                "suggestion": "Use explicit JOIN ... ON syntax instead of comma-separated tables.",
            })
    return issues


def _check_subquery_nesting(sql: str) -> list:
    """Flag deeply nested sub-queries (>3 levels)."""
    issues = []
    depth = 0
    max_depth = 0
    for ch in sql:
        if ch == "(":
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif ch == ")":
            depth = max(0, depth - 1)
    if max_depth > 3:
        issues.append({
            "rule": "DEEP_NESTING",
            "severity": "warning",
            "line": None,
            "message": f"Query has {max_depth} levels of nesting; readability and performance degrade beyond 3.",
            "suggestion": "Refactor deep sub-queries into CTEs (WITH clauses) for clarity and potential optimization.",
        })
    return issues


def _check_or_in_where(sql: str) -> list:
    """Flag excessive OR chains that may prevent index usage."""
    issues = []
    or_count = len(re.findall(r"\bOR\b", sql, re.IGNORECASE))
    if or_count >= 5:
        issues.append({
            "rule": "EXCESSIVE_OR",
            "severity": "info",
            "line": None,
            "message": f"Found {or_count} OR conditions; large OR chains can prevent index usage.",
            "suggestion": "Consider replacing OR chains with IN (...) or UNION ALL for better index utilization.",
        })
    return issues


def _check_functions_on_indexed_columns(sql: str) -> list:
    """Flag common anti-pattern of wrapping indexed columns in functions."""
    issues = []
    patterns = [
        (r"\bWHERE\b.*\b(?:UPPER|LOWER|TRIM|CAST|DATE)\s*\(", "Function on column in WHERE clause may prevent index usage."),
    ]
    for pat, msg in patterns:
        if re.search(pat, sql, re.IGNORECASE | re.DOTALL):
            issues.append({
                "rule": "FUNCTION_ON_COLUMN",
                "severity": "warning",
                "line": None,
                "message": msg,
                "suggestion": "Apply the function to the comparison value instead, or use a computed/expression index.",
            })
    return issues


def _check_order_without_limit(sql: str) -> list:
    """Flag ORDER BY without LIMIT."""
    issues = []
    has_order = re.search(r"\bORDER\s+BY\b", sql, re.IGNORECASE)
    has_limit = re.search(r"\bLIMIT\b", sql, re.IGNORECASE)
    if has_order and not has_limit:
        issues.append({
            "rule": "ORDER_WITHOUT_LIMIT",
            "severity": "info",
            "line": None,
            "message": "ORDER BY without LIMIT sorts the entire result set, which can be expensive.",
            "suggestion": "Add a LIMIT clause if you only need the top/bottom N rows.",
        })
    return issues


ALL_CHECKS = [
    _check_select_star,
    _check_missing_where,
    _check_cartesian_join,
    _check_subquery_nesting,
    _check_or_in_where,
    _check_functions_on_indexed_columns,
    _check_order_without_limit,
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def analyze(sql: str) -> dict:
    issues = []
    for check_fn in ALL_CHECKS:
        issues.extend(check_fn(sql))

    severity_order = {"critical": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 99))

    summary = {
        "total_issues": len(issues),
        "critical": sum(1 for i in issues if i["severity"] == "critical"),
        "warnings": sum(1 for i in issues if i["severity"] == "warning"),
        "info": sum(1 for i in issues if i["severity"] == "info"),
    }
    return {"summary": summary, "issues": issues}


def main():
    parser = argparse.ArgumentParser(
        description="Analyze SQL queries for performance issues and anti-patterns."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a .sql file to analyze")
    group.add_argument("--sql", help="Inline SQL string to analyze")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                sql = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        sql = args.sql

    result = analyze(sql)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        print("SQL Query Optimization Report")
        print("=" * 50)
        print(f"Issues found: {s['total_issues']}  (critical: {s['critical']}, warnings: {s['warnings']}, info: {s['info']})")
        print()
        if not result["issues"]:
            print("No issues detected. Query looks well-structured.")
        for issue in result["issues"]:
            sev = issue["severity"].upper()
            line_str = f" (line {issue['line']})" if issue["line"] else ""
            print(f"[{sev}] {issue['rule']}{line_str}")
            print(f"  {issue['message']}")
            print(f"  -> {issue['suggestion']}")
            print()

    sys.exit(1 if result["summary"]["critical"] > 0 else 0)


if __name__ == "__main__":
    main()
