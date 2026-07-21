# WCAG Contrast Reference

Everything needed to reason about, compute, and remediate color contrast in a
document theme — the math, the thresholds, the exemptions, and the failure modes
that automated checks miss.

## The math

### Step 1 — sRGB channel linearization

Screen color values are gamma-encoded. Luminance math requires linear values. For
each channel `C` in `{R, G, B}` with an 8-bit integer value `v`:

```
c = v / 255

if c <= 0.03928:  C_lin = c / 12.92
else:             C_lin = ((c + 0.055) / 1.055) ^ 2.4
```

The `0.03928` breakpoint and the `12.92` slope come from the sRGB transfer
function's linear toe near black. Skipping the toe and using a plain 2.2 power
curve produces errors of several percent in dark colors — enough to flip a
borderline 4.4 into a reported 4.5.

### Step 2 — relative luminance

```
L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
```

The coefficients are the luminous efficiency of each primary. **Green carries 71%
of perceived brightness; blue carries 7%.** This single fact explains most
surprising contrast results:

- Pure blue `#0000ff` on white is only **8.6:1** despite looking very dark.
- Pure yellow `#ffff00` on white is **1.07:1** — effectively invisible.
- Pure green `#00ff00` on white is **1.37:1**, worse than mid-gray.

A designer's sense of "dark enough" tracks saturation; the formula tracks
luminance. Saturated warm colors are the usual casualties.

### Step 3 — contrast ratio

```
ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

The `+0.05` term models ambient screen flare. It bounds the ratio to the range
**1:1 (identical) to 21:1 (pure black on pure white)** and it is why no real
color pair ever reaches 21:1 unless it is literally `#000` on `#fff`.

Contrast is symmetric: swapping foreground and background gives the same ratio.
The validator sorts the two luminances rather than trusting the caller's labels.

## The thresholds

### WCAG 2.1 conformance levels

| Content | AA | AAA |
|---------|-----|------|
| Body text (< 18.66px regular, < 24px bold) | **4.5:1** | **7:1** |
| Large text (>= 18.66px regular, >= 24px bold) | **3:1** | **4.5:1** |
| UI components and graphical objects | **3:1** | 3:1 (no AAA criterion) |
| Decorative / inactive / logo | no minimum | no minimum |

Success criteria: **1.4.3 Contrast (Minimum)** is the AA text rule, **1.4.6
Contrast (Enhanced)** is AAA, and **1.4.11 Non-text Contrast** is the 3:1 rule
for components and meaningful graphics.

### The large-text boundary

"Large" is **18.66px (14pt) bold** or **24px (18pt) regular**. The pt-to-px
conversion at 96dpi is `px = pt * 4/3`. This matters when a modular scale puts an
H3 at 23.5px — it is *not* large text, and a 3.2:1 heading color fails.

Check the generated type scale before assigning a usage class. In the sample
theme's 1.25 scale on a 17px base, `lg` is 26.56px (large), `md` is 21.25px (not
large, despite feeling like a heading).

### What the `decor` class is for

WCAG 1.4.11 applies to graphics **required to understand the content** and to UI
component boundaries that indicate state. It explicitly does not apply to purely
decorative elements.

A table rule, a horizontal divider, or a subtle card edge is decorative: removing
it loses no information, because the table still has headers, cells, and
alignment. Enforcing 3:1 on those produces heavy-handed documents and pushes
designers to disable the check entirely — the worst outcome.

The validator therefore offers a `decor` usage class with a **1.5:1** floor. That
number is not from WCAG; it is a practical visibility floor. Below roughly 1.5:1
a rule is invisible on a mid-quality laptop screen at typical brightness, which
means it is not doing its decorative job either.

**Be honest about the classification.** If a border is the *only* thing
distinguishing an input from its surroundings, or the only thing separating two
adjacent data regions, it is `ui` and it needs 3:1.

### Exemptions worth knowing

| Exempt | Condition |
|--------|-----------|
| Inactive controls | Disabled and not operable |
| Pure decoration | Conveys no information, can be removed losslessly |
| Logotypes | Text that is part of a brand mark |
| Incidental text | Text in a photograph that is not the point of the photograph |

Exemptions are narrow. "It is just a caption" is not an exemption — captions are
body text and need 4.5:1.

## Contrast targets by document element

Beyond the legal minimum, these are the values that produce comfortable long-form
reading. Treat the WCAG column as the gate and the target column as the goal.

| Element | WCAG minimum | Practical target | Note |
|---------|--------------|------------------|------|
| Body text | 4.5:1 | **10-16:1** | Below ~8:1 sustained reading tires; above ~17:1 causes halation on OLED |
| Headings | 3:1 (if large) | 12-18:1 | Headings are scanned; they can be the darkest thing on the page |
| Captions / footnotes | 4.5:1 | **5.5-8:1** | Must stay clearly subordinate to body but remain readable |
| Inline links | 4.5:1 | 5-8:1 | Also needs 3:1 *against the body text* if color is the only cue |
| Code text | 4.5:1 | 9-14:1 | On its own tinted surface, not the page surface |
| Table rules | none | 1.5-3:1 | Decorative unless load-bearing |
| Focus ring | 3:1 | 3-6:1 | Against **both** the element and the adjacent background |

### The maximum-contrast trap

Pure `#000` on pure `#fff` is 21:1 and is **worse** than ~16:1 for extended
reading. On high-brightness and OLED displays the maximum-contrast pair produces
halation — glyph edges appear to bleed — and readers with astigmatism or dyslexia
report the strongest discomfort here.

**[RECOMMENDED] Use a very dark neutral (not black) on a very light neutral (not
white) for body copy.** `#0f172a` on `#ffffff` is 17.9:1; `#0f172a` on `#f8fafc`
is 17.1:1. Both are far above the gate and materially more comfortable.

### The link-color trap

WCAG 1.4.1 (Use of Color) requires that color is not the **only** means of
conveying information. An inline link distinguished from body text purely by
color must satisfy **3:1 against the surrounding text color** — not just against
the background.

Do the arithmetic on the sample theme: body `#0f172a` against link `#0369a1`
lands at **3.01:1** — passing by one hundredth. A margin that thin is not a pass
you can build on; any future darkening of the link or lightening of the body text
breaks it silently. Two ways out, and the second is better:

1. Push the link color further from the body color (usually lighter, which then
   fights the 4.5:1 requirement against the background — a narrow corridor).
2. **[PROVEN] Underline inline links in body copy.** The underline is a non-color
   cue, 1.4.1 is satisfied regardless of hue, and it is what readers expect. Only
   drop underlines in navigation and lists where position already signals
   linkness.

## Remediation recipes

### A pairing fails by a small margin (within ~15%)

Move the foreground one ramp step. A well-formed neutral ramp step is worth
roughly **1.25-1.4x** of ratio, so one step reliably clears a near miss without
visibly changing the design.

### A pairing fails badly (below ~60% of target)

The role is pointing at the wrong end of the ramp. Check the mode: this is the
signature of a dark-mode role that was copied from light without re-anchoring.

### An accent fails in dark mode only

Move the dark-mode accent 2-3 steps lighter. Saturated mid-tones lose contrast
against dark surfaces faster than neutrals do, because their luminance is already
low. `accent.600` (#0369a1) on near-black (#020617) is only
**3.4:1**; `accent.300` (#7dd3fc) reaches **12.1:1**.

### A pairing cannot be fixed without breaking the palette

Change the **surface**, not the text. Lightening `surface-raised` from ramp 100 to
ramp 50 lifts every foreground on it simultaneously. Fixing five text roles
individually is five chances to introduce inconsistency.

### AAA is failing across the board

Expected, and usually acceptable. AAA body text at 7:1 forces a narrow palette:
mid-tone accents and warning colors rarely reach it against white. Pursue AAA
when the audience is known to include low-vision readers, when the document is a
public-sector deliverable under a AAA procurement requirement, or when the
content is dense reference material read for hours. Otherwise ship AA and use the
practical targets above, which exceed AA anyway for the elements that matter.

In the sample theme, AA passes on all 20 pairings while AAA fails 6 — the
failures are `link`, `warn`, and `accent`, exactly the saturated mid-tones. That
is the normal shape of an AAA run.

## What automated contrast checking does not catch

A green validator run is necessary, not sufficient. These require human review:

1. **Text over images or gradients.** The computed background is one flat color;
   a photograph is thousands. Needs a scrim, a solid plate, or a text shadow —
   and none of those can be verified by pairing math.
2. **Semi-transparent overlays.** `rgba(0,0,0,0.5)` over an unknown backdrop has
   no fixed luminance. Composite the color against the actual backdrop first,
   then feed the resulting opaque hex to the validator.
3. **State changes.** Hover, focus, and visited-link colors are pairings too, and
   they are the ones most often left out of the `pairings` block.
4. **Adjacent-color contrast.** Two chart series that both pass against the
   background can be indistinguishable from each other. The check is
   foreground-vs-foreground, which the pairings block does not model by default.
5. **Color-blind distinguishability.** Red/green pairs at identical luminance
   pass every contrast test and are invisible to a deuteranopic reader. Contrast
   ratio is a luminance metric; it is hue-blind by construction.
6. **Rendered weight.** A 300-weight font at 4.5:1 reads worse than a 400-weight
   font at the same ratio. Thin type needs headroom above the minimum — treat
   4.5:1 as the floor for 400-weight and target 7:1 for anything lighter.

## Running the checks in CI

The validator exits non-zero when any pairing fails, which makes it a gate:

```bash
python3 markdown-html/design-system/scripts/contrast_validator.py \
  --input tokens.json --level AA --format json
```

Two useful modes:

- `--all-pairs` ignores the declared `pairings` block and crosses every
  foreground role against every surface-like role. Use it when adding roles — it
  finds combinations nobody declared but a stylesheet will eventually produce.
- `--no-gate` reports without failing. Use it for the AAA run so an aspirational
  target does not block a release, while the AA run stays a hard gate.

**[RECOMMENDED] Gate on AA, report on AAA.** Two invocations, one blocking.
