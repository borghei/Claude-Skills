# bolder — raise one section to the conviction the rest already has

**Job:** amplify a named section that reads flat, using the system's own strongest moves.

**Run when:** a critique calls a section "safe", "bland" or "forgettable"; a persuade page whose
hero or proof section looks like a template. Never routed from the detector: no finding means
"too quiet".

## By mode

- **Persuade / Showcase:** this is the home of bolder. One decisive move per section.
- **Operate / Read:** bolder is rare here. Usually it means a sharper type scale or a confident
  colour region in the shell, not effects. The router drops it on these modes unless asked.

## Change

- Scale: the display size and weight the system already owns, at full strength for this section.
- Contrast of density: let the section be noticeably denser or airier than its neighbours, so it
  reads as a peak in the scroll.
- The system's own motif or signature device, used here more fully.
- Content: real evidence (a product screen crop, a real number with its source) instead of a
  decorative image, when the owner can supply it.

## Do not touch

- Anything outside the named section. Neighbours stay exactly as they are.
- The system's primitives: no new colour, font, radius, shadow or token without the owner's
  approval. If the system genuinely cannot express the idea, stop and ask, naming the exact
  addition and the job it would do.
- Claims. Keep existing facts; ask for evidence rather than inventing it.

## Steps

1. Look at what neighbouring sections do that the flat one does not. Usually the flat section has
   opted out of the system's strongest device.
2. Pick one move. Write it in one sentence before editing.
3. Make that move completely, then quiet what surrounds it so it reads.
4. **Skeleton test:** blank out the copy. Does the structure alone still show what the section is
   and why it matters? If boldness lives only in the words, it is not in the design.

## Verify

- `git diff` touches only the named section's markup and styles.
- No new colour, font or radius values appear in the diff (search the diff for `#`, `rgb(`,
  `font-family`, `border-radius`).
- Before/after screenshots at phone and desktop width; the section is the clear peak.
- Detector on the target exits 0 at `--fail-on medium` (bolder must not buy volume with glows,
  gradient text or stripes).

## When the owner asks for "all-out"

A request to go far past the current look (scroll-driven scenes, shader or canvas backgrounds,
physics-based motion) is still a bolder pass on one named section, with three extra conditions:

- **Propose before building.** Describe two or three directions in a sentence each, with their
  cost (bundle weight, device support, accessibility risk), and let the owner pick.
- **Progressive enhancement.** The section must read completely with the effect off: no script,
  `prefers-reduced-motion: reduce`, or an older device. Gate the effect behind feature detection.
- **A budget.** The first screen still paints fast and the effect holds a steady frame rate on a
  mid-range phone; if it cannot, scale it down or drop it. Verify in a real browser, not by reading
  the code.

## Hand-off

`polish`. Never pair with `quieter` on the same target in one plan; pick the direction first.
