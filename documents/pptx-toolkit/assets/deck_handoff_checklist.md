# Deck Handoff Checklist

For board, investor, sales, and conference decks before sending or presenting.

---

## Document Info

- **File:** [filename]
- **Audit run:** `python scripts/pptx_auditor.py [filename]`
- **Deck purpose:** [conference talk / investor pitch / board / sales / internal review / training]
- **Recipient or audience:** [name / org / event]
- **Sender:** [name]
- **Date:** [YYYY-MM-DD]

---

## Audit Output Sign-Off

| Check | Audit reports | Pass for this deck purpose? |
|-------|--------------|----------------------------|
| Slide count appropriate for time budget | `slide_count` | [ ] |
| No leftover hidden slides | `hidden_slide_count = 0` | [ ] |
| Speaker-notes coverage adequate | `notes_coverage_pct` ≥ target | [ ] |
| Words-per-slide max within target | `words_per_slide_max` ≤ rubric target | [ ] |
| Animation count within target | `animations_total` ≤ 100 | [ ] |
| Brand theme applied | `theme` matches brand template | [ ] |
| Embedded media plays | manual check | [ ] |

## Content Sign-Off

- [ ] Title slide carries correct deck title, presenter name(s), and date
- [ ] Confidentiality marking on appropriate slides (footer or title)
- [ ] Pricing / numbers / claims dated and current
- [ ] Customer logos used with permission
- [ ] No leftover [TBD], [TODO], or placeholder text
- [ ] Charts and tables sourced; sources cited

## Distribution Format

For decks that get forwarded or stored:

- [ ] PDF export tested — animations render acceptably
- [ ] PDF metadata audited (run `pdf-toolkit/scripts/pdf_auditor.py`)
- [ ] Filename versioned: `[deck-purpose]-[date]-v[n].pptx`

## Reviewer Sign-Off

- [ ] Reviewer 1 (author): [name] · [date]
- [ ] Reviewer 2 (peer / lead): [name] · [date]
- [ ] Reviewer 3 (legal / compliance, if applicable): [name] · [date]

---

**Send only after all boxes are checked.**
