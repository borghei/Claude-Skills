# Document Handoff Checklist

Sign off on this checklist before sending the `.docx` externally.

---

## Document Info

- **File:** [filename]
- **Audit run:** `python scripts/docx_auditor.py [filename]`
- **Recipient:** [name / org]
- **Sender:** [name]
- **Date:** [YYYY-MM-DD]

---

## Audit Sign-Off

Run the auditor and confirm each:

| Check | Audit reports | Pass? |
|-------|--------------|-------|
| Comments resolved | comment_count = 0 | [ ] |
| Tracked changes accepted/rejected | tracked_changes_present = false | [ ] |
| Heading hierarchy clean | heading_gaps = [] | [ ] |
| Style sprawl in check | styles_used count ≤ 8 | [ ] |
| Word count within target | [your spec] | [ ] |
| Image count expected | [your spec] | [ ] |

## Content Sign-Off

| Check | Pass? |
|-------|-------|
| All placeholders ([TBD], [TODO], names, dates) replaced | [ ] |
| Cross-references and TOC regenerated | [ ] |
| Pricing / numbers / dates correct for this deal | [ ] |
| Recipient name correct in salutation | [ ] |
| Confidentiality footer / watermark on every page | [ ] |
| Filename includes version, date, or both | [ ] |
| Document properties (author, company) scrubbed | [ ] |

## Reviewer Sign-Off

- [ ] Reviewer 1 (author): [name] · [date]
- [ ] Reviewer 2 (peer / lead): [name] · [date]
- [ ] Reviewer 3 (legal, if applicable): [name] · [date]

---

**Send only after all boxes are checked.**
