#!/usr/bin/env python3
"""
Schema Explorer - Generate documentation from SQL DDL files.

Parses CREATE TABLE, CREATE INDEX, and constraint definitions to produce
a complete schema catalog with relationships and documentation.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class Column:
    """A table column."""
    name: str
    data_type: str
    nullable: bool
    default: Optional[str]
    is_primary_key: bool
    is_unique: bool


@dataclass
class ForeignKey:
    """A foreign key relationship."""
    columns: List[str]
    ref_table: str
    ref_columns: List[str]
    name: Optional[str] = None


@dataclass
class Index:
    """A database index."""
    name: str
    columns: List[str]
    unique: bool


@dataclass
class Table:
    """A database table."""
    name: str
    columns: List[Column] = field(default_factory=list)
    primary_key: List[str] = field(default_factory=list)
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    indexes: List[Index] = field(default_factory=list)


class DDLParser:
    """Parse SQL DDL statements."""

    CREATE_TABLE = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.*?)\)\s*;',
        re.IGNORECASE | re.DOTALL
    )
    CREATE_INDEX = re.compile(
        r'CREATE\s+(UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s+ON\s+["`]?(\w+)["`]?\s*\(([^)]+)\)',
        re.IGNORECASE
    )
    COLUMN_PATTERN = re.compile(
        r'^\s*["`]?(\w+)["`]?\s+([\w().,\s]+?)(?:\s+(NOT\s+NULL|NULL))?'
        r'(?:\s+DEFAULT\s+(.+?))?(?:\s+(PRIMARY\s+KEY))?(?:\s+(UNIQUE))?(?:\s*,?\s*)$',
        re.IGNORECASE
    )
    PK_CONSTRAINT = re.compile(
        r'(?:CONSTRAINT\s+\w+\s+)?PRIMARY\s+KEY\s*\(([^)]+)\)',
        re.IGNORECASE
    )
    FK_CONSTRAINT = re.compile(
        r'(?:CONSTRAINT\s+["`]?(\w+)["`]?\s+)?FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\(([^)]+)\)',
        re.IGNORECASE
    )
    UNIQUE_CONSTRAINT = re.compile(
        r'(?:CONSTRAINT\s+\w+\s+)?UNIQUE\s*\(([^)]+)\)',
        re.IGNORECASE
    )

    SKIP_KEYWORDS = {"PRIMARY", "FOREIGN", "CONSTRAINT", "UNIQUE", "CHECK", "INDEX", "KEY"}

    def parse(self, sql: str) -> Dict[str, Table]:
        """Parse DDL into table definitions."""
        tables: Dict[str, Table] = {}

        # Parse CREATE TABLE statements
        for match in self.CREATE_TABLE.finditer(sql):
            table_name = match.group(1)
            body = match.group(2)
            table = self._parse_table_body(table_name, body)
            tables[table_name] = table

        # Parse standalone CREATE INDEX statements
        for match in self.CREATE_INDEX.finditer(sql):
            is_unique = bool(match.group(1))
            idx_name = match.group(2)
            table_name = match.group(3)
            columns = [c.strip().strip('"`') for c in match.group(4).split(",")]

            if table_name in tables:
                tables[table_name].indexes.append(Index(
                    name=idx_name, columns=columns, unique=is_unique
                ))

        return tables

    def _parse_table_body(self, table_name: str, body: str) -> Table:
        """Parse the body of a CREATE TABLE statement."""
        table = Table(name=table_name)

        # Split on commas, but respect parentheses
        parts = self._split_body(body)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check for constraints first
            pk_match = self.PK_CONSTRAINT.search(part)
            if pk_match:
                table.primary_key = [c.strip().strip('"`') for c in pk_match.group(1).split(",")]
                continue

            fk_match = self.FK_CONSTRAINT.search(part)
            if fk_match:
                fk = ForeignKey(
                    name=fk_match.group(1),
                    columns=[c.strip().strip('"`') for c in fk_match.group(2).split(",")],
                    ref_table=fk_match.group(3),
                    ref_columns=[c.strip().strip('"`') for c in fk_match.group(4).split(",")],
                )
                table.foreign_keys.append(fk)
                continue

            uq_match = self.UNIQUE_CONSTRAINT.search(part)
            if uq_match:
                continue

            # Skip constraint-like lines
            first_word = part.split()[0].upper().strip('"`') if part.split() else ""
            if first_word in self.SKIP_KEYWORDS:
                continue

            # Parse as column definition
            col = self._parse_column(part)
            if col:
                table.columns.append(col)
                if col.is_primary_key:
                    table.primary_key.append(col.name)

        return table

    def _split_body(self, body: str) -> List[str]:
        """Split table body on commas, respecting parentheses."""
        parts = []
        depth = 0
        current = ""
        for char in body:
            if char == "(":
                depth += 1
                current += char
            elif char == ")":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                parts.append(current)
                current = ""
            else:
                current += char
        if current.strip():
            parts.append(current)
        return parts

    def _parse_column(self, definition: str) -> Optional[Column]:
        """Parse a column definition string."""
        definition = definition.strip()
        if not definition:
            return None

        parts = definition.split()
        if len(parts) < 2:
            return None

        name = parts[0].strip('"`')
        upper_def = definition.upper()

        # Extract data type (everything between name and constraints)
        type_parts = []
        i = 1
        while i < len(parts):
            word = parts[i].upper().strip('"`')
            if word in ("NOT", "NULL", "DEFAULT", "PRIMARY", "UNIQUE",
                       "REFERENCES", "CHECK", "CONSTRAINT", "AUTO_INCREMENT",
                       "SERIAL", "GENERATED"):
                break
            type_parts.append(parts[i])
            i += 1

        data_type = " ".join(type_parts).strip(",").strip()
        nullable = "NOT NULL" not in upper_def
        is_pk = "PRIMARY KEY" in upper_def
        is_unique = "UNIQUE" in upper_def

        # Extract default value
        default = None
        default_match = re.search(r'DEFAULT\s+(.+?)(?:\s+(?:NOT|NULL|PRIMARY|UNIQUE|CHECK|CONSTRAINT)|$)',
                                   definition, re.IGNORECASE)
        if default_match:
            default = default_match.group(1).strip().rstrip(",")

        # Serial/auto-increment implies not null
        if "SERIAL" in upper_def or "AUTO_INCREMENT" in upper_def:
            nullable = False

        return Column(
            name=name,
            data_type=data_type,
            nullable=nullable,
            default=default,
            is_primary_key=is_pk,
            is_unique=is_unique,
        )


def format_text(tables: Dict[str, Table]) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("DATABASE SCHEMA DOCUMENTATION")
    lines.append("=" * 60)
    lines.append(f"\nTables: {len(tables)}")

    for name in sorted(tables.keys()):
        lines.append(f"  - {name} ({len(tables[name].columns)} columns)")

    for name in sorted(tables.keys()):
        table = tables[name]
        lines.append(f"\n{'=' * 40}")
        lines.append(f"TABLE: {name}")
        lines.append(f"{'=' * 40}")

        if table.primary_key:
            lines.append(f"Primary Key: {', '.join(table.primary_key)}")

        lines.append(f"\n{'Column':<25} {'Type':<20} {'Nullable':<10} {'Default':<15}")
        lines.append("-" * 70)

        for col in table.columns:
            null_str = "YES" if col.nullable else "NO"
            default_str = str(col.default) if col.default else ""
            pk_marker = " (PK)" if col.is_primary_key else ""
            uq_marker = " (UQ)" if col.is_unique else ""
            lines.append(f"{col.name + pk_marker + uq_marker:<25} {col.data_type:<20} {null_str:<10} {default_str:<15}")

        if table.foreign_keys:
            lines.append(f"\nForeign Keys:")
            for fk in table.foreign_keys:
                fk_name = fk.name or "(unnamed)"
                lines.append(f"  {fk_name}: ({', '.join(fk.columns)}) -> {fk.ref_table}({', '.join(fk.ref_columns)})")

        if table.indexes:
            lines.append(f"\nIndexes:")
            for idx in table.indexes:
                unique_str = "UNIQUE " if idx.unique else ""
                lines.append(f"  {idx.name}: {unique_str}({', '.join(idx.columns)})")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_markdown(tables: Dict[str, Table]) -> str:
    """Format as Markdown documentation."""
    lines = []
    lines.append("# Database Schema\n")
    lines.append(f"**Tables:** {len(tables)}\n")

    # Table of contents
    lines.append("## Tables\n")
    for name in sorted(tables.keys()):
        lines.append(f"- [{name}](#{name.lower()})")
    lines.append("")

    for name in sorted(tables.keys()):
        table = tables[name]
        lines.append(f"### {name}\n")

        if table.primary_key:
            lines.append(f"**Primary Key:** {', '.join(table.primary_key)}\n")

        lines.append("| Column | Type | Nullable | Default |")
        lines.append("|--------|------|----------|---------|")

        for col in table.columns:
            null_str = "YES" if col.nullable else "NO"
            default_str = str(col.default) if col.default else "-"
            col_name = f"**{col.name}** (PK)" if col.is_primary_key else col.name
            lines.append(f"| {col_name} | {col.data_type} | {null_str} | {default_str} |")

        if table.foreign_keys:
            lines.append(f"\n**Foreign Keys:**\n")
            for fk in table.foreign_keys:
                lines.append(f"- `{', '.join(fk.columns)}` -> `{fk.ref_table}({', '.join(fk.ref_columns)})`")

        lines.append("")

    return "\n".join(lines)


def format_json(tables: Dict[str, Table]) -> str:
    """Format as JSON."""
    data = {}
    for name, table in tables.items():
        data[name] = {
            "columns": [asdict(c) for c in table.columns],
            "primary_key": table.primary_key,
            "foreign_keys": [asdict(fk) for fk in table.foreign_keys],
            "indexes": [asdict(idx) for idx in table.indexes],
        }
    return json.dumps({"tables": data, "table_count": len(data)}, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate schema documentation from SQL DDL files."
    )
    parser.add_argument("--file", "-f", required=True, help="Path to SQL DDL file")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text",
                       help="Output format")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    sql = path.read_text()
    ddl_parser = DDLParser()
    tables = ddl_parser.parse(sql)

    if not tables:
        print("No tables found in DDL file.", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        print(format_json(tables))
    elif args.format == "markdown":
        print(format_markdown(tables))
    else:
        print(format_text(tables))


if __name__ == "__main__":
    main()
