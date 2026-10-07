# Classification Rules

How `scripts/hook_classifier.py` decides which pattern an opening belongs to,
and how to make the same decision by hand when the tool is unsure.

The method is cue matching: regular expressions look for surface signs in the
first line, each pattern adds up the weights of the signs it cares about, and
the highest total wins. It is deterministic, and it is a heuristic. It reads
shapes and keywords, not meaning, and it will be wrong on openings that are
ironic, unusual or not in English.

## Contents

1. What counts as the opening
2. The cues
3. From cues to a pattern
4. Confidence
5. The slot template
6. Body shape and close
7. Cautions
8. Known misfires
9. Classifying by hand
10. Changing the rules

---

## 1. What counts as the opening

The opening is the **first non-empty line** of the post. Classification uses
that line only.

The second non-empty line is reported alongside (`second_line`) because it is
often what makes the first one work, but it does not affect the score. This is
deliberate: a pattern that only emerges in line two is a fact about the post's
structure, not about its opening.

Consequences:

- An author who breaks the opening sentence across two lines will be
  classified on the first fragment. Rejoin the lines before analysing.
- A label line beginning `# ` at the top of a post in the input file is
  treated as the label, not the opening.

---

## 2. The cues

Each cue is a yes-or-no test on the opening. Matching ignores case, and curly
apostrophes are straightened first.

| Cue | Fires on | Example fragment |
|-----|----------|------------------|
| `number` | Any digit | "41 days" |
| `starts_number` | A digit or currency symbol at the very start | "£18,200 and…" |
| `money` | A currency symbol before a digit, or a digit before a currency word | "£212", "40k euros" |
| `percent` | A digit before %, or the word percent | "30%" |
| `time_anchor` | "N days/weeks/months/years ago", "last week/March/spring", "on the 9th", "9 June", "in 2023", a month name, "yesterday", "on Thursday" | "Last March" |
| `first_person` | I, we, my, our and their contractions | "I rejected" |
| `error` | mistake, wrong, lost, failed, broke, missed, regret, fired, outage, churned, cancelled, botched, rejected, ignored, dismissed, overpaid, underestimated, "cost us/me" | "I rejected" |
| `belief` | "used to think/believe/say", "I thought/believed/assumed", "changed my mind", "for years I", "I was sure/convinced" | "For years I told" |
| `counter` | overrated, "is a myth", "doesn't/don't/won't work", "you don't need", "is wrong/backwards/broken/dead/a waste", "most … are wrong", "nobody needs", "bad advice", unpopular | "don't work" |
| `gap` | "from … N … to … N", "went from", cut/grew/dropped/rose/fell/doubled/halved/tripled followed by a digit, "N → N", "N vs N", "N (units) to N" | "went from 11…to 4" |
| `quote` | A quotation mark at the start, or a quoted span of eight or more characters | "\"I don't need…\"" |
| `said` | said, told me/us, wrote, texted, emailed, messaged | "told me" |
| `rule` | "my/our/one/the … rule", "I/we never", "I/we always", non-negotiable | "Our rule:" |
| `sample` | I/we + reviewed, read, interviewed, audited, analysed, looked at, talked to, spoke to, hired, sat in on, tested, graded, watched, ran + a digit later in the sentence | "I reviewed 140" |
| `asked` | "asked me/us", "keep getting asked", "question I get", "someone asked", "people ask" | "asked me last week" |
| `thanks` | thanks, thank you, grateful, shout-out, "credit to/goes", "I owe", "couldn't have" | "Credit to" |
| `define` | "in plain English/words/terms", explained, "actually/really means", "is just", "what is/are …" | "actually means" |
| `bet` | "by 20xx / the end of / next year / Q3", "I predict", "my bet", prediction, "within N months/years", "will be gone/dead/standard/normal/obsolete" | "by the end of next year" |
| `list` | A count at the start followed within three words by things, ways, lessons, rules, mistakes, questions, signs, steps, reasons, tools, habits, checks, tips | "Six checks I run" |
| `question` | The line ends with a question mark | "…an email?" |
| `announce` | excited/thrilled/happy/proud/pleased/delighted/humbled/honoured to share/announce/say/join; "I'm joining"; "we're hiring"; "big news" | "thrilled to announce" |
| `command` | First word is stop, start, quit, never, always, don't, do not, try, remember, forget, delete | "Stop sending" |
| `scene` | Starts with a clock time, "it was", "at N", "I was sitting/standing/in/on", "we were", "the room/call/email/meeting/office/phone"; or contains midnight, a.m./p.m., "6am" | "At 6:40 on a Tuesday" |
| `proper` | A capitalised word that is not at the start of a sentence | "…to Jonas Reyes" |
| `teaser` | Derived: eight words or fewer, a pointing word (this, here's, nobody, no one, secret, truth, everything, what happened), and neither `number` nor `proper` | "Nobody tells you this…" |

List the live cues and weights at any time:

```bash
python3 scripts/hook_patterns.py --list
python3 scripts/hook_patterns.py --show dated-error
```

---

## 3. From cues to a pattern

Each pattern has:

- **Core cues.** At least one must fire or the pattern is not considered.
- **Weights.** Points added for each cue that fires.

| Pattern | Core | Weights |
|---------|------|---------|
| receipt | number | starts_number 2, money 2, number 1, percent 1, first_person 1 |
| dated-error | error | error 2, time_anchor 2, first_person 1, number 1 |
| cold-scene | scene | scene 3, first_person 1, quote 1 |
| belief-flip | belief | belief 4, first_person 1, time_anchor 1 |
| counter-position | counter | counter 3, number 1 |
| gap | gap | gap 3, time_anchor 1, percent 1, number 1 |
| borrowed-line | quote | quote 3, said 2 |
| house-rule | rule | rule 3, first_person 1 |
| field-count | sample | sample 4, number 1 |
| asked-question | asked | asked 4, quote 1, said 1 |
| credit | thanks | thanks 3, proper 2 |
| plain-definition | define | define 4, quote 1 |
| dated-bet | bet | bet 4, number 1 |
| list-promise | list | list 5 |
| direct-question | question | question 3 |
| announcement | announce | announce 5 |
| teaser | teaser | teaser 4 |
| command | command | command 3 |

The pattern with the highest total wins. Ties go to the pattern listed earlier
in the table, which is why the order runs from the most material-dependent
patterns to the least.

### Why the weights look like this

- **Receipt is cheap to trigger and scores low.** Any digit makes it a
  candidate, so it wins only when nothing more specific does. An opening with
  two figures and "went from" scores higher as a gap; one with a verb of
  examining scores higher as a field count.
- **Rare, unambiguous phrases score high.** "For years I", "asked me" and a
  counted plural at the start almost never mean anything else, so they carry 4
  or 5 points.
- **Caution-class patterns score in the same range as reusable ones.** A stock
  announcement should beat a faint match to a reusable pattern; otherwise the
  swipe-file summary under-reports them.

---

## 4. Confidence

```
confidence = top_score / (top_score + runner_up_score + 1)
```

The figure rises when the winning pattern scores well and nothing else comes
close. It is a ratio for sorting results, not a probability of being right.

| Top | Runner-up | Confidence | Band |
|-----|-----------|------------|------|
| 5 | 0 | 0.83 | high |
| 5 | 2 | 0.62 | high |
| 5 | 4 | 0.50 | medium |
| 3 | 0 | 0.75 | high |
| 3 | 3 | 0.43 | medium |
| 2 | 2 | 0.40 | medium |
| 1 | 0 | 0.50 | medium |
| 1 | 1 | 0.33 | unclassified at the default floor |

Bands: **high** at 0.60 and above, **medium** from 0.40, **low** below that.
Anything under `--min-confidence` (default 0.34) is reported as unclassified,
as is any opening where no core cue fired.

A medium result with a runner-up is the signature of a blend. Read both.

---

## 5. The slot template

The tool produces a first-pass template by substitution, in this order:

| Order | What is replaced | Slot |
|-------|------------------|------|
| 1 | Quoted speech of four or more characters | `"{their exact words}"` |
| 2 | Currency amounts | `{amount}` |
| 3 | Percentages | `{percent}` |
| 4 | Time anchors | `{when}` |
| 5 | Remaining numbers | `{number}` |
| 6 | Capitalised words mid-sentence | `{name}` |

Example:

```
opening : Our month-end close went from 11 working days to 4 between January and June.
template: Our month-end close went from {number} working days to {number} {when} {when}.
```

This is a starting point. It still contains "month-end close" and "working
days", which belong to the original author. Finish the job by hand:

```
abstract: {measure} went from {before} to {after} {over what period}.
```

The abstract template for each pattern is given in `pattern-library.md`. Use
the tool's output to see *where* the material sat in the sentence, and the
library's template to write a new one.

---

## 6. Body shape and close

Reported for context. They do not affect the pattern.

| Body shape | Rule |
|------------|------|
| numbered list | Three or more lines starting with a digit and a full stop or bracket |
| bulleted list | Three or more lines starting with a dash, bullet, arrow or tick |
| single block | Two paragraphs or fewer |
| one-line paragraphs | At least 70% of paragraphs are a single line of 25 words or fewer |
| story paragraphs | Anything else |

| Close | Rule (last prose line, ignoring a hashtag line) |
|-------|--------------------------------------------------|
| stock engagement ask | The last two lines contain "what do you think?", "agree?", "tag someone", "repost if", "follow for more", "comment … below" |
| postscript | Starts with P.S. |
| pointer to a link | Contains a URL or "link in the comments" |
| question | Ends with a question mark |
| statement | Anything else |

A stock engagement ask is reported as a caution so that it is not carried over
with the pattern.

---

## 7. Cautions

The tool attaches a caution when:

- the opening is longer than `--fold-chars` (default 140, a conservative
  estimate of the truncation point as of writing; verify in the product);
- the pattern is caution-class;
- the close is a stock engagement ask;
- the post has more than three hashtags;
- the opening is unclassified.

Cautions describe the saved post. They are reminders of what not to inherit.

---

## 8. Known misfires

| Opening | Tool says | Should be | Why it misfires |
|---------|-----------|-----------|-----------------|
| "3 a.m. and the pager went off again." | receipt, with cold-scene close behind | cold-scene | The digit triggers receipt; the clock time is the real signal. Medium confidence flags it |
| "We never expected 4,000 sign-ups in a day." | house-rule | receipt | "we never" is read as a rule |
| "Nobody had asked us to move it." | teaser or asked-question | unclassified or dated-error | Keyword overlap with no real match |
| "I thought the demo went well." | belief-flip | cold-scene or unclassified | "I thought" is a belief cue even when it is narration |
| "I work 9 to 5 and still answer email at ten." | gap | cold-scene or unclassified | "N to N" is read as a before and after |
| "In 2019 we had 4 customers." | receipt | gap (the second figure is in line two) | Only the first line is scored |
| An opening in another language | unclassified or noise | — | The cues are English-only |
| An ironic announcement ("Thrilled to announce I've been made redundant.") | announcement | dated-error | The tool does not detect irony |

These are reasons to read every medium- and low-confidence result, not reasons
to distrust the high-confidence ones.

---

## 9. Classifying by hand

When the tool is unsure, ask these in order and stop at the first yes.

1. Does the line open with someone else's quoted words? → **borrowed-line**
2. Does it report a question the author was asked? → **asked-question**
3. Does it give two figures for one measure at two times? → **gap**
4. Does it give a count of things the author examined? → **field-count**
5. Does it promise a counted set of items? → **list-promise**
6. Does it describe a past error of the author's, with a time? → **dated-error**
7. Does it state a belief the author used to hold? → **belief-flip**
8. Does it state a rule the author keeps? → **house-rule**
9. Does it predict something by a date? → **dated-bet**
10. Does it restate a term in plain words? → **plain-definition**
11. Does it name a person and what they did, with thanks? → **credit**
12. Does it flatly reject a common practice? → **counter-position**
13. Does it begin inside a moment (time, place, someone present)? → **cold-scene**
14. Is the main content a single precise figure? → **receipt**
15. Is it a question to the reader, a feeling announced, a tease, or an
    instruction? → the matching **caution-class** pattern
16. None of the above → **unclassified**

The order differs from the tool's table on purpose. By hand, the most
distinctive structures are checked first; receipt comes late because a figure
appears inside many other patterns.

Validate a hand classification by checking the pattern's "what the body owes"
in the library against the actual post. If the body does not deliver it, the
classification is probably wrong, or the post is weaker than it looked.

---

## 10. Changing the rules

Everything lives in `scripts/hook_patterns.py`.

- **A cue misses a phrase used in your field:** add the phrase to that cue's
  pattern in `_CUE_SOURCES`.
- **A pattern wins too easily:** lower its heaviest weight by one and re-run
  the sample file to check nothing else moved.
- **A new pattern is needed:** add a cue for its core sign and a row in `_P`
  with a slug, name, core cue, weights, reuse status and note. Place it in the
  table according to how much material it demands.
- **After any change:** re-run the classifier on
  `assets/sample_saved_posts.txt` and confirm the pattern mix is unchanged
  (one each of nine patterns plus one unclassified), then on your own swipe
  file to see what moved.

Keep the tool deterministic. Do not add scoring that depends on post
performance figures; how a post did is a separate question from what its
opening is.
