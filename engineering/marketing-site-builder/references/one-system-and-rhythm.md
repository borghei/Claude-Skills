# One System and Section Rhythm

A page looks designed when a visitor cannot find two ways of doing the same thing. It looks
assembled when every section was solved on its own. This file sets the rules for the system a page
is built on, the rhythm its sections follow, and how its edges line up. `scripts/consistency_check.py`
counts what can be counted; the rest is a reading of the rendered page.

## 1. What "one system" means

One of each, used everywhere:

| Part | The rule | Why |
|---|---|---|
| Spacing scale | 8 to 10 steps on a 4px grid (4, 8, 12, 16, 24, 32, 48, 64, 96, 128) | Off-scale gaps (13px, 37px) are what makes a layout look hand-nudged |
| Radius family | 2 to 4 values: controls, panels, cards, and a pill if the button look needs one | Five radii means five people designed the page |
| Colour | One near-black ink, one muted text colour, two or three grounds, one hairline, one accent | Colour should come from the photographs and the product, not the interface |
| Accent | One hue, two at most (a second only for a state such as an error) | Three accent hues read as a template's demo palette |
| Type | Two families at most: one display, one text. Sizes on a scale of 7 to 9 steps | A third family is almost always a leftover from a template |
| Buttons | One primary and one secondary style; one filled button marks the main action in any view | A ghost, a gradient and a pill button on one page tell the reader nothing about priority |
| Cards | One card recipe (padding, radius, border or ground, no shadow at rest) | Mixed card styles break the grid more than mixed content does |
| Shadow | None at rest, or one soft shadow for raised layers; two styles at most | Shadows used as decoration age a page faster than anything else |
| Link look | One underline style for running text, one for nav and footer | |
| Motion timing | 5 durations for the interface (hover in, hover out, press, image in, image out) plus one for the entrance | See `imagery-motion-effects.md` |

The budgets in `assets/site_budget.json` encode these as numbers. They are house defaults: a
design system with a documented reason for a sixth radius can raise the budget in its own copy of the
file. What it should not do is raise the budget to make a red check go green.

## 2. Tokens first, values never

Write every value once, as a custom property on `:root`, and use `var(--token)` in rules. The
checker resolves `var()` references, so tokens do not hide anything from it; what they do is make
the page's real scale visible in one place, and make the "% through var()" figure a quick read of
how disciplined the stylesheet is. Under 50% usually means values were typed in as needed.

[RECOMMENDED] Name tokens by role, not by value: `--s-4` or `--gap-card`, never `--16px`.

### Colour rules worth keeping

- The interface stays almost neutral. As a rough test, cover the photographs: what is left should be
  ink, grounds and one accent.
- Ink is a near-black, often slightly warm or cool to match the photographs. Pure `#000` text on a
  white ground is harsh at body size; the checker warns on it.
- Body text people read meets 7:1 against its ground where possible, and never less than 4.5:1.
  Muted text is for labels, dates and metadata, not for paragraphs.
- Highlight by weight or size, not by colouring words. Colour inside a heading once a page at most.
- Gradients, glows and tinted panels are effects, not colour choices. They follow the effect budget
  in `imagery-motion-effects.md`.
- The interface stays 90 to 95% neutral. The accent marks the main button, links, focus and state,
  and covers under about 3% of any screen elsewhere; its label meets 4.5:1 on it.
- Take the accent from the client's material: the product, the shopfront paint, the packaging, the
  logo. Violet and lavender (OKLCH hue roughly 270 to 330 degrees) are the default hue of generated
  pages; `style_rules.py` warns on them so the choice is made on purpose, not by habit. A real
  third-party logo keeps its own colours.
- Words sit on a photograph only in the hero or one closing band, on a calm, dark, empty part of the
  crop (at the phone crop too) or on a solid box. Never a scrim or gradient laid over a photograph to
  rescue contrast, and never on a place page.
- `style_rules.py` computes contrast where one rule sets both the text colour and a solid ground;
  pairs set in different rules still need the screenshot check.

### Type rules worth keeping

- Body text 16px or larger, line height 1.5 to 1.7, lines of 45 to 75 characters.
- One size per kind of element across the page: every card title the same, every figure the same.
- Sentence case for headings, labels and buttons. No tracked all-caps labels over every section.
- Every word is live text, never baked into an image.
- Load only the weights in use. Two families with two weights each is four files; that is the budget.
- Headlines carry weight through size and tight tracking (about -0.5% to -4% at 40px and up), at
  400 or 500, never 700 to 900. Bold-and-big is the template look; `style_rules.py` warns on it.
- Each heading level is at least 1.3 times the next from tablet width up. A figure never outgrows the
  h2. Display text of 40px or more outside a grid item is a heading and is marked up as one.
- Nothing on the page under 13px: legal lines, notes and labels included. Labels are 13px at
  weight 500, in sentence case, never tracked capitals or small caps.
- Pick a pairing with a reason (the trade, the client's logo, a period). The faces every template
  ships (Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Space Grotesk and their kin) are a
  `default-face` warning: keep one only when the client's brand already uses it, and say so.
- Load web fonts with `font-display: swap` (or `display=swap` on a hosted link).

## 3. Section rhythm

The page is planned as a list of screens before anything is built (see
`assets/site-plan-template.md`). Each section has one idea and one picture.

| Rule | Detail |
|---|---|
| One section per screen | At 1440x900, a section is one screen tall or two, not 1.4. The next section's heading should not peek in at the bottom of a screenshot. |
| The hero is alone on the first screen | It says what is sold, for whom or where, with one hard fact and the main action inside it. |
| Heading first, top-aligned | Every section opens with its h2 at the same top padding. Never centre a short block vertically in a tall section. |
| Separation by ground or space | A change of ground colour across the full width, or space. No rules, shadows or inset boxes between sections. |
| Short content merges | A logo row, a quote, a stat line or a two-question FAQ is not a section. It joins the section above as its last element. |
| One main action per screen | The same action can repeat down the page (hero, close), with the same wording each time. |
| Close and footer together | The final call to action and the footer form one last section, not two thin bands. |

What each section may carry, the one-object rule, layout repeats and proof objects:
`sections-cards-forms.md`, section 1.

[RECOMMENDED] A landing page holds 5 to 9 sections. Past ten, readers lose the order; split into
sub-pages. `page_gate.py` warns past the `max_sections` budget.

### Words per screen

Copy expands to fill space unless it has a budget. Rough targets per screen at desktop width:

| Page kind | Words per screen | Whole page |
|---|---|---|
| Place (cafe, shop, guesthouse) | 40 to 60 | under 700 |
| Product or service | 40 to 80 | under 900 |
| Software, tools, hardware | 60 to 90, counted outside UI mock-ups | under 1,100 |

When a section runs over, cut in this order: the second sentence under a heading, card bodies down to
one sentence, the fourth card, a list a picture already shows.

## 4. Equal edges

Every block sits on the same content edges: one wrapper (`.wrap`) with one max width and one side
padding, used by every section, the header and the footer.

- The logo starts on the left edge; the header's button ends on the right edge.
- Grids use the wrapper's columns. Nothing is pushed out to one side for "interest".
- Full-bleed pictures bleed on both sides or neither.
- No horizontal scroll at 320px. Nothing overlaps anything at any width.

Edges cannot be measured from source; check them on screenshots at 1440, 1024, 768 and 390 (the
browser checklist in `finish-gate.md`).

## 5. The hero

- Fills the first screen and only the first screen. Content ends above the fold at every width.
- The h1 names the category and the buyer or place, in 2 to 8 words; never a slogan or a question.
- One sub-line, 15 to 30 words: how it works and the main benefit, or the place's facts.
- At most two buttons; one on a place.
- The picture is the work: the product, the room, the real interface. Never a mood image or an
  abstract shape standing in for the thing sold.
- The hero image loads eagerly with `fetchpriority="high"`; every other image is lazy.

## 6. Shell and chrome

- The body renders a header, `main`, the footer and nothing else fixed: no chat bubble, cookie
  pill, back-to-top button, newsletter modal or floating badge unless the client requires one.
- The header is solid, the same at every scroll depth: no blur, transparency, shrink or hide.
- Forms: visible labels above fields, 16px text, errors under their field naming what to type, a
  success line only after a real send.
