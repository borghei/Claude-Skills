#!/usr/bin/env python3
"""Parse SQL DDL and generate Mermaid ER diagrams showing table relationships.

Reads CREATE TABLE statements and outputs a Mermaid erDiagram block with:
- All tables and their columns (with PK/FK/UK annotations)
- Relationships inferred from REFERENCES clauses
- Nullable vs required relationship cardinality

Supports PostgreSQL, MySQL, and SQLite DDL syntax.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class Column:
    name: str
    data_type: str
    is_pk: bool = False
    is_fk: bool = False
    is_unique: bool = False
    nullable: bool = True
    references_table: Optional[str] = None
    references_column: Optional[str] = None


@dataclass
class Table:
    name: str
    columns: List[Column] = field(default_factory=list)


@dataclass
class Relationship:
    from_table: str
    to_table: str
    from_column: str
    to_column: str
    nullable: bool
    label: str


def parse_ddl(sql: str) -> Tuple[List[Table], List[Relationship]]:
    """Parse SQL DDL into tables and relationships."""
    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    tables: List[Table] = []
    relationships: List[Relationship] = []
    table_map: Dict[str, Table] = {}

    table_pattern = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'(?:"?(\w+)"?\.)?'
        r'"?(\w+)"?'
        r'\s*\((.*?)\)\s*;',
        re.IGNORECASE | re.DOTALL
    )

    for match in table_pattern.finditer(sql):
        _schema, tname, body = match.group(1), match.group(2), match.group(3)
        table = Table(name=tname)

        # Track unique constraints at table level
        unique_cols = set()
        unique_match = re.findall(r'UNIQUE\s*\(\s*"?(\w+)"?\s*\)', body, re.IGNORECASE)
        for u in unique_match:
            unique_cols.add(u)

        pk_cols = set()
        pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', body, re.IGNORECASE)
        if pk_match:
            pk_cols = {c.strip().strip('"') for c in pk_match.group(1).split(',')}

        parts = _split_comma_top_level(body)

        for part in parts:
            part = part.strip()
            upper = part.upper()

            # Skip table-level constraints
            if re.match(r'(PRIMARY\s+KEY|UNIQUE|INDEX|KEY|CONSTRAINT|CHECK|FOREIGN\s+KEY)\s', upper):
                # But extract FOREIGN KEY ... REFERENCES
                fk_match = re.match(
                    r'(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(\s*"?(\w+)"?\s*\)\s*'
                    r'REFERENCES\s+"?(\w+)"?\s*\(\s*"?(\w+)"?\s*\)',
                    part, re.IGNORECASE
                )
                if fk_match:
                    fk_col, ref_table, ref_col = fk_match.group(1), fk_match.group(2), fk_match.group(3)
                    # Mark existing column as FK
                    for col in table.columns:
                        if col.name == fk_col:
                            col.is_fk = True
                            col.references_table = ref_table
                            col.references_column = ref_col
                            relationships.append(Relationship(
                                from_table=tname, to_table=ref_table,
                                from_column=fk_col, to_column=ref_col,
                                nullable=col.nullable,
                                label=fk_col.replace('_id', '').replace('_', ' ')
                            ))
                            break
                continue

            # Column definition
            col_match = re.match(r'"?(\w+)"?\s+(\w[\w\s()]*)', part, re.IGNORECASE)
            if not col_match:
                continue

            cname = col_match.group(1)
            ctype = col_match.group(2).strip().split()[0]  # first word of type

            is_pk = bool(re.search(r'PRIMARY\s+KEY', part, re.IGNORECASE)) or cname in pk_cols
            is_unique = bool(re.search(r'\bUNIQUE\b', part, re.IGNORECASE)) or cname in unique_cols
            nullable = not bool(re.search(r'NOT\s+NULL', part, re.IGNORECASE)) and not is_pk

            ref_match = re.search(
                r'REFERENCES\s+"?(\w+)"?\s*(?:\(\s*"?(\w+)"?\s*\))?',
                part, re.IGNORECASE
            )
            ref_table = ref_match.group(1) if ref_match else None
            ref_col = ref_match.group(2) if ref_match and ref_match.group(2) else 'id'

            col = Column(
                name=cname, data_type=_normalize_type(ctype),
                is_pk=is_pk, is_fk=bool(ref_table), is_unique=is_unique,
                nullable=nullable, references_table=ref_table, references_column=ref_col
            )
            table.columns.append(col)

            if ref_table:
                relationships.append(Relationship(
                    from_table=tname, to_table=ref_table,
                    from_column=cname, to_column=ref_col,
                    nullable=nullable,
                    label=cname.replace('_id', '').replace('_', ' ')
                ))

        tables.append(table)
        table_map[tname] = table

    return tables, relationships


def _split_comma_top_level(s: str) -> List[str]:
    """Split on commas not inside parentheses."""
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


def _normalize_type(t: str) -> str:
    """Normalize SQL types to short display names."""
    mapping = {
        'CHARACTER': 'varchar', 'VARCHAR': 'varchar', 'TEXT': 'text',
        'INTEGER': 'int', 'INT': 'int', 'BIGINT': 'bigint',
        'SERIAL': 'serial', 'BIGSERIAL': 'bigserial',
        'BOOLEAN': 'bool', 'BOOL': 'bool',
        'TIMESTAMP': 'timestamp', 'TIMESTAMPTZ': 'timestamptz',
        'DATE': 'date', 'TIME': 'time',
        'NUMERIC': 'numeric', 'DECIMAL': 'decimal',
        'FLOAT': 'float', 'DOUBLE': 'double',
        'REAL': 'real', 'UUID': 'uuid', 'JSONB': 'jsonb', 'JSON': 'json',
    }
    return mapping.get(t.upper(), t.lower())


def _table_display_name(name: str) -> str:
    """Convert snake_case to PascalCase for Mermaid display."""
    return ''.join(word.capitalize() for word in name.split('_'))


def generate_mermaid(tables: List[Table], relationships: List[Relationship]) -> str:
    """Generate Mermaid ER diagram syntax."""
    lines = ["erDiagram"]

    # Deduplicate relationships by (from_table, to_table, from_column)
    seen = set()
    for rel in relationships:
        key = (rel.from_table, rel.to_table, rel.from_column)
        if key in seen:
            continue
        seen.add(key)

        from_name = _table_display_name(rel.from_table)
        to_name = _table_display_name(rel.to_table)

        # Determine cardinality:
        # parent (to_table) has one, child (from_table) has many
        # nullable FK = zero-or-more, non-nullable = one-or-more
        if rel.nullable:
            # to_table ||--o{ from_table : "label"
            connector = "||--o{"
        else:
            connector = "||--|{"

        lines.append(f"    {to_name} {connector} {from_name} : \"{rel.label}\"")

    lines.append("")

    # Table definitions
    for table in tables:
        display = _table_display_name(table.name)
        lines.append(f"    {display} {{")
        for col in table.columns:
            annotations = []
            if col.is_pk:
                annotations.append("PK")
            if col.is_fk:
                annotations.append("FK")
            if col.is_unique and not col.is_pk:
                annotations.append("UK")

            ann_str = ",".join(annotations)
            if ann_str:
                lines.append(f"        {col.data_type} {col.name} {ann_str}")
            else:
                lines.append(f"        {col.data_type} {col.name}")
        lines.append("    }")

    return '\n'.join(lines)


def generate_summary(tables: List[Table], relationships: List[Relationship]) -> Dict:
    """Generate a structured summary of the schema."""
    return {
        "table_count": len(tables),
        "relationship_count": len(relationships),
        "tables": [
            {
                "name": t.name,
                "column_count": len(t.columns),
                "columns": [
                    {
                        "name": c.name,
                        "type": c.data_type,
                        "pk": c.is_pk,
                        "fk": c.is_fk,
                        "unique": c.is_unique,
                        "nullable": c.nullable,
                        **({"references": f"{c.references_table}.{c.references_column}"} if c.references_table else {})
                    }
                    for c in t.columns
                ]
            }
            for t in tables
        ],
        "relationships": [
            {
                "from": f"{r.from_table}.{r.from_column}",
                "to": f"{r.to_table}.{r.to_column}",
                "nullable": r.nullable
            }
            for r in relationships
        ]
    }


def format_human(tables: List[Table], relationships: List[Relationship], mermaid: str) -> str:
    """Format output for human reading."""
    lines = []
    lines.append("ERD Generator Report")
    lines.append("=" * 50)
    lines.append(f"Tables: {len(tables)}")
    lines.append(f"Relationships: {len(relationships)}")
    lines.append("")
    lines.append("Mermaid ER Diagram:")
    lines.append("-" * 50)
    lines.append(f"```mermaid")
    lines.append(mermaid)
    lines.append("```")
    lines.append("")
    lines.append("Table Summary:")
    lines.append("-" * 50)
    for t in tables:
        pk_cols = [c.name for c in t.columns if c.is_pk]
        fk_cols = [c.name for c in t.columns if c.is_fk]
        lines.append(f"  {t.name} ({len(t.columns)} columns)")
        if pk_cols:
            lines.append(f"    PK: {', '.join(pk_cols)}")
        if fk_cols:
            lines.append(f"    FK: {', '.join(fk_cols)}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse SQL DDL and generate Mermaid ER diagrams showing table relationships."
    )
    parser.add_argument("file", help="Path to SQL DDL file")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON (includes Mermaid diagram and structured summary)")
    parser.add_argument("-o", "--output", help="Write Mermaid diagram to file (raw .mmd)")
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

    tables, relationships = parse_ddl(sql)

    if not tables:
        print("Warning: No CREATE TABLE statements found.", file=sys.stderr)
        sys.exit(0)

    mermaid = generate_mermaid(tables, relationships)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(mermaid + '\n')
            print(f"Mermaid diagram written to {args.output}")
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(2)

    if args.json_output:
        summary = generate_summary(tables, relationships)
        summary["mermaid"] = mermaid
        print(json.dumps(summary, indent=2))
    elif not args.output:
        print(format_human(tables, relationships, mermaid))
    elif args.output and not args.json_output:
        # Already wrote file, print summary
        print(f"Tables: {len(tables)}, Relationships: {len(relationships)}")

    sys.exit(0)


if __name__ == '__main__':
    main()
