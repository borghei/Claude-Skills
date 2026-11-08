# Interface context: (product name)

<!-- Save as interface-context.md at the project root. Replace every line in parentheses.
     Lint with: python3 scripts/context_linter.py --input interface-context.md -->

## Platform

(one of: web, ios, android, cross-platform)

## Users and jobs

- Primary: (who, in what situation, doing which job; one sentence)
- Job: (what they must get done here and what "done" looks like)
- Secondary: (other audience, only if confirmed)

## Purpose and positioning

- Purpose: (what the product does and what success means)
- Positioning: (the mechanism or claim a neighbouring product could not truthfully copy)

## Surfaces

<!-- One line per surface: "- <route or screen>: <mode> - <job>". Modes: persuade, operate, read, showcase. -->
- (route): (mode) - (the visitor's job on this surface)

## Voice and terms

- Voice: (one or two sentences on how the product speaks, and how it speaks under stress)
- Terms: (preferred term (never "other term")), ...
- Numbers: (currency, date and unit formats)

## Evidence on hand

<!-- Each line needs a path or URL, or a stated absence ("none, do not invent"). -->
- (asset): (path)
- Testimonials: (path, or "none, do not invent")

## Principles

<!-- Two to five durable decisions the team can cite in review. No visual recipes. -->
- (principle)

## Brand commitments

<!-- Optional: name, voice, assets or identity constraints the owner made binding. Delete if none. -->
- (commitment)

## Constraints

- Accessibility: (standard, e.g. WCAG 2.2 AA)
- Locales: (languages and their expansion)
- Browsers and devices: (support matrix)

## Visual system

<!-- Written by the `document` command from shipped code, or seeded by the owner. -->

### Palette roles

- surface: (colour)
- text: (colour)
- text-muted: (colour)
- action: (colour)
- action-text: (colour)

### Type roles

- body: (family), (size)px/(line-height), (weight)
- heading: (family), (size)px/(line-height), (weight)

### Spacing scale

- steps: (e.g. 4, 8, 12, 16, 24, 40, 64)

### Radius

- control: (px)
- container: (px)

### Elevation

- resting: (none, 1px border, or a shadow)
- raised: (shadow, and which components may use it)

### Layout

- content width: (e.g. 72rem; prose capped at 65ch)
- grid: (columns and breakpoints)

### Components

- button: (shape, fill rules, states)
- field: (label, hint and error placement)

### Motion

- durations: (e.g. 150ms, 250ms, 400ms)
- easing: (curve)
- reduced motion: (what happens instead)

### Named rules

- **The (Name) Rule.** (one sentence the team can cite in review)

### Refusals

<!-- Detector rule ids this product refuses; see references/detector-rules.md. At least three. -->
- (rule-id)
