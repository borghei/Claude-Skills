# Print and PDF Production

How an HTML document becomes a page. Covers the CSS Paged Media model, page
geometry, break control, the browser-support reality, and the failure modes that
only appear on paper.

## The core problem

A screen is one continuous surface of unknown height. A page is a fixed
rectangle, and there are many of them. Every print defect traces back to content
authored for the first model being poured into the second: a heading stranded at
the foot of a page, a table split mid-row, a link whose destination exists only
as an attribute nobody can click.

CSS Paged Media (`@page`, `break-*`, margin boxes) is the mechanism for
controlling that pour. `print_profile.py` generates it from a JSON profile so the
values are reviewable and consistent across a document series.

## Page geometry

### Sizes

| Name | Dimensions | Region | Text width at 20mm margins |
|------|------------|--------|----------------------------|
| A4 | 210 x 297mm | International | 170mm (~92 chars at 11pt) |
| Letter | 8.5 x 11in (216 x 279mm) | North America | 176mm |
| A5 | 148 x 210mm | Booklets, handbooks | 108mm |
| Legal | 8.5 x 14in | Legal filings | 176mm |

**Default to A4 unless the audience is exclusively North American.** A4 pages
print acceptably on Letter stock with minor margin loss; Letter content on A4
clips at the foot, which is the worse failure.

### Margins and the measure problem

A 170mm text column at 11pt is roughly 92 characters — well outside the 55-85
character comfort band. This is the most common defect in HTML-to-PDF output:
the screen stylesheet constrains the measure with `max-width`, the print
stylesheet sets `max-width: none` to use the page, and the line length becomes
unreadable.

Three fixes, in order of preference:

1. **[RECOMMENDED] Widen the margins.** 25-30mm side margins on A4 bring the
   measure to 75-85 characters. Generous margins also read as considered design.
2. **[RECOMMENDED] Raise the type size.** 11pt to 12pt reduces characters per
   line proportionally and improves legibility for older readers.
3. **[EXPERIMENTAL] Two columns.** Halves the measure but multiplies break
   complexity — figures must be column-width or full-bleed, and browser support
   for balanced columns in paged media is inconsistent. Risk: content reflows
   unpredictably across page boundaries. Do not attempt without proofing every
   page of the actual document.

### Mirrored margins for double-sided printing

Bound documents need a wider inner margin — the gutter — because binding
consumes it. Set `double_sided: true` and the generator emits `@page :left` and
`@page :right` with the inner and outer margins swapped:

```css
@page :left  { margin: 22mm 20mm 20mm 18mm; }
@page :right { margin: 22mm 18mm 20mm 20mm; }
```

Skip this for single-sided or screen-read PDFs. A mirrored margin in a document
nobody binds just makes alternating pages look misaligned.

## Margin boxes: running heads and page numbers

The 16 margin boxes (`@top-left`, `@bottom-center`, and so on) hold content that
repeats on every page. Their `content` property accepts counters and strings:

```css
@page {
  @bottom-center { content: counter(page); }
  @top-left { content: "Storage Tiering Review"; }
}
```

| Element | Recommended position | Note |
|---------|---------------------|------|
| Page number | `@bottom-center` | Safest; survives single- and double-sided |
| Page number (bound) | `@bottom-outer` | Thumb-findable when flipping |
| Document title | `@top-left` | Constant across the document |
| Section title | `@top-right` | Requires named strings — poor browser support |
| Confidentiality mark | `@bottom-left` | If required by policy |

**Suppress running heads on the first page.** A title page with its own running
head reads as an error. The generator emits `@page :first` overrides
automatically unless `show_on_first_page` is true.

### The named-strings gap

Genuine running section headers — the current chapter title in the header —
require `string-set` and `content: string(chapter)`. **No mainstream browser
implements this.** It works in dedicated paged-media engines only. If you need
per-section running heads, either accept a static document title or use a real
print formatter, and do not spend a day discovering this in Chrome.

## Break control

### The properties

| Property | Effect | Use on |
|----------|--------|--------|
| `break-before: page` | Force a new page before | `h1` (chapter starts) |
| `break-after: avoid-page` | Do not break immediately after | `h1, h2, h3` |
| `break-inside: avoid` | Keep the element whole | `figure, table, pre, blockquote` |
| `orphans: N` | Minimum lines left at page foot | `p, li` |
| `widows: N` | Minimum lines carried to next page | `p, li` |

`break-after: avoid-page` on headings is the single highest-value print rule. It
prevents the stranded heading — a section title alone at the foot of a page with
its content overleaf. Without it, this occurs in roughly one page in eight for a
typical report.

### Orphans and widows

- **Orphan:** the first line of a paragraph alone at the bottom of a page.
- **Widow:** the last line of a paragraph alone at the top of the next page.

`orphans: 3; widows: 3` is the typographic standard and the right default. Values
above 3 start forcing large gaps at page feet; below 2 the artifacts are visible.

Browser support is genuinely partial — Chrome honors both, Firefox historically
does not. Set them anyway; they cost nothing and improve output where supported.

### The unbreakable-element trap

`break-inside: avoid` on an element taller than the page body has undefined
behavior: browsers variously clip it, overflow it, or ignore the rule. A
three-page table with `break-inside: avoid` is a defect waiting to happen.

**[PROVEN] Apply `break-inside: avoid` only to elements that fit on one page.**
For long tables, allow breaking and repeat the header row instead:

```css
thead { display: table-header-group; }
```

This makes the header repeat on every page the table spans — it is the single
most useful long-table print rule, and it is well supported.

## Color on paper

### Never let dark mode print

A dark theme reaching a printer produces one of two bad outcomes: a page of solid
toner, or — because **browsers strip background colors by default** — light gray
text on white paper, effectively blank.

The print profile forces the light role set unconditionally inside `@media
print`. This is not a preference; it is the only correct behavior. Setting
`force_light_theme: false` triggers a warning from the generator for this reason.

### Do not rely on background printing

`print-color-adjust: exact` requests that backgrounds be preserved, but the user
can override it and many print dialogs default it off. Any information carried
**only** by a background color is lost on paper.

Design so color is redundant: a warning callout gets a left border and a label,
not just a tinted background. This is the same discipline WCAG 1.4.1 requires on
screen, and print is where the failure becomes obvious.

### Ink cost

Full-bleed background tints on a 40-page report are expensive to print and
rarely improve comprehension. Reserve tinted surfaces for code blocks and
callouts where they carry structure.

## Link URLs on paper

A hyperlink is inert on paper. The print stylesheet expands external URLs into
visible text:

```css
a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 9pt; }
```

Three rules for doing this well:

1. **Only external links.** Expanding in-document anchors produces "(#section-3)"
   after every cross-reference — noise with no value. The profile's
   `skip_selectors` suppresses TOC links, cross-references, and footnote
   back-links.
2. **Allow the URL to break.** `word-break: break-all` stops a long URL from
   overflowing the measure.
3. **Consider a link appendix instead.** Above roughly 30 external links,
   inline expansion overwhelms the prose. A numbered appendix reads better.

## Export mechanics

### Browser print-to-PDF

**[PROVEN] This is the right default.** Chrome's print-to-PDF produces
selectable text, working internal links, and reasonable file sizes, with zero
dependencies.

Requirements for a clean export:
- "Background graphics" enabled if the design depends on tinted surfaces.
- Margins set to "Default" — the browser's own margin setting *overrides*
  `@page`, and a user-set "None" will clip content that assumes margins.
- Headers and footers disabled, or the browser's own URL/date stamps collide
  with the running heads.

### Headless generation

`chrome --headless --print-to-pdf` runs the same engine in CI. Note that
`--print-to-pdf` does not honor every `@page` margin box in all versions; proof
the output rather than assuming parity with interactive printing.

### What breaks in export

| Symptom | Cause | Fix |
|---------|-------|-----|
| Content clipped at page edge | Browser margin setting overrides `@page` | Set margins to Default in the dialog |
| Backgrounds missing | Background graphics disabled | Enable it, or make color redundant |
| Blank pages | `break-before: page` on the first element | Use `h1:not(:first-child)` |
| Fonts substituted | Font not embeddable or not loaded | Use a system stack or embed as data URI |
| Links dead in PDF | Generated by a tool that rasterizes | Use browser print-to-PDF |
| Enormous file | Full-resolution images | Downsample to 150-200 DPI before embedding |

### Image resolution

Screen images are typically 72-96 DPI; print wants 150-300 DPI. An image that
looks sharp on screen prints soft.

| Use | Target DPI | Width at 170mm |
|-----|-----------|----------------|
| Screen only | 96 | ~640px |
| Acceptable print | 150 | ~1000px |
| Good print | 200 | ~1340px |
| Photographic | 300 | ~2000px |

Above 300 DPI adds file size and no visible quality. For a self-contained
document with data-URI images, note that base64 encoding adds ~33% overhead on
top of the raw bytes.

## Proofing checklist

Automated checks do not catch page-level defects. Before publishing a PDF:

- [ ] Every page proofed at 100% zoom, not just the first three
- [ ] No stranded headings at any page foot
- [ ] No table split mid-row without a repeated header
- [ ] No figure separated from its caption
- [ ] Page numbers present, correct, and starting where intended
- [ ] Running heads absent from the title page
- [ ] TOC page numbers match reality (if manually maintained)
- [ ] External URLs expanded and not overflowing the measure
- [ ] Printed once in grayscale — any information carried only by hue is now visible as a defect
- [ ] File size reasonable for distribution (under ~10MB for email)
