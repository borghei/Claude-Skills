# Design Token Generation Guide

Reference for color palette algorithms, typography scales, and WCAG accessibility checking.

---

## Table of Contents

- [Color Palette Generation](#color-palette-generation)
- [Typography Scale System](#typography-scale-system)
- [Spacing Grid System](#spacing-grid-system)
- [Accessibility Contrast](#accessibility-contrast)
- [Export Formats](#export-formats)

---

## Color Palette Generation

### HSV Color Space Algorithm

The token generator uses HSV (Hue, Saturation, Value) color space for precise control.

```
┌─────────────────────────────────────────────────────────────┐
│                    COLOR SCALE GENERATION                   │
├─────────────────────────────────────────────────────────────┤
│  Input: Brand Color (#0066CC)                               │
│  ↓                                                          │
│  Convert: Hex → RGB → HSV                                   │
│  ↓                                                          │
│  For each step (50, 100, 200... 900):                      │
│    • Adjust Value (brightness)                              │
│    • Adjust Saturation                                      │
│    • Keep Hue constant                                      │
│  ↓                                                          │
│  Output: 10-step color scale                                │
└─────────────────────────────────────────────────────────────┘
```

### Brightness Algorithm

```python
# Dark half (500-900): linear decrease in HSV value
new_value = base_value * (1 - (step - 500) / 500)
# At step 900: brightness ≈ base_value * 0.2

# Light half (50-400): step 500 mixed toward white in sRGB
# share of white per step (references/token-presets.json, light_tint_mix):
#   50: 0.92  100: 0.84  200: 0.68  300: 0.48  400: 0.26
channel = c500 + (255 - c500) * white
```

Lightness falls step by step from 50 to 900, so 50-100 are real background tints and
200 is a usable hover or selected fill.

### Saturation Scaling

```python
# Dark half only: saturation rises from 70% (500) to 100% (900) of the base
new_saturation = base_saturation * (0.3 + 0.7 * (step / 900))
```

### Complementary Color Generation

```
Brand Color: #0066CC (H=210°, S=100%, V=80%)
                    ↓
           Add 180° to Hue
                    ↓
Secondary: #CC6600 (H=30°, S=100%, V=80%)
```

### Color Scale Output

| Step | Use Case | Brightness | Saturation |
|------|----------|------------|------------|
| 50 | Page tint, subtle backgrounds | 500 + 92% white | - |
| 100 | Light backgrounds, selected rows | 500 + 84% white | - |
| 200 | Hover fills on light surfaces | 500 + 68% white | - |
| 300 | Borders | 500 + 48% white | - |
| 400 | Decorative accents | 500 + 26% white | - |
| 500 | Mid tone (not the brand hex) | Original | 70% |
| 600 | Hover (dark) | Original × 0.8 | 78% |
| 700 | Active states | Original × 0.6 | 86% |
| 800 | Text | Original × 0.4 | 94% |
| 900 | Headings | Original × 0.2 | 100% |

`DEFAULT` holds the brand hex exactly as given. Step 500 keeps the brand's brightness but
only ~70% of its saturation, so it is lighter: for `#0066CC`, 500 is `#3f85cc` (3.86:1 on
white, fails AA for text) while `DEFAULT` is 5.57:1. Steps 50-400 are step 500 mixed toward
white (`#f0f5fb` to `#71a5d9` for `#0066CC`). Use `DEFAULT` for fills and links when the checker passes it.

---

## Typography Scale System

### Modular Scale (Major Third)

The generator uses a **1.25x ratio** (major third) to create harmonious font sizes.

```
Base: 16px

Scale calculation:
  Smaller sizes: 16px ÷ 1.25^n
  Larger sizes: 16px × 1.25^n

Result:
  xs:   10px (16 ÷ 1.25²)
  sm:   13px (16 ÷ 1.25¹)
  base: 16px
  lg:   20px (16 × 1.25¹)
  xl:   25px (16 × 1.25²)
  2xl:  31px (16 × 1.25³)
  3xl:  39px (16 × 1.25⁴)
  4xl:  49px (16 × 1.25⁵)
  5xl:  61px (16 × 1.25⁶)
```

### Type Scale Ratios

| Ratio | Name | Multiplier | Character |
|-------|------|------------|-----------|
| 1.067 | Minor Second | Tight | Compact UIs |
| 1.125 | Major Second | Subtle | App interfaces |
| 1.200 | Minor Third | Moderate | General use |
| **1.250** | **Major Third** | **Balanced** | **Default** |
| 1.333 | Perfect Fourth | Pronounced | Marketing |
| 1.414 | Augmented Fourth | Bold | Editorial |
| 1.618 | Golden Ratio | Dramatic | Headlines |

### Pre-composed Text Styles

| Style | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|-------------|----------------|
| h1 | 48px | 700 | 1.2 | -0.02em |
| h2 | 36px | 700 | 1.3 | -0.01em |
| h3 | 28px | 600 | 1.4 | 0 |
| h4 | 24px | 600 | 1.4 | 0 |
| h5 | 20px | 600 | 1.5 | 0 |
| h6 | 16px | 600 | 1.5 | 0.01em |
| body | 16px | 400 | 1.5 | 0 |
| small | 14px | 400 | 1.5 | 0 |
| caption | 12px | 400 | 1.5 | 0.01em |

---

## Spacing Grid System

### 8pt Grid Foundation

All spacing values are multiples of 8px for visual consistency.

```
Base Unit: 8px

Multipliers: 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8...

Results:
  0:  0px
  1:  4px  (0.5 × 8)
  2:  8px  (1 × 8)
  3:  12px (1.5 × 8)
  4:  16px (2 × 8)
  5:  20px (2.5 × 8)
  6:  24px (3 × 8)
  ...
```

### Semantic Spacing Mapping

| Token | Numeric | Value | Use Case |
|-------|---------|-------|----------|
| xs | 1 | 4px | Inline icon margins |
| sm | 2 | 8px | Button padding |
| md | 4 | 16px | Card padding |
| lg | 6 | 24px | Section spacing |
| xl | 8 | 32px | Component gaps |
| 2xl | 12 | 48px | Section margins |
| 3xl | 16 | 64px | Page sections |

### Why 8pt Grid?

1. **Divisibility**: 8 divides evenly into common screen widths
2. **Consistency**: Creates predictable vertical rhythm
3. **Accessibility**: Touch targets naturally align to 48px (8 × 6)
4. **Integration**: Most design tools default to 8px grids

---

## Accessibility Contrast

### WCAG Contrast Requirements

| Level | Normal Text | Large Text | Definition |
|-------|-------------|------------|------------|
| AA | 4.5:1 | 3:1 | Minimum requirement |
| AAA | 7:1 | 4.5:1 | Enhanced accessibility |

**Large text**: ≥18pt regular or ≥14pt bold

### Contrast Ratio Formula

```
Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)

Where:
  L1 = Relative luminance of lighter color
  L2 = Relative luminance of darker color

Relative Luminance:
  L = 0.2126 × R + 0.7152 × G + 0.0722 × B
  (Values linearized from sRGB)
```

### Which Step Passes

It depends on the brand colour, so do not use a fixed table: run
`scripts/token_contrast_checker.py`. When the brand hex fails as text or a fill it names the
lightest primary step that passes on the page background.

### Semantic Colors Accessibility

Each semantic colour carries a `contrast` label colour: the first of white, neutral-900
(`#111827`) and black that reaches 4.5:1 on `base`. With the bundled bases that is `#111827`
for all four, because white fails on them (2.15:1 on the warning amber):

```json
{
  "success": {
    "base": "#10B981",
    "light": "#34D399",
    "dark": "#059669",
    "contrast": "#111827"  // For text on base
  }
}
```

---

## Export Formats

### JSON Format

Best for: Design tool plugins, JavaScript/TypeScript projects, APIs

```json
{
  "colors": {
    "primary": {
      "50": "#f0f5fb",
      "500": "#3f85cc",
      "900": "#001428",
      "DEFAULT": "#0066CC"
    }
  },
  "typography": {
    "fontSize": {
      "base": "16px",
      "lg": "20px"
    }
  }
}
```

### CSS Custom Properties

Best for: Web applications, CSS frameworks

```css
:root {
  --colors-primary-50: #f0f5fb;
  --colors-primary-500: #3f85cc;
  --colors-primary-900: #001428;
  --colors-primary-DEFAULT: #0066CC;
  --typography-fontSize-base: 16px;
  --typography-fontSize-lg: 20px;
}
```

### SCSS Variables

Best for: SCSS/SASS projects, component libraries

```scss
$colors-primary-50: #f0f5fb;
$colors-primary-500: #3f85cc;
$colors-primary-900: #001428;
$colors-primary-DEFAULT: #0066CC;
$typography-fontSize-base: 16px;
$typography-fontSize-lg: 20px;
```

### Format Selection Guide

| Format | When to Use |
|--------|-------------|
| JSON | Figma plugins, Storybook, JS/TS, design tool APIs |
| CSS | Plain CSS projects, CSS-in-JS (some), web apps |
| SCSS | SASS pipelines, component libraries, theming |
| Summary (`--format text`) | Quick verification, debugging |

---

## Quick Reference

### Generation Command

```bash
# Default (modern style, JSON output)
python3 scripts/design_token_generator.py "#0066CC"

# Classic style, CSS output
python3 scripts/design_token_generator.py "#8B4513" classic css

# Playful style, summary view
python3 scripts/design_token_generator.py "#FF6B6B" playful summary
```

### Style Differences

| Aspect | Modern | Classic | Playful |
|--------|--------|---------|---------|
| Fonts | Inter, Fira Code | Helvetica, Courier | Poppins, Source Code Pro |
| Border Radius | 8px default | 4px default | 16px default |
| Shadows | Layered, subtle | Single layer | Same set as modern |

The bundled values live in `token-presets.json`; edit them there, not in the script.

---

*See also: `component-architecture.md` for component design patterns*
