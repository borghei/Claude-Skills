# Readability, Accessibility, and Terminology Standards

The formulas, target bands, WCAG success criteria, and style-governance methods behind the
readability and accessibility checks. Everything here is implemented in the shipped scripts with
no external dependencies.

---

## 1. Flesch Reading Ease

Published by Rudolf Flesch in 1948 and still the most widely cited readability metric in
plain-language regulation.

### Formula

```
FRE = 206.835 - 1.015 × (total_words / total_sentences) - 84.6 × (total_syllables / total_words)
```

Two inputs drive the score: **average sentence length** and **average syllables per word**. Nothing
else. This is the metric's strength and its weakness — it is trivially reproducible and completely
blind to meaning.

The output is an unbounded scale conventionally read from 0 to 100. Scores above 100 (very short
sentences of one-syllable words) and below 0 (long sentences of polysyllabic words) are both
achievable and both signal something has gone wrong.

### Interpretation bands

| Score | Band | Grade level | Typical content |
| --- | --- | --- | --- |
| 90-100 | Very easy | 5th grade | Children's material, emergency instructions |
| 80-89 | Easy | 6th grade | Consumer product instructions |
| 70-79 | Fairly easy | 7th grade | Popular fiction, consumer web copy |
| 60-69 | Plain English | 8th-9th grade | Quality journalism, general business writing |
| 50-59 | Fairly difficult | 10th-12th grade | Technical documentation, trade press |
| 30-49 | Difficult | College | Academic writing, legal summaries |
| 0-29 | Very difficult | Graduate | Regulatory text, primary research papers |

### Target bands by audience

**This is the table that matters.** A score is meaningless without a target audience.

| Audience | Target FRE | Max FK grade | Notes |
| --- | --- | --- | --- |
| General public / consumer | 60-80 | 8.0 | Health, government, and consumer content |
| General technical (default) | 50-70 | 12.0 | Developer docs, runbooks, internal guides |
| Specialist practitioner | 40-60 | 14.0 | API reference, security advisories |
| Academic / regulatory | 30-50 | 16.0 | Papers, compliance filings, standards text |
| Emergency / safety-critical | 70-90 | 6.0 | Incident runbooks, evacuation, first-response |

The safety-critical band is the one teams get wrong most often. Under stress, reading
comprehension drops sharply; an incident runbook written at grade 12 is effectively unreadable at
3am during an outage. Target grade 6 for anything a person reads while something is on fire.

### Regulatory floors

Several jurisdictions mandate readability minimums, which is why the metric persists despite its
crudeness:

| Context | Requirement |
| --- | --- |
| US health insurance summaries (SBC) | Plain-language standard, commonly interpreted as FRE ≥ 60 |
| Several US states, consumer insurance policies | FRE ≥ 40-50 depending on state |
| US federal plain-language guidance | Grade 8 or below for public-facing material |
| UK government service manual | Reading age 9 for public-facing content |

If your content falls under any of these, the target band is not a style preference.

### Only the floor should block

**Scoring above the target band is not a defect.** Prose that is easier than required is prose that
more people can read. The gate implemented here breaches only on the lower bound and records
exceeding the ceiling as info.

Teams that gate on both bounds end up with authors padding sentences to hit a band, which is the
exact opposite of the metric's purpose.

---

## 2. Flesch-Kincaid Grade Level

The same two inputs, rescaled to US school grades. Developed for the US Navy in 1975 to assess
technical manual difficulty.

### Formula

```
FKGL = 0.39 × (total_words / total_sentences) + 11.8 × (total_syllables / total_words) - 15.59
```

The output approximates the US school grade required to comprehend the text on first reading.
FKGL 8.0 means an average 8th-grader (age 13-14) should understand it.

### FRE and FKGL move together

Because both derive from the same two ratios, they are strongly inversely correlated. Reporting
both is still worthwhile:

- **FRE** is better for comparing documents against a policy band.
- **FKGL** is better for communicating with non-specialists — "grade 14" lands harder than "score 44".

A large divergence between the two normally means the sentence count is wrong, which usually means
abbreviations or decimal numbers were treated as sentence boundaries.

---

## 3. Syllable counting

Both formulas depend on a syllable count, and English orthography makes exact counting impossible
without a pronunciation dictionary. The heuristic implemented here is the standard vowel-group
approach with correction rules.

### Algorithm

1. Lowercase the word and strip every non-alphabetic character.
2. If the result is 3 characters or shorter, return 1. (Short words are effectively always
   monosyllabic, and the correction rules misfire badly on them.)
3. Strip a trailing silent `e`: remove a final `e` not preceded by `l`, and remove `ed` and
   consonant + `es` endings.
4. Strip a leading `y` — it functions as a consonant there (`yellow`, `young`).
5. Count maximal runs of `[aeiouy]`. Each run is one syllable.
6. **Correction — syllabic `-le`:** add 1 for words ending in `le`/`les` where the preceding
   letter is a consonant (`table`, `simple`, `handles`).
7. **Correction — vowel hiatus:** add 1 for words ending in `ia`, `io`, `ua`, `eo`, where the
   vowels belong to separate syllables (`media`, `ratio`, `video`).
8. Return at least 1.

### Accuracy

Against a pronunciation dictionary, this heuristic lands within ±1 syllable on roughly 92-95% of
common English words. Errors are roughly symmetric, so aggregate counts over a document of 200+
words are accurate to within about 2%, which is far below the noise floor of the readability
formulas themselves.

### Known failure cases

| Word | Heuristic | Actual | Cause |
| --- | --- | --- | --- |
| `queue` | 1 | 1 | Correct by accident |
| `business` | 3 | 2 | Silent `i` |
| `every` | 2 | 2 | Correct |
| `chocolate` | 3 | 3 | Correct |
| `orange` | 2 | 2 | Correct |
| `create` | 2 | 2 | Correct after hiatus rule |
| `poem` | 1 | 2 | `oe` hiatus not covered |
| `science` | 1 | 2 | `ie` hiatus not covered |

Do not add per-word exception lists. They grow without bound, are corpus-specific, and improve the
aggregate score by less than the measurement noise.

---

## 4. Sentence-level checks

Aggregate scores hide the actual problem. A document can score FRE 62 while containing three
sentences that no one can parse — the short sentences average out the monsters. Sentence-level
checks find those.

### Long sentences

| Threshold | Level | Reasoning |
| --- | --- | --- |
| ≤ 20 words | fine | Comfortable for any audience |
| 21-30 words | acceptable | Normal upper range for technical prose |
| 31-45 words | warning | Comprehension drops measurably; usually two sentences |
| 46+ words | error | Reader must re-read; almost always fixable by splitting |

Target: **mean sentence length ≤ 20 words, with no more than 10% of sentences above 30 words.**

The 10% ceiling matters more than the mean. A document averaging 18 words with 20% of sentences
over 30 words is harder to read than one averaging 22 words with none.

### Sentence segmentation

Sentences are split on `.`, `!`, `?` followed by whitespace. Before splitting, the text is
pre-processed to remove the constructs that produce false boundaries:

- Fenced and indented code blocks (removed entirely)
- Inline code spans
- Bare URLs
- Table rows
- Headings (they are labels, not sentences, and including them deflates mean sentence length)
- Image and link syntax (link text is kept; targets are dropped)

Fragments with fewer than 3 words are discarded rather than counted as sentences — this catches
list markers, stray abbreviations, and version strings that survive pre-processing.

**Known limitation:** abbreviations ending in a period followed by a capitalized word (`e.g. The`,
`Inc. The`) split incorrectly. This inflates sentence count and therefore inflates the readability
score slightly. On technical documentation the effect is well under one FRE point.

### Passive voice

Detected as a form of *to be* (`is`, `are`, `was`, `were`, `be`, `been`, `being`, `am`, plus the
`get`-passive) followed within three words by a past participle — either an `-ed` form longer than
four characters, or a member of an irregular participle list. Intervening adverbs (`not`,
`already`, `still`, `often`, …) are skipped; any other intervening word ends the match.

At most one finding per sentence, so the reported percentage is "percent of sentences containing
passive construction" — a meaningful figure — rather than a raw construction count that can exceed
100%.

**Target: ≤ 15% of sentences.** Zero is the wrong target. Passive voice is correct when:

- The actor is unknown: "The database was corrupted during the migration."
- The actor is irrelevant: "The certificate is rotated every ninety days."
- The object is the topic: "Your request has been approved."
- Naming the actor would assign blame unhelpfully in a post-mortem.

Passive voice is reported at **info** severity for exactly this reason. It is a signal to review,
never a defect to fix mechanically.

Known false positives: `is required`, `is related`, `is expected`, `is based` — these are
predicate adjectives, not passives. They inflate the count by a few percent. The threshold accounts
for this; do not chase the last few points.

---

## 5. Accessibility checks and their WCAG basis

Every accessibility rule here maps to a specific WCAG 2.2 success criterion. Markdown source
checks can only cover the criteria that survive conversion to HTML — the rest need a rendered page.

### 1.1.1 Non-text Content (Level A)

> All non-text content presented to the user has a text alternative that serves the equivalent
> purpose.

**Checked:** every image has non-empty, non-placeholder alt text.

Alt text quality rules:

| Situation | Correct alt text |
| --- | --- |
| Informative image | Describe the information, not the image. "Deployment pipeline: build, test, stage, deploy" not "Diagram of pipeline" |
| Screenshot of UI | Describe what the UI shows and its state, not "screenshot" |
| Chart or graph | State the finding: "Error rate fell from 4% to 0.2% after the November release" |
| Decorative image | Empty alt (`![](path)`) **with an explicit decorative marker** in the surrounding markup |
| Image of text | Reproduce the text verbatim |
| Logo | The organization name, plus "logo" only if the fact that it is a logo matters |

Length guidance: **10-150 characters.** Below 10 is almost always a placeholder. Above 150 means
the content belongs in a caption or in the body text, where every reader benefits from it, rather
than hidden in an attribute only some readers hear.

The placeholder list — `image`, `photo`, `screenshot`, `figure`, `diagram`, `graphic`, `todo`,
`tbd` — catches the most common non-descriptions. Extend it with your team's habits.

### 1.3.1 Info and Relationships (Level A)

> Information, structure, and relationships conveyed through presentation can be programmatically
> determined.

**Checked, two ways:**

1. **Heading hierarchy.** Skipped levels break the programmatic outline that screen-reader users
   navigate with. This is the single most common Level A failure in documentation.
2. **Table headers.** A pipe table without a delimiter row renders as a table with no `<th>`
   cells. Screen readers then cannot announce the column a cell belongs to, and a data table
   becomes unreadable in cell-by-cell navigation.

### 2.4.4 Link Purpose (In Context) — Level A / 2.4.9 Link Purpose (Link Only) — Level AAA

> The purpose of each link can be determined from the link text alone, or from the link text
> together with its programmatically determined context.

**Checked:** link text is not in the non-descriptive list, and is not a bare URL.

Screen-reader users commonly navigate by pulling up a list of every link on the page, stripped of
surrounding context. A page with six links reading "click here" presents six identical entries.

| Bad | Good |
| --- | --- |
| Click [here](x) to request access | Request access through the [internal access portal](x) |
| [Read more](x) | [Read the full incident report](x) |
| See [this link](x) | See the [credential rotation runbook](x) |
| [https://example.com/docs/v2/api](x) | [API reference, v2](x) |

Passing 2.4.4 requires context; passing 2.4.9 requires the link text to stand alone. **Target
2.4.9.** It costs nothing extra at authoring time and produces better prose for everyone.

### 2.4.6 Headings and Labels (Level AA)

> Headings and labels describe topic or purpose.

**Partially checked** via the single-H1 rule and the minimum section length rule. Whether a heading
is *descriptive* is a human judgment the gate cannot make.

### 3.1.1 Language of Page (Level A)

> The default human language of each page can be programmatically determined.

**Checked indirectly** — add `lang` to `required_fields` if your converter maps frontmatter to the
`<html lang>` attribute.

### Criteria that cannot be checked in Markdown source

| Criterion | Why it needs a rendered page |
| --- | --- |
| 1.4.3 Contrast (Minimum), AA | Requires computed colors |
| 1.4.4 Resize Text, AA | Requires layout at 200% zoom |
| 1.4.10 Reflow, AA | Requires responsive layout at 320 CSS px |
| 2.1.1 Keyboard, A | Requires interactive DOM |
| 2.4.3 Focus Order, A | Requires focusable elements |
| 2.4.7 Focus Visible, AA | Requires focus styling |
| 4.1.2 Name, Role, Value, A | Requires the accessibility tree |

Run these against the converted HTML. The Markdown gate covers what the source can prove; claiming
more is how teams end up with a "WCAG compliant" badge on an inaccessible site.

---

## 6. Terminology governance

### Why a term map beats a style guide

A style guide is a document people read once. A term map is a check that runs on every commit. The
second one changes behavior.

The map is a one-to-many mapping from the preferred spelling to its disallowed variants:

```json
"terminology": {
  "front-end": ["frontend", "front end"],
  "email": ["e-mail", "E-Mail"],
  "JavaScript": ["Javascript", "javascript"],
  "GitHub": ["Github"],
  "sign in": ["signin", "log in"]
}
```

### Case sensitivity rule

A variant containing any uppercase letter is matched **case-sensitively**; an all-lowercase variant
is matched **case-insensitively**.

This is what makes capitalization rules expressible. `"JavaScript": ["Javascript"]` flags
`Javascript` but not `JavaScript` itself. `"front-end": ["frontend"]` flags `frontend`,
`Frontend`, and `FRONTEND` alike.

Matching uses word boundaries that treat hyphens as word characters, so `front-end` does not
trigger the `frontend` rule and `e-mail` does not partially match inside `e-mailing`. Overlapping
variants are resolved longest-first, and each source span is reported once.

### What belongs in the map

**Include:**

- Product and technology names with a canonical capitalization (`GitHub`, `PostgreSQL`, `macOS`)
- Compound terms with contested hyphenation (`front-end`, `back-end`, `open source`)
- Terms with a house-style preference (`sign in` vs `log in`, `setup` the noun vs `set up` the verb)
- Deprecated product names and old brand spellings
- Inclusive-language replacements (`allowlist` for `whitelist`, `primary` for `master`)

**Exclude:**

- Anything a spell checker already catches — duplication makes both noisier
- Terms that appear inside code samples (the scorer already strips code, but ambiguous cases still
  produce noise)
- Words with legitimate multiple meanings in your domain
- Anything where the "wrong" form is correct in quoted external material

### Severity: warning, always

Terminology findings are a house-style matter. Blocking a release on `Github` versus `GitHub`
teaches authors that the gate is petty, and a gate perceived as petty gets bypassed. Warning level
with a `max_warnings` budget applies steady pressure without friction.

### Map maintenance

Review quarterly. A term map that only grows becomes a source of false positives as products get
renamed and house style evolves. Every entry should have a reason someone could state out loud.

---

## 7. Measurement discipline

### Score the right text

Readability scored over the wrong text is worse than no score. Exclude:

- Code blocks — they are not prose and destroy syllable ratios
- Tables — cell fragments are not sentences
- Headings — labels, not sentences; including them deflates mean sentence length
- URLs — pathological syllable counts
- Frontmatter — metadata, not content

### Minimum sample size

**Do not report a readability score for a document under 100 words.** Below that, a single long
sentence swings FRE by 15+ points. Report the raw counts instead and let the reviewer judge.

### Score trends, not snapshots

A single FRE score is a weak signal. The strong signal is the distribution across a corpus and its
movement over time:

- Median score across all published documents, tracked monthly
- Percentage of documents outside their audience band
- Count of very-long sentences per 1,000 words
- Terminology findings per document, tracked against map size

A corpus whose median drifts down 5 points per quarter has a systemic problem no per-document gate
will surface.

### The metric's real limits

Flesch measures sentence length and word length. It does not measure:

- Whether the content is organized in a sensible order
- Whether jargon is defined before use
- Whether examples are present
- Whether the reader has the prerequisite knowledge
- Whether the document answers the question the reader arrived with

A document can score FRE 75 and be useless. **Use readability as a floor, never as a definition of
quality.** The score catches prose that is mechanically hard to parse; it says nothing about
whether the prose is worth parsing.
