# Developer Handoff Guide

How to get the generator's tokens into code and design tools. Every name below is what
`scripts/design_token_generator.py` actually emits: nested JSON keys joined with `-`, so
`colors.primary.DEFAULT` becomes `--colors-primary-DEFAULT` (CSS) and
`$colors-primary-DEFAULT` (SCSS). Versions checked 2026-11: Tailwind CSS 4.3, React 19.3,
Next.js 16, Style Dictionary 5, Storybook 10.

---

## Export Formats

| Format | Command | Use for |
|--------|---------|---------|
| JSON | `python3 scripts/design_token_generator.py "#0066CC" modern json > design-tokens.json` | JS/TS themes, Style Dictionary, Tokens Studio, the contrast checker |
| CSS | `... modern css > design-tokens.css` | Any web stack; Tailwind 4 via `@theme` |
| SCSS | `... modern scss > _design-tokens.scss` | Sass pipelines |
| Summary | `... modern --format text` | A quick look at what was generated |

Sample of each (brand `#0066CC`, modern):

```css
:root {
  --colors-primary-500: #3f85cc;
  --colors-primary-600: #2664a3;
  --colors-primary-DEFAULT: #0066CC;
  --colors-surface-background: #FFFFFF;
  --typography-fontSize-base: 16px;
  --spacing-md: 16px;
  --borders-radius-DEFAULT: 8px;
  --sizing-components-button-md-height: 40px;
}
```

```scss
$colors-primary-DEFAULT: #0066CC;
$typography-fontSize-base: 16px;
$spacing-md: 16px;
```

The SCSS export is flat variables only; build Sass maps yourself if you need `map.get`.

---

## Integration Patterns

### Plain CSS (any framework)

```css
@import "./design-tokens.css";

.btn {
  height: var(--sizing-components-button-md-height);
  padding: 0 var(--sizing-components-button-md-paddingX);
  font-size: var(--typography-fontSize-base);
  border-radius: var(--borders-radius-DEFAULT);
  transition: background-color var(--animation-duration-fast) var(--animation-easing-easeOut);
}
.btn-primary { background: var(--colors-primary-DEFAULT); color: var(--colors-surface-background); }
.btn-primary:hover { background: var(--colors-primary-600); }
.btn:focus-visible { outline: 2px solid var(--colors-primary-DEFAULT); outline-offset: 2px; }
```

Use `primary-DEFAULT` only when `token_contrast_checker.py` passes it; otherwise use the
shade it names. Check the hover shade the same way if it carries text.

### Tailwind CSS 4

Tailwind 4 is configured in CSS; `tailwind.config.js` is no longer the default. Import the
generated file, then map it into Tailwind's theme namespaces with `@theme inline` (inline,
because the values are `var()` references):

```css
/* app/globals.css */
@import "tailwindcss";
@import "./design-tokens.css";

@theme inline {
  --color-primary: var(--colors-primary-DEFAULT);
  --color-primary-50: var(--colors-primary-50);
  --color-primary-600: var(--colors-primary-600);
  --color-primary-700: var(--colors-primary-700);
  --color-neutral-500: var(--colors-neutral-500);
  --color-success: var(--colors-semantic-success-base);
  --color-on-success: var(--colors-semantic-success-contrast);
  --font-sans: var(--typography-fontFamily-sans);
  --font-mono: var(--typography-fontFamily-mono);
  --radius-md: var(--borders-radius-md);
  --shadow-md: var(--shadows-md);
}
```

`--spacing` in Tailwind 4 is a single base unit (`p-4` = 4 × `--spacing`); leave it at its
default 0.25rem, which matches the generator's 4px half-step. Breakpoints are set with
`--breakpoint-*` if you want the generator's values instead of Tailwind's.

```tsx
<button className="bg-primary hover:bg-primary-600 text-white px-4 h-10 rounded-md">Save</button>
```

In Next.js 16 (App Router) import `globals.css` once in `app/layout.tsx`.

### JavaScript theme (styled-components, Emotion, React Native)

```typescript
import tokens from "./design-tokens.json";

export const theme = {
  colors: tokens.colors,
  fontSize: tokens.typography.fontSize,
  spacing: tokens.spacing,
  radii: tokens.borders.radius,
  shadows: tokens.shadows,
};
export type Theme = typeof theme;
```

Wrap the app in the library's `ThemeProvider` and read `theme.colors.primary.DEFAULT`.

### Style Dictionary (iOS, Android, multi-platform)

The JSON is plain nested values, not W3C DTCG (`$value`/`$type`). Style Dictionary 5
reads it as-is for CSS/JS targets; for typed platform outputs, wrap leaves as
`{ "value": ... }` or convert to DTCG first.

---

## Design Tool Integration

- **Figma variables:** import the JSON with Tokens Studio, or a variables-import plugin.
  The Figma Variables REST API needs an Enterprise plan.
- **Storybook 10:** import `design-tokens.css` in `.storybook/preview.ts` and set
  backgrounds to `--colors-surface-background` and `--colors-neutral-900`.
- Keep the JSON as the source of truth; regenerate CSS/SCSS from it, never hand-edit the
  exports (the next run overwrites them).

---

## Handoff Checklist

- [ ] Tokens generated from the agreed brand colour and style
- [ ] `token_contrast_checker.py` verdict PASS at the agreed target, output pasted into the handoff
- [ ] Exports committed: JSON plus the format the stack uses
- [ ] Components use tokens only (no raw hex or px in component styles)
- [ ] Focus ring visible on every interactive element
- [ ] Dark mode, if required, has its own checked palette (the generator emits light only)

## Versioning

Bump the token package by what consumers must do:

| Change | Bump | Consumer action |
|--------|------|-----------------|
| Add a token | Minor | None |
| Change a value | Minor (patch if a fix) | Visual review |
| Rename or remove a token | Major | Code change required |

---

*See also: `token-generation.md` for how each value is computed.*
