---
name: md-document
description: >
  Convert authored markdown into a polished self-contained HTML document with a
  table of contents, numbered figures and tables, cross-references, footnotes,
  and print-ready CSS. Use when publishing a report, whitepaper, or memo.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: markdown-html
  domain: document-publishing
  updated: 2026-07-21
  tags: [markdown, html, publishing, pdf, cross-references, typography]
---

# Markdown Document Publishing

Turn an authored markdown file into a single HTML document you can email, host,
or print — semantic structure, an automatic table of contents, figures and
tables numbered and referenceable by number, footnotes, and a print stylesheet
that survives contact with a PDF exporter. One file out, no runtime dependencies,
no external assets.

## When to use this skill

- **Publishing a report or whitepaper** that must arrive as one file, not a folder
- **Producing a PDF** from markdown without a LaTeX or Pandoc toolchain
- **Numbering figures and tables** so prose can reference them instead of saying "below"
- **Converting untrusted or contributed markdown** where injection safety matters
- **Standardizing a document series** so every issue looks like the same publication
- **Catching broken cross-references** before a document reaches readers

## Inputs the skill expects

- A markdown source file, optionally with YAML frontmatter
- Figure images as relative paths (or data URIs, for true single-file output)
- The intended output: screen, print, or both
- Document length and whether a table of contents is warranted
- Page geometry, if printing: size, margins, single- or double-sided
- A stylesheet, if not using the bundled theme

## Clarify First

Before converting, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Screen, print, or both** — why it changes the output: print needs a page profile, forced light colors, and break control; skipping it produces a document that looks right on screen and breaks on paper
- [ ] **Whether images must be embedded** — why it changes the output: relative image paths mean the HTML file is not actually self-contained, which defeats the point if it will be emailed
- [ ] **Document length and TOC expectation** — why it changes the output: a TOC on a two-page memo is noise; depth 3 on a long report produces a TOC longer than some sections
- [ ] **Whether the markdown is trusted** — why it changes the output: it does not change escaping (always on), but it determines whether a review gate should run first

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Convert a document to self-contained HTML

1. Audit labels and references first — the converter's gate reports broken
   references, but the auditor explains what to do about each one.
2. Convert. The bundled theme is inlined automatically; pass `--css` to override.
3. Check the gate. A non-zero exit means the rendered document contains visible
   `[?fig:name]` markers where numbers should be.

```bash
python3 markdown-html/md-document/scripts/crossref_auditor.py \
  --input markdown-html/md-document/assets/sample_document.md --format text

python3 markdown-html/md-document/scripts/md_to_html.py \
  --input markdown-html/md-document/assets/sample_document.md \
  --out build/report.html --toc-depth 2 --format text
```

### Workflow 2 — Produce a print-ready PDF

1. Generate the print block from a page profile and append it to the theme, so
   the exported file carries its own print rules.
2. Convert with the extended stylesheet.
3. Open in a browser, print to PDF with margins set to **Default** — a browser
   margin setting overrides `@page` and will clip content.

```bash
python3 markdown-html/md-document/scripts/print_profile.py \
  --input markdown-html/md-document/assets/sample_print_profile.json \
  --out build/print.css --format text

cat markdown-html/md-document/assets/document_theme.css build/print.css > build/full.css

python3 markdown-html/md-document/scripts/md_to_html.py \
  --input markdown-html/md-document/assets/sample_document.md \
  --css build/full.css --out build/report.html
```

### Workflow 3 — Gate a document series in CI

1. Run the auditor at `warning` severity so unlabelled figures block, not just
   broken references.
2. Run the conversion gate; it fails on unresolved references and undefined
   footnotes — both render as visible defects.
3. Emit JSON for both so a CI job can annotate the diff.

```bash
python3 markdown-html/md-document/scripts/crossref_auditor.py \
  --input markdown-html/md-document/assets/sample_document.md --max-severity warning --format json

python3 markdown-html/md-document/scripts/md_to_html.py \
  --input markdown-html/md-document/assets/sample_document.md --out build/report.html --format json
```

## Decision frameworks

### Table-of-contents depth

| Document length | TOC | `--toc-depth` |
|-----------------|-----|---------------|
| Under 3 pages | none — omit `[TOC]` | n/a |
| 3-10 pages | yes | 1 (`##` only) |
| 10-30 pages | yes | 2 (default) [PROVEN] |
| Over 30 pages | yes | 2, plus per-section navigation |

If the TOC exceeds one screen, reduce the depth. A contents list longer than the
first section is a navigation failure, not thoroughness.

### Reference style

| Situation | Write | Not |
|-----------|-------|-----|
| Pointing at a figure | `[@fig:access]` | "the chart below" |
| Pointing at a table | `[@tbl:policies]` | "see the table above" |
| Pointing at a section | `[@sec:context]` | "as discussed earlier" |
| A caveat that breaks the sentence | a footnote | a parenthetical |
| Evidence the argument depends on | body text | a footnote |

**[PROVEN] Never use positional language in a document that may be paginated.**
"Below" breaks when the table lands on the next page, breaks silently when a
section is reordered, and means nothing to a reader navigating by heading.

### Alt text versus caption

| | Alt text | Caption |
|---|---------|---------|
| Audience | Non-sighted readers | Everyone |
| Length | 15-125 characters | One or two sentences |
| Says | What the image depicts | What to conclude, plus the number |
| Fails as | "chart", "figure 3", "" | "See above" |

The auditor flags placeholder alt text (`chart`, `image`, `screenshot`, empty) at
**error** severity and alt text under 15 or over 125 characters at **warning**.

### Print geometry

| Decision | Default | Change when |
|----------|---------|-------------|
| Page size | A4 [RECOMMENDED] | Audience is exclusively North American → Letter |
| Side margins | 25-30mm | Never below 20mm — the measure exceeds 90 characters |
| Body size | 11pt | 12pt for older audiences or dense reference material |
| Mirrored margins | off | The document will be bound double-sided |
| `break-inside: avoid` | figures, tables, code | Never on an element taller than one page |

At A4 with 20mm margins the text column is ~92 characters — well outside the
55-85 comfort band. Widening the margins is the fix; `max-width: none` on `main`
is what causes the problem.

## Anti-Patterns

### The "see the table below" reference
**Mistake:** Writing positional prose — "the chart below", "as shown above" — instead of a numbered cross-reference.
**Why it happens:** It reads naturally while drafting, when the author can see the whole document at once and the table genuinely is below.
**Instead:** Write `[@tbl:policies]`. Pagination moves content, reordering breaks positional claims silently, and a reader navigating by heading has no "below". The auditor cannot detect a broken "below"; it fails the build on a broken `[@tbl:policies]`.

### Allowing raw HTML through the converter
**Mistake:** Adding an escape hatch so authors can drop `<div class="...">` or an embed into the markdown.
**Why it happens:** A real formatting need appears that the subset does not cover, and passing HTML through is a one-line change.
**Instead:** Extend the subset or the stylesheet. The escape-then-render ordering is the entire security model — the moment raw HTML passes through, every document becomes an injection vector, and the converter can no longer be pointed at contributed content. There is deliberately no `--allow-html` flag.

### Reusing the caption as alt text
**Mistake:** Writing one string and letting it serve as both the figure caption and the alt attribute.
**Why it happens:** The converter falls back to exactly this when no caption is given, which makes it look sanctioned.
**Instead:** Write both. The caption tells a sighted reader what to conclude; the alt text describes what the figure shows to someone who cannot see it. "Figure 3. Costs fall 40% under Policy B" is a fine caption and useless alt text — it states the conclusion without describing the chart.

### Print rules added after the fact
**Mistake:** Building the document for screen, then bolting on a print stylesheet when someone asks for a PDF.
**Why it happens:** Print feels like a rendering detail rather than a design constraint, and the screen version already looks finished.
**Instead:** Decide print-or-not before converting. Retrofitted print CSS produces the classic failures — stranded headings, tables split mid-row, dark theme reaching paper as invisible gray text, a 92-character measure. `print_profile.py` exists so the geometry is a reviewed input, not an afterthought.

### Trusting the gate as a proof of quality
**Mistake:** Treating a passing conversion as evidence the document is ready to publish.
**Why it happens:** The gate is automated and green, which reads as authoritative.
**Instead:** The gate checks that references resolve and footnotes are defined. It cannot see a stranded heading, a figure separated from its caption, a table split across pages, or a PDF whose margins clipped the content. Proof every page of the actual output at 100% zoom before publishing.

## Files

| File | Purpose |
|------|---------|
| `scripts/md_to_html.py` | CLI: convert markdown to a self-contained HTML document; gates on broken references |
| `scripts/md_render.py` | Markdown subset parser, escaping-first inline renderer, label numbering — imported by `md_to_html.py`, not a CLI |
| `scripts/crossref_auditor.py` | Audit labels, references, alt text, and heading hierarchy; CI gate |
| `scripts/print_profile.py` | Generate a print/PDF stylesheet from a JSON page profile |
| `references/markdown-conventions.md` | Supported syntax, labelling contract, escaping and URL-allowlist model |
| `references/print-and-pdf-production.md` | Paged media, break control, export mechanics, proofing checklist |
| `assets/sample_document.md` | Working document exercising every construct; converts clean |
| `assets/sample_print_profile.json` | A4 double-sided print profile with running heads |
| `assets/document_theme.css` | Bundled theme inlined by default — this skill's own copy |
| `assets/document_outline_template.md` | Starting structure for a new report or memo |

All scripts share one exit-code contract: **0** clean, **2** gate failed (findings at or above the threshold), **1** the tool itself errored. A CI job can therefore tell a real defect from a broken invocation.

**Three CLI tools, one module.** `md_render.py` is a library, not a fourth
command — it holds the parser that `md_to_html.py` imports. A single-file
converter came to 429 lines, well over the 300-line ceiling. Splitting CLI from
parser is the remedy the tool-design standard prescribes for an oversized script,
and same-directory imports keep the package self-contained: `md-slides` carries
its own separate `slide_render.py` rather than importing this one.
