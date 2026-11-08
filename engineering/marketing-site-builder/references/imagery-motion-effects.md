# Imagery, Motion and Effects

The kind of business decides what a page may show and how much may move. A cafe shown through a
shader looks like a template; a developer tool shown only through stock photographs of laptops looks
like nobody built the product. Set the kind first, then follow its column.

## 1. The four kinds

| Kind | Examples | Leads with |
|---|---|---|
| `tech` | SaaS, AI and developer tools, fintech apps, games, hardware and devices | The product's own interface as live HTML, or the device in photographs |
| `product` | A chair, a bike, coffee beans sold online, a skincare line | Photographs of the product, whole and large, a different view in each section |
| `service` | Clinics, law firms, agencies, studios, trades | Photographs of the people, the rooms and the finished work |
| `place` | Cafes, bakeries, guesthouses, shops, gyms, local studios | Photographs of the room, the counter, the goods, two or more per screen |

A maker that also opens its door (a bakery with a web shop) is a place. Declare the kind on the page
as `<html data-kind="...">` so `page_gate.py` can apply the right budget.

## 2. Photographs

### Where pictures come from, in order of preference

1. **The client's own,** shot for the site or on a phone. A half-day with a local photographer beats
   any library. Hand the client a shot list: the front from across the street, the room from the
   door, the counter or workbench, three products on one surface, hands at work, one detail. Daylight,
   no flash, no filters, both landscape and portrait.
2. **Licensed stand-ins** of the same kind of thing, used only until the client's arrive, and listed
   as stand-ins in the handover report. Never shown with another business's name or logo visible.
3. **Library stock** only in detail slots (hands, tools, materials, a process), never for the hero,
   a room, a shopfront, a product or a person, and never more than one picture in three.
4. **Nothing,** when nothing true fits: the real interface, or type. Never a near-fit or a mood shot
   standing in for the subject.

### Rules for every picture

- `alt` on every `<img>`: what it shows, in a sentence, for content images; `alt=""` for decoration.
- `width` and `height` (or a CSS `aspect-ratio`) on every image, so nothing shifts while loading.
- The hero image loads eagerly with `fetchpriority="high"`; every other image has `loading="lazy"`
  and `decoding="async"`.
- Serve AVIF or WebP through `srcset` at no more than twice the displayed width. Keep the hero under
  about 400 KiB and every other image under about 250 KiB.
- A photograph below the fold is an `<img>`, not a CSS background (backgrounds cannot be lazy).
- No captions explaining a picture. A heading names the set; a product's name and price sit in its
  card. Licence credits go in one footer line.
- Never filter, tint, duotone or grade a photograph. Never put words on a busy part of one.
- The same picture never appears twice on a page.

`page_gate.py` checks alt, dimensions, lazy loading, the eager hero, captions and the byte weight of
local image files. Whether a photograph is the right subject is a judgement for the screenshot pass.

## 3. Motion: three layers and nothing else

Every page moves in exactly three ways.

1. **The hero's entrance,** once on load: the heading arrives, then the sub-line and buttons, then
   the picture settles. About one second in all, then it stands still.
2. **One or two moments,** in sections of their own, that a visitor will remember: photographs
   that change in place as the reader scrolls through a pinned section, a statement whose words light
   up in reading order, a photograph that develops. Two on a long page (eight sections or more),
   never three.
3. **The hover and press layer** on every link, button, linked card and linked photograph.

Nothing else moves. In particular, no card, row or tile fades or slides in as the page scrolls; no
parallax on text; no scroll-jacking or smooth-scroll library; no carousel or auto-rotating tabs.

### House timings

| Interaction | Movement | Duration |
|---|---|---|
| Button hover | Fill steps toward the ink; box rises 1px | 150ms in, 120ms out |
| Button press | Sinks 1px below rest, scale 0.985 | 90ms |
| Linked card hover | Lifts 2px; border darkens one step | 150ms in, 120ms out |
| Linked photograph hover | Scales 1.02 to 1.03 inside its frame (`overflow: hidden`) | 600ms in, 400ms out |
| Link hover | One underline drawn left to right | 150ms |
| Menu panel | Fades in with a 6px drop | 150ms open, 120ms close |
| Focus | 2px ring in the accent colour, 2px offset | none: focus never animates |

That is five durations in all (90, 120, 150, 400 and 600ms). The default `durations` budget is six:
these five plus one for the hero entrance or a loop. `consistency_check.py` counts every time in a
`transition` or `animation`, delays included, so stagger the entrance with delays drawn from the
same values. One UI easing curve for every step (an ease-out such as `cubic-bezier(.2,.8,.2,1)`), one curve
for entrances that settle, linear for loops. No bounce, no overshoot. A UI transition over about
700ms feels sluggish; `consistency_check.py` warns on it.

### Rules that keep motion cheap and safe

- Animate `transform` and `opacity` (and colour on hover). Never `width`, `height`, `top`, `left`,
  `margin` or `padding`; never `transition: all`. `page_gate.py` warns on both.
- Hover effects only for a fine pointer: `@media (hover: hover) and (pointer: fine)`.
- Every page that moves has a `@media (prefers-reduced-motion: reduce)` rule under which everything
  rests and nothing stays hidden. `page_gate.py` fails a page that moves without one.
- Anything that moves for more than five seconds has a pause control.
- Content is complete without script: motion only adds to a page that already reads whole.
- The plan names each motion and its purpose in a few words ("hero entrance: the name arrives, then
  what to do"). A motion with no purpose is cut.

### Loops and counts (tech pages only)

- One timed loop a page, in the hero or the one visual frame; one count a page, its final figure in
  the HTML so it reads without script, under reduced motion and on phones. Never a year, price or
  phone number as a count.
- A card loop cycles in 2.5 to 4 seconds, starts on its finished picture and holds it for the last
  10 to 15% of each cycle, so a screenshot never catches an empty window. One subject changes per
  cycle; the card, its panel and the window never move.
- Never two self-moving things on one screen, never two loops in one panel. Anything still moving
  five seconds after it is seen has a pause button, the same size and place on every card.
- Timed loops start on load and never start or stop on scroll; an observer may only mount them lazily.
- Every moment has a still: under reduced motion, without script and where a phone cannot run it,
  it shows its finished frame with its text live and readable.

## 4. Effects and their budget

An effect is anything drawn by a shader, a canvas, WebGL or a heavy CSS treatment: animated grounds,
3D objects, particle fields, gradients and glows, glass (`backdrop-filter`), blur filters, blend
modes, autoplay video, and the libraries that drive scroll scenes. Utility classes count the same
as the CSS they compile to: `bg-gradient-to-r`, `backdrop-blur-md` and `mix-blend-multiply` are
effects, and a translucent blurred header is glass.

| Kind | Effects allowed | Instead |
|---|---|---|
| `tech` | One per page: a hero ground, one 3D object or one scene, mounted lazily, with a still fallback | Real interface fragments in cards; small diagram cards |
| `product` | None (a product render only when the brief asks for 3D) | Photographs, flat colour, type |
| `service` | None | Photographs, flat colour, type |
| `place` | None | Photographs, flat colour, type |

[RECOMMENDED] On tech pages keep live WebGL contexts to four at most, render at a pixel ratio of 1.5
or less, draw still grounds once and release the context, and give every effect a poster image shown
first and kept when the shader fails.

The subject comes before the effect. An effect never stands where the product, the device, the
interface or the room should be.

## 5. Weight budget

These are static-checkable proxies for a fast page; real timing needs a browser (see
`finish-gate.md`).

| Item | Warn | Fail |
|---|---|---|
| Single local image | over 350 KiB | over 700 KiB |
| All local images | over 1,200 KiB | over 2,400 KiB |
| Font families | 3 | 4 or more |
| Font files | over 4 | |
| `<img>` without dimensions, or below the hero and not lazy | 1 to 3 | 4 or more |
| Scripts in `<head>` without `defer`, `async` or `type="module"` | each | |
| Large inline `data:` image | over 40 KiB | |

All numbers live in `assets/site_budget.json`.
