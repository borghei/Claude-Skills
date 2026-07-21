# Markdown Conventions for Publishable Documents

The authoring contract for `md_to_html.py`: exactly what syntax is supported,
what each construct becomes in HTML, and the labelling conventions that make
cross-references resolve. Anything not listed here is passed through as escaped
text — it will not silently become markup.

## Why this is a subset, not a full markdown implementation

Full CommonMark is roughly 600 pages of edge cases: nested list interruption,
lazy continuation, HTML blocks, reference-style links, entity handling. A
document pipeline needs about 12 constructs. The subset is a deliberate choice
with three consequences worth stating plainly:

1. **Raw HTML in the source is escaped, not rendered.** This is the security
   property that makes the converter safe to point at untrusted markdown. There
   is no `--allow-html` flag, because that flag is how injection gets shipped.
2. **Nested lists are not supported.** A document that needs three levels of
   nesting usually needs headings instead. This is a real limitation; if you
   need nested lists, the honest answer is that this converter is the wrong
   tool.
3. **Reference-style links (`[text][ref]`) are not supported.** Use inline
   links. The cross-reference system covers the case reference links usually
   serve in documents.

## Supported constructs

### Headings

```markdown
# Document title
## Section {#sec:policies}
### Subsection
```

- `#` through `######` map to `<h1>`-`<h6>`.
- Every heading gets an auto-generated `id` slugified from its text.
- An optional `{#sec:name}` suffix registers a referenceable section label.
- The **first `# ` heading becomes the document title** unless `--title` overrides it.

**Never skip a level.** `# ` followed by `### ` produces a broken document
outline. Screen-reader users navigate by heading level; a skipped level reads as
a missing section. `crossref_auditor.py` flags this as `HEADING_SKIP` at error
severity.

### Emphasis and code spans

| Source | Output | Note |
|--------|--------|------|
| `**bold**` | `<strong>` | Semantic strength, not visual weight |
| `*italic*` | `<em>` | Not applied inside words |
| `` `code` `` | `<code>` | Contents are escaped; emphasis inside is **not** interpreted |

Code spans are extracted before escaping and reinserted afterwards. This is why
`` `**not bold**` `` renders literally — the correct behavior, and the one most
naive converters get wrong.

### Lists

```markdown
- flat unordered item
- second item

1. flat ordered item
2. second item
```

Flat only. A blank line or any other block type ends the list.

### Tables

```markdown
| Policy | Saving | Latency |
|--------|--------|---------|
| A      | $8,400 | 15-40ms |

Table: Modelled outcomes per policy {#tbl:policies}
```

- The first row becomes `<th scope="col">` cells. `scope` is what lets a screen
  reader associate a data cell with its column header (WCAG 1.3.1).
- The delimiter row (`|---|---|`) is consumed, not rendered.
- A `Table:` line **after** the table — blank lines between are fine — becomes a
  numbered `<caption>`. The optional `{#tbl:name}` makes it referenceable.
- Tables are wrapped in `<div class="table-wrap">` so wide tables scroll inside
  their own container instead of forcing the page to scroll horizontally.

Alignment markers (`:---:`) are parsed and discarded. Column alignment in a
document is a stylesheet decision, not an authoring one — inconsistent per-table
alignment is a common source of visual noise in long reports.

### Figures

```markdown
![Read frequency by object age, 90-day window](figures/access.png){#fig:access}
```

A standalone image line becomes a `<figure>` with an auto-numbered
`<figcaption>`. Text after the closing paren becomes the caption; when absent,
the alt text is reused as the caption.

**Alt text and caption are not the same thing.** The caption tells a sighted
reader what to conclude; the alt text describes what the figure shows to someone
who cannot see it. Reusing one as the other is a fallback, not the goal.

| | Alt text | Caption |
|---|---------|---------|
| Audience | Non-sighted readers | Everyone |
| Length | 15-125 characters | One or two sentences |
| Content | What the image depicts | What it means, plus the figure number |
| Bad | "chart", "figure 3", "screenshot" | "See above" |

### Blockquotes, rules, code blocks

````markdown
> A quoted line.

---

```yaml
lifecycle:
  - id: cold-to-ia
```
````

Fenced code blocks take an optional language that becomes
`class="language-yaml"` — a hook for a highlighter, not highlighting itself. The
converter deliberately ships no syntax highlighter: every one requires either a
runtime dependency or thousands of lines of embedded JavaScript, and the
self-contained output constraint makes both a bad trade.

### Footnotes

```markdown
Policy C changes the failure mode.[^retrieval]

[^retrieval]: Archive-class retrieval is billed per request *and* per gigabyte.
```

- Reference `[^id]` anywhere; define `[^id]:` anywhere (conventionally at the end).
- Footnotes are numbered by **order of first reference**, not order of definition.
- Each note renders with a back-link to its reference point.
- A referenced but undefined note renders a visible marker and **fails the gate**.

Use footnotes for the caveat that would break the sentence. Do not use them for
citations of things a reader must follow to understand the argument — if it is
load-bearing, it belongs in the body.

## Cross-references

### The labelling contract

| Kind | Label syntax | Reference syntax | Renders as |
|------|--------------|------------------|------------|
| Figure | `{#fig:name}` on the image line | `[@fig:name]` | "Figure 3" (linked) |
| Table | `{#tbl:name}` on the `Table:` line | `[@tbl:name]` | "Table 2" (linked) |
| Section | `{#sec:name}` on the heading | `[@sec:name]` | "Section 4.1" (linked) |

Names are `[A-Za-z0-9_-]+`. Numbering is assigned in a **first pass over the
whole document**, before any rendering, which is why a reference can appear
before the thing it points at and still resolve to the right number.

Section numbers are hierarchical and derived from heading depth: the second `##`
is `2`, its third `###` child is `2.3`. `# ` (the title) is excluded from
numbering.

### Why "see below" is a defect

Prose that says "the table below" breaks in three ways a numbered reference does
not:

1. **Pagination moves it.** In print or PDF the table lands on the next page and
   "below" becomes wrong.
2. **Reordering breaks it silently.** Moving a section leaves the prose pointing
   at nothing, and no tool can detect it.
3. **Non-linear readers cannot use it.** A screen-reader user jumping by heading
   has no "below".

Write `[@tbl:policies]`. If the table moves, the number follows it, and
`crossref_auditor.py` fails the build if the label ever disappears.

### Unreferenced labels

The auditor reports labels nobody references at `info` severity, not `warning`.
A label on every figure is good practice even when the current draft does not
reference all of them — the cost is one line, and it makes future prose cheap to
write. The finding exists to catch typos in reference names, not to discourage
labelling.

## Frontmatter

A leading YAML block delimited by `---` is stripped before conversion:

```markdown
---
title: Storage Tiering Review
author: Platform Engineering
date: 2026-07-21
status: draft
---
```

The converter does not parse it — it strips it so the fields do not render as a
stray table. Validating frontmatter fields is a review-gate concern, upstream of
conversion.

## Escaping and injection safety

The inline renderer follows one rule, and the ordering is the whole security
model:

```
1. lift code spans out
2. HTML-escape everything that remains
3. apply markdown patterns to the escaped text
4. reinsert code spans, escaped
```

Because escaping happens **before** any markup is emitted, no byte of user
content can become a tag. `<script>alert(1)</script>` in the source arrives in
the output as `&lt;script&gt;alert(1)&lt;/script&gt;` — visible text, inert.

### URL scheme allowlist

Link and image URLs are matched against an allowlist before they reach an
attribute:

| Allowed | Blocked |
|---------|---------|
| `https:` `http:` | `javascript:` |
| `mailto:` | `data:` |
| `#anchor` | `vbscript:` |
| `./relative` `/absolute` | `file:` |
| `path/to/file.png` | any unrecognized scheme |

A blocked URL becomes `#blocked-url` — the link stays visible so the problem is
noticed, but it cannot execute. This is an allowlist rather than a
`javascript:`-blocklist on purpose: blocklists are defeated by encoding tricks
(`java\tscript:`, `JaVaScRiPt:`, `&#106;avascript:`), allowlists are not.

### The parenthesis limitation

The link pattern stops at the first `)`, so a URL containing a literal
parenthesis — `https://en.wikipedia.org/wiki/Foo_(bar)` — truncates and leaves a
stray character. Percent-encode it as `%28` / `%29`. This is a real limitation of
a regex-based inline parser and is called out rather than hidden.

## Semantic HTML mapping

| Markdown | HTML | Why this element |
|----------|------|------------------|
| Heading | `<h1>`-`<h6>` with `id` | Document outline; anchor targets |
| Standalone image | `<figure>` + `<figcaption>` | Associates caption with image programmatically |
| Table | `<table>` + `<caption>` + `<th scope>` | Header association for assistive tech (1.3.1) |
| Footnote ref | `<sup><a>` | Linked both directions |
| TOC | `<nav aria-label="Table of contents">` | Landmark navigation |
| Body | `<main>` | Skip-to-content landmark |

Every one of these is a semantic choice with an accessibility consequence.
Rendering a caption as a `<p>` after an `<img>` looks identical and conveys
nothing to a screen reader; `<figcaption>` inside `<figure>` is what creates the
association.

## The table of contents

Place `[TOC]` on its own line where the contents should appear. Without the
marker, no TOC is emitted — a two-page memo does not need one.

`--toc-depth` counts levels **below** H1: the default of 2 lists `##` and `###`.

| Document length | Recommended depth |
|-----------------|-------------------|
| Under 3 pages | No TOC |
| 3-10 pages | 1 (`##` only) |
| 10-30 pages | 2 (default) |
| Over 30 pages | 2, plus per-section navigation |

Depth 3 on a long document produces a TOC longer than some of its sections. If
the TOC exceeds one screen, reduce the depth rather than accepting it.

## The conversion gate

`md_to_html.py` exits non-zero when the document contains unresolved
cross-references or undefined footnotes. Both are **silent failures in the
rendered output** — the reader sees a marker where a number should be — which is
exactly the class of defect a gate should catch before publication.

Use `--no-gate` for intermediate drafts where references to unwritten sections
are expected. Do not use it in CI; that defeats the purpose.
