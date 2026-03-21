#!/usr/bin/env python3
"""Validate SQL DDL schemas for normalization violations, missing indexes,
naming conventions, and common anti-patterns.

Parses CREATE TABLE statements and checks for:
- Missing indexes on foreign key columns
- Missing timestamp columns (created_at, updated_at)
- Naming convention violations (snake_case enforcement)
- Missing primary keys
- Soft-delete columns without partial indexes
- Sequential integer PKs exposed (suggests CUID2/UUIDv7)
- Missing NOT NULL on foreign keys
- Tables without any indexes
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Finding:
    table: str
    severity: str
    rule: str
    message: str
    suggestion: str


@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool
    is_pk: bool
    default: Optional[str]
    references: Optional[str]  # referenced table


@dataclass
class Index:
    name: str
    columns: List[str]
    unique: bool
    where_clause: Optional[str]


@dataclass
class Table:
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)
    indexes: List[Index] = field(default_factory=list)
    primary_key: Optional[List[str]] = None


def parse_ddl(sql: str) -> List[Table]:
    """Parse SQL DDL into structured Table objects."""
    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    tables: List[Table] = []
    table_map: Dict[str, Table] = {}

    # Extract CREATE TABLE blocks
    table_pattern = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'(?:"?(\w+)"?\.)?'   # optional schema
        r'"?(\w+)"?'          # table name
        r'\s*\((.*?)\)\s*;',
        re.IGNORECASE | re.DOTALL
    )

    for match in table_pattern.finditer(sql):
        _schema, tname, body = match.group(1), match.group(2), match.group(3)
        table = Table(name=tname)

        # Split body on commas, respecting parentheses depth
        parts = _split_comma_top_level(body)

        for part in parts:
            part = part.strip()
            upper = part.upper()

            # Table-level PRIMARY KEY
            pk_match = re.match(r'PRIMARY\s+KEY\s*\(([^)]+)\)', part, re.IGNORECASE)
            if pk_match:
                table.primary_key = [c.strip().strip('"') for c in pk_match.group(1).split(',')]
                continue

            # Table-level UNIQUE or INDEX (inline)
            if re.match(r'(UNIQUE|INDEX|KEY|CONSTRAINT)\s', upper):
                continue

            # Column definition
            col_match = re.match(
                r'"?(\w+)"?\s+(\w[\w\s()]*?)(?:\s+(NOT\s+NULL|NULL|PRIMARY\s+KEY|DEFAULT\s+.+?|REFERENCES\s+\w+(?:\s*\([^)]*\))?))*\s*$',
                part, re.IGNORECASE
            )
            if col_match:
                cname = col_match.group(1)
                ctype = col_match.group(2).strip()

                is_pk = bool(re.search(r'PRIMARY\s+KEY', part, re.IGNORECASE))
                nullable = not bool(re.search(r'NOT\s+NULL', part, re.IGNORECASE)) and not is_pk
                default_match = re.search(r'DEFAULT\s+(\S+)', part, re.IGNORECASE)
                ref_match = re.search(r'REFERENCES\s+"?(\w+)"?', part, re.IGNORECASE)

                col = Column(
                    name=cname,
                    data_type=ctype,
                    nullable=nullable,
                    is_pk=is_pk,
                    default=default_match.group(1) if default_match else None,
                    references=ref_match.group(1) if ref_match else None,
                )
                table.columns[cname] = col
                if is_pk:
                    table.primary_key = [cname]

        tables.append(table)
        table_map[tname] = table

    # Extract CREATE INDEX statements
    idx_pattern = re.compile(
        r'CREATE\s+(UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?'
        r'"?(\w+)"?\s+ON\s+"?(\w+)"?\s*(?:USING\s+\w+\s*)?\(([^)]+)\)'
        r'(?:\s+WHERE\s+(.+?))?;',
        re.IGNORECASE | re.DOTALL
    )
    for match in idx_pattern.finditer(sql):
        unique = bool(match.group(1))
        idx_name = match.group(2)
        tname = match.group(3)
        cols = [c.strip().strip('"') for c in match.group(4).split(',')]
        where = match.group(5).strip() if match.group(5) else None

        idx = Index(name=idx_name, columns=cols, unique=unique, where_clause=where)
        if tname in table_map:
            table_map[tname].indexes.append(idx)

    return tables


def _split_comma_top_level(s: str) -> List[str]:
    """Split on commas that are not inside parentheses."""
    parts = []
    depth = 0
    current = []
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
            continue
        current.append(ch)
    if current:
        parts.append(''.join(current))
    return parts


def validate(tables: List[Table]) -> List[Finding]:
    """Run all validation rules against parsed tables."""
    findings: List[Finding] = []

    for table in tables:
        _check_naming(table, findings)
        _check_primary_key(table, findings)
        _check_timestamps(table, findings)
        _check_fk_indexes(table, findings)
        _check_fk_nullable(table, findings)
        _check_soft_delete_index(table, findings)
        _check_sequential_pk(table, findings)
        _check_no_indexes(table, findings)

    return findings


def _check_naming(table: Table, findings: List[Finding]):
    """Enforce snake_case naming for tables and columns."""
    snake = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
    if not snake.match(table.name):
        findings.append(Finding(
            table=table.name, severity=Severity.WARNING, rule="naming_convention",
            message=f"Table name '{table.name}' is not snake_case.",
            suggestion=f"Rename to '{_to_snake(table.name)}'."
        ))
    for cname in table.columns:
        if not snake.match(cname):
            findings.append(Finding(
                table=table.name, severity=Severity.WARNING, rule="naming_convention",
                message=f"Column '{cname}' is not snake_case.",
                suggestion=f"Rename to '{_to_snake(cname)}'."
            ))


def _to_snake(name: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower().replace(' ', '_').replace('-', '_')


def _check_primary_key(table: Table, findings: List[Finding]):
    if not table.primary_key:
        findings.append(Finding(
            table=table.name, severity=Severity.ERROR, rule="missing_primary_key",
            message=f"Table '{table.name}' has no PRIMARY KEY defined.",
            suggestion="Add a PRIMARY KEY column (e.g., id TEXT PRIMARY KEY or id UUID PRIMARY KEY)."
        ))


def _check_timestamps(table: Table, findings: List[Finding]):
    cols = set(table.columns.keys())
    if 'created_at' not in cols:
        findings.append(Finding(
            table=table.name, severity=Severity.WARNING, rule="missing_created_at",
            message=f"Table '{table.name}' is missing a 'created_at' column.",
            suggestion="Add: created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ))
    if 'updated_at' not in cols:
        findings.append(Finding(
            table=table.name, severity=Severity.WARNING, rule="missing_updated_at",
            message=f"Table '{table.name}' is missing an 'updated_at' column.",
            suggestion="Add: updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ))


def _check_fk_indexes(table: Table, findings: List[Finding]):
    indexed_cols = set()
    for idx in table.indexes:
        if idx.columns:
            indexed_cols.add(idx.columns[0])

    for cname, col in table.columns.items():
        if col.references and cname not in indexed_cols and not col.is_pk:
            findings.append(Finding(
                table=table.name, severity=Severity.ERROR, rule="missing_fk_index",
                message=f"Foreign key column '{cname}' has no index.",
                suggestion=f"CREATE INDEX idx_{table.name}_{cname} ON {table.name} ({cname});"
            ))


def _check_fk_nullable(table: Table, findings: List[Finding]):
    for cname, col in table.columns.items():
        if col.references and col.nullable:
            findings.append(Finding(
                table=table.name, severity=Severity.INFO, rule="nullable_fk",
                message=f"Foreign key column '{cname}' is nullable.",
                suggestion="Consider adding NOT NULL if the relationship is mandatory."
            ))


def _check_soft_delete_index(table: Table, findings: List[Finding]):
    if 'deleted_at' not in table.columns:
        return
    has_partial = any(
        idx.where_clause and 'deleted_at' in idx.where_clause.lower()
        for idx in table.indexes
    )
    if not has_partial:
        findings.append(Finding(
            table=table.name, severity=Severity.WARNING, rule="soft_delete_no_partial_index",
            message=f"Table '{table.name}' has soft deletes but no partial index filtering deleted rows.",
            suggestion="Add a partial index: WHERE deleted_at IS NULL on frequently queried columns."
        ))


def _check_sequential_pk(table: Table, findings: List[Finding]):
    if not table.primary_key:
        return
    for pk_col_name in table.primary_key:
        col = table.columns.get(pk_col_name)
        if col and col.data_type.upper() in ('SERIAL', 'BIGSERIAL', 'INT', 'INTEGER', 'BIGINT'):
            if col.is_pk:
                findings.append(Finding(
                    table=table.name, severity=Severity.INFO, rule="sequential_pk",
                    message=f"Primary key '{pk_col_name}' uses sequential integer type '{col.data_type}'.",
                    suggestion="Consider CUID2 or UUIDv7 for non-guessable, sortable IDs (especially if exposed in URLs)."
                ))


def _check_no_indexes(table: Table, findings: List[Finding]):
    if not table.indexes and len(table.columns) > 2:
        findings.append(Finding(
            table=table.name, severity=Severity.WARNING, rule="no_indexes",
            message=f"Table '{table.name}' has no indexes besides the primary key.",
            suggestion="Add indexes on columns used in WHERE clauses, JOINs, and ORDER BY."
        ))


def format_human(findings: List[Finding], tables: List[Table]) -> str:
    """Format findings for human-readable output."""
    lines = []
    lines.append(f"Schema Validation Report")
    lines.append(f"{'=' * 50}")
    lines.append(f"Tables analyzed: {len(tables)}")

    error_count = sum(1 for f in findings if f.severity == Severity.ERROR)
    warn_count = sum(1 for f in findings if f.severity == Severity.WARNING)
    info_count = sum(1 for f in findings if f.severity == Severity.INFO)

    lines.append(f"Findings: {error_count} errors, {warn_count} warnings, {info_count} info")
    lines.append("")

    if not findings:
        lines.append("No issues found. Schema looks good!")
        return '\n'.join(lines)

    severity_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
    sorted_findings = sorted(findings, key=lambda f: (severity_order.get(f.severity, 3), f.table))

    icons = {Severity.ERROR: "[ERROR]", Severity.WARNING: "[WARN] ", Severity.INFO: "[INFO] "}

    for f in sorted_findings:
        icon = icons.get(f.severity, "       ")
        lines.append(f"{icon} {f.table}: {f.message}")
        lines.append(f"         -> {f.suggestion}")
        lines.append("")

    return '\n'.join(lines)


def format_json(findings: List[Finding], tables: List[Table]) -> str:
    """Format findings as JSON."""
    return json.dumps({
        "tables_analyzed": len(tables),
        "summary": {
            "errors": sum(1 for f in findings if f.severity == Severity.ERROR),
            "warnings": sum(1 for f in findings if f.severity == Severity.WARNING),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        },
        "findings": [
            {
                "table": f.table,
                "severity": f.severity,
                "rule": f.rule,
                "message": f.message,
                "suggestion": f.suggestion,
            }
            for f in findings
        ]
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Validate SQL DDL schemas for normalization violations, missing indexes, and naming conventions."
    )
    parser.add_argument("file", help="Path to SQL DDL file to validate")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with code 1 on any warning (not just errors)")
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            sql = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(2)

    tables = parse_ddl(sql)
    if not tables:
        print("Warning: No CREATE TABLE statements found in the file.", file=sys.stderr)
        sys.exit(0)

    findings = validate(tables)

    if args.json_output:
        print(format_json(findings, tables))
    else:
        print(format_human(findings, tables))

    error_count = sum(1 for f in findings if f.severity == Severity.ERROR)
    warn_count = sum(1 for f in findings if f.severity == Severity.WARNING)

    if error_count > 0:
        sys.exit(1)
    if args.strict and warn_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
