# Sections, Cards, Forms and the Shell

What goes in each section, how a card is built, how a form behaves, and what the page frame holds.
`one-system-and-rhythm.md` sets the tokens and heights; this file sets the content rules that make a
page read as built for one client. `access_links_check.py` checks the parts that show in source.

## 1. What each section carries

| Rule | Detail |
|---|---|
| Every section shows the real thing | A photograph, the client's interface, real tool icons, a diagram, or (tech only) the one effect. Sections without a picture are allowed only for a price list, an FAQ, a specs table, a booking form or one statement moment, once each, and two of them are never neighbours. |
| One object does not carry the page | The product or the hero object shown whole leads the hero and at most two more sections. The rest carry another kind of visual the material supports: the product in use, its parts close up, the people, the room, a diagram, a type moment. A new angle or a recolour of the whole is the same object again. |
| Write the visual kind on each plan line | object, use, parts, people, place, interface, diagram, type, slot. Three object lines at most. |
| Layouts repeat at most twice | 2x2, bento, three cards, split, open tiles: each at most twice a page, and neighbouring sections never share one. |
| Calm after busy | On product, service and software pages, a calm section (prices, a quote, the FAQ) follows at most two visual ones, and the last third of the page is calmer before the close. |
| One idea per section | One h2, one action besides the main one at most. A two-screen section holds one list, table or form, or one idea in two groups, never two ideas. |
| Short blocks merge | A quote, a logo row, a stat line or a two-question FAQ joins the section above as its last element, with no heading or ground of its own. |
| Proof as small exact objects | A named quote with a face, a footnoted figure, a rating line or real customer logos with permission, all from the brief. No row of big numbers, no check-icon list, no logo wall. |
| The client's own assets get slots | A trailer, screenshots, CAD renders or key art the brief names each get a frame at the file's final ratio that reads finished now (a poster still, a stand-in photograph of the same kind of thing), named in a comment for the client's file. Never an empty or grey frame, never a line saying the file is missing. The report lists every slot. |

### By kind

- **Product page:** the product big, whole, most of its frame; a different picture in each section,
  never the same view twice; every promise in a headline pictured (a family bike shows the child
  seat); a colour swatch changes the picture; no fact said twice. Without client photographs, use
  stand-ins of the same kind of thing and list each one; a 3D render only when the brief asks for it.
- **Software:** the product's own interface as live HTML, showing the real thing it works on (a
  code-review tool shows a diff with its accept button), in one app frame; cards hold fragments of
  that interface with the client's names and numbers, never a generic dashboard.
- **Game:** its name and genre in the h1, the launch date or status as the hard fact, its world as
  full-bleed key art (or its name set large over a photograph of its setting).
- **Place:** photographs lead (8 or more on a full page); the visit block (street, hours, way in) is
  screen two; one main action per screen; no effect, loop or count.

## 2. The card

1. **Barely there.** One step off the page ground, a 1px hairline at 8 to 14% ink, generous padding
   (24px minimum, 32px on desktop). No shadow at rest; a linked card may take a soft one on hover.
2. **Two levels, never three.** Card, then its picture, then the product inside the picture. Never
   a card inside a card, never a patterned panel holding a white box holding text, never glass.
3. **Text in the ink.** Card titles one line, a verb and an object ("Warns about double shifts").
   Body 16px in the main ink, one or two sentences, 25 words at most. Muted small text only for labels
   such as a unit or a date. Never 14 or 15px grey card copy.
4. **Rows are full and even.** 6+6, 4+4+4 or 3+3+3+3 on the grid; the first card on the left edge,
   the last on the right; one height per row; no half-empty row.
5. **Cut, not floated.** A product fragment sits at true size and is cut by its panel's edge, as a
   glimpse of something bigger; never a small window floating dead centre on an even ground.
6. **Lengths follow the material.** A card the brief knows a lot about may run longer than its
   neighbours. Four real features are four cards; three is not a rule.

## 3. Forms

One recipe for every form: booking, enquiry, call request, newsletter.

- **It sends somewhere real.** The client's form endpoint, or a `mailto:` stand-in that the report
  lists as the address still to supply. Never `action="#"`, an empty action, or a submit a script
  swallows. `access_links_check.py` fails a form that sends nowhere.
- **Visible labels.** A `<label for>` above every field, saying what goes in ("Arrival", "Guests").
  A placeholder is not a label and an `aria-label` alone is not visible.
- **The right field.** `type="email"` with `autocomplete="email"`, `autocomplete="name"`,
  `inputmode="numeric"` for counts, `type="tel"` only when the brief asks for a phone number.
  Fields 48px tall, 16px text (so phones do not zoom), six fields at most, one column on a phone.
- **Errors on submit, under the field.** Never while typing. The failing field gets
  `aria-invalid="true"` and its reason under it through `aria-describedby`, naming the field and what
  to type ("Write an email address with an @"). Focus moves to the first failing field.
- **One status line** with `role="status"`: "Sending", then the confirmation or the failure. A
  failure keeps everything typed.
- **Success only after a real send.** The confirmation names what was sent in the button's own words
  ("Your table request is in. We reply before noon the next day."). A mailto stand-in shows no
  success line. Never a modal.

## 4. Access and the head

| Item | Rule |
|---|---|
| Names | Every link, button and field has a name; an icon-only button gets `aria-label` in the page's language |
| Pictures | Content photographs say what they show in `alt`; decoration takes `alt=""`; a drawn mock takes `role="img"` and a label |
| Order | Headings step down one level at a time; no `tabindex` above 0 |
| Skip link | The first Tab reaches "Skip to content", which shows over the logo and never pushes the layout |
| Focus | A 2px ring in the action colour, shown at once, never hidden under the fixed header |
| Menu button | `aria-expanded` says whether the menu is open |
| Language | `<html lang>` is the language the page is written in |
| Head | A title of the form "Name: what it is, for whom or where"; a one-sentence description that is not the title; `og:title`, `og:description`, `og:type`, `og:image` (a still of the page's own hero) and `twitter:card`; an icon; `theme-color` set to the page ground; `canonical` only once the real domain exists |

## 5. Links and actions

- **Every link lands:** an `#id` that exists on the page, or a page that exists. Never `#`, never a
  `/contact` that was not built.
- **One target, one wording:** two different labels never lead to the same place (nav words aside).
- **Buttons start with a verb:** book, buy, order, reserve, try, start, get, download, compare, see,
  watch, read, join, subscribe, contact, request, send, add, configure.
- **The main action reads the same** word for word in the hero, the close or booking block, and the
  nav button; at most two copies on one screen.
- **Ten labels at most** across the page body. More means the page asks for too many things.

## 6. The shell and the nav

- The body renders the header, `main` and the footer, plus a phone action bar on a place. Nothing
  else floats: no chat bubble, cookie pill, back-to-top square, newsletter modal or badge unless the
  client requires it.
- The header is fixed, opaque, with a hairline under it from the first paint, the same at every
  scroll depth: no blur, transparency, shrink, hide or colour flip.
- Nav: the logo on the left edge, four to six one-word nouns that never wrap, each to its own section,
  the main action as the one button ending on the right edge. One word may open a flat panel.
- Phone: the menu opens a full-screen sheet; a place adds a fixed action bar with the main action,
  which stays away from a screen that already shows that action.
- No carousel, auto-advancing slider, timed tabs, rotating notice or logo marquee. Rows show whole
  items; tabs, where software needs them, change only on a click.
- No embedded map loading with the page. "Get directions" opens a map search for the street.
- FAQ answers are shown open; nothing animates height to reveal them.
- The page's own code never tests for a headless or automated browser. A page that behaves
  differently for a checker hides its faults from the gate, and `access_links_check.py` fails it.
