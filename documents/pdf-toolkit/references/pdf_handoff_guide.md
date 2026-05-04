# PDF Handoff Guide

PDFs are *not* opaque. Most PDFs carry searchable metadata, embedded thumbnails, layered author identifiers, and sometimes JavaScript or attached files. This guide covers what to scrub before sending a PDF outside your org, and what to verify when receiving one.

---

## What Leaks From a PDF You Send

| Surface | What it can reveal | How to scrub |
|---------|--------------------|--------------|
| `Author` (Info dict) | Original document author or laptop owner | Re-export from source; clean Word/Pages document properties first |
| `Title` (Info dict) | Working titles like "DRAFT 3 - Acme Pricing" | Set explicit Title in source; or use export "Properties" dialog |
| `Producer` / `Creator` | Internal toolchain ("Confluence", "Notion Export") | Re-export through a generic PDF printer |
| `CreationDate` / `ModDate` | Implies how long you sat on it | Cannot fully scrub; expect this to be visible |
| Embedded thumbnails | Earlier-page layouts, prior versions | Disable thumbnail generation in source |
| Embedded fonts subset names | Sometimes reveal source platform | Largely unavoidable |
| Embedded files (`/EmbeddedFiles`) | Excel sheets, source documents | Don't attach unless intended |
| Attached forms / scripts | JavaScript can phone home or fingerprint | Avoid in outbound business documents |

## What to Audit on a PDF You Receive

| Indicator | Concern |
|-----------|---------|
| JavaScript present (`/JS`, `/JavaScript`) | Could attempt network call, fingerprint, or trigger on open |
| `/AA` (Additional Actions) | Auto-runs on open / page change / form events |
| Embedded files | Could carry malware or unintended documents |
| Encrypted with non-trivial owner password | Sender may have intended recipient-only viewing — handle accordingly |
| Producer = unfamiliar tool | Worth a quick search to verify legitimacy |

---

## Re-Export vs. Redact

The safest scrub is **regenerate the PDF from a clean source document**. Tools that claim to "remove" PDF metadata often leave traces:

- Removing the `/Info` dictionary doesn't always remove XMP metadata.
- Object streams sometimes carry the same fields in multiple locations.
- "Save as Optimized PDF" varies by tool — some preserve metadata.

If you must work with a PDF directly:
1. Confirm scrub success by re-running the auditor.
2. Check for both `/Info` and XMP entries (the auditor reports both).
3. Open the scrubbed PDF in a different viewer (e.g., Preview vs. Adobe) and re-check Properties.

---

## PDF/A and PDF/UA

For documents intended to last:

- **PDF/A** — Archival format. Self-contained (embedded fonts, no external references), no JavaScript, no encryption.
- **PDF/UA** — Accessibility format. Properly tagged structure for screen readers, alt text on images, reading order specified.

Both are conformance levels of regular PDF — exporting "as PDF/A-2b" from Word, Pages, or LibreOffice is straightforward. Use PDF/A for any document that needs to be readable in 10 years.

---

## Common Leakage Patterns

- **The Confluence-export giveaway.** A PDF "Producer" of "Confluence" tells the recipient you exported from your wiki; sometimes that reveals what tools you use internally.
- **The "DRAFT 1, 2, 3" working title.** The Title field carries the working name forever, even if the on-page title is clean.
- **The intern's laptop.** Author metadata can survive multiple Save-As operations if not explicitly re-set.
- **The other client's name.** Templates reused across clients sometimes carry the prior client name in metadata.

---

## Quick Pre-Send Routine

```bash
# Audit
python scripts/pdf_auditor.py outbound.pdf

# Check the Info dictionary
# - Author = your name (or your company)?
# - Title = the actual document title?
# - Producer = generic / acceptable?
# - JavaScript = no?
# - Embedded files = no?
# If any answer is "wrong", re-export from source with cleaned properties.
```

---

## What This Toolkit Does Not Do

- **Decrypt encrypted PDFs** — design choice; respect the encryption.
- **Extract text reliably** — PDF text extraction is genuinely hard with stdlib. Use `pdfplumber` or `pypdf` for that.
- **Modify PDFs** — read-only by design. Modify by re-exporting from the source document.
- **Detect malicious JavaScript** — only flags presence. A real PDF malware sandbox is a separate tool.
