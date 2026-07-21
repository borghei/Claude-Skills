---
title: Markdown & HTML Skills
description: The markdown-to-HTML publishing pipeline — self-contained documents, slide decks, a pre-publication review gate, and a shared design-token layer. Stdlib only including the markdown parser, and zero network calls.
---

# Markdown & HTML Skills

**4 skills** with **14 stdlib-only Python tools** for the markdown-to-HTML publishing pipeline.

Authored markdown goes in, a polished self-contained HTML artefact comes out, with a review gate in front of it and a shared design-token layer underneath. Distinct from [Documents](other.md) (docx, pdf, pptx, xlsx), which *parses* existing OOXML and PDF binaries — this domain *produces* HTML from markdown you wrote.

!!! info "New domain (July 2026)"
    Two hard constraints apply across the domain. **Stdlib only, including the markdown parser** — no `markdown`, `mistune`, `jinja2`, or CSS toolchain; each converter implements the markdown subset it needs itself. **No network access, ever** — `md-review`'s link checker resolves relative and anchor targets on disk, external URLs are inventoried but never fetched, and the tools report `network_requests_made: 0`. All rendered user content is HTML-escaped at the boundary.

## Skills

### md-document — Self-contained HTML documents

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/markdown-html/md-document){ .md-button }

An authored markdown file into a single HTML document you can email, host, or print: semantic structure, an automatic table of contents, figures and tables numbered and referenceable, footnotes, and a print stylesheet that survives contact with a PDF exporter.

**Workflows:**

- Convert to self-contained HTML → `crossref_auditor.py` then `md_to_html.py` (`--toc-depth`, bundled theme inlined automatically, `--css` to override; non-zero exit means visible `[?fig:name]` markers survived into the output)
- Produce a print-ready PDF → `print_profile.py` (page geometry into a print CSS block appended to the theme, then convert with the extended stylesheet and print with browser margins set to Default)
- Gate a document series in CI → `crossref_auditor.py --max-severity warning` plus the conversion gate, both emitting `--format json` for diff annotation

**Use when:** publishing a report or whitepaper that must arrive as one file, producing a PDF without a LaTeX or Pandoc toolchain, numbering figures so prose can reference them, converting contributed markdown where injection safety matters, standardising a document series, or catching broken cross-references before readers do.

### md-slides — Self-contained HTML slide decks

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/markdown-html/md-slides){ .md-button }

A markdown file into a deck that is one HTML file: six layouts, speaker notes, keyboard and remote navigation, light/dark theming, and handout printing. The density linter is the part that matters most — it catches the slides an audience cannot absorb before you are standing in front of them.

**Workflows:**

- Build a deck and check density → `slide_density_linter.py --profile present` then `md_to_slides.py` (theme and navigation script inlined automatically; lint first, fix by moving sentences into speaker notes)
- Time a talk against its slot → `notes_runsheet.py` (`--wpm`, `--target-minutes`; `*` markers flag slides with no notes, whose duration is guessed and least reliable; `--format markdown` for a written runsheet)
- Convert a document into a deck → `md_to_slides.py --split-on h2` for a first pass, then lint — the failure list is the edit plan

**Use when:** building a deck from markdown kept in version control, presenting without a presentation app or cloud account, cutting an overloaded deck, timing a talk before rehearsing, converting a document as a starting point, or producing a handout with speaker notes.

### md-review — Pre-publication review gate

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/markdown-html/md-review){ .md-button }

The quality gate that runs *before* markdown becomes HTML. A converter will happily render a document with three H1s, four dead links, an image with no alt text, and a 67-word sentence — the HTML validates and the page is still bad. Zero network calls by design: a gate that fails because someone else's server was slow is a gate engineers learn to ignore.

**Workflows:**

- Gate a document before publication → `md_review_gate.py` (structure, frontmatter schema, accessibility), `link_checker.py --root` (on-disk relative and anchor resolution), and `readability_scorer.py` (readability band, terminology, passive voice) — any non-zero exit blocks
- Audit a corpus without blocking → run every file with `--fail-on never`, emit JSON into a JSONL stream, rank rules by frequency before switching the gate on
- Calibrate prose to an audience → `readability_scorer.py` with sentence-level findings; rewrite the very-long sentences first, then confirm the long-sentence share is under 10%

!!! warning "Exit-code contract"
    `md-review` exits **2** on blocking findings, **1** on tool error, and **0** on a clean pass. The shipped `sample_article.md` contains deliberate defects so the failure path is demonstrable — a non-zero exit on it is correct behaviour, not a broken example. `sample_article_clean.md` exercises the pass path.

**Use when:** publishing a doc or article that will become HTML, wiring a docs CI gate that blocks on real defects without blocking on style, auditing an inherited corpus to size the link-rot and accessibility backlog, enforcing house terminology, or calibrating prose to its audience.

### design-system — Document design tokens and theming

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/markdown-html/design-system){ .md-button }

The visual layer the other three consume: a token file in, a single inlinable CSS bundle out, with every colour pairing checked against WCAG before it ships. This is theming for **documents** — type scales, reading measure, print roles, light/dark surfaces. It is not a product UI component library.

**Workflows:**

- Generate a themed CSS bundle → `token_linter.py` then `theme_builder.py` (lint first — a malformed ramp produces a valid-looking bundle with inverted colours)
- Gate a palette on WCAG contrast → `contrast_validator.py --level AA` (exits non-zero on any failure, so it drops into CI directly); `--all-pairs` finds undeclared combinations, `--level AAA --no-gate` is an aspirational report
- Audit and repair an inherited theme → linter for structural rot (non-monotonic ramps, roles present in one mode only, literal hex values), then the full contrast matrix; fix ramp order, then mode parity, then contrast

**Use when:** theming a report or whitepaper that must render as one self-contained file, building a deck theme legible at projection distance, auditing a palette before a public or regulated publication, diagnosing dark-mode drift, standardising across a document series, or answering "does this pass AA?" with a number.

## Quality standard

Each skill in this domain:

- Uses stdlib-only Python and makes zero network calls
- Supports both JSON and human-readable output (`--format` flag)
- HTML-escapes all user content
- Ships runnable sample input for every documented workflow
- Emits a single self-contained artefact with CSS and JS inlined

## Related skills

- **[`documents/`](https://github.com/borghei/Claude-Skills/tree/main/documents)** — parsing docx, pdf, pptx, and xlsx (the opposite direction)
- **[Product Team](product.md)** — `ui-design-system` for product UI components, rather than document theming
- **[Engineering](engineering.md)** — `write-a-skill` for the authoring standards this library follows
- **[Marketing](marketing.md)** — `content-production` for the content workflow upstream of publishing
