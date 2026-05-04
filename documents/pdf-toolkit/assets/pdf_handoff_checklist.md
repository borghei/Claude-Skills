# PDF Handoff Checklist

Sign off before sending a PDF externally.

---

## Document Info

- **File:** [filename]
- **Audit run:** `python scripts/pdf_auditor.py [filename]`
- **Recipient:** [name / org]
- **Sender:** [name]
- **Date:** [YYYY-MM-DD]

---

## Audit Output Sign-Off

| Check | Audit reports | Pass? |
|-------|--------------|-------|
| Author metadata is sender (not "intern", not prior client) | `info_dictionary.Author` | [ ] |
| Title is the real title | `info_dictionary.Title` | [ ] |
| Producer is acceptable for external view | `info_dictionary.Producer` | [ ] |
| No JavaScript | `javascript_present = false` | [ ] |
| No additional actions | `additional_actions_present = false` | [ ] |
| No unintended embedded files | `embedded_files_present = false` | [ ] |
| Encryption is intentional or absent | `encrypted` = expected | [ ] |
| Page count matches expectation | `page_count` | [ ] |
| File size reasonable | `size_kb` | [ ] |

## Source Document Sign-Off

- [ ] Source document properties scrubbed before export (Word/Pages → File → Properties)
- [ ] Re-exported through the cleanest available PDF path (avoid third-party PDF-from-anything)
- [ ] PDF/A used for archival documents
- [ ] PDF/UA used for accessibility-mandatory documents

## Naming and Footer

- [ ] Filename includes version, date, or both — not "Final-final-v3.pdf"
- [ ] Confidentiality footer / watermark present where required
- [ ] Page numbers correct

## Reviewer Sign-Off

- [ ] Reviewer 1 (author): [name] · [date]
- [ ] Reviewer 2 (peer / lead): [name] · [date]

---

**Send only after all boxes are checked.**
