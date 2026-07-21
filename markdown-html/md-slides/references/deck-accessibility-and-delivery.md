# Deck Accessibility and Delivery

An HTML deck is a web page pretending to be a presentation. That buys real
accessibility capability that native presentation formats lack — and introduces
failure modes that only appear in a room with a projector.

## Why HTML decks are worth the trade

| | HTML deck | Native presentation file |
|---|-----------|--------------------------|
| Version control | Diffable markdown source | Opaque binary |
| Distribution | One file, opens anywhere | Requires an app or a converter |
| Accessibility | Full semantic HTML, screen-reader capable | Depends on the app's export |
| Speaker notes | Toggled in-page, or printed | Requires presenter view |
| Offline | Yes, fully self-contained | Yes |
| Animation | Minimal by design | Extensive |
| Collaborative editing | Via git | Via the vendor's cloud |

The honest cost: **no animation, no transitions, no per-element builds.** If a
deck's argument depends on a five-step animated build, this is the wrong tool.
In practice that dependency is rare and usually indicates a slide doing too much.

## Accessibility

### Slide visibility and assistive technology

Hiding an inactive slide with `display: none` removes it from the accessibility
tree, which is correct — but only if the mechanism is consistent. The generated
deck does two things together:

```js
slide.classList.toggle("active", active);
slide.setAttribute("aria-hidden", active ? "false" : "true");
```

Setting `aria-hidden` without also hiding visually — or vice versa — produces
the two classic failures: a screen reader announcing all 40 slides at once, or a
visible slide that assistive tech insists is not there.

### Focus management

On slide change the deck moves focus to the new slide, which carries
`tabindex="-1"` so it is programmatically focusable but not in the tab order.

Without this, a keyboard or screen-reader user advances the slide and their
focus stays where it was — on the previous slide's content, now hidden. The
announcement never comes and the deck appears frozen. `preventScroll: true`
stops the browser from jumping the viewport while doing it.

### The slide counter as a live region

`<div id="counter" aria-live="polite">` announces "4 / 12" on each change. It
gives non-sighted users the positional awareness a progress bar gives sighted
users. `polite` rather than `assertive` so it queues behind the slide content
rather than interrupting it.

### Keyboard interface

| Key | Action | Note |
|-----|--------|------|
| Right / Down / Space / PageDown | Next slide | Space and PageDown match presenter remotes |
| Left / Up / PageUp | Previous slide | |
| Home / End | First / last slide | |
| N | Toggle speaker notes | |
| T | Toggle light/dark theme | |
| F | Toggle full screen | |

**Presenter remotes send PageUp/PageDown.** A deck that only binds arrow keys
fails with a clicker, which is discovered on stage. This is why both are bound.

Modifier combinations are ignored (`if (event.metaKey || event.ctrlKey) return`)
so browser shortcuts — Cmd+L, Ctrl+F — still work.

### Contrast at projection

Projected slides face conditions a monitor never does: ambient light, poor
projector contrast ratios, off-axis viewing, and washed-out blacks.

| Context | Minimum contrast | Note |
|---------|------------------|------|
| Monitor / screen share | 4.5:1 (WCAG AA) | Standard |
| Well-lit conference room | 7:1 | Treat AAA as the floor |
| Bright room, weak projector | 10:1 | Near-maximum contrast |

**[PROVEN] Present in light mode in a bright room and dark mode in a dark one.**
Dark themes look better on a laptop and wash out badly under ambient light; a
dark slide in a lit room turns mid-gray text invisible. The `T` key exists so
this is a decision made in the room, not an hour earlier.

### Type size at distance

The legibility rule of thumb: **1 inch of cap height per 10 feet of viewing
distance.** For a typical room with a rear row at 30 feet, that is roughly
3-inch capitals on the projected image.

Translated to the deck's scale: body text renders at `clamp(18px, 2.2vw, 28px)`,
so it grows with the viewport. The failure mode is authoring on a laptop where
2.2vw is small, and never checking full screen.

**Proof the deck at full screen on the actual display before presenting.** Tables
and code blocks are where this bites — they are set smaller than body text and
are the first thing to become unreadable from the back.

### Color is never the only signal

WCAG 1.4.1 applies to slides. A chart with three series distinguished only by hue
excludes roughly 1 in 12 men in the room. Add direct labels, distinct line
styles, or shape markers.

Direct labelling is better than a legend regardless of color vision — a legend
forces a lookup the audience does not have time for while listening.

## Delivery

### Speaker notes

Notes toggle in-page with `N`. There is no dual-screen presenter view; that
requires a second window and a synchronization channel, which conflicts with
single-file self-containment. Two workable approaches:

1. **[RECOMMENDED] Print the runsheet.** `notes_runsheet.py --format markdown`
   produces a timed sheet with notes. Paper does not crash, sleep, or mirror to
   the projector by accident.
2. **[RECOMMENDED] Open the deck twice.** Two browser windows on the same file;
   present one full screen on the projector, keep the other on the laptop with
   notes toggled on. They do not sync — you advance both — but it works with no
   extra machinery.

The `N` toggle itself is a trap when the laptop is mirroring the projector:
notes appear on the big screen. Know which mode you are in before pressing it.

### Handout printing

`@media print` in the deck theme puts each slide on its own landscape A4 page and
appends the speaker notes below each one via `content: attr(data-notes)`.

Forced light colors, positioned layout, and `break-after: page` per slide are all
applied automatically. Print to PDF for a handout that includes what you said,
not just what was projected.

### Pre-flight checklist

- [ ] Opened full screen on the presentation display, not just the laptop
- [ ] Advanced through every slide with the actual remote or keyboard
- [ ] Theme chosen for the room's lighting (`T`)
- [ ] Tables and code blocks legible from the back row
- [ ] Images load — a broken relative path shows an alt-text box on the projector
- [ ] Runsheet total inside the slot, with Q&A time left over
- [ ] Notes printed or a second window ready
- [ ] Browser chrome hidden; notifications and screen sleep disabled

### The self-containment check

The deck is only truly portable if its images are embedded. A deck referencing
`figures/chart.png` is a folder, not a file, and it will break when emailed.

For genuine single-file output, embed images as data URIs. Base64 adds ~33%
overhead, so downsample first — a 200KB chart becomes ~270KB inline, which is
fine; a 4MB photograph becomes 5.3MB, which is not.

## Anti-patterns

### The deck that only works on the author's machine
Relative image paths, a system font nobody else has, a stylesheet loaded from
disk. Discovered in the room. Test by copying the single HTML file to a different
directory and opening it there.

### Presenting in dark mode by default
It looks best where you built it — a dim office at a laptop — and worst where you
present it. Decide in the room.

### Animation nostalgia
Rebuilding per-element builds with custom JavaScript because the previous tool
had them. Each one is bespoke code in a file that must stay self-contained, and
almost every build is a slide that should have been two slides.

### Notes as a script
Writing full sentences to read aloud. Notes are cues — the number to remember,
the transition, the question to expect. A read script sounds read, and the
runsheet's timing estimate becomes a floor rather than an estimate.

### Skipping the full-screen proof
Authoring in a windowed browser and presenting full screen. Type scales with
viewport width, so every size decision changes. This is a two-minute check that
prevents the most common in-room failure.
