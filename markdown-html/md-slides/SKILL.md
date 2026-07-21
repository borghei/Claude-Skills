---
name: md-slides
description: >
  Convert markdown into a self-contained HTML slide deck with layouts, speaker
  notes, keyboard navigation, and a content-density linter. Use when building a
  deck from markdown, cutting an overloaded deck, or timing a talk.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: markdown-html
  domain: presentation-authoring
  updated: 2026-07-21
  tags: [slides, presentation, markdown, html, speaker-notes, accessibility]
---

# Markdown Slide Decks

Turn a markdown file into a slide deck that is one HTML file: six layouts,
speaker notes, keyboard and remote navigation, light/dark theming, and handout
printing. The density linter is the part that matters most — it catches the
slides an audience cannot absorb before you are standing in front of them.

## When to use this skill

- **Building a deck from markdown** you want to keep in version control
- **Presenting from a laptop** without a presentation app or a cloud account
- **Cutting an overloaded deck** where every slide is a wall of text
- **Timing a talk** against a fixed slot before rehearsing it
- **Converting a document into a deck** as a starting point, then editing down
- **Producing a handout** that includes speaker notes alongside each slide

## Inputs the skill expects

- A markdown deck source, slides separated by `---`
- The talk length and format — presented live, or circulated to be read
- Layout intent per slide: title, section divider, bullets, two-column, quote, image
- Speaker notes after a `???` marker on each content slide
- Images as relative paths, or as data URIs for a genuinely single-file deck
- The presentation environment: room lighting and display size

## Clarify First

Before building, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Presented live or circulated to read** — why it changes the output: it selects the density profile, and the two budgets differ by roughly 2x; the wrong one produces a deck that fails at the job it actually has
- [ ] **Talk length and slot** — why it changes the output: it sets the slide count and drives the runsheet; a 60-slide deck for a 15-minute slot is an unfinished edit, not a pacing choice
- [ ] **Whether images must be embedded** — why it changes the output: relative paths mean the deck is a folder, not a file, and it breaks when emailed
- [ ] **Room lighting, if presenting** — why it changes the output: dark themes wash out under ambient light; this decides the default theme and the contrast floor

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Build a deck and check its density

1. Lint first. Building an overloaded deck and reading it on screen is a slower
   way to learn the same thing.
2. Fix what the linter flags — usually by moving sentences into speaker notes.
3. Build. The theme and navigation script are inlined automatically.

```bash
python3 markdown-html/md-slides/scripts/slide_density_linter.py \
  --input markdown-html/md-slides/assets/sample_deck.md --profile present

python3 markdown-html/md-slides/scripts/md_to_slides.py \
  --input markdown-html/md-slides/assets/sample_deck.md \
  --out build/deck.html --format text
```

### Workflow 2 — Time a talk against its slot

1. Generate the runsheet at your actual speaking rate, not the default.
2. Read the `*` markers — those slides have no notes, so their duration is
   guessed from on-slide content and is the least reliable number in the sheet.
3. If the total is over, cut slides. Speaking faster does not create time.

```bash
python3 markdown-html/md-slides/scripts/notes_runsheet.py \
  --input markdown-html/md-slides/assets/sample_deck.md \
  --wpm 130 --target-minutes 15 --format text

python3 markdown-html/md-slides/scripts/notes_runsheet.py \
  --input markdown-html/md-slides/assets/sample_deck.md \
  --format markdown > build/runsheet.md
```

### Workflow 3 — Convert a document into a deck

1. Split on every `## ` heading to get a first pass with the document's own
   structure.
2. Lint immediately. The result will fail — a document section carries far more
   than a slide's budget. That failure list is the edit plan.
3. Rewrite headings as claims, demote sentences to notes, then rebuild.

```bash
python3 markdown-html/md-slides/scripts/md_to_slides.py \
  --input markdown-html/md-slides/assets/sample_deck.md --split-on h2 --out build/draft.html

python3 markdown-html/md-slides/scripts/slide_density_linter.py \
  --input markdown-html/md-slides/assets/sample_deck.md --profile present --format json
```

## Decision frameworks

### Density budget

| Metric | `present` target | Warn | Error | `read` warn / error |
|--------|------------------|------|-------|---------------------|
| Words per slide | <= 40 | 50 | 75 | 90 / 130 |
| Bullets per slide | <= 5 | 6 | 8 | 8 / 12 |
| Words per bullet | <= 8 | 12 | 20 | 18 / 28 |
| Heading characters | <= 50 | 60 | 90 | 70 / 100 |
| Table rows | <= 5 | 6 | 9 | 9 / 14 |
| Code lines | <= 10 | 12 | 20 | 18 / 30 |

Every threshold is a proxy for one rule: **a slide must be readable in under 5
seconds, or it competes with the presenter.** An audience cannot read and listen
simultaneously — when a slide carries prose, the room reads it faster than you
can say it and then disengages.

`title`, `section`, `quote`, and `image` layouts are exempt from the body rules.

### Layout selection

| Layout | Use for | Limit |
|--------|---------|-------|
| `title` | Opening slide | One per deck; heading plus one subtitle line |
| `section` | Divider between movements | One every 5-8 content slides |
| `default` | Heading plus content | The workhorse; full density budget applies |
| `two-column` | A comparison, or image beside explanation | [RECOMMENDED] Not a way to fit twice the content |
| `quote` | One sentence worth sitting with | One per deck; a second dilutes the first |
| `image` | Full-bleed visual | Alt text mandatory — the linter errors without it |

### Deck length by slot

| Talk length | Content slides | Note |
|-------------|----------------|------|
| 5 min | 5-7 | ~45s per slide |
| 15 min | 12-18 | The common conference slot |
| 30 min | 20-30 | Plus 2-3 section dividers |
| 60 min | 30-45 | Needs interaction, not more slides |

The runsheet adds a **4-second transition allowance per slide** — real, and
routinely forgotten. Thirty slides carry two minutes of dead air before anyone
speaks.

### Where content goes when a slide is too dense

| Content | Belongs |
|---------|---------|
| The claim | Slide heading |
| The evidence, compressed | Slide body, at label length |
| The sentences | Speaker notes [PROVEN] |
| The full table | Appendix slide |
| The caveat | Speaker notes, then Q&A |

### Contrast at projection

| Context | Minimum |
|---------|---------|
| Monitor / screen share | 4.5:1 (WCAG AA) |
| Well-lit room | 7:1 |
| Bright room, weak projector | 10:1 |

**[PROVEN] Present light in a bright room, dark in a dark one.** The `T` key
toggles theme so this is decided in the room, not an hour before.

## Anti-Patterns

### The document in slide clothing
**Mistake:** Full paragraphs on every slide, because the deck must also work as a leave-behind for people who were not there.
**Why it happens:** It is one artifact instead of two, and the request to "make sure it stands alone" is reasonable on its face.
**Instead:** Pick one job. A presented deck uses the `present` budget with the sentences in speaker notes; a circulated deck uses `--profile read`. Trying to serve both produces something too dense to present and too fragmentary to read. If it will mostly be read, write a document and build a thin deck that points at it.

### Bullets as sentences
**Mistake:** Writing each bullet as a complete sentence, so the slide reads correctly on its own.
**Why it happens:** Fragments feel unfinished while drafting, and complete sentences feel more rigorous.
**Instead:** A bullet is a label the presenter expands, not a sentence the audience reads. Past roughly 12 words it is prose and the room stops listening. Move the sentence into the speaker notes, where it is genuinely useful — that is what notes are for, and it is why the linter flags a dense slide with empty notes.

### Topic headings
**Mistake:** Heading a slide with its subject — "Options", "Results", "Storage costs".
**Why it happens:** It matches how the deck was outlined, and outlines are built from topics.
**Instead:** Write the heading as the sentence you want remembered: "Cold data is paying hot prices", "Latency held; spend fell 31%". Someone who reads only the headings should still receive the argument. This single change improves a deck more than any layout decision.

### Speaking faster to fit the slot
**Mistake:** Discovering the deck runs long and planning to talk quickly rather than cutting slides.
**Why it happens:** Cutting means giving up content you already built and believe in.
**Instead:** Cut. Speaking faster converts an over-long talk into an over-long talk nobody follows, and it eliminates the pauses that let a point land. The runsheet says "cut content, do not speak faster" for this reason.

### Skipping the full-screen proof
**Mistake:** Authoring in a windowed browser and presenting full screen without checking.
**Why it happens:** The deck looks finished on the laptop, and full screen feels like the same thing but bigger.
**Instead:** Open it full screen on the actual display and walk every slide with the actual remote. Type scales with viewport width, so every size decision changes — tables and code blocks are set smaller than body text and are the first things to become unreadable from the back row. Presenter remotes send PageUp/PageDown, which is also worth confirming before you are on stage.

## Files

| File | Purpose |
|------|---------|
| `scripts/md_to_slides.py` | CLI: build a self-contained HTML deck with inlined theme and navigation |
| `scripts/slide_render.py` | Slide splitting, layouts, note extraction, escaping-first renderer — imported by `md_to_slides.py`, not a CLI |
| `scripts/slide_density_linter.py` | Flag slides over the word, bullet, table, and code budgets; CI gate |
| `scripts/notes_runsheet.py` | Timed runsheet from speaker notes; text, JSON, or markdown |
| `references/slide-density-and-layout.md` | Thresholds and their rationale, layout patterns, deck length |
| `references/deck-accessibility-and-delivery.md` | Focus management, keyboard interface, projection contrast, pre-flight |
| `assets/sample_deck.md` | Working deck using every layout; passes the density gate |
| `assets/deck_theme.css` | Bundled deck theme — this skill's own copy |
| `assets/deck_nav.js` | Inlined navigation: keyboard, hash routing, notes, theme toggle |
| `assets/deck_outline_template.md` | Starting structure for a new deck |

All scripts share one exit-code contract: **0** clean, **2** gate failed (findings at or above the threshold), **1** the tool itself errored. A CI job can therefore tell a real defect from a broken invocation.

**Three CLI tools, one module.** `slide_render.py` is a library, not a fourth
command — it holds the parser and renderer that `md_to_slides.py` imports. A
single-file converter came to 324 lines, over the 300-line ceiling, and the only
ways to fit were deleting docstrings or dropping features. Splitting CLI from
parser is the remedy the tool-design standard prescribes for an oversized
script, and same-directory imports keep the package self-contained: nothing here
imports from another skill, and `md-document` carries its own separate copy of
the equivalent renderer rather than sharing this one.
