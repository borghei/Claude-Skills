# Docx Review Checklist

A pre-handoff checklist for any `.docx` going to a customer, partner, or counterparty. Run the auditor first, then walk this list.

---

## Mechanical (catchable by audit)

- [ ] Comment count = 0 (or all remaining comments are intentional and addressed to the recipient)
- [ ] No tracked changes pending — accept or reject before sending
- [ ] Heading hierarchy contiguous: no H1 → H3 jumps without H2
- [ ] Paragraph-style count under ~8 (style sprawl makes formatting fragile)
- [ ] Images load on open (no broken references)
- [ ] Hyperlinks point where intended (audit lists count; spot-check destinations)

## Content (not catchable by audit — requires reading)

- [ ] Document title in metadata matches the on-page title
- [ ] Headers/footers correct (date, version, footer disclaimers)
- [ ] All `[TBD]`, `[TODO]`, `[XXX]`, `[INSERT NAME]` placeholders removed
- [ ] All `Lorem ipsum` removed
- [ ] Cross-references (`see Section 4.2`) point to current section numbers
- [ ] Table of contents regenerated and matches actual headings
- [ ] Page numbering present and correct
- [ ] Footnotes resolved (no orphan `[1]` markers)

## Authorship

- [ ] Author metadata matches the sender (File → Properties)
- [ ] Last-modified-by no longer says "Bob's intern"
- [ ] Document properties scrubbed if the recipient should not see internal tracking

## Compliance and Legal

- [ ] Confidentiality marking on every page (footer or watermark)
- [ ] Document version in filename (`Contract-v3.docx`, not `Contract-final-final.docx`)
- [ ] Sensitive client names redacted if this is a template based on prior work
- [ ] Personally identifiable information removed unless required by purpose

## Common Rework Triggers

- "Track changes" left on by accident → next-recipient sees revision history they shouldn't
- Final version sent with internal-only commentary in footnotes
- TOC not regenerated → internal page references broken
- Same PDF exported from a docx with comments → leaks comments into the PDF metadata
- Author metadata reveals the document was originally for another client

## Mistakes That Survive Automated Audits

These tools cannot catch:

- Wrong recipient name in salutation
- Wrong jurisdiction in a contract clause
- Outdated pricing in a proposal
- Hardcoded dates that should reference the deal date
- Mathematical errors in tables
- Inconsistent terminology (the same concept named two different ways across the doc)

For these, a human read pass is the only check that works. Allow time for it.
