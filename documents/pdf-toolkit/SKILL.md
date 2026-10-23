---
name: pdf-toolkit
description: >
  Audit PDF files for metadata leakage, page count, encryption, JavaScript,
  embedded files, and version. Use before sending a PDF externally, when
  redacting sensitive metadata, or running a PDF security review.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: documents
  domain: document-automation
  updated: 2026-05-04
  python-tools: pdf_auditor.py
  tech-stack: pdf
  tags:
    - pdf
    - document-audit
    - metadata
    - redaction
    - security
---

# PDF Toolkit

Audit `.pdf` files for metadata, page count, encryption status, embedded JavaScript, embedded files, and PDF version — using the standard library only.

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

pdf, pdf audit, pdf metadata, pdf review, pdf leakage, pdf security, redaction, document handoff

---

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Audit purpose (pre-handoff metadata scrub, inbound security triage, or bulk outbound check):** selects which of the 3 workflows and which fields you act on.
- **Recipient / handling context (external party, managed laptop):** sets what counts as a leak or a threat worth quarantining.
- **Expected legitimate metadata (who the author/title should be):** without it you can't distinguish a leak from expected data.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python scripts/pdf_auditor.py contract.pdf
```

Outputs: PDF version, page count, file size, metadata (Author, Title, Producer, Creator, dates), encryption status, embedded JavaScript indicators, embedded file indicators.

---

## Core Workflows

### Workflow 1: Pre-Handoff PDF Metadata Audit

**Goal:** Stop leaking author identity, prior client names, or document history when handing a PDF to an external party.

**Steps:**
1. Run: `python scripts/pdf_auditor.py document.pdf`
2. Review metadata fields:
   - `Author` matches the sender (not "Bob's intern" from a prior project)
   - `Title` matches the document, not a leftover working title
   - `Producer` doesn't reveal an internal-only PDF tool
   - `CreationDate` and `ModDate` are reasonable for the deal
3. If metadata leaks, re-export from source with cleaned properties (or use a redaction tool)

**Time Estimate:** 2-3 minutes per document.

### Workflow 2: PDF Security Triage

**Goal:** Decide whether a received PDF can be opened safely on a managed laptop.

**Steps:**
1. Run audit
2. JavaScript indicator present → quarantine; review in a sandbox
3. Embedded files indicator present → list of file types; quarantine if unexpected
4. Encrypted with non-empty owner password → request password from sender via separate channel
5. Decision: open / quarantine / reject

**Time Estimate:** 1-2 minutes per inbound document.

### Workflow 3: Bulk Audit of an Outbound Document Set

**Goal:** Audit every PDF in a folder before zipping for a customer or partner.

**Steps:**
1. Loop: `for f in *.pdf; do python scripts/pdf_auditor.py "$f" --json; done > audit.jsonl`
2. Parse the JSON Lines for any metadata leakage or anomalies
3. Re-export problem files from source
4. Re-run audit until clean

**Time Estimate:** 1-2 minutes per file.

---

## Tools

### pdf_auditor.py

Reads a PDF using stdlib parsing — no `pypdf` or `pdfplumber` required. Detects:

- PDF version (from header)
- Page count (via `/Type /Page` object scan)
- File size
- Document Info / XMP metadata (Title, Author, Subject, Keywords, Producer, Creator, CreationDate, ModDate)
- Encryption status (`/Encrypt` reference present)
- JavaScript indicators (`/JS`, `/JavaScript`, `/AA` keys)
- Embedded files indicator (`/EmbeddedFiles`)

```bash
python scripts/pdf_auditor.py document.pdf
python scripts/pdf_auditor.py document.pdf --json
```

**Limits:**
- Does **not** extract text content — pure PDF text extraction with stdlib is unreliable. For text extraction install `pdfplumber` or `pypdf` separately.
- Cannot decrypt encrypted files.
- Detects only the presence of JavaScript/embedded files, not their behavior.

---

## Reference Guides

- **`references/pdf_handoff_guide.md`** — What to scrub from PDFs before external send; PDF/A and PDF/UA basics; common leakage patterns

---

## Templates

- **`assets/pdf_handoff_checklist.md`** — Pre-send PDF sign-off checklist

---

## Best Practices

- **Re-export rather than redact.** Redaction tools that "remove" content can leave it recoverable. The safest path is regenerating the PDF from the source document with sensitive fields removed.
- **Scrub document properties at the source.** In Word: File → Inspect Document → Document Inspector. In Pages: File → Properties. Then export to PDF.
- **Don't trust filenames.** A file named `Public-Report.pdf` can carry private metadata indistinguishable to the human eye.
- **Use PDF/A for archival.** PDF/A removes JavaScript and external dependencies, making documents safe for long-term archive.

---

## Scope & Limitations

**In Scope:**
- Read-only audit of `.pdf` files with `scripts/pdf_auditor.py`, using standard-library parsing with no `pypdf` or `pdfplumber`
- PDF version, page count, file size, Info dictionary and XMP metadata, encryption status, and JavaScript and embedded-file indicators
- Three workflows: pre-handoff metadata audit, inbound security triage, and bulk audit of an outbound set with JSON output
- A handoff guide covering leakage patterns, re-export versus redaction, and PDF/A and PDF/UA basics

**Out of Scope:**
- Extracting text or tables from a PDF
- Decrypting, editing, redacting or re-exporting PDFs; fixes happen in the source document
- Analysing whether embedded JavaScript or attachments are malicious; that needs a sandbox
- Producing PDFs or HTML documents (see `markdown-html/md-document/`)

**Important Caveats:**
- The auditor scans the raw file bytes with pattern matching and does not decompress streams. Page counts, metadata and indicators stored inside compressed object streams can be missed, so a clean result is not proof that nothing is there.
- A JavaScript or embedded-file indicator means the marker is present, not that the file is harmful.
- Checks such as an "unscrubbed" author or a working-title title are heuristics. Only you know which metadata values are expected for this document.

---

## Integration Points

- Pairs with `legal/` for redacted contract handoffs
- Pairs with `c-level-advisor/board-deck-builder` for board pack handoff
- Used by `marketing/` for whitepaper / case-study handoff
