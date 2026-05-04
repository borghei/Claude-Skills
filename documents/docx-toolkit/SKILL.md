---
name: docx-toolkit
description: >
  Audit Microsoft Word (.docx) documents for word count, heading hierarchy,
  comments, tracked changes, broken cross-references, and style consistency.
  Use when reviewing a contract draft, preparing a document for handoff,
  enforcing a style guide, or when the user mentions Word document review,
  docx audit, comment cleanup, or tracked-changes resolution.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: documents
  domain: document-automation
  updated: 2026-05-04
  python-tools: docx_auditor.py
  tech-stack: docx, OOXML
---

# Docx Toolkit

Audit `.docx` files using the standard library only — no `python-docx` required. Reads OOXML directly with `zipfile` + `xml.etree`.

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

docx, Word, Microsoft Word, document, document review, comments, tracked changes, redline, headings, style guide, word count, document audit

---

## Quick Start

```bash
python scripts/docx_auditor.py contract.docx
```

Outputs: word count, paragraph count, heading hierarchy, comment count, tracked-changes status, hyperlink count, list of unique paragraph styles used.

---

## Core Workflows

### Workflow 1: Pre-Handoff Document Audit

**Goal:** Catch the issues that embarrass a sender — leftover comments, unresolved track changes, broken heading hierarchy — before the document leaves.

**Steps:**
1. Run: `python scripts/docx_auditor.py document.docx`
2. Review the audit output:
   - Comment count > 0 → resolve or remove before sending
   - Tracked changes detected → accept or reject before sending
   - Heading-hierarchy gaps (H1 → H3 with no H2) → restructure
   - Style sprawl (more than 8 paragraph styles) → consolidate
3. Re-run until clean

**Time Estimate:** 5-15 minutes per document.

### Workflow 2: Contract Review Triage

**Goal:** Quantify how much rework a returned contract needs before reading it line-by-line.

**Steps:**
1. Run audit on the returned `.docx`
2. Comment count > 20 or tracked-change paragraphs > 30% → expect a heavy review pass; schedule time
3. Comment count < 5 → likely cosmetic; quick turnaround possible
4. Use `references/docx_review_checklist.md` for the actual content review

**Time Estimate:** 1 minute per document for triage.

### Workflow 3: Style-Guide Enforcement

**Goal:** Detect documents drifting from your style guide before they ship to a customer.

**Steps:**
1. Define allowed styles in your style guide (see `assets/style_compliance_template.md`)
2. Run audit on candidate documents
3. Flag any document using styles outside the allowed set
4. Map non-conforming paragraphs back to standard styles

**Time Estimate:** 2-5 minutes per document.

---

## Tools

### docx_auditor.py

Reads a `.docx` file as a ZIP archive and parses OOXML directly. No external dependencies.

```bash
# Human-readable
python scripts/docx_auditor.py document.docx

# JSON
python scripts/docx_auditor.py document.docx --json
```

**Reports:**
- Word and paragraph counts
- Heading hierarchy (with gap detection)
- Number of comments
- Whether tracked changes are present
- Unique paragraph styles used
- Hyperlink count
- Image count
- Table count

**Limits:** This tool reads existing docx files. For *generating* docx, use the templates in `assets/` and edit in Word, or install `python-docx` separately.

---

## Reference Guides

- **`references/docx_review_checklist.md`** — Pre-handoff checklist; common rework triggers; mistakes that survive automated audits

---

## Templates

- **`assets/style_compliance_template.md`** — Format for declaring allowed paragraph styles
- **`assets/handoff_checklist_template.md`** — Pre-send checklist with sign-off boxes

---

## Best Practices

- **Audit before every external send.** A 30-second audit catches 80% of avoidable embarrassment.
- **Resolve comments before "Final v3.docx".** Files named "final" with active comments are how lawyers get tickled.
- **Lock heading hierarchy.** H1 → H3 with no H2 breaks navigation, accessibility, and table-of-contents generation.
- **Prefer styles over inline formatting.** A style change in one place beats hundreds of inline overrides.

---

## Integration Points

- Pairs with `legal/` skills for contract redlines
- Pairs with `marketing/copywriting/` for content review
- Used by `c-level-advisor/board-deck-builder` for board-pack documents
