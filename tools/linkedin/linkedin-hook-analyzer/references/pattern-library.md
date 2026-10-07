# Pattern Library

The eighteen opening patterns recognised by `scripts/hook_classifier.py`:
fourteen that are worth reusing and four that are worth recognising. This file
is written for analysis: for each pattern it gives the signs to look for in
someone else's post, an example, the abstract template, and what a writer must
possess before the pattern is available to them.

Every example is invented, about fictional people and organisations. Notes on
what a pattern is "good for" are editorial heuristics, not measurements.

## Contents

1. How to read an entry
2. Reusable patterns (14)
3. Caution-class patterns (4)
4. Unclassified openings
5. Blends
6. Quick recognition table

---

## 1. How to read an entry

| Field | Meaning |
|-------|---------|
| **Slug** | The identifier the tools use |
| **What it is** | The relationship between the author's material and the first line |
| **Signs** | What to look for in the text; these correspond to the classifier's cues |
| **Example** | An invented opening |
| **Abstract template** | The opening with its content removed. Slots describe roles, not words |
| **To use it you need** | Material the writer must really have |
| **What the body owes** | What the rest of the post must deliver for the opening to be honest |

The abstract template is more general than the tool's output. The tool swaps
numbers, dates, names and quoted speech for slots and leaves the remaining
words in place; turning that into a template means also replacing the nouns
that belong to the original author's subject.

---

## 2. Reusable patterns

### receipt — Receipt line

**What it is:** a precise figure placed first, tied at once to what it counts.

**Signs:** a numeral in the first few characters; a currency symbol or unit;
often a second figure; a colon or "that's what" joining number to meaning.

**Example:** "£18,200 and 41 days: that's what it cost us to move a database
nobody had asked us to move."

**Abstract template:** `{exact cost or count} + {what it bought or measured} + {the detail that makes it sting or surprise}`

**To use it you need:** your own figure, exact, and the ability to say how it
was counted.

**What the body owes:** the method, and what was done about it.

### dated-error — Dated mistake

**What it is:** a specific past decision by the author that went wrong, with
when and what it cost.

**Signs:** a time anchor ("last March", "on the 9th", "two years ago"); first
person; a verb of loss or error (rejected, lost, missed, cancelled, got wrong).

**Example:** "Last March I rejected a candidate in the first ten minutes
because she didn't have a degree."

**Abstract template:** `{when} + I/we {did the thing that turned out wrong} + {because of what assumption}`

**To use it you need:** a real mistake of your own, a date, a consequence you
are willing to state.

**What the body owes:** the consequence, and the change it led to.

### cold-scene — Cold scene

**What it is:** the post begins inside a moment, with no introduction.

**Signs:** a clock time, a place, or "it was"/"we were"/"I was standing"; a
concrete object; often a line of speech.

**Example:** "At 6:40 on a Tuesday the loading bay was empty and the phone on
the wall was ringing."

**Abstract template:** `{time or place} + {who or what was there} + {the one detail that is slightly wrong}`

**To use it you need:** to have been there, and to remember a detail nobody
would invent.

**What the body owes:** what the moment meant, and what changed afterwards.

### belief-flip — Changed mind

**What it is:** the author states a belief they used to hold, in order to show
what ended it.

**Signs:** "for years I", "I used to think", "I was sure", "I assumed"; past
tense; first person.

**Example:** "For years I told junior designers to show three options in every
review."

**Abstract template:** `For {how long} I {believed or advised X}` followed in line two by `Then {the evidence}`

**To use it you need:** a belief you really held and can describe fairly, and
the specific thing that changed it.

**What the body owes:** the evidence, the new practice, and where the old one
still applies.

### counter-position — Counter-position

**What it is:** a flat disagreement with a common practice.

**Signs:** "is overrated", "doesn't work", "you don't need", "most X are
wrong"; present tense; no first person in the claim itself.

**Example:** "Exit interviews don't work, at least not when HR runs them."

**Abstract template:** `{widely accepted practice} + {flat negative claim} + {the case it applies to}`

**To use it you need:** evidence, and a stated boundary where the usual
practice is right.

**What the body owes:** the opposing view at its strongest, then the evidence.

### gap — Measured gap

**What it is:** two figures for the same measure at two times.

**Signs:** "from … to …", "went from", an arrow, "cut", "grew", "dropped";
two numerals; a time span.

**Example:** "Our month-end close went from 11 working days to 4 between
January and June."

**Abstract template:** `{measure} went from {before} to {after} + {time span}`

**To use it you need:** both figures, measured the same way, and the period.

**What the body owes:** what caused it, in order of effect, and what did not.

### borrowed-line — Borrowed line

**What it is:** the post opens with someone else's exact words.

**Signs:** an opening quotation mark; "said", "told me", "wrote" close by.

**Example:** "\"I don't need a success manager, I need the export button to
work.\""

**Abstract template:** `"{their exact words}"` followed by `{who said it, by role} + {when}`

**To use it you need:** a sentence someone really said to you, and either
their consent or their anonymity.

**What the body owes:** the situation, and what you did about it.

### house-rule — House rule

**What it is:** a rule the author or their team keeps, stated as a rule.

**Signs:** "our rule", "my one rule", "we never", "I always",
"non-negotiable"; present tense; short.

**Example:** "Our rule: no discount is approved on a call."

**Abstract template:** `{Our/My} rule: {the rule in under ten words}`

**To use it you need:** a rule you actually follow, and the incident behind it.

**What the body owes:** the incident, the exception, and the cost of keeping it.

### field-count — Field count

**What it is:** the author examined a number of things and reports a pattern
with its count.

**Signs:** first person plus a verb of examination (reviewed, read,
interviewed, audited, tested, sat in on) plus a numeral; often a second
numeral for the pattern.

**Example:** "I reviewed 140 incident reports from the last two years and 61
of them had the same root cause field: 'human error.'"

**Abstract template:** `I/we {examined} {how many} {of what} + {how many} of them {shared this}`

**To use it you need:** to have counted. An estimate ("hundreds") is not this
pattern.

**What the body owes:** how the sample was chosen, and what the pattern means.

### asked-question — Reported question

**What it is:** a question someone put to the author, reported as an event.

**Signs:** "asked me", "keeps asking", "the question I get most"; the asker
identified by role; the line itself is a statement.

**Example:** "A founder asked me last week whether she should hire a head of
sales before she'd closed ten deals herself."

**Abstract template:** `{who, by role} asked me {when} + {their question in their words}`

**To use it you need:** a question you were really asked.

**What the body owes:** your answer and your reasoning.

### credit — Named credit

**What it is:** a named person and the specific thing they did.

**Signs:** thanks, "grateful", "credit to", "couldn't have"; a proper name; a
concrete act.

**Example:** "Credit to Jonas Reyes, who rewrote our fourteen most-used support
macros over one weekend without being asked."

**Abstract template:** `{name} + {the specific act} + {what it made possible}`

**To use it you need:** a real person, their agreement to be named, and one
act you can describe exactly.

**What the body owes:** the before, the act, the after.

### plain-definition — Plain definition

**What it is:** a term of art restated in everyday words.

**Signs:** "in plain English", "actually means", "is just", "what is a…";
a term in quotation marks.

**Example:** "\"Net revenue retention\" actually means: if you sold nothing
new this year, would last year's customers pay you more or less?"

**Abstract template:** `"{term}" actually means {everyday restatement, often as a question}`

**To use it you need:** a term your audience uses loosely, and a restatement
they would accept as fair.

**What the body owes:** a worked example and the common misuse.

### dated-bet — Dated bet

**What it is:** a prediction with a date and, ideally, a way to be wrong.

**Signs:** "by 2028", "by the end of next year", "within three years", "I
predict", "my bet"; future tense.

**Example:** "My bet: by the end of next year, most first-round interviews at
companies our size will be asynchronous."

**Abstract template:** `{by when} + {what will be true} + {what would prove it wrong}`

**To use it you need:** a view you will stand behind when the date arrives.

**What the body owes:** the evidence so far and the best counter-argument.

### list-promise — Counted list

**What it is:** a number of items of a named kind.

**Signs:** a numeral or number word at the start, followed within a few words
by a plural such as things, ways, lessons, rules, mistakes, questions, steps.

**Example:** "Six checks I run before I approve any vendor contract."

**Abstract template:** `{how many} {kind of item} + {the context in which the author uses them}`

**To use it you need:** that many real items, each with a detail of its own.

**What the body owes:** every item, with none that could be in anyone's list.

---

## 3. Caution-class patterns

These are common, easy to recognise, and sometimes attached to posts that
travelled widely. The classifier labels them so that a swipe file can tell
"I saved this for its opening" from "I saved this in spite of its opening".

### direct-question — Question to the reader

**Signs:** the first line ends in a question mark and is addressed to "you".

**Example:** "Ever feel like your meetings could have been an email?"

**Why caution:** it requests attention before offering a reason. The honest
answer is usually "yes" and the reader has learned nothing yet.

**The reusable cousin:** asked-question. Report a question someone really asked.

### announcement — Announcement

**Signs:** "excited / thrilled / proud / humbled to share / announce".

**Example:** "I'm thrilled to announce that we've closed our seed round!"

**Why caution:** the first words are the author's feeling. The news is the
content and arrives second.

**The reusable cousin:** receipt or dated-bet. Put the news in the first clause.

### teaser — Teaser

**Signs:** eight words or fewer, no numeral, no name, and a pointing word
(this, here's, nobody, secret, truth, everything).

**Example:** "Nobody tells you this about your first hire."

**Why caution:** the subject is withheld, so the reader cannot judge whether
the post concerns them. It reuses badly because it is identical across topics.

**The reusable cousin:** cold-scene, or simply the withheld fact itself.

### command — Command

**Signs:** the first word is an imperative: stop, start, quit, never, always,
don't, try.

**Example:** "Stop sending calendar invites without an agenda."

**Why caution:** an instruction with no reason given yet. Readers who already
agree nod; the rest leave.

**The reusable cousin:** house-rule ("Our rule: no invite without an agenda")
or counter-position, both of which commit the author to explaining.

---

## 4. Unclassified openings

Some good openings match no pattern.

> "The quarter went sideways and nobody on the team could say exactly when."

There is no figure, date, quote or rule in that line, and it is not a tease:
the subject is stated. It works through voice and through the second line.
The classifier reports it as unclassified with zero confidence, and that is
the correct output.

For an unclassified opening, study instead:

- **The second line.** What does it add that makes the first worth having?
- **The first concrete detail.** How many lines in does it arrive?
- **The body shape and close.** The tool still reports these.

Do not derive a template from an unclassified opening. What it has is the
author's own way of putting things.

---

## 5. Blends

Many strong openings carry two patterns. The classifier reports the higher
score as the pattern and the other as runner-up.

| Blend | Example | How to file it |
|-------|---------|----------------|
| receipt + dated-error | "£18,200 and 41 days: what it cost us to move a database nobody had asked us to move." | By what leads. Here the figure leads: receipt |
| field-count + borrowed-line | "I reviewed 140 incident reports and 61 had the same root cause field: 'human error.'" | The count is the claim; the quote is evidence: field-count |
| belief-flip + field-count | "For years I asked for three options. Then I sat in on 22 reviews and counted." | Two lines, two patterns. File under the first; note the second as the body's opening move |
| gap + receipt | "Close time: 11 days to 4." | Two figures on one measure is always gap |
| house-rule + dated-error | "We never approve a discount on a call. I learned why on a Thursday in 2023." | The rule leads: house-rule |

When recording a blend in a swipe file, write both slugs. A blend is often
more useful than either pattern alone, because it shows how to get two pieces
of material into two lines.

---

## 6. Quick recognition table

| If the opening has… | Look first at |
|---------------------|---------------|
| A numeral in the first few characters | receipt, list-promise, gap |
| Two numerals | gap, field-count |
| A date or "ago" | dated-error, belief-flip |
| A quotation mark first | borrowed-line |
| "asked me" | asked-question |
| "rule", "never", "always" with I/we | house-rule |
| "used to", "for years I" | belief-flip |
| A verb of examining plus a count | field-count |
| A person's name plus thanks | credit |
| "means", "in plain words" | plain-definition |
| "by" plus a future date | dated-bet |
| A negative claim about a practice | counter-position |
| A clock time or place | cold-scene |
| A question mark at the end | direct-question (caution) |
| "to share", "to announce" | announcement (caution) |
| Short, with "this" or "nobody" and no specifics | teaser (caution) |
| An imperative first word | command (caution) |
| None of these | unclassified |
