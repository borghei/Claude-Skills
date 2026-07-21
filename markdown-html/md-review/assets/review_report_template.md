# Markdown pre-publication review — {{DOCUMENT_TITLE}}

**File:** `{{FILE_PATH}}`
**Reviewed:** {{REVIEW_DATE}}
**Reviewer:** {{REVIEWER}}
**Config profile:** `{{CONFIG_PROFILE}}`
**Gate result:** {{PASS_OR_FAIL}} (fail-on: `{{FAIL_ON_LEVEL}}`)

---

## 1. Verdict

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| Errors | {{ERROR_COUNT}} | 0 | {{ERROR_STATUS}} |
| Warnings | {{WARNING_COUNT}} | {{MAX_WARNINGS}} | {{WARNING_STATUS}} |
| Info | {{INFO_COUNT}} | — | — |
| Broken internal links | {{BROKEN_LINK_COUNT}} | 0 | {{LINK_STATUS}} |
| Flesch Reading Ease | {{FLESCH}} | {{FLESCH_BAND}} | {{FLESCH_STATUS}} |
| Flesch-Kincaid grade | {{FK_GRADE}} | ≤ {{MAX_GRADE}} | {{FK_STATUS}} |

**One-line call:** {{VERDICT_SENTENCE}}

---

## 2. Blocking findings (errors)

Every item here must be fixed before publication.

| ID | Rule | Line | Finding | Fix |
| --- | --- | --- | --- | --- |
| E1 | {{RULE_ID}} | {{LINE}} | {{MESSAGE}} | {{SUGGESTED_FIX}} |
| E2 | | | | |

---

## 3. Non-blocking findings (warnings)

Fix before the next content review cycle.

| ID | Rule | Line | Finding | Owner |
| --- | --- | --- | --- | --- |
| W1 | {{RULE_ID}} | {{LINE}} | {{MESSAGE}} | {{OWNER}} |
| W2 | | | | |

---

## 4. Structure

- **Heading tree depth:** {{MAX_DEPTH}} (limit {{DEPTH_LIMIT}})
- **H1 count:** {{H1_COUNT}} (must be 1)
- **Skipped levels:** {{SKIPPED_LEVELS}}
- **Longest section:** `{{LONGEST_SECTION}}` at {{LONGEST_SECTION_WORDS}} words
- **Heading capitalization style detected:** {{HEADING_CASE}} ({{HEADING_CASE_CONSISTENCY}}% consistent)

Outline as parsed:

```
{{HEADING_OUTLINE}}
```

---

## 5. Links

**Resolved on disk. No network requests were made.**

| Target | Type | Status | Line |
| --- | --- | --- | --- |
| {{LINK_TARGET}} | relative-file / anchor / external | ok / broken / not-checked | {{LINE}} |

**External link inventory ({{EXTERNAL_COUNT}} links, unverified):**

| URL | Occurrences | Host |
| --- | --- | --- |
| {{URL}} | {{COUNT}} | {{HOST}} |

External links are inventoried, never fetched. Verify them manually or with a
separate network-enabled job that runs outside the publication gate.

---

## 6. Readability

| Measure | Value | Target band | Reading |
| --- | --- | --- | --- |
| Flesch Reading Ease | {{FLESCH}} | {{FLESCH_BAND}} | {{FLESCH_READING}} |
| Flesch-Kincaid grade | {{FK_GRADE}} | {{FK_BAND}} | {{FK_READING}} |
| Sentences | {{SENTENCE_COUNT}} | — | — |
| Mean sentence length | {{MEAN_SENTENCE_WORDS}} words | ≤ 20 | {{MSL_STATUS}} |
| Long sentences (> {{LONG_LIMIT}} words) | {{LONG_COUNT}} ({{LONG_PCT}}%) | ≤ {{MAX_LONG_PCT}}% | {{LONG_STATUS}} |
| Passive constructions | {{PASSIVE_COUNT}} ({{PASSIVE_PCT}}%) | ≤ {{MAX_PASSIVE_PCT}}% | {{PASSIVE_STATUS}} |

**Worst sentences to rewrite first:**

1. Line {{LINE}} ({{WORDS}} words): "{{SENTENCE_EXCERPT}}"
2.
3.

---

## 7. Accessibility

| Check | WCAG SC | Result |
| --- | --- | --- |
| Images have meaningful alt text | 1.1.1 Non-text Content (A) | {{ALT_RESULT}} |
| Heading levels not skipped | 1.3.1 Info and Relationships (A) | {{HEADING_RESULT}} |
| Tables have header rows | 1.3.1 Info and Relationships (A) | {{TABLE_RESULT}} |
| Link text is descriptive out of context | 2.4.4 Link Purpose (A) / 2.4.9 (AAA) | {{LINK_TEXT_RESULT}} |
| Document has one descriptive top heading | 2.4.6 Headings and Labels (AA) | {{H1_RESULT}} |
| Language declared in frontmatter | 3.1.1 Language of Page (A) | {{LANG_RESULT}} |

---

## 8. Terminology and style

| Found | Preferred | Occurrences | Lines |
| --- | --- | --- | --- |
| {{FOUND_TERM}} | {{PREFERRED_TERM}} | {{COUNT}} | {{LINES}} |

---

## 9. Decision

- [ ] **Publish** — no errors, warnings accepted by owner
- [ ] **Publish with follow-up** — warnings tracked in {{TICKET}}
- [ ] **Hold** — blocking findings remain

**Signed off by:** {{APPROVER}}
**Date:** {{DATE}}

---

## Appendix — reproduce this report

```bash
python3 markdown-html/md-review/scripts/md_review_gate.py \
  --input {{FILE_PATH}} \
  --config markdown-html/md-review/assets/sample_review_config.json \
  --format text

python3 markdown-html/md-review/scripts/link_checker.py \
  --input {{FILE_PATH}} --format text

python3 markdown-html/md-review/scripts/readability_scorer.py \
  --input {{FILE_PATH}} \
  --config markdown-html/md-review/assets/sample_review_config.json \
  --format text
```
