# Markdown-HTML Skills - Claude Code Guidance

This domain is the **markdown-to-HTML publishing pipeline**: authored markdown
goes in, a polished self-contained HTML artefact comes out, with a review gate in
front of it and a shared design-token layer underneath.

Distinct from `documents/` (docx, pdf, pptx, xlsx), which *parses* existing
OOXML and PDF binaries. This domain *produces* HTML from markdown you wrote.

## Markdown-HTML Skills Overview (4 skills)

- **md-document/** — render markdown into a polished self-contained HTML
  document: semantic structure, automatic table of contents, figure/table
  numbering with cross-references, footnotes, and print/PDF-ready CSS with page
  breaks. Use when producing a report, whitepaper, or memo for distribution.

- **md-slides/** — render markdown into a self-contained HTML slide deck: slide
  splitting rules, speaker notes, per-slide layouts, keyboard navigation, and a
  content-density linter that flags overloaded slides. Use when building a deck
  from an outline or auditing an existing one for density.

- **md-review/** — pre-publication review gate: heading-hierarchy and structure
  validation, on-disk link and anchor checking, readability scoring, terminology
  consistency, alt-text and accessibility checks, and frontmatter schema
  validation. Use before publishing, or wire it into CI.

- **design-system/** — the shared visual layer the other three consume: design
  tokens (type scale, spacing, color ramps, semantic roles), light/dark theming
  via CSS custom properties, WCAG contrast validation, and generation of a single
  inlinable CSS bundle. Use when establishing or auditing document theming.

**Total Tools:** 14 Python automation tools (stdlib only)

## Scope Boundary

`design-system/` is the **document/HTML theming layer** — tokens and CSS for
rendered output. It is not a product UI component library; for that, see
`product-team/ui-design-system`.

## Hard Constraints

Two constraints apply across this domain and must not be relaxed:

1. **Stdlib only, including the markdown parser.** No `markdown`, `mistune`,
   `jinja2`, or CSS toolchain. Each converter implements the markdown subset it
   needs itself.
2. **No network access, ever.** `md-review`'s link checker resolves relative and
   anchor targets **on disk**. External URLs are inventoried, never fetched — the
   tools report `network_requests_made: 0`. This keeps the gate fast,
   deterministic, and safe to run in CI.

All rendered user content is HTML-escaped at the boundary. Treat any change that
emits unescaped input as a security regression.

## Common Patterns

```
markdown-html/<skill>/
├── SKILL.md
├── references/
│   └── *.md (rulebooks, severity models, layout and density guidance)
├── scripts/
│   └── *.py (render, lint, validate — stdlib only)
└── assets/
    └── theme CSS/JS + sample_*.md and sample_*.json inputs
```

Per Pattern 9, each skill carries its own copy of any shared helper — md-document,
md-slides, and design-system do not import from one another.

## Exit Code Contract

`md-review` is a gate: it exits **2** on blocking findings, **1** on tool error,
**0** on a clean pass. Its shipped `sample_article.md` contains deliberate defects
so the failure path is demonstrable; `sample_article_clean.md` exercises the pass
path. Both are intentional — a non-zero exit on the flawed sample is correct
behaviour, not a broken example.

## Related Skills

- `documents/` — parsing docx, pdf, pptx, xlsx (opposite direction)
- `product-team/ui-design-system` — product UI components
- `engineering/write-a-skill` — authoring standards for this library
- `marketing/content-production` — content workflow upstream of publishing

## Quality Standard

Each skill must:
- Use stdlib-only Python and make zero network calls
- Support both JSON and human-readable output (`--format` flag)
- HTML-escape all user content
- Ship runnable sample input for every documented workflow
- Emit a single self-contained artefact with CSS/JS inlined

---

**Last Updated:** July 2026
**Skills Deployed:** 4/4 markdown-html skills
