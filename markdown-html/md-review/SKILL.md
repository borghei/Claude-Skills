---
name: md-review
description: >
  Pre-publication quality gate for authored Markdown — heading structure, on-disk link
  resolution, readability, accessibility, terminology. Use when reviewing docs before
  publishing, wiring a docs CI gate, or auditing a Markdown corpus.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: markdown-html
  domain: markdown-review
  updated: 2026-07-21
  tags: [markdown, review, accessibility, readability, ci-gate, wcag, documentation]
---

# Markdown Review Gate

The quality gate that runs *before* Markdown becomes HTML. A converter will happily render a
document with three H1s, four dead links, an image with no alt text, and a 67-word sentence — the
HTML validates and the page is still bad. This skill catches those defects while they are still
cheap to fix, and fails the build when they are blocking.

**Zero network calls, by design.** Relative links and anchors resolve on disk; external URLs are
inventoried and reported but never fetched. A gate that fails because someone else's server was
slow is a gate engineers learn to ignore.

## When to use this skill

- **Before publishing** a doc, guide, or article that will be converted to HTML
- **Wiring a docs CI gate** that must block a merge on real defects without blocking on style
- **Auditing an inherited Markdown corpus** to size the accessibility and link-rot backlog
- **Enforcing house terminology** across a docs set (`front-end` vs `frontend`, `GitHub` vs `Github`)
- **Checking accessibility of source content** against the WCAG criteria that survive conversion
- **Calibrating prose to an audience** — a runbook read at 3am needs a different band than an API reference

## Inputs the skill expects

- One or more Markdown files (with or without YAML frontmatter)
- A review config JSON: required frontmatter fields, structure and accessibility thresholds, term map, gate settings
- The target audience for the prose (drives the readability band — the single most consequential input)
- The project root, when the corpus uses root-relative (`/docs/...`) links
- The blocking policy: which severity fails the build, and the warning budget

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target audience for the prose** — why it changes the output: selects the Flesch band and grade ceiling; a general-public band (60-80) and a specialist band (40-60) flag opposite sets of sentences
- [ ] **Required frontmatter fields** — why it changes the output: every missing field is an error, so guessing the schema produces either false blockers or a silent gap
- [ ] **Blocking severity and warning budget** — why it changes the output: decides whether the run reports or blocks, which determines whether this is an audit or a gate
- [ ] **Whether the corpus is new or inherited** — why it changes the output: an inherited corpus needs report-only phase 1, not a gate that fails on day one

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Gate a document before publication

The default path. Run all three tools; any non-zero exit blocks.

1. Pick or write a config profile (start from `assets/sample_review_config.json`).
2. Run the structure/frontmatter/accessibility gate.
3. Run the offline link checker.
4. Run the readability and terminology scorer.
5. Fix errors; triage warnings against the budget.

```bash
cd "$(git rev-parse --show-toplevel)"
CFG=markdown-html/md-review/assets/sample_review_config.json
DOC=markdown-html/md-review/assets/sample_article.md

python3 markdown-html/md-review/scripts/md_review_gate.py --input "$DOC" --config "$CFG" --format text
python3 markdown-html/md-review/scripts/link_checker.py --input "$DOC" --root "$PWD" --format text
python3 markdown-html/md-review/scripts/readability_scorer.py --input "$DOC" --config "$CFG" --format text
```

The shipped `sample_article.md` deliberately contains real defects, so this run exits non-zero.
Swap in `sample_article_clean.md` to see all three pass.

### Workflow 2 — Audit a corpus without blocking anything

Phase 1 of any rollout. Collect the real finding distribution before deciding what to enforce.

1. Run every file with `--fail-on never` so nothing exits non-zero.
2. Emit JSON and append to a single JSONL stream.
3. Rank rules by frequency; tune thresholds and the term map before switching the gate on.

```bash
cd "$(git rev-parse --show-toplevel)"
CFG=markdown-html/md-review/assets/sample_review_config.json

find markdown-html/md-review/assets -name '*.md' -print0 |
  xargs -0 -I{} python3 markdown-html/md-review/scripts/md_review_gate.py \
    --input {} --config "$CFG" --format json --fail-on never > /tmp/md_audit.jsonl

python3 -c "import json;[print(f['rule']) for l in open('/tmp/md_audit.jsonl') if l.strip().startswith('{')]" 2>/dev/null || \
  echo "inspect /tmp/md_audit.jsonl for the per-file finding arrays"
```

### Workflow 3 — Calibrate prose to an audience

When the complaint is "nobody reads our docs" rather than "our docs are broken".

1. Score the document and read the sentence-level findings, not just the aggregate.
2. Rewrite the very-long sentences first — they dominate the score and the reader's experience.
3. Re-score and confirm the long-sentence percentage is under 10%.

```bash
cd "$(git rev-parse --show-toplevel)"
CFG=markdown-html/md-review/assets/sample_review_config.json

# Full report, including passive-voice and terminology findings
python3 markdown-html/md-review/scripts/readability_scorer.py \
  --input markdown-html/md-review/assets/sample_article.md --config "$CFG" --format text

# Readability band only — ignore terminology while rewriting sentences
python3 markdown-html/md-review/scripts/readability_scorer.py \
  --input markdown-html/md-review/assets/sample_article.md --config "$CFG" \
  --fail-on readability --no-passive --format json
```

## Decision frameworks

### Severity assignment — what earns an error [PROVEN]

A finding blocks publication only if it passes all three tests. Everything else is a warning.

| Test | Question | Fails if |
| --- | --- | --- |
| Reader-visible | Is someone reading the published page worse off? | It only inconveniences maintainers |
| Unambiguous | Is there any legitimate reason to author it this way? | Reasonable authors disagree |
| Mechanically fixable | Can the author fix it without a product decision? | It needs a rewrite or a decision |

Broken link, missing alt text, skipped heading level, headerless table, missing required
frontmatter field → **error**. Long sections, terminology drift, heading capitalization,
readability band → **warning**. Passive voice → **info**.

**Never downgrade `a11y.missing-alt`.** Every other rule has a defensible exception; this one does
not. If an image is decorative, mark it decorative — do not suppress the rule.

### Readability target bands by audience [PROVEN]

The single table that makes readability scoring useful. A score without a target audience is noise.

| Audience | Flesch Reading Ease | Max FK grade | Max long-sentence % |
| --- | --- | --- | --- |
| Emergency / safety-critical runbook | 70-90 | 6.0 | 5% |
| General public / consumer | 60-80 | 8.0 | 8% |
| General technical (default) | 50-70 | 12.0 | 10% |
| Specialist practitioner | 40-60 | 14.0 | 12% |
| Academic / regulatory | 30-50 | 16.0 | 15% |

**Only the floor blocks.** Prose easier than its band is prose more people can read; the scorer
records it as info. Gating both bounds teaches authors to pad sentences, which inverts the point.

The safety-critical row is the one teams get wrong. Comprehension collapses under stress — an
incident runbook written at grade 12 is unreadable at 3am during an outage.

### Sentence-length thresholds [PROVEN]

| Words | Level | Action |
| --- | --- | --- |
| ≤ 20 | fine | None |
| 21-30 | acceptable | None |
| 31-45 | warning | Usually two sentences wearing a trench coat |
| 46+ | error | Split it; the reader is re-reading |

Target mean ≤ 20 words with ≤ 10% of sentences over 30. **The percentage matters more than the
mean** — an 18-word average with 20% monsters reads worse than a 22-word average with none.

### WCAG coverage — what source-level checks can and cannot prove [RECOMMENDED]

| Success criterion | Level | Checked here | Mechanism |
| --- | --- | --- | --- |
| 1.1.1 Non-text Content | A | Yes | Alt text present, non-placeholder, 10-150 chars |
| 1.3.1 Info and Relationships | A | Yes | Heading hierarchy + table header rows |
| 2.4.4 Link Purpose (In Context) | A | Yes | Link text not in the non-descriptive list |
| 2.4.9 Link Purpose (Link Only) | AAA | Yes | Same check, stricter target — aim here |
| 2.4.6 Headings and Labels | AA | Partial | Single-H1 and minimum-section rules |
| 3.1.1 Language of Page | A | Optional | Add `lang` to `required_fields` |
| 1.4.3 Contrast | AA | No | Needs computed colors |
| 2.1.1 Keyboard | A | No | Needs an interactive DOM |
| 4.1.2 Name, Role, Value | A | No | Needs the accessibility tree |

Run the bottom three against converted HTML. Claiming source-level checks prove WCAG conformance
is how teams end up with a compliance badge on an inaccessible site.

### Rollout sequence for an existing corpus [PROVEN]

Switching a gate on across a legacy corpus in one step fails every time.

| Phase | Duration | `fail_on` | Goal |
| --- | --- | --- | --- |
| 1. Observe | 2 weeks | `never` | Learn the real finding distribution; tune the term map |
| 2. Changed files only | 4 weeks | `error` on the diff | Stop the bleeding without a backlog cleanup |
| 3. Ratchet | 1-2 quarters | `error`, descending `max_warnings` | Burn down legacy debt |
| 4. Steady state | ongoing | `error`, fixed budget | Maintain |

Phase 2 carries the value. Gating only the files a change touches makes the gate immediately
useful and never blocking on unrelated debt.

### Exit code contract [PROVEN]

| Code | Meaning | Who fixes it |
| --- | --- | --- |
| 0 | Passed | Nobody |
| 1 | Tool error — bad path, malformed config | Repository maintainer |
| 2 | Gate failed — blocking findings | Document author |

Keep 1 and 2 distinct. Collapsing them sends every failure to the wrong person first.

## Anti-Patterns

### The Network Link Checker In The Merge Gate
**Mistake:** Wiring an HTTP link checker into the blocking pre-merge gate so every external URL gets fetched on every run.
**Why it happens:** Dead external links are a real problem, and checking them feels like the same job as checking internal ones. The tooling usually offers both behind one flag.
**Instead:** Resolve internal targets on disk in the blocking gate — it is deterministic and finishes in milliseconds. Inventory external URLs and verify them in a separate scheduled, non-blocking job. A gate that intermittently fails on someone else's 503 gets re-run reflexively within two weeks, and then nobody reads the real failures either.

### Gating On The Readability Ceiling
**Mistake:** Failing the build when a document scores *above* its target Flesch band, on the theory that the band is a specification to hit.
**Why it happens:** The band is written as a range, so both ends look like thresholds. Treating it symmetrically feels rigorous.
**Instead:** Block only on the floor. Prose easier than its audience requires is a win, not a defect — record it as info. Teams that gate both ends get authors padding sentences with subordinate clauses to climb back into range, producing exactly the writing the metric exists to prevent.

### The Term Map That Only Grows
**Mistake:** Adding every style disagreement to the terminology map and never removing anything, until the map has 400 entries and every document produces twenty warnings.
**Why it happens:** Adding an entry is a one-line fix that closes a style argument permanently. Removing one requires re-litigating it.
**Instead:** Cap the map at the terms that actually matter — product names with canonical capitalization, contested hyphenation, deprecated names, inclusive-language replacements — and review it quarterly. Every entry should have a reason someone can state out loud. Keep terminology at warning severity; blocking a release on `Github` teaches authors the gate is petty, and a gate perceived as petty gets bypassed.

### Zero Warnings On Day One
**Mistake:** Adopting the gate with `max_warnings: 0` against an inherited corpus, producing a 400-finding first run.
**Why it happens:** Zero is the obviously correct end state, and starting anywhere else feels like tolerating defects.
**Instead:** Set the budget at the current warning count, then ratchet down 10-20% per quarter. A first run that produces one enormous cleanup PR gets rubber-stamped, not reviewed, and the debt returns within a release. Phase the rollout: observe, then gate changed files, then ratchet.

### Inline Suppression Comments
**Mistake:** Adding `<!-- md-review-disable a11y.missing-alt -->` markers in documents to silence findings the author disagrees with.
**Why it happens:** It unblocks the immediate merge and feels surgical compared to changing the shared config.
**Instead:** Fix the config, downgrade the severity, or disable the rule globally with a recorded reason. Inline suppressions spread by copy-paste, are never reviewed, and become permanent exemptions nobody can justify. If a rule needs suppression often enough to want an inline escape hatch, the rule itself is wrong — change it once, in the open.

## Files

| File | Purpose |
| --- | --- |
| `scripts/md_review_gate.py` | Heading structure, frontmatter schema, and accessibility checks with a configurable severity gate; exits 2 on blocking findings |
| `scripts/link_checker.py` | Resolves relative file targets and anchor fragments on disk, reports duplicate heading anchors, inventories external URLs without fetching them |
| `scripts/readability_scorer.py` | Flesch Reading Ease, Flesch-Kincaid grade, syllable counting, long-sentence and passive-voice heuristics, and term-map consistency |
| `references/review-rulebook-and-severity-model.md` | Full rule catalog with default severities, config schema, slug algorithm, gate design, and CI integration patterns |
| `references/readability-accessibility-and-terminology.md` | Readability formulas, audience target bands, syllable heuristic and its failure cases, WCAG success criteria per check, term-map governance |
| `assets/sample_review_config.json` | Working config profile: required frontmatter fields, thresholds, term map, severity overrides, gate settings |
| `assets/sample_article.md` | Sample input containing deliberate defects; drives the non-zero-exit demonstration for all three scripts |
| `assets/sample_article_clean.md` | Clean sample input that passes all three scripts with exit code 0 |
| `assets/review_report_template.md` | Reviewer-facing report template with verdict, findings, link, readability, accessibility, and sign-off sections |
