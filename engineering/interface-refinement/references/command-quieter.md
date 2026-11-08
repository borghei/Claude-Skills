# quieter — lower the volume, keep the point of view

**Job:** reduce visual intensity on a surface that shouts, without sliding into grey generic.

**Run when:** the detector reports `side-stripe-border`, `glow-shadow`, `hard-offset-shadow`,
`repeating-stripes`, `grid-line-background`, `radial-glow`, `organic-clip-path` or
`hairline-wide-shadow`; a critique says "noisy", "busy", "tiring".

## By mode

- **Persuade / Showcase:** a more restrained palette, more air, fewer simultaneous effects. The
  drama drops a step; the idea stays.
- **Operate / Read:** less background colour, flatter containers, less motion. The tool recedes
  behind the task.

## Change

- **Effects:** remove glows, colour halos, radial hazes, decorative stripes, grid paper and
  clip-path blobs. Elevation becomes
  one neutral shadow with a vertical offset, or a 1px border, never both on every card.
- **Stripes:** a side stripe on a card becomes a labelled status inside the card, or nothing.
- **Colour:** lower saturation on large areas; keep saturated colour for the action and real
  status. Grey text on a coloured ground becomes a shade of that ground's hue.
- **Weight:** step heavy weights down (black to bold, bold to medium) where they are not headings.
- **Motion:** shorter distances, decelerating curves, no bounce, no idle loops.

## Do not touch

- Hierarchy. Quieter does not mean everything the same size and weight.
- The brand palette's identity: desaturate within the hue, do not swap hues.
- Affordances: buttons must still look pressable, links still look like links.
- A deliberate brutalist or neon direction the context file records; that is not noise.

## Steps

1. Rank the loud sources: effects, colour area, weight, motion, density. Fix the top two first and
   look again; the rest may already read calmer.
2. Decide which one or two elements stay loud (the primary action, the key figure).
3. Apply the reductions through tokens where they exist, so neighbours stay consistent.

## Verify

- Detector: the routed rules no longer fire on the target.
- The primary action is still the first thing found in a squint test.
- Covering the logo, the page is still recognisably this product, not a neutral template.
- Contrast pairs still pass (`ui_rules.py --contrast`) after desaturation.

## Hand-off

`polish`.
