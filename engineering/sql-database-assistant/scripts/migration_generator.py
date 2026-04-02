#!/usr/bin/env python3
"""
Migration Generator - Generate SQL migration from schema differences.

Compares two SQL DDL files and generates ALTER TABLE, CREATE TABLE,
and DROP TABLE statements to migrate from one schema to another.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Set


@dataclass
class Column:
    """A table column."""
    name: str
    data_type: str
    nullable: bool
    default: Optional[str]


@dataclass
class Table:
    """A table definition."""
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)


@dataclass
class MigrationStep:
    """A single migration step."""
    operation: str  # add_table, drop_table, add_column, drop_column, alter_column
    table: str
    column: Optional[str]
    sql_up: str
    sql_down: str
    description: str


class SimpleDDLParser:
    """Minimal DDL parser for schema comparison."""

    CREATE_TABLE = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.*?)\)\s*;',
        re.IGNORECASE | re.DOTALL
    )
    SKIP_KEYWORDS = {"PRIMARY", "FOREIGN", "CONSTRAINT", "UNIQUE", "CHECK", "INDEX", "KEY"}

    def parse(self, sql: str) -> Dict[str, Table]:
        """Parse DDL into table definitions."""
        tables = {}
        for match in self.CREATE_TABLE.finditer(sql):
            table_name = match.group(1)
            body = match.group(2)
            table = Table(name=table_name)
            table.columns = self._parse_columns(body)
            tables[table_name] = table
        return tables

    def _parse_columns(self, body: str) -> Dict[str, Column]:
        """Parse column definitions from table body."""
        columns = {}
        parts = self._split_commas(body)

        for part in parts:
            part = part.strip()
            if not part:
                continue
            first_word = part.split()[0].upper().strip('"`')
            if first_word in self.SKIP_KEYWORDS:
                continue

            col = self._parse_column(part)
            if col:
                columns[col.name] = col

        return columns

    def _split_commas(self, text: str) -> List[str]:
        """Split on commas respecting parentheses."""
        parts = []
        depth = 0
        current = ""
        for ch in text:
            if ch == "(":
                depth += 1
                current += ch
            elif ch == ")":
                depth -= 1
                current += ch
            elif ch == "," and depth == 0:
                parts.append(current)
                current = ""
            else:
                current += ch
        if current.strip():
            parts.append(current)
        return parts

    def _parse_column(self, definition: str) -> Optional[Column]:
        """Parse a single column definition."""
        parts = definition.split()
        if len(parts) < 2:
            return None

        name = parts[0].strip('"`')
        upper_def = definition.upper()

        # Extract type
        type_parts = []
        for i in range(1, len(parts)):
            word = parts[i].upper().strip('"`')
            if word in ("NOT", "NULL", "DEFAULT", "PRIMARY", "UNIQUE",
                       "REFERENCES", "CHECK", "CONSTRAINT", "AUTO_INCREMENT",
                       "SERIAL", "GENERATED"):
                break
            type_parts.append(parts[i])

        data_type = " ".join(type_parts).strip(",")
        nullable = "NOT NULL" not in upper_def

        default = None
        default_match = re.search(r'DEFAULT\s+(.+?)(?:\s+(?:NOT|NULL|PRIMARY|UNIQUE|CHECK)|$)',
                                   definition, re.IGNORECASE)
        if default_match:
            default = default_match.group(1).strip().rstrip(",")

        return Column(name=name, data_type=data_type, nullable=nullable, default=default)


class MigrationGenerator:
    """Generate migration SQL from schema differences."""

    def __init__(self, from_tables: Dict[str, Table], to_tables: Dict[str, Table]):
        self.from_tables = from_tables
        self.to_tables = to_tables
        self.steps: List[MigrationStep] = []

    def generate(self) -> List[MigrationStep]:
        """Generate migration steps."""
        from_names = set(self.from_tables.keys())
        to_names = set(self.to_tables.keys())

        # New tables
        for table_name in sorted(to_names - from_names):
            self._add_create_table(table_name)

        # Dropped tables
        for table_name in sorted(from_names - to_names):
            self._add_drop_table(table_name)

        # Modified tables
        for table_name in sorted(from_names & to_names):
            self._compare_table(table_name)

        return self.steps

    def _add_create_table(self, name: str):
        """Generate CREATE TABLE migration."""
        table = self.to_tables[name]
        col_defs = []
        for col in table.columns.values():
            col_def = f"    {col.name} {col.data_type}"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default:
                col_def += f" DEFAULT {col.default}"
            col_defs.append(col_def)

        sql_up = f"CREATE TABLE {name} (\n{','.join(chr(10) + d for d in col_defs)}\n);"
        sql_down = f"DROP TABLE IF EXISTS {name};"

        self.steps.append(MigrationStep(
            operation="add_table",
            table=name,
            column=None,
            sql_up=sql_up,
            sql_down=sql_down,
            description=f"Create new table '{name}' with {len(table.columns)} columns.",
        ))

    def _add_drop_table(self, name: str):
        """Generate DROP TABLE migration."""
        table = self.from_tables[name]
        col_defs = []
        for col in table.columns.values():
            col_def = f"    {col.name} {col.data_type}"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default:
                col_def += f" DEFAULT {col.default}"
            col_defs.append(col_def)

        sql_up = f"DROP TABLE IF EXISTS {name};"
        sql_down = f"CREATE TABLE {name} (\n{','.join(chr(10) + d for d in col_defs)}\n);"

        self.steps.append(MigrationStep(
            operation="drop_table",
            table=name,
            column=None,
            sql_up=sql_up,
            sql_down=sql_down,
            description=f"Drop table '{name}'.",
        ))

    def _compare_table(self, name: str):
        """Compare two versions of a table and generate column migrations."""
        from_cols = self.from_tables[name].columns
        to_cols = self.to_tables[name].columns

        from_col_names = set(from_cols.keys())
        to_col_names = set(to_cols.keys())

        # New columns
        for col_name in sorted(to_col_names - from_col_names):
            col = to_cols[col_name]
            null_str = "" if col.nullable else " NOT NULL"
            default_str = f" DEFAULT {col.default}" if col.default else ""

            sql_up = f"ALTER TABLE {name} ADD COLUMN {col.name} {col.data_type}{null_str}{default_str};"
            sql_down = f"ALTER TABLE {name} DROP COLUMN {col.name};"

            self.steps.append(MigrationStep(
                operation="add_column",
                table=name,
                column=col_name,
                sql_up=sql_up,
                sql_down=sql_down,
                description=f"Add column '{col_name}' ({col.data_type}) to '{name}'.",
            ))

        # Dropped columns
        for col_name in sorted(from_col_names - to_col_names):
            col = from_cols[col_name]
            null_str = "" if col.nullable else " NOT NULL"
            default_str = f" DEFAULT {col.default}" if col.default else ""

            sql_up = f"ALTER TABLE {name} DROP COLUMN {col_name};"
            sql_down = f"ALTER TABLE {name} ADD COLUMN {col.name} {col.data_type}{null_str}{default_str};"

            self.steps.append(MigrationStep(
                operation="drop_column",
                table=name,
                column=col_name,
                sql_up=sql_up,
                sql_down=sql_down,
                description=f"Drop column '{col_name}' from '{name}'.",
            ))

        # Modified columns (type or nullability changed)
        for col_name in sorted(from_col_names & to_col_names):
            from_col = from_cols[col_name]
            to_col = to_cols[col_name]

            if from_col.data_type.upper() != to_col.data_type.upper() or from_col.nullable != to_col.nullable:
                null_str_to = "" if to_col.nullable else " NOT NULL"
                null_str_from = "" if from_col.nullable else " NOT NULL"

                sql_up = f"ALTER TABLE {name} ALTER COLUMN {col_name} TYPE {to_col.data_type};"
                if from_col.nullable != to_col.nullable:
                    if to_col.nullable:
                        sql_up += f"\nALTER TABLE {name} ALTER COLUMN {col_name} DROP NOT NULL;"
                    else:
                        sql_up += f"\nALTER TABLE {name} ALTER COLUMN {col_name} SET NOT NULL;"

                sql_down = f"ALTER TABLE {name} ALTER COLUMN {col_name} TYPE {from_col.data_type};"
                if from_col.nullable != to_col.nullable:
                    if from_col.nullable:
                        sql_down += f"\nALTER TABLE {name} ALTER COLUMN {col_name} DROP NOT NULL;"
                    else:
                        sql_down += f"\nALTER TABLE {name} ALTER COLUMN {col_name} SET NOT NULL;"

                changes = []
                if from_col.data_type.upper() != to_col.data_type.upper():
                    changes.append(f"type {from_col.data_type} -> {to_col.data_type}")
                if from_col.nullable != to_col.nullable:
                    changes.append(f"nullable {from_col.nullable} -> {to_col.nullable}")

                self.steps.append(MigrationStep(
                    operation="alter_column",
                    table=name,
                    column=col_name,
                    sql_up=sql_up,
                    sql_down=sql_down,
                    description=f"Alter column '{col_name}' in '{name}': {', '.join(changes)}.",
                ))


def format_text(steps: List[MigrationStep]) -> str:
    """Format as human-readable migration script."""
    lines = []
    lines.append("-- " + "=" * 58)
    lines.append("-- MIGRATION SCRIPT")
    lines.append("-- " + "=" * 58)
    lines.append(f"-- Steps: {len(steps)}")
    lines.append("")

    if not steps:
        lines.append("-- No schema differences found.")
        return "\n".join(lines)

    lines.append("-- ==================== UP ====================")
    lines.append("BEGIN;")
    lines.append("")
    for i, step in enumerate(steps, 1):
        lines.append(f"-- Step {i}: {step.description}")
        lines.append(step.sql_up)
        lines.append("")
    lines.append("COMMIT;")

    lines.append("")
    lines.append("-- ==================== DOWN (ROLLBACK) ====================")
    lines.append("-- BEGIN;")
    for step in reversed(steps):
        lines.append(f"-- {step.sql_down}")
    lines.append("-- COMMIT;")

    return "\n".join(lines)


def format_json(steps: List[MigrationStep]) -> str:
    """Format as JSON."""
    return json.dumps({
        "steps": [asdict(s) for s in steps],
        "summary": {
            "total": len(steps),
            "add_table": sum(1 for s in steps if s.operation == "add_table"),
            "drop_table": sum(1 for s in steps if s.operation == "drop_table"),
            "add_column": sum(1 for s in steps if s.operation == "add_column"),
            "drop_column": sum(1 for s in steps if s.operation == "drop_column"),
            "alter_column": sum(1 for s in steps if s.operation == "alter_column"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SQL migration by comparing two schema DDL files."
    )
    parser.add_argument("--from", dest="from_file", required=True, help="Path to source (current) DDL file")
    parser.add_argument("--to", dest="to_file", required=True, help="Path to target (desired) DDL file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    from_path = Path(args.from_file)
    to_path = Path(args.to_file)

    for p, label in [(from_path, "source"), (to_path, "target")]:
        if not p.exists():
            print(f"Error: {label} file not found: {p}", file=sys.stderr)
            sys.exit(2)

    ddl_parser = SimpleDDLParser()
    from_tables = ddl_parser.parse(from_path.read_text())
    to_tables = ddl_parser.parse(to_path.read_text())

    generator = MigrationGenerator(from_tables, to_tables)
    steps = generator.generate()

    if args.format == "json":
        print(format_json(steps))
    else:
        print(format_text(steps))


if __name__ == "__main__":
    main()
