# Financial Model Audit Guide

Most financial models contain at least one error of the kind that survives spot-checks but matters for the decision. This guide describes how to audit a workbook in layers — structure first, then formulas, then values — and what to look for at each layer.

---

## Three-Layer Audit

### Layer 1 — Structure

Use the auditor's per-sheet output to characterize the model:

| Sheet density | Sheet purpose | Audit focus |
|---------------|---------------|-------------|
| 0-10% formulas | Inputs / assumptions | Are inputs labeled, range-validated, sourced? |
| 10-70% formulas | Mixed (working sheets, dashboards) | This is where errors hide — needs slowest read |
| > 70% formulas | Calculation engines | Should follow consistent column patterns |

A well-structured model has a **clear separation**: inputs → calculations → outputs. If any sheet does all three, slow down.

### Layer 2 — Formulas

The auditor counts formulas but doesn't evaluate them. For formula correctness:

- Sample 5-10 formulas across the densest calculation sheets
- Trace dependencies (Excel: Trace Precedents)
- Look for **inconsistent formulas across a row** — the most common error
- Check IF / SUMIF / VLOOKUP for hardcoded numbers buried inside (e.g., `IF(B2>500, …)`)
- Audit any cell with a number typed inside a formula — those are usually unmarked assumptions

### Layer 3 — Values

Sanity checks on outputs:

- Do totals reconcile? Sum of segments = total
- Period continuity: month-end of period N = month-start of period N+1
- Sign conventions: revenue positive, costs negative (or whichever convention the model uses, but **consistent**)
- Growth rate sanity: any line growing > 100% YoY without an explanation
- Currency consistency: every number in the same currency, or explicit conversion column

---

## Common Error Categories

| Error | How it happens | How to catch |
|-------|---------------|--------------|
| **Inconsistent formulas across a row** | Manual edit of one cell, copy-paste skipped a column | Visual scan; conditional formatting on `ISFORMULA` |
| **Hardcoded numbers in formulas** | Quick "fix" left in the model | Audit every formula containing a digit |
| **Broken absolute references** | Missing `$` in copy-down | Spot-check that copied formulas reference the right cells |
| **Circular references** | Two formulas reference each other | Excel warns, but iterative calc may suppress; check Calculation Options |
| **Wrong-period calculations** | Off-by-one when columns are months | Pick a random period and compute manually |
| **Stale named ranges** | Range moved but name kept the old reference | Audit each named range's reference |
| **Hidden assumption** | Number typed directly into a formula | Refactor to a labeled input cell |
| **Unit mismatch** | One sheet in thousands, another in millions | Label units in every sheet header |

---

## Defensive Model Structure

A model that resists errors over time:

1. **Cover sheet** — purpose, owner, version, last reviewed date.
2. **Inputs sheet** — all assumptions. Cells labeled. Sources linked.
3. **Outputs sheet** — final figures, charts.
4. **Calculation sheets** — one purpose per sheet (revenue, costs, balance sheet, cash flow).
5. **Named ranges for key inputs** — so cell moves don't break formulas.
6. **No mixed types in a column** — values vs. formulas should be visually distinct (color or named-style convention).
7. **No external file links** — embed values or use shared cloud-stored references.
8. **Versioning** — archive a copy on every meaningful change.

---

## Auditor-Specific Triage

After running the auditor:

1. **Hidden sheets > 0** — open and confirm intentional. Many models have leftover "scratch" sheets the original author meant to delete.
2. **External links > 0** — every external link is a future #REF error. Re-link to a shared source or hard-code values.
3. **Named ranges = 0 in a complex model** — the model is brittle to structural changes; consider adding ranges for key inputs.
4. **Named ranges with cryptic names** (`_xlnm`, `Range1`, `Sheet2!A1:B10` as the name) — usually cruft from copy-pasting; clean up.
5. **One sheet with > 10,000 cells** — consider whether it's doing too many things.

---

## Common External Link Sources

External links often look like one of these in an audit:

- `'C:\Users\name\Desktop\old-model.xlsx'!Range` → personal-laptop reference; will break on handoff
- `'\\server\share\models\source.xlsx'!Range` → corporate share; may break externally
- `'https://...sharepoint.com/...'!Range` → SharePoint live link; may work for some recipients only
- `'[other-workbook.xlsx]Sheet1'!A1` → relative link; depends on file co-location

For external handoff: **resolve all external links to embedded values or to a shared cloud source the recipient can access**.

---

## When to Stop Auditing

A model is "good enough" when:

- Auditor reports zero hidden sheets and zero external links you didn't expect
- Sample of 20 random formulas all pass spot-checks
- Top-line outputs reconcile to component sums
- An independent reviewer can re-derive the headline number from the inputs in under 30 minutes

If you cannot reach all four within reasonable effort, the model is too complex for the decision being made — simplify.
