# Workbook Handoff Checklist

Sign off before sending an `.xlsx` workbook externally.

---

## Document Info

- **File:** [filename]
- **Audit run:** `python scripts/xlsx_auditor.py [filename]`
- **Workbook purpose:** [model / dashboard / data export / template]
- **Recipient:** [name / org]
- **Sender:** [name]
- **Date:** [YYYY-MM-DD]

---

## Audit Output Sign-Off

| Check | Audit reports | Pass? |
|-------|--------------|-------|
| No leftover hidden sheets | `hidden_sheet_count = 0` | [ ] |
| External links absent or to public sources | `external_links` reviewed | [ ] |
| External links never reference a local path (C:\, /Users/, etc.) | manual review of `external_links` | [ ] |
| Named ranges all intentional and named meaningfully | `named_ranges` reviewed | [ ] |
| Sheet count matches expectation | `sheet_count` | [ ] |
| File size reasonable | `size_kb` | [ ] |
| Total formula count plausible for model purpose | `total_formulas` | [ ] |

## Content Sign-Off

- [ ] Cover / instructions sheet present (recipient knows where to start)
- [ ] Input cells labeled and visually distinct from calculations
- [ ] Output cells labeled and clearly the "answer"
- [ ] All numbers have units stated in their header or label
- [ ] Currency consistent or explicit conversion present
- [ ] No `[TBD]`, `[TODO]`, or placeholder text in any cell
- [ ] No customer-private data left from a prior version (filter by old client name)

## Distribution Format

- [ ] Recipient can open `.xlsx` (vs. needing `.csv`, Google Sheets, or a CSV export)
- [ ] No macros required for read-only review (if macros: send as `.xlsm` and warn recipient)
- [ ] Charts render correctly when opened on a fresh machine
- [ ] Data ranges within charts reference visible sheets, not deleted ones
- [ ] Filename versioned: `[purpose]-[date]-v[n].xlsx`

## Reviewer Sign-Off

- [ ] Reviewer 1 (author): [name] · [date]
- [ ] Reviewer 2 (peer / lead): [name] · [date]
- [ ] Reviewer 3 (finance / compliance, if applicable): [name] · [date]

---

**Send only after all boxes are checked.**
