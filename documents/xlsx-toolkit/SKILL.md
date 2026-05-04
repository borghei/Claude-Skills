---
name: xlsx-toolkit
description: >
  Audit Microsoft Excel (.xlsx) workbooks for sheet count, cell count, formula
  density, external references, named ranges, hidden sheets, and data
  validation rules. Use when reviewing a financial model, sharing a workbook
  externally, or when the user mentions xlsx audit, spreadsheet review,
  formula audit, or workbook leakage check.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: documents
  domain: document-automation
  updated: 2026-05-04
  python-tools: xlsx_auditor.py
  tech-stack: xlsx, OOXML
---

# Xlsx Toolkit

Audit `.xlsx` files using the standard library only — no `openpyxl` required. Reads OOXML directly via `zipfile` + `xml.etree`.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## Keywords

xlsx, Excel, spreadsheet, workbook, financial model, formula audit, hidden sheets, external references, named ranges, data validation

---

## Quick Start

```bash
python scripts/xlsx_auditor.py model.xlsx
```

Outputs: sheet count and names, hidden-sheet count, cell count per sheet, formula count per sheet, external link count, named range count, data validation rule count.

---

## Core Workflows

### Workflow 1: Pre-Send Workbook Audit

**Goal:** Catch the issues that embarrass the sender — leftover hidden sheets, broken external links, unused named ranges, formulas referencing local file paths.

**Steps:**
1. Run audit
2. Hidden sheets > 0 → confirm intentional or delete
3. External links > 0 → verify links point to public / shared sources, not your local drive
4. Named-range count anomalies (very high) → likely cruft from prior model versions; clean up
5. Re-run until clean

**Time Estimate:** 5-10 minutes per workbook.

### Workflow 2: Financial Model Review

**Goal:** Quantify the rough complexity of a financial model before reading cell-by-cell.

**Steps:**
1. Run audit; capture per-sheet cell counts and formula counts
2. Sheets with formula density > 70% are calculation sheets; should be well-structured
3. Sheets with formula density 0-10% are inputs; should be obviously labeled
4. Sheets with formula density 10-70% are mixed — easiest place for errors to hide
5. Cross-reference with `references/financial_model_audit_guide.md`

**Time Estimate:** 30-60 minutes per model audit (audit + targeted reading).

### Workflow 3: Workbook Handoff Check

**Goal:** Ensure a workbook handed off to another team or partner won't break on their machine.

**Steps:**
1. Run audit
2. External links → re-link to shared paths (OneDrive, SharePoint, S3) or hard-code values
3. Custom named ranges → document if recipient is expected to extend; remove if internal
4. Macros (xlsm) → audit shows non-`.xlsx` extension expected; convert if recipient cannot run macros
5. File size > 10 MB → consider splitting or removing image / chart blobs

**Time Estimate:** 10-20 minutes per workbook.

---

## Tools

### xlsx_auditor.py

Reads a `.xlsx` file as a ZIP archive and parses OOXML directly.

```bash
python scripts/xlsx_auditor.py model.xlsx
python scripts/xlsx_auditor.py model.xlsx --json
```

**Reports:**
- Sheet list with name, hidden status, cell count, formula count, formula density %
- Total cell and formula counts
- Named ranges and their scopes
- External link references (file paths or URLs)
- Data validation rule count
- File size

**Limits:**
- Does **not** evaluate formulas. To check whether formulas are *correct*, use Excel itself or a financial-model-checker library.
- Does **not** read cell values for non-shared-string cells beyond counting; full value extraction requires more parsing than this tool does.

---

## Reference Guides

- **`references/financial_model_audit_guide.md`** — Patterns for auditing financial models; common error categories; defensive structure tips

---

## Templates

- **`assets/workbook_handoff_checklist.md`** — Pre-send xlsx sign-off checklist

---

## Best Practices

- **Hide internal-only sheets only when intended.** If a sheet is hidden because it's WIP, delete it before sending.
- **Avoid external links across handoffs.** A formula referencing `'C:\Users\you\Desktop\old-model.xlsx'` is the workbook equivalent of leaving your laptop name in the document author field.
- **Name your inputs.** Cells like `Inputs!B7` mean nothing. Named ranges like `WACC` and `RevenueGrowth` survive structural changes.
- **One model, one purpose.** Workbooks that calculate, present, and serve as a database of records always end up broken.

---

## Integration Points

- Pairs with `finance/` skills for financial-model review
- Pairs with `c-level-advisor/cfo-advisor` for board-pack workbook review
- Used by `data-analytics/` for ad-hoc analytics handoff
