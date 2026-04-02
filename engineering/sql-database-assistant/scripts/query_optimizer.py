#!/usr/bin/env python3
"""
SQL Query Optimizer - Analyze SQL queries for performance issues.

Detects common anti-patterns like SELECT *, leading wildcards in LIKE,
missing indexes, N+1 patterns, and full table scans.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class Finding:
    """A query optimization finding."""
    severity: str  # critical, warning, info
    category: str
    query_excerpt: str
    message: str
    recommendation: str


class SQLQueryAnalyzer:
    """Analyzes SQL queries for performance issues."""

    def __init__(self):
        self.findings: List[Finding] = []

    def analyze(self, sql: str, source: str = "") -> List[Finding]:
        """Analyze a SQL query or batch of queries."""
        self.findings = []

        # Split on semicolons to handle multiple statements
        statements = [s.strip() for s in sql.split(";") if s.strip()]

        for stmt in statements:
            self._analyze_statement(stmt)

        return self.findings

    def _analyze_statement(self, sql: str):
        """Analyze a single SQL statement."""
        upper = sql.upper()

        if not any(upper.startswith(kw) for kw in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH"]):
            return

        self._check_select_star(sql, upper)
        self._check_like_patterns(sql, upper)
        self._check_missing_where(sql, upper)
        self._check_subqueries(sql, upper)
        self._check_joins(sql, upper)
        self._check_or_conditions(sql, upper)
        self._check_functions_on_columns(sql, upper)
        self._check_distinct(sql, upper)
        self._check_order_by(sql, upper)
        self._check_limit(sql, upper)
        self._check_null_comparisons(sql, upper)

    def _check_select_star(self, sql: str, upper: str):
        """Check for SELECT * usage."""
        if re.search(r'\bSELECT\s+\*\s', upper):
            # Exclude COUNT(*) and EXISTS(SELECT *)
            if not re.search(r'\bCOUNT\s*\(\s*\*\s*\)', upper) and \
               not re.search(r'\bEXISTS\s*\(\s*SELECT\s+\*', upper):
                self.findings.append(Finding(
                    severity="warning",
                    category="select",
                    query_excerpt=sql[:100],
                    message="SELECT * fetches all columns, including unnecessary data.",
                    recommendation="List only the specific columns needed. This reduces I/O, memory, and network usage.",
                ))

    def _check_like_patterns(self, sql: str, upper: str):
        """Check for leading wildcard LIKE patterns."""
        # Match LIKE '%something' or LIKE '%something%'
        leading_wildcard = re.findall(r"LIKE\s+['\"]%[^'\"]+['\"]", upper)
        if leading_wildcard:
            for pattern in leading_wildcard:
                self.findings.append(Finding(
                    severity="critical",
                    category="index",
                    query_excerpt=pattern,
                    message="Leading wildcard in LIKE prevents index usage, causing full table scan.",
                    recommendation="Use full-text search (FTS), trigram indexes, or restructure to avoid leading wildcards.",
                ))

        # Trailing wildcard is fine but note it
        trailing_only = re.findall(r"LIKE\s+['\"][^%][^'\"]*%['\"]", upper)
        if trailing_only:
            for pattern in trailing_only:
                self.findings.append(Finding(
                    severity="info",
                    category="index",
                    query_excerpt=pattern,
                    message="Trailing wildcard LIKE can use B-tree indexes efficiently.",
                    recommendation="Ensure the column used in LIKE has a B-tree index.",
                ))

    def _check_missing_where(self, sql: str, upper: str):
        """Check for queries without WHERE clause."""
        if upper.startswith("SELECT") and "WHERE" not in upper:
            # Skip if it's a simple lookup or has LIMIT
            if "LIMIT" not in upper and "TOP" not in upper:
                from_match = re.search(r'\bFROM\s+(\w+)', upper)
                table = from_match.group(1) if from_match else "unknown"
                self.findings.append(Finding(
                    severity="warning",
                    category="scan",
                    query_excerpt=sql[:100],
                    message=f"SELECT from '{table}' without WHERE clause may cause full table scan.",
                    recommendation="Add WHERE conditions to filter rows, or add LIMIT if fetching a sample.",
                ))

        if upper.startswith("UPDATE") and "WHERE" not in upper:
            self.findings.append(Finding(
                severity="critical",
                category="safety",
                query_excerpt=sql[:100],
                message="UPDATE without WHERE clause will modify ALL rows.",
                recommendation="Add a WHERE clause to target specific rows.",
            ))

        if upper.startswith("DELETE") and "WHERE" not in upper:
            self.findings.append(Finding(
                severity="critical",
                category="safety",
                query_excerpt=sql[:100],
                message="DELETE without WHERE clause will remove ALL rows.",
                recommendation="Add a WHERE clause to target specific rows. Use TRUNCATE if intentional.",
            ))

    def _check_subqueries(self, sql: str, upper: str):
        """Check for correlated subqueries (N+1 pattern)."""
        # Look for subqueries in SELECT or WHERE that reference outer table
        subquery_in_select = re.findall(r'\(\s*SELECT\b[^)]+\)', upper)
        for sq in subquery_in_select:
            # Simple heuristic: if subquery is in SELECT clause
            if "WHERE" in sq:
                self.findings.append(Finding(
                    severity="warning",
                    category="n+1",
                    query_excerpt=sq[:80],
                    message="Subquery in SELECT/WHERE may execute once per row (correlated subquery).",
                    recommendation="Rewrite as a JOIN or use a CTE (WITH clause) for better performance.",
                ))

    def _check_joins(self, sql: str, upper: str):
        """Check JOIN patterns."""
        # Check for implicit joins (comma-separated FROM)
        from_match = re.search(r'\bFROM\s+(\w+\s*,\s*\w+(?:\s*,\s*\w+)*)', upper)
        if from_match:
            self.findings.append(Finding(
                severity="info",
                category="join",
                query_excerpt=from_match.group(0)[:80],
                message="Implicit join (comma syntax) found. Prefer explicit JOIN syntax.",
                recommendation="Use explicit JOIN ... ON syntax for clarity and to prevent accidental cross joins.",
            ))

        # Check for CROSS JOIN
        if "CROSS JOIN" in upper:
            self.findings.append(Finding(
                severity="warning",
                category="join",
                query_excerpt="CROSS JOIN detected",
                message="CROSS JOIN produces cartesian product of both tables.",
                recommendation="Ensure CROSS JOIN is intentional. Consider INNER JOIN with ON condition.",
            ))

        # Check for missing ON in JOIN
        join_without_on = re.findall(r'\bJOIN\s+\w+\s+(?:AS\s+)?\w+\s+(?!ON\b)', upper)
        if join_without_on:
            self.findings.append(Finding(
                severity="warning",
                category="join",
                query_excerpt=str(join_without_on[0])[:80],
                message="JOIN without ON condition detected.",
                recommendation="Add ON condition to specify the join relationship.",
            ))

    def _check_or_conditions(self, sql: str, upper: str):
        """Check for OR conditions that prevent index usage."""
        or_count = len(re.findall(r'\bOR\b', upper))
        if or_count >= 3:
            self.findings.append(Finding(
                severity="info",
                category="index",
                query_excerpt=f"{or_count} OR conditions",
                message=f"Multiple OR conditions ({or_count}) may prevent efficient index usage.",
                recommendation="Consider rewriting with IN clause, UNION, or separate indexed queries.",
            ))

    def _check_functions_on_columns(self, sql: str, upper: str):
        """Check for functions applied to indexed columns in WHERE."""
        function_patterns = [
            (r'WHERE\s+\w+\s*\(\s*\w+\s*\)\s*=', "Function on column in WHERE"),
            (r'WHERE\s+UPPER\s*\(', "UPPER() on column prevents index usage"),
            (r'WHERE\s+LOWER\s*\(', "LOWER() on column prevents index usage"),
            (r'WHERE\s+CAST\s*\(', "CAST() on column prevents index usage"),
            (r'WHERE\s+COALESCE\s*\(', "COALESCE() on column prevents index usage"),
            (r'WHERE\s+DATE\s*\(', "DATE() on column prevents index usage"),
            (r'WHERE\s+YEAR\s*\(', "YEAR() on column prevents index usage"),
        ]

        for pattern, msg in function_patterns:
            if re.search(pattern, upper):
                self.findings.append(Finding(
                    severity="warning",
                    category="index",
                    query_excerpt=msg,
                    message=f"{msg} - prevents index usage.",
                    recommendation="Apply the function to the comparison value instead, or create a computed/expression index.",
                ))

    def _check_distinct(self, sql: str, upper: str):
        """Check for DISTINCT usage that might indicate a JOIN issue."""
        if re.search(r'\bSELECT\s+DISTINCT\b', upper):
            self.findings.append(Finding(
                severity="info",
                category="query",
                query_excerpt="SELECT DISTINCT",
                message="DISTINCT may indicate duplicate rows from incorrect JOINs.",
                recommendation="Review JOIN conditions. If duplicates are expected, DISTINCT is fine; otherwise fix the JOIN.",
            ))

    def _check_order_by(self, sql: str, upper: str):
        """Check ORDER BY patterns."""
        if re.search(r'ORDER\s+BY\s+\w+\s*,\s*\w+\s*,\s*\w+', upper):
            self.findings.append(Finding(
                severity="info",
                category="performance",
                query_excerpt="Multi-column ORDER BY",
                message="Sorting by 3+ columns may be expensive without a matching composite index.",
                recommendation="Ensure a composite index exists matching the ORDER BY column order.",
            ))

    def _check_limit(self, sql: str, upper: str):
        """Check for large offset in LIMIT."""
        offset_match = re.search(r'OFFSET\s+(\d+)', upper)
        if offset_match:
            offset = int(offset_match.group(1))
            if offset > 1000:
                self.findings.append(Finding(
                    severity="warning",
                    category="performance",
                    query_excerpt=f"OFFSET {offset}",
                    message=f"Large OFFSET ({offset}) requires scanning and discarding {offset} rows.",
                    recommendation="Use keyset/cursor pagination instead of OFFSET for better performance.",
                ))

    def _check_null_comparisons(self, sql: str, upper: str):
        """Check for incorrect NULL comparisons."""
        if re.search(r'=\s*NULL\b', upper) or re.search(r'!=\s*NULL\b', upper) or re.search(r'<>\s*NULL\b', upper):
            self.findings.append(Finding(
                severity="critical",
                category="correctness",
                query_excerpt="comparison with NULL",
                message="Using = or != with NULL always evaluates to NULL (unknown), not TRUE/FALSE.",
                recommendation="Use IS NULL or IS NOT NULL instead.",
            ))


def format_text(findings: List[Finding], source: str) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("SQL QUERY OPTIMIZATION REPORT")
    lines.append("=" * 60)
    if source:
        lines.append(f"Source: {source}")

    critical = [f for f in findings if f.severity == "critical"]
    warnings = [f for f in findings if f.severity == "warning"]
    info = [f for f in findings if f.severity == "info"]

    lines.append(f"\nFindings: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info")
    lines.append("-" * 60)

    for sev, group in [("CRITICAL", critical), ("WARNING", warnings), ("INFO", info)]:
        if not group:
            continue
        lines.append(f"\n[{sev}]")
        for f in group:
            lines.append(f"  [{f.category}] {f.message}")
            lines.append(f"    Query: {f.query_excerpt}")
            lines.append(f"    Fix: {f.recommendation}")
            lines.append("")

    if not findings:
        lines.append("\nNo optimization issues found.")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(findings: List[Finding], source: str) -> str:
    """Format as JSON."""
    return json.dumps({
        "source": source,
        "findings": [asdict(f) for f in findings],
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.severity == "critical"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "info": sum(1 for f in findings if f.severity == "info"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze SQL queries for performance issues and optimization opportunities."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Path to SQL file")
    group.add_argument("--query", "-q", help="SQL query string to analyze")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any finding")
    args = parser.parse_args()

    analyzer = SQLQueryAnalyzer()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(2)
        sql = path.read_text()
        source = str(path)
    else:
        sql = args.query
        source = "inline"

    findings = analyzer.analyze(sql, source)

    if args.format == "json":
        print(format_json(findings, source))
    else:
        print(format_text(findings, source))

    if any(f.severity == "critical" for f in findings):
        sys.exit(1)
    if args.strict and findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
