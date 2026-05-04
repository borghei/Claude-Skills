#!/usr/bin/env python3
"""
Xlsx Auditor — audit a Microsoft Excel .xlsx file using the Python standard
library only. Reads OOXML directly via zipfile + xml.etree.

Usage:
    python xlsx_auditor.py model.xlsx
    python xlsx_auditor.py model.xlsx --json
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


X_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def parse_xml(blob):
    try:
        return ET.fromstring(blob)
    except ET.ParseError:
        return None


def list_sheets_from_workbook(workbook_xml, rels_xml):
    """Return list of (name, sheetId, relId, hidden, target) by joining workbook.xml + rels."""
    wb = parse_xml(workbook_xml)
    if wb is None:
        return []

    rels_targets = {}
    if rels_xml:
        rels = parse_xml(rels_xml)
        if rels is not None:
            for rel in rels:
                rels_targets[rel.attrib.get("Id", "")] = rel.attrib.get("Target", "")

    sheets = []
    for sheet in wb.findall(f"{X_NS}sheets/{X_NS}sheet"):
        rel_id = sheet.attrib.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", ""
        )
        sheets.append({
            "name": sheet.attrib.get("name", "(unnamed)"),
            "sheet_id": sheet.attrib.get("sheetId", ""),
            "rel_id": rel_id,
            "hidden": sheet.attrib.get("state", "visible") in ("hidden", "veryHidden"),
            "target": rels_targets.get(rel_id, ""),
        })
    return sheets


def audit_sheet(sheet_xml):
    doc = parse_xml(sheet_xml)
    if doc is None:
        return {"cell_count": 0, "formula_count": 0}
    cells = doc.findall(f".//{X_NS}c")
    cell_count = len(cells)
    formula_count = sum(1 for c in cells if c.find(f"{X_NS}f") is not None)
    return {"cell_count": cell_count, "formula_count": formula_count}


def named_ranges(workbook_xml):
    wb = parse_xml(workbook_xml)
    if wb is None:
        return []
    return [
        {"name": dn.attrib.get("name", ""), "scope": dn.attrib.get("localSheetId", "global")}
        for dn in wb.findall(f"{X_NS}definedNames/{X_NS}definedName")
    ]


def external_links(files):
    """Count external link parts; capture targets where possible."""
    targets = []
    for name, blob in files.items():
        if name.startswith("xl/externalLinks/_rels/"):
            doc = parse_xml(blob)
            if doc is not None:
                for rel in doc:
                    target = rel.attrib.get("Target", "")
                    if target:
                        targets.append(target)
    return targets


def data_validation_count(sheet_xml):
    doc = parse_xml(sheet_xml)
    if doc is None:
        return 0
    return len(doc.findall(f".//{X_NS}dataValidation"))


def audit(path):
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Not a valid .xlsx file: {path}")
    with zipfile.ZipFile(path) as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    workbook_xml = files.get("xl/workbook.xml")
    if not workbook_xml:
        raise ValueError("Missing xl/workbook.xml — file may be corrupt")

    rels_xml = files.get("xl/_rels/workbook.xml.rels")
    sheets = list_sheets_from_workbook(workbook_xml, rels_xml)

    total_cells = 0
    total_formulas = 0
    total_validations = 0

    for sheet in sheets:
        target = sheet["target"]
        if not target:
            sheet.update({"cell_count": 0, "formula_count": 0, "formula_density_pct": 0, "validations": 0})
            continue
        target_norm = target.replace("../", "").replace("./", "")
        if target_norm.startswith("xl/"):
            blob = files.get(target_norm)
        else:
            blob = files.get(f"xl/{target_norm}")
        if not blob:
            sheet.update({"cell_count": 0, "formula_count": 0, "formula_density_pct": 0, "validations": 0})
            continue
        sheet_stats = audit_sheet(blob)
        cell_count = sheet_stats["cell_count"]
        formula_count = sheet_stats["formula_count"]
        validations = data_validation_count(blob)
        density = round(100 * formula_count / cell_count, 1) if cell_count else 0
        sheet.update({
            "cell_count": cell_count,
            "formula_count": formula_count,
            "formula_density_pct": density,
            "validations": validations,
        })
        total_cells += cell_count
        total_formulas += formula_count
        total_validations += validations

    return {
        "file": str(path),
        "size_kb": round(Path(path).stat().st_size / 1024, 1),
        "sheet_count": len(sheets),
        "hidden_sheet_count": sum(1 for s in sheets if s["hidden"]),
        "total_cells": total_cells,
        "total_formulas": total_formulas,
        "total_validations": total_validations,
        "named_ranges": named_ranges(workbook_xml),
        "external_links": external_links(files),
        "sheets": sheets,
    }


def render_human(result):
    lines = [f"Audit: {result['file']}"]
    lines.append("")
    lines.append(f"  Size:                  {result['size_kb']} KB")
    lines.append(f"  Sheets:                {result['sheet_count']} ({result['hidden_sheet_count']} hidden)")
    lines.append(f"  Total cells (non-empty):{result['total_cells']}")
    lines.append(f"  Total formulas:        {result['total_formulas']}")
    lines.append(f"  Data validations:      {result['total_validations']}")
    lines.append(f"  Named ranges:          {len(result['named_ranges'])}")
    lines.append(f"  External links:        {len(result['external_links'])}")
    lines.append("")
    if result["sheets"]:
        lines.append(f"{'Sheet':<32}{'Cells':>8}{'Formulas':>10}{'Density':>10}  Hidden")
        lines.append("-" * 70)
        for s in result["sheets"]:
            density = f"{s.get('formula_density_pct', 0)}%"
            hidden = "yes" if s["hidden"] else ""
            name = s["name"][:30]
            lines.append(f"{name:<32}{s.get('cell_count', 0):>8}{s.get('formula_count', 0):>10}{density:>10}  {hidden}")
    if result["external_links"]:
        lines.append("")
        lines.append("External links (review carefully):")
        for link in result["external_links"][:10]:
            lines.append(f"  • {link}")
    if result["named_ranges"]:
        lines.append("")
        lines.append(f"Named ranges (top 10 of {len(result['named_ranges'])}):")
        for nr in result["named_ranges"][:10]:
            lines.append(f"  • {nr['name']} (scope: {nr['scope']})")
    lines.append("")
    issues = []
    if result["hidden_sheet_count"] > 0:
        issues.append(f"{result['hidden_sheet_count']} hidden sheet(s)")
    if result["external_links"]:
        issues.append(f"{len(result['external_links'])} external link(s)")
    for link in result["external_links"]:
        if any(p in link.lower() for p in ["c:\\", "users\\", "/users/", ".local"]):
            issues.append("external link references a local path")
            break
    if issues:
        lines.append("Pre-handoff issues:")
        for i in issues:
            lines.append(f"  • {i}")
    else:
        lines.append("Pre-handoff issues: none detected.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit a .xlsx file (stdlib only).")
    parser.add_argument("xlsx", help="Path to .xlsx file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.xlsx)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        result = audit(path)
    except (ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
