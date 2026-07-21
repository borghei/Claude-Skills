# Slide Density and Layout

The thresholds the linter enforces, where they come from, and the layout
patterns that let you stay inside them without losing content.

## The governing constraint

An audience cannot read and listen at the same time. Reading is a language task;
listening is a language task; they compete for the same processing. When a slide
carries prose, the room reads it — faster than the presenter can say it — then
disengages until the next slide.

This is not a style preference. It produces a hard rule:

**A slide should be readable in under 5 seconds, or it is competing with the presenter.**

Every threshold below is a proxy for that 5-second budget.

## Density thresholds

The linter ships two profiles because the constraint genuinely differs by use.

### `present` profile (default) — a deck someone speaks over

| Metric | Target | Warning above | Error above | Why |
|--------|--------|---------------|-------------|-----|
| Words per slide | <= 40 | 50 | 75 | ~40 words is about 5 seconds of reading |
| Bullets per slide | <= 5 | 6 | 8 | Beyond ~6 items the list stops being scannable |
| Words per bullet | <= 8 | 12 | 20 | A bullet is a label; past ~12 words it is a sentence |
| Heading characters | <= 50 | 60 | 90 | Longer headings wrap to two lines and eat the slide |
| Table rows | <= 5 | 6 | 9 | Projected tables become illegible fast |
| Code lines | <= 10 | 12 | 20 | Nobody reads 20 lines of projected code |

### `read` profile — a deck circulated instead of presented

| Metric | Warning above | Error above |
|--------|---------------|-------------|
| Words per slide | 90 | 130 |
| Bullets per slide | 8 | 12 |
| Words per bullet | 18 | 28 |
| Heading characters | 70 | 100 |
| Table rows | 9 | 14 |
| Code lines | 18 | 30 |

**Be honest about which one you are building.** The most common deck failure is
a document formatted as slides: too dense to present, too fragmentary to read.
If it will be emailed and never presented, use `--profile read` — or write a
document instead, which is usually the right answer.

### Exempt layouts

`title`, `section`, `quote`, and `image` skip the body-density rules. Their
purpose is to carry one element at large size; a word budget would be
meaningless. They are still checked for heading length and image alt text.

## Where the words go instead

The density rules do not ask you to have less to say. They ask you to put it
where it belongs.

| Content | Belongs |
|---------|---------|
| The claim | Slide heading |
| The evidence, compressed | Slide body (label-length bullets) |
| The sentences | Speaker notes |
| The full table | Appendix slide or a linked document |
| The caveat | Speaker notes, then the Q&A |
| The methodology | A backup slide after the last one |

**[PROVEN] Speaker notes are the pressure valve.** A slide that fails the word
budget almost always passes once its sentences move into notes. The linter
reports a content slide with no notes at `info` severity for exactly this
reason — a dense deck with empty notes means the content has nowhere to go.

## Layouts

### `title`
The first slide. Heading plus one subtitle line. Everything else on it is
noise — no agenda, no logo wall, no date-and-location block nobody reads.

### `section`
A divider between movements of the talk. One heading on a tinted surface. Its
job is to let the room know a new thing is starting, which is worth a slide
precisely because it carries nothing else.

Use one every 5-8 content slides. More often and they lose meaning; less often
and a long deck reads as undifferentiated.

### `default`
Heading plus content. The workhorse. Subject to every density rule.

### `two-column`
Content split by a `:::` marker. Genuinely useful for exactly two things:

1. **A comparison** — before/after, option A/option B, cost/benefit.
2. **An image beside its explanation.**

It is not a way to fit twice the content on one slide. The density budget
applies to the slide, not per column, and the linter counts both columns.

### `quote`
One quotation at large size. Use for a customer sentence, a regulator's wording,
or a line you want the room to sit with. One per deck; a second one dilutes the
first.

### `image`
A full-bleed image, centered. Alt text is mandatory and the linter errors
without it — an image-only slide with no alt text is a slide that does not exist
for a non-sighted attendee.

## Slide splitting

### `--split-on rule` (default)
A line of exactly `---` starts a new slide. Explicit and predictable: what you
see in the source is what you get. Use this for decks authored as decks.

### `--split-on h2`
Every `## ` heading additionally starts a slide. Useful when converting an
existing document into a deck, where headings already mark the natural breaks.

The result is almost always too dense — a document section carries far more than
40 words. Treat h2-splitting as the **first step** of a conversion, then run the
density linter and cut. A document converted straight to slides and presented
unedited is the origin of most bad decks.

## Deck length

| Talk length | Content slides | Rationale |
|-------------|----------------|-----------|
| 5 min (lightning) | 5-7 | ~45s per slide |
| 15 min | 12-18 | The most common conference slot |
| 30 min | 20-30 | Plus 2-3 section dividers |
| 60 min (workshop) | 30-45 | Requires breaks and interaction, not more slides |

These are ranges, not rules — a single slide held for ten minutes of discussion
is legitimate. But a 60-slide deck for a 15-minute slot is not a pacing choice;
it is an unfinished edit.

`notes_runsheet.py` estimates duration from speaker-note word count at a
configurable rate, plus a 4-second per-slide transition allowance. That
transition cost is real and routinely forgotten: 30 slides carry two minutes of
dead air before anyone says a word.

### Speaking rates

| Style | Words per minute | When |
|-------|------------------|------|
| Deliberate | 110 | Technical detail, non-native audience, translation |
| Conversational | 130 | The default; most presenters land here |
| Brisk | 150 | Familiar material, energetic delivery |
| Rushed | 170 | You are over time and the room can tell |

**If the runsheet says you are over, cut content.** Speaking faster does not
create time; it converts an over-long talk into an over-long talk nobody
follows. This is why the tool prints "cut content, do not speak faster" rather
than suggesting a higher rate.

## Writing the heading

The heading is the most-read text on the slide, and it is usually wasted on a
topic label.

| Weak (topic) | Strong (claim) |
|--------------|----------------|
| "Storage costs" | "Cold data is paying hot prices" |
| "Options" | "Three policies, modelled" |
| "Recommendation" | "Recommendation: Policy B" |
| "Results" | "Latency held; spend fell 31%" |

**[PROVEN] Write the heading as the sentence you want remembered.** An audience
that reads only the headings should still receive the argument. This single
change does more for deck quality than any layout decision.

## Anti-patterns

### The document in slide clothing
Full paragraphs on every slide because the deck also has to work as a leave-behind.
It does neither job. Write the document, and build a thin deck that references it.

### The agenda slide
"Agenda: 1. Background 2. Analysis 3. Recommendation." It tells the room nothing
they will not learn by watching. Section dividers do this job in context, at the
moment it matters.

### The build-up
Fifteen slides of background before the recommendation. In a business setting the
recommendation goes early — slide 2 or 3 — and the rest is support. A room that
knows where you are heading follows the evidence better.

### Reading the slides aloud
The direct consequence of putting sentences on slides. If the presenter reads
them, the slide should not exist; if they do not, the audience is reading
something different from what they are hearing. Both are failures of the same
cause.

### The appendix nobody flagged
Twenty backup slides after the last one, undifferentiated. Put a `section`
divider titled "Backup" in front of them so a reader of the file knows the talk
has ended.
