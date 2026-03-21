#!/usr/bin/env python3
"""Compare two SQL schema files and generate migration SQL (ALTER statements).

Performs a structural diff between an 'old' and 'new' SQL DDL schema and produces:
- ALTER TABLE ADD COLUMN for new columns
- ALTER TABLE DROP COLUMN for removed columns
- ALTER TABLE ALTER COLUMN for type changes
- CREATE TABLE for new tables
- DROP TABLE for removed tables
- CREATE INDEX / DROP INDEX for index changes
- Rollback SQL for reversing the migration

Supports PostgreSQL syntax. Designed for review before execution.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set


@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool
    is_pk: bool
    default: Optional[str]
    references: Optional[str]
    full_definition: str  # original DDL fragment for comparison


@dataclass
class Index:
    name: str
    table: str
    columns: List[str]
    unique: bool
    where_clause: Optional[str]
    original: str


@dataclass
class Table:
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)
    pk_columns: List[str] = field(default_factory=list)
    original_ddl: str = ""


@dataclass
class Migration:
    description: str
    up_sql: str
    down_sql: str
    risk: str  # "low", "medium", "high"


def parse_schema(sql: str) -> Tuple[Dict[str, Table], Dict[str, Index]]:
    """Parse SQL DDL into tables and indexes."""
    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    tables: Dict[str, Table] = {}
    indexes: Dict[str, Index] = {}

    # Parse CREATE TABLE
    table_pattern = re.compile(
        r'(CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'(?:"?(\w+)"?\.)?'
        r'"?(\w+)"?'
        r'\s*\((.*?)\)\s*;)',
        re.IGNORECASE | re.DOTALL
    )

    for match in table_pattern.finditer(sql):
        full_ddl = match.group(1)
        tname = match.group(3)
        body = match.group(4)
        table = Table(name=tname, original_ddl=full_ddl)

        pk_cols = set()
        pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', body, re.IGNORECASE)
        if pk_match:
            pk_cols = {c.strip().strip('"') for c in pk_match.group(1).split(',')}

        parts = _split_comma_top_level(body)

        for part in parts:
            part = part.strip()
            upper = part.upper()

            if re.match(r'(PRIMARY\s+KEY|UNIQUE|INDEX|KEY|CONSTRAINT|CHECK|FOREIGN\s+KEY)\s', upper):
                continue

            col_match = re.match(r'"?(\w+)"?\s+(.+)', part, re.IGNORECASE)
            if not col_match:
                continue

            cname = col_match.group(1)
            rest = col_match.group(2).strip()

            # Extract type (first token, possibly with parenthesized args)
            type_match = re.match(r'(\w+(?:\s*\([^)]*\))?)', rest)
            ctype = type_match.group(1).upper() if type_match else rest.split()[0].upper()

            is_pk = bool(re.search(r'PRIMARY\s+KEY', part, re.IGNORECASE)) or cname in pk_cols
            nullable = not bool(re.search(r'NOT\s+NULL', part, re.IGNORECASE)) and not is_pk
            default_match = re.search(r'DEFAULT\s+((?:\'[^\']*\'|\S+))', part, re.IGNORECASE)
            ref_match = re.search(r'REFERENCES\s+"?(\w+)"?', part, re.IGNORECASE)

            col = Column(
                name=cname,
                data_type=ctype,
                nullable=nullable,
                is_pk=is_pk,
                default=default_match.group(1) if default_match else None,
                references=ref_match.group(1) if ref_match else None,
                full_definition=rest,
            )
            table.columns[cname] = col
            if is_pk:
                table.pk_columns.append(cname)

        tables[tname] = table

    # Parse CREATE INDEX
    idx_pattern = re.compile(
        r'(CREATE\s+(UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?'
        r'"?(\w+)"?\s+ON\s+"?(\w+)"?\s*(?:USING\s+\w+\s*)?\(([^)]+)\)'
        r'(?:\s+WHERE\s+(.+?))?)\s*;',
        re.IGNORECASE | re.DOTALL
    )
    for match in idx_pattern.finditer(sql):
        original = match.group(1) + ';'
        unique = bool(match.group(2))
        idx_name = match.group(3)
        tname = match.group(4)
        cols = [c.strip().strip('"') for c in match.group(5).split(',')]
        where = match.group(6).strip() if match.group(6) else None

        indexes[idx_name] = Index(
            name=idx_name, table=tname, columns=cols,
            unique=unique, where_clause=where, original=original
        )

    return tables, indexes


def _split_comma_top_level(s: str) -> List[str]:
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


def diff_schemas(
    old_tables: Dict[str, Table], old_indexes: Dict[str, Index],
    new_tables: Dict[str, Table], new_indexes: Dict[str, Index]
) -> List[Migration]:
    """Compare two schemas and generate migrations."""
    migrations: List[Migration] = []

    old_names = set(old_tables.keys())
    new_names = set(new_tables.keys())

    # New tables
    for tname in sorted(new_names - old_names):
        table = new_tables[tname]
        migrations.append(Migration(
            description=f"Create table '{tname}'",
            up_sql=table.original_ddl,
            down_sql=f"DROP TABLE IF EXISTS {tname};",
            risk="low"
        ))

    # Dropped tables
    for tname in sorted(old_names - new_names):
        table = old_tables[tname]
        migrations.append(Migration(
            description=f"Drop table '{tname}'",
            up_sql=f"DROP TABLE IF EXISTS {tname};",
            down_sql=table.original_ddl,
            risk="high"
        ))

    # Modified tables
    for tname in sorted(old_names & new_names):
        old_t = old_tables[tname]
        new_t = new_tables[tname]
        old_cols = set(old_t.columns.keys())
        new_cols = set(new_t.columns.keys())

        # Added columns
        for cname in sorted(new_cols - old_cols):
            col = new_t.columns[cname]
            parts = [f"ALTER TABLE {tname} ADD COLUMN {cname} {col.data_type}"]
            if not col.nullable:
                if col.default:
                    parts.append(f"NOT NULL DEFAULT {col.default}")
                else:
                    # Suggest safe pattern for NOT NULL without default
                    parts = [
                        f"-- Phase 1: Add nullable column",
                        f"ALTER TABLE {tname} ADD COLUMN {cname} {col.data_type};",
                        f"-- Phase 2: Backfill data (adjust value as needed)",
                        f"-- UPDATE {tname} SET {cname} = <default_value> WHERE {cname} IS NULL;",
                        f"-- Phase 3: Set NOT NULL after backfill",
                        f"-- ALTER TABLE {tname} ALTER COLUMN {cname} SET NOT NULL;",
                    ]
                    migrations.append(Migration(
                        description=f"Add column '{cname}' to '{tname}' (NOT NULL, needs backfill)",
                        up_sql='\n'.join(parts),
                        down_sql=f"ALTER TABLE {tname} DROP COLUMN IF EXISTS {cname};",
                        risk="medium"
                    ))
                    continue
            else:
                if col.default:
                    parts.append(f"DEFAULT {col.default}")
            if col.references:
                parts.append(f"REFERENCES {col.references}")

            up_sql = ' '.join(parts) + ';'
            migrations.append(Migration(
                description=f"Add column '{cname}' to '{tname}'",
                up_sql=up_sql,
                down_sql=f"ALTER TABLE {tname} DROP COLUMN IF EXISTS {cname};",
                risk="low"
            ))

        # Removed columns
        for cname in sorted(old_cols - new_cols):
            col = old_t.columns[cname]
            rebuild_parts = [f"{cname} {col.data_type}"]
            if not col.nullable:
                rebuild_parts.append("NOT NULL")
            if col.default:
                rebuild_parts.append(f"DEFAULT {col.default}")

            migrations.append(Migration(
                description=f"Drop column '{cname}' from '{tname}'",
                up_sql=f"ALTER TABLE {tname} DROP COLUMN IF EXISTS {cname};",
                down_sql=f"ALTER TABLE {tname} ADD COLUMN {' '.join(rebuild_parts)};",
                risk="high"
            ))

        # Modified columns (type or nullability changes)
        for cname in sorted(old_cols & new_cols):
            old_c = old_t.columns[cname]
            new_c = new_t.columns[cname]

            stmts_up = []
            stmts_down = []

            if old_c.data_type != new_c.data_type:
                stmts_up.append(
                    f"ALTER TABLE {tname} ALTER COLUMN {cname} TYPE {new_c.data_type} "
                    f"USING {cname}::{new_c.data_type};"
                )
                stmts_down.append(
                    f"ALTER TABLE {tname} ALTER COLUMN {cname} TYPE {old_c.data_type} "
                    f"USING {cname}::{old_c.data_type};"
                )

            if old_c.nullable and not new_c.nullable:
                stmts_up.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} SET NOT NULL;")
                stmts_down.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} DROP NOT NULL;")
            elif not old_c.nullable and new_c.nullable:
                stmts_up.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} DROP NOT NULL;")
                stmts_down.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} SET NOT NULL;")

            if old_c.default != new_c.default:
                if new_c.default:
                    stmts_up.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} SET DEFAULT {new_c.default};")
                else:
                    stmts_up.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} DROP DEFAULT;")
                if old_c.default:
                    stmts_down.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} SET DEFAULT {old_c.default};")
                else:
                    stmts_down.append(f"ALTER TABLE {tname} ALTER COLUMN {cname} DROP DEFAULT;")

            if stmts_up:
                risk = "medium" if any('TYPE' in s for s in stmts_up) else "low"
                migrations.append(Migration(
                    description=f"Alter column '{cname}' in '{tname}'",
                    up_sql='\n'.join(stmts_up),
                    down_sql='\n'.join(stmts_down),
                    risk=risk
                ))

    # Index changes
    old_idx_names = set(old_indexes.keys())
    new_idx_names = set(new_indexes.keys())

    for iname in sorted(new_idx_names - old_idx_names):
        idx = new_indexes[iname]
        migrations.append(Migration(
            description=f"Create index '{iname}' on '{idx.table}'",
            up_sql=idx.original,
            down_sql=f"DROP INDEX IF EXISTS {iname};",
            risk="low"
        ))

    for iname in sorted(old_idx_names - new_idx_names):
        idx = old_indexes[iname]
        migrations.append(Migration(
            description=f"Drop index '{iname}' from '{idx.table}'",
            up_sql=f"DROP INDEX IF EXISTS {iname};",
            down_sql=idx.original,
            risk="medium"
        ))

    return migrations


def format_sql(migrations: List[Migration], include_rollback: bool = True) -> str:
    """Format migrations as executable SQL."""
    if not migrations:
        return "-- No schema differences found."

    lines = []
    lines.append("-- Migration Script")
    lines.append("-- Generated by migration_diffr.py")
    lines.append(f"-- Changes: {len(migrations)}")
    lines.append("")

    # Group by risk
    high = [m for m in migrations if m.risk == "high"]
    medium = [m for m in migrations if m.risk == "medium"]
    low = [m for m in migrations if m.risk == "low"]

    if high:
        lines.append("-- ============================================")
        lines.append("-- HIGH RISK (review carefully, may lose data)")
        lines.append("-- ============================================")
        for m in high:
            lines.append(f"")
            lines.append(f"-- {m.description}")
            lines.append(m.up_sql)

    if medium:
        lines.append("")
        lines.append("-- ============================================")
        lines.append("-- MEDIUM RISK (may require backfill or lock)")
        lines.append("-- ============================================")
        for m in medium:
            lines.append(f"")
            lines.append(f"-- {m.description}")
            lines.append(m.up_sql)

    if low:
        lines.append("")
        lines.append("-- ============================================")
        lines.append("-- LOW RISK (safe, additive changes)")
        lines.append("-- ============================================")
        for m in low:
            lines.append(f"")
            lines.append(f"-- {m.description}")
            lines.append(m.up_sql)

    if include_rollback:
        lines.append("")
        lines.append("")
        lines.append("-- ============================================")
        lines.append("-- ROLLBACK SCRIPT")
        lines.append("-- ============================================")
        for m in reversed(migrations):
            lines.append(f"")
            lines.append(f"-- Rollback: {m.description}")
            lines.append(m.down_sql)

    return '\n'.join(lines)


def format_human(migrations: List[Migration]) -> str:
    """Format a human-readable summary."""
    lines = []
    lines.append("Migration Diff Report")
    lines.append("=" * 50)
    lines.append(f"Total changes: {len(migrations)}")

    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for m in migrations:
        risk_counts[m.risk] += 1

    lines.append(f"Risk breakdown: {risk_counts['high']} high, {risk_counts['medium']} medium, {risk_counts['low']} low")
    lines.append("")

    if not migrations:
        lines.append("Schemas are identical. No migration needed.")
        return '\n'.join(lines)

    for i, m in enumerate(migrations, 1):
        risk_label = {"high": "[HIGH]  ", "medium": "[MEDIUM]", "low": "[LOW]   "}
        lines.append(f"  {i}. {risk_label[m.risk]} {m.description}")

    lines.append("")
    lines.append("SQL Migration:")
    lines.append("-" * 50)
    lines.append(format_sql(migrations))

    return '\n'.join(lines)


def format_json(migrations: List[Migration]) -> str:
    """Format as JSON."""
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for m in migrations:
        risk_counts[m.risk] += 1

    return json.dumps({
        "total_changes": len(migrations),
        "risk_summary": risk_counts,
        "migrations": [
            {
                "description": m.description,
                "risk": m.risk,
                "up": m.up_sql,
                "down": m.down_sql,
            }
            for m in migrations
        ],
        "up_sql": format_sql(migrations, include_rollback=False),
        "down_sql": format_sql(
            migrations, include_rollback=False
        ).replace("Migration Script", "Rollback Script") if migrations else "",
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two SQL schema files and generate migration ALTER statements."
    )
    parser.add_argument("old_schema", help="Path to the current/old SQL schema file")
    parser.add_argument("new_schema", help="Path to the target/new SQL schema file")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.add_argument("--no-rollback", action="store_true",
                        help="Omit rollback SQL from output")
    parser.add_argument("-o", "--output", help="Write migration SQL to file")
    args = parser.parse_args()

    try:
        with open(args.old_schema, 'r') as f:
            old_sql = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.old_schema}", file=sys.stderr)
        sys.exit(2)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(args.new_schema, 'r') as f:
            new_sql = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.new_schema}", file=sys.stderr)
        sys.exit(2)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(2)

    old_tables, old_indexes = parse_schema(old_sql)
    new_tables, new_indexes = parse_schema(new_sql)

    migrations = diff_schemas(old_tables, old_indexes, new_tables, new_indexes)

    if args.output:
        try:
            sql_out = format_sql(migrations, include_rollback=not args.no_rollback)
            with open(args.output, 'w') as f:
                f.write(sql_out + '\n')
            print(f"Migration SQL written to {args.output}")
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(2)

    if args.json_output:
        print(format_json(migrations))
    elif not args.output:
        print(format_human(migrations))

    # Exit code: 0 = no changes, 1 = changes found (useful in CI)
    sys.exit(0 if not migrations else 1)


if __name__ == '__main__':
    main()
