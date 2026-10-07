# Emoji Patterns

What `scripts/emoji_audit.py` looks for, how its score is built, and how to
tell a decoration from a habit. The rules describe **placement and
repetition**. No rule here says emoji are bad, and no rule claims a particular
emoji proves anything about who wrote a post.

Everything in this file is an editorial heuristic. The "stock set" in
particular is a judgement list, not a frequency table, and should be edited to
fit the author and the audience.

## Contents

1. Why placement, not presence
2. The eight rules
3. How the score is built
4. What a hand-placed emoji looks like
5. Rewrites
6. Tuning to an author
7. Limits of the tool

---

## 1. Why placement, not presence

Two posts can each contain four emoji and read completely differently.

In the first, a person finishes a sentence about a launch that slipped twice
and adds a single grimace, then three paragraphs later puts a cake after the
line about the team's fifth anniversary. The emoji follow the feeling of the
sentence they are in.

In the second, each of three consecutive lines starts with a different bright
symbol, followed by a two-word bold label and a dash. The emoji are structure:
they are doing the job of bullet points and headings. That layout is what a
drafting tool produces when asked for something "engaging", and readers have
learned its shape.

So the scorer ignores the question "how many?" unless the count is high for the
length, and asks instead: where are they, do they repeat a position, and do
they come from the small set that gets used as ornament?

---

## 2. The eight rules

| ID | Rule | Fires when | Penalty |
|----|------|------------|---------|
| EM-01 | Density above the cap | At least three emoji, more than `--usual`, and emoji per 100 words above `--cap` (default 2.0) | 15 |
| EM-02 | Emoji bullet run | Three or more consecutive non-empty lines each begin with an emoji | 25 |
| EM-03 | Emoji in the opening line | Any emoji in the first non-empty line | 10 |
| EM-04 | Emoji heading | A line begins with an emoji, then a short capitalised label, then a colon or dash | 15 |
| EM-05 | Stock decoration set | At least three emoji and 60% or more come from the stock set | 15 |
| EM-06 | Emoji cluster | Two or more emoji sit side by side | 10 |
| EM-07 | Line-end decoration | Three or more lines of prose end with an emoji | 10 |
| EM-08 | Pointing closer | A downward pointer appears in the last two lines | 5 |

### EM-02 is the heaviest, on purpose

A bullet run reorganises the post around the emoji. Removing them usually
reveals that the "bullets" were three versions of the same claim, which is a
content problem the emoji were covering.

### EM-04 survives asterisk removal

Markdown bold around the label is ignored when matching, so a heading is caught
whether or not the asterisks are still there. Stripping the emoji from a
heading leaves a label-and-colon line, which the tell audit reports separately
as RD-17. Fix the sentence, not the symbol.

### The stock set

The tool's list is the group of symbols most often used as generic section
markers and emphasis: rocket, light bulb, sparkles, pointing hand, tick, flame,
target, rising chart, flexed arm, raised hands, key, lightning, thread, down
pointer, pin, star, briefcase, handshake, brain, trophy, hundred, bar chart,
magnifier. They share a property: each can be attached to almost any business
sentence. An emoji that could go anywhere is carrying no meaning where it is.

Edit `STOCK_SET` in the script if an author has a real habit drawn from it. A
founder who has ended launch posts with a rocket for six years is not
decorating.

---

## 3. How the score is built

```
score = 100 - sum(penalties of rules that fired)      # floor of 0
```

| Score | Band | Reading |
|-------|------|---------|
| No emoji | nothing to score | Reported as 100; no rule can fire |
| 85 to 100 | hand-placed | At most one light rule fired |
| 60 to 84 | noticeable pattern | Fix the flagged placements |
| Below 60 | templated | The emoji layout is doing the formatting |

The gate fails below `--fail-under` (default 60). The sample draft scores 25:
density, a three-line bullet run, three headings, an all-stock set and a
pointing closer.

A draft cannot fail on EM-03, EM-06, EM-07 or EM-08 alone, or on any two of
them together. That is deliberate. Those are style notes; the failing
combinations all involve emoji being used as structure.

---

## 4. What a hand-placed emoji looks like

A checklist for deciding whether to keep one the tool flagged:

- [ ] It sits after the words it reacts to, not before them.
- [ ] Removing it changes the tone of that sentence.
- [ ] It could not be moved to another sentence in the post and still fit.
- [ ] The author uses it, or ones like it, in their unassisted posts.
- [ ] It is not repeated in the same position on neighbouring lines.

Three or more ticks: keep it, and raise `--usual` so the density rule stops
counting it.

---

## 5. Rewrites

All examples invented.

### Bullet run to prose

Before:

```
🚀 Speed: we shipped in six weeks
💡 Clarity: one owner per decision
✨ Focus: we said no to four requests
```

After:

```
We shipped in six weeks. Two things made that possible: every decision had one
owner, and we turned down four requests that would each have added a fortnight.
```

The three "bullets" were not parallel. Two were causes and one was the result.
Prose can say that; a bullet list cannot.

### Bullet run to a plain numbered list

When the items really are parallel steps, keep the list and drop the symbols:

```
1. Team leads post a written update by 10:00 on Monday.
2. Questions go in one thread and are answered by Wednesday.
3. First Monday of the month: a 20-minute call, questions only.
```

### Opening-line emoji

Before: `🔥 Big news from the Lanternworks team!`

After: `Lanternworks is opening a second office, in Leeds, in March.`

### Line-end decoration

Before:

```
We hit our target 🎯
The team was incredible 🙌
Onwards 🚀
```

After: `We hit the Q3 target nine days early. Dalia's team did the last 40 installs in a week.`

### One worth keeping

`We finally deleted the 2019 pricing spreadsheet. It had 31 tabs 🫠`

One emoji, after the words, reacting to them, not from the stock set. As a line
inside a longer post, no rule fires.

---

## 6. Tuning to an author

| Author's habit | Setting |
|----------------|---------|
| Never uses emoji | Defaults. Any emoji in a draft is probably the tool's, not theirs |
| One or two per post, placed after sentences | `--usual 2` so EM-01 does not fire on their normal count |
| A signature emoji from the stock set | Remove it from `STOCK_SET` |
| Writes for an audience that expects none (legal, clinical, public sector) | `--fail-under 85` |
| Uses emoji as real bullets by long habit | Accept the EM-02 finding and record the decision in the voice profile; do not lower the penalty for everyone |

`scripts/voice_fingerprint.py` reports the author's median emoji per post. Use
that figure for `--usual`.

---

## 7. Limits of the tool

- It recognises emoji by Unicode range. Rare symbols outside the main
  pictograph blocks, and plain typographic arrows, are not counted.
- It treats a joined sequence (a figure with a skin tone or a combined family)
  as one emoji, which is right for counting but means the "distinct" list shows
  sequences whole.
- It cannot judge whether an emoji suits the sentence. Rule 4's checklist is
  for a person or the agent to apply.
- It knows nothing about how emoji affect distribution in the feed, and makes
  no claim about it.
