---
name: invoice-organizer
description: >
  Categorize invoices and receipts by vendor, expense, and tax bucket, detect
  duplicates, and produce a tax-ready monthly summary. Use during bookkeeping,
  tax prep, or expense reimbursement.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: bookkeeping
  updated: 2026-05-04
  python-tools: invoice_categorizer.py
  tech-stack: bookkeeping, tax
  tags:
    - invoices
    - receipts
    - bookkeeping
    - tax-prep
    - expenses
---

# Invoice Organizer

Bulk-categorize a CSV of invoices or receipts, detect duplicates, and produce a tax-ready monthly summary.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)
- [Scope & Limitations](#scope--limitations)

---

## Keywords

invoice, invoices, receipt, receipts, expense, expenses, bookkeeping, accounting, tax, tax prep, categorization, vendor, reimbursement, monthly summary

---

## Clarify First

Before categorizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Receipt CSV fields:** date, vendor, description, amount drive categorization and duplicate detection.
- **Tax bucket scheme:** US Schedule C vs UK self-employment vs generic sets which categories the summary maps to.
- **Recurring-vendor rules:** known vendor→category mappings to seed `category_rules.json` and cut the uncategorized bucket.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

### Categorize 200 Receipts in 1 Minute

1. Export receipts from your bank or expense tool as a CSV with columns: `date,vendor,description,amount`, all in one currency (convert any foreign-currency rows first)
2. Run:
   ```bash
   python scripts/invoice_categorizer.py receipts.csv
   ```
3. Review the categorized output and override anything wrong via the rules file
4. Export the monthly summary for handoff to your accountant

---

## Core Workflows

### Workflow 1: Monthly Bookkeeping

**Goal:** Convert a month of unstructured receipts into a categorized, tax-ready summary in under 10 minutes.

**Steps:**
1. Export receipts as CSV from your bank, card, or expense tool
2. Run: `python scripts/invoice_categorizer.py receipts.csv`
3. Review the **uncategorized** bucket — these need rules added or manual override
4. Add rules to `assets/category_rules.json` for any recurring vendors
5. Re-run; uncategorized count should drop each month as the rules file grows
6. Drop the monthly summary into `assets/monthly_summary_template.md`

**Expected Output:** Categorized expense list + monthly totals by category + duplicate-suspect list.

**Time Estimate:** 10 minutes/month after initial rules are seeded.

### Workflow 2: Duplicate Detection

**Goal:** Catch double-entered receipts before they reach the books.

**Steps:**
1. Run: `python scripts/invoice_categorizer.py receipts.csv --json`
2. Inspect the `duplicates_suspected` list
3. Confirm whether each is a true duplicate (same charge entered twice) or a coincidence (same amount on different days at different vendors)
4. Remove confirmed duplicates from the source CSV; re-run

**Expected Output:** Cleaned CSV with no duplicate rows.

**Time Estimate:** 2-3 minutes per month.

### Workflow 3: Vendor Spend Review

**Goal:** Find spend creep — vendors whose monthly total grew significantly without you noticing.

**Steps:**
1. Run categorizer for the last 3-6 months separately
2. Compare per-vendor totals month-over-month
3. Flag any vendor where total grew > 25% with no obvious business reason
4. Either renegotiate, switch, or accept; revisit quarterly

**Expected Output:** Vendor-spend trend list with flagged growth.

**Time Estimate:** 15 minutes per quarter.

---

## Tools

### invoice_categorizer.py

Reads a CSV of receipts/invoices and:

- **Categorizes** each row by vendor + description against rules in `assets/category_rules.json` (extensible)
- **Aggregates** totals per category and per vendor
- **Detects** likely duplicates (same vendor + amount within 3 days)
- **Flags** uncategorized items for manual review

```bash
# Human-readable summary
python scripts/invoice_categorizer.py receipts.csv

# JSON for programmatic use
python scripts/invoice_categorizer.py receipts.csv --json

# Use a custom rules file
python scripts/invoice_categorizer.py receipts.csv --rules my-rules.json
```

**Expected CSV columns:** `date, vendor, description, amount`. Amounts are treated as one currency. A `currency` column is allowed but ignored: it is not read, shown in the output, or used to convert.
**Date formats accepted:** `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`

---

## Reference Guides

- **`references/expense_categorization_guide.md`** — Standard expense categories, common tax buckets (US Schedule C, UK self-employment, generic), how to map vendors to categories

---

## Templates

- **`assets/category_rules.json`** — Default rules; extend with your recurring vendors
- **`assets/monthly_summary_template.md`** — Format for handing the monthly summary to an accountant

---

## Best Practices

- **Categorize monthly, not annually.** Annual catch-up bookkeeping always misses receipts and produces guess-categorization.
- **Grow the rules file over time.** First month: 30% uncategorized. Sixth month: < 5%. The compounding return on rule-writing is high.
- **Keep evidence.** Categorization is bookkeeping; receipts (PDFs, photos) are tax evidence. Store separately from this script's output.
- **Don't trust auto-categorization for tax filing.** Use it for prep; have a human (you or your accountant) sign off before filing.
- **Currency consistency.** The script sums every amount as if it were one currency. If you have multi-currency receipts, convert them at the month-end FX rate before the run; it does not handle FX.

---

## Scope & Limitations

**In Scope:**
- Categorization of a receipts CSV by vendor and description against rules in `assets/category_rules.json` or a custom `--rules` file (`invoice_categorizer.py`).
- Totals per category and per vendor, and an uncategorized list for manual review.
- Duplicate suspects, defined as the same vendor and amount within 3 days.
- Expense categories mapped to tax buckets (US Schedule C by default, UK self-employment and generic) in `references/expense_categorization_guide.md`, plus a monthly summary template.

**Out of Scope:**
- Reading bank feeds, accounting software, or receipt PDFs and photos. Input is an exported CSV.
- Currency conversion. Multi-currency receipts are converted before the run.
- Tax filing, deductibility decisions, and VAT or sales-tax returns.
- Budgeting, forecasting and variance analysis (see `finance/financial-analyst/`), and SaaS seat and renewal savings (see `business-operations/procurement-optimizer/`).

**Important Caveats:**
- The output is not tax, accounting or legal advice. Bucket assignments need sign-off from the user or a licensed accountant before filing.
- Categorization is rule-based matching. New vendors land in the uncategorized bucket until rules are added.
- Duplicate detection is a heuristic. Flagged pairs can be legitimate repeat charges, and duplicates more than 3 days apart are not flagged.
- Tax line numbers and rules change by year and jurisdiction, so the reference mapping can go stale.

---

## Integration Points

- Pairs with `finance/` skills for budgeting and forecasting
- Feeds into `c-level-advisor/cfo-advisor` cash-flow workflows
- Used by solo-founder persona for monthly close
