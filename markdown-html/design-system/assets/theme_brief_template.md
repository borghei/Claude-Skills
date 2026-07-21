# Theme Brief — <theme name>

Fill this in before writing a single hex value. Every field below changes the
token file; guessing them means rebuilding the theme after the first review.

## 1. Output context

- **Artifact types this theme serves:** <reports / whitepapers / memos / slide decks>
- **Primary reading surface:** <screen / print / both>
- **Will it be exported to PDF?** <yes / no> — if yes, print roles are mandatory
- **Longest expected document:** <pages> — drives TOC, running headers, page breaks
- **Projection or shared-screen use?** <yes / no> — if yes, minimum type sizes rise

## 2. Conformance target

- **Contrast level to gate on:** <AA (default) / AAA>
- **Known audience accessibility needs:** <low vision / color vision deficiency / none stated>
- **Regulatory requirement driving this?** <e.g. public-sector procurement / none>

> Gate on AA and report on AAA unless a stated requirement says otherwise.
> AAA constrains the palette hard: saturated mid-tones rarely reach 7:1 on white.

## 3. Brand inputs

| Input | Value | Source |
|-------|-------|--------|
| Primary brand color | `#______` | <brand guide / logo / none> |
| Secondary / accent | `#______` | |
| Body typeface | | <licensed? web-safe fallback?> |
| Heading typeface | | |
| Mono typeface | | |

- **Font licensing:** self-contained HTML cannot fetch web fonts. Either embed as
  a data URI (check the license permits it) or fall back to a system stack.
- **If no brand exists:** say so. A neutral ramp plus one accent is a complete
  theme; inventing brand color is out of scope for a theme brief.

## 4. Scale decisions

| Decision | Value | Rationale |
|----------|-------|-----------|
| Base font size | ___px | 16 floor; 17-18 for long-form |
| Type ratio | ___ | 1.25 documents / 1.333 slides |
| Number of type steps | ___ | 7-8 covers caption through H1 |
| Measure | ___ch | 66-75 for prose |
| Spacing base | ___px | 8 default, 4 for dense |

## 5. Role inventory

List every semantic role and its light/dark ramp binding. Both modes are
required — a role defined in only one mode fails the linter's parity check.

| Role | Light | Dark | Used by |
|------|-------|------|---------|
| `surface` | | | page background |
| `surface-raised` | | | callouts, code wells |
| `text` | | | body, headings |
| `text-muted` | | | captions, footnotes |
| `border` | | | rules, table lines |
| `link` | | | inline anchors |
| `accent` | | | quote bars, focus ring |
| `code-surface` | | | code blocks |
| `code-text` | | | code foreground |
| `warn` | | | caution callouts |
| `danger` | | | error callouts |

## 6. Declared pairings

Every foreground/background combination the stylesheet will actually produce,
with its usage class. Anything not listed here is not checked.

| Foreground | Background | Usage | Why this class |
|------------|------------|-------|----------------|
| `text` | `surface` | body | |
| `text-muted` | `surface` | body | captions are body text, not decoration |
| `link` | `surface` | body | |
| `border` | `surface` | decor | not load-bearing — table has headers and alignment |

Usage classes: `body` (4.5:1 AA), `large` (3:1 AA, >=18.66px bold / >=24px
regular), `ui` (3:1, component boundaries and meaningful graphics), `decor`
(1.5:1 visibility floor, no WCAG minimum).

## 7. Open questions

- <question> — blocking / non-blocking
- <question> — blocking / non-blocking

## 8. Sign-off checklist

- [ ] `token_linter.py` reports zero errors
- [ ] `contrast_validator.py --level AA` gate passes in **both** modes
- [ ] `contrast_validator.py --all-pairs` reviewed; every real failure either
      fixed or reclassified with a written justification
- [ ] Dark mode rendered and eyeballed, not just computed
- [ ] Print stylesheet forces light roles
- [ ] Inline links carry a non-color cue (underline) or clear 3:1 against body text
- [ ] Theme bundle regenerated and inlined into the target artifact
