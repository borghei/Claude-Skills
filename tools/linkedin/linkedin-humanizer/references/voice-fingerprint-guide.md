# Voice Fingerprint Guide

How `scripts/voice_fingerprint.py` describes an author, how its output protects
their habits from the audit, and how to resolve the cases where a rule and a
habit disagree.

The fingerprint is a set of medians. It describes surface habits (how long the
sentences run, how often the author says "I", whether they use dashes). It does
not capture what the author thinks, what they find funny, or what they would
never say; those go in `assets/voice_profile_template.md` by hand.

## Contents

1. What goes in
2. What comes out
3. Reading the measures
4. Protected rules
5. Comparing a draft
6. Rule versus habit: settling conflicts
7. Keeping the fingerprint honest
8. What the fingerprint cannot do

---

## 1. What goes in

A plain-text file of the author's own posts, separated by lines containing only
`---`.

**Choose posts that are:**

- Written by the author, not by a comms team or a drafting tool. If a post was
  assisted, leave it out: a fingerprint built on assisted text protects the
  wrong habits.
- Recent enough to reflect how they write now. People's style drifts.
- Of the kind they intend to keep writing. A fingerprint built from hiring
  announcements will not describe their opinion posts.
- Complete. Paste the whole post including line breaks.

**How many:**

| Posts | Tool's confidence label | Use |
|-------|-------------------------|-----|
| 1 or 2 | thin | Treat every number as a guess; a warning is printed |
| 3 to 5 | usable | Enough to protect obvious habits |
| 6 or more | solid | Medians are stable against one unusual post |

Five is the practical minimum worth asking an author for. Ten is better than
five; thirty is not noticeably better than ten.

---

## 2. What comes out

Text output is a summary. JSON output (`--format json`) is the file the audit
reads with `--voice`:

```json
{
  "posts_analysed": 5,
  "confidence": "usable",
  "medians": { "words": 98.0, "words_per_sentence": 11.62, "dashes_per_100": 1.02 },
  "signature_words": ["page", "people", "first", "team"],
  "protected_rules": [
    { "id": "RD-11", "reason": "the author's own posts carry about this many dashes",
      "measure": "dashes_per_100", "value": 1.02 }
  ]
}
```

(Abbreviated; the real file lists every measure.)

---

## 3. Reading the measures

Each measure is computed per post, then the median across posts is reported.

| Measure | What it describes | What a draft far from it suggests |
|---------|-------------------|-----------------------------------|
| `words` | Typical post length | The draft is a different kind of post |
| `opening_chars` | Length of the first line | Longer: the opening is carrying setup the author usually skips |
| `words_per_sentence` | Average sentence length | Much shorter: fragments were added. Much longer: essay register |
| `sentence_spread` | How much sentence lengths vary | Near zero: assembled cadence |
| `words_per_paragraph` | Paragraph weight | Much lower: one-line paragraphs were imposed |
| `first_person_per_100` | How present the author is | Lower: the draft generalises where the author would narrate |
| `contractions_per_100` | Spoken versus formal register | Zero against a contracting author: over-edited |
| `dashes_per_100` | Dash habit | Higher: the drafting tool's rhythm, not theirs |
| `fragments` | Sentences of three words or fewer | Higher: staged emphasis |
| `tiny_paragraphs` | One- or two-word paragraphs | Higher: staged emphasis |
| `triples` | Lists of three | Higher: default list length of generated prose |
| `label_lines` | Lines opening with a short label and a colon | Higher: slide formatting |
| `emoji` | Emoji per post | Use as `--usual` in the emoji audit |
| `questions`, `exclamations` | Punctuation habits | Higher: engagement prompts or enthusiasm the author does not show |
| `lowercase_starts` | Lines that begin lowercase | A deliberate style; never "correct" it |
| `closes_on_question` | Share of posts ending with a question | Tells you whether a closing question is in character |

`signature_words` are content words that appear in at least a third of the
posts. They are a prompt for the editor ("this author says 'team' and
'customers', not 'stakeholders'"), not a list to insert. Forcing them into a
draft is keyword stuffing with a personal touch.

---

## 4. Protected rules

Some reduce-tier rules describe habits a person may really have. When the
author's median crosses a threshold, the fingerprint lists the rule as
protected, and `tell_audit.py --voice` displays the finding but adds nothing to
the load.

| Rule | Protected when the author's median is at least | Meaning |
|------|-----------------------------------------------|---------|
| RD-11 Dash density | 0.8 dashes per 100 words | They write with dashes |
| RD-06 Staccato fragments | 3 fragments per post | They write in fragments |
| RD-07 One-word paragraph | 1.5 per post | They use the dramatic pause |
| RD-05 Triple list | 1.5 per post | They list in threes |
| RD-17 Label-and-colon reveal | 1.5 per post | They label their takeaways |

The thresholds are heuristics set just below the audit's own allowances, so a
rule is waived only when the author's ordinary writing would trip it.

**What can never be protected:**

- Any remove-tier rule. Nobody's voice includes a placeholder.
- RD-09 and RD-10 (stock opener and closer), RD-04 (question-and-answer
  bridge), RD-08 (announced candor), RD-19 (vocabulary cluster). These are
  either borrowed formulas or the absence of content, and an author who uses
  them habitually is better served by hearing so.
- RD-16 (nothing only the author could know). A habit of vagueness is not a
  voice.

Protection is a waiver, not an instruction. A protected rule means "do not
penalise this", never "add more of this".

---

## 5. Comparing a draft

`--compare draft.txt` measures the draft the same way and reports each measure
that falls outside the author's range.

| Measure | Tolerance (whichever is larger) |
|---------|--------------------------------|
| Words per sentence | 35% of the author's median, or 3 words |
| Words per paragraph | 50%, or 8 words |
| First-person words per 100 | 50%, or 1.5 |
| Contractions per 100 | 60%, or 1.0 |
| Dashes per 100 | 100%, or 0.6 |
| Fragments per post | 100%, or 2 |
| Emoji per post | 100%, or 1 |
| Questions per post | 100%, or 1 |

The gate fails (exit 1) when more than `--max-drift` measures are out of range;
the default is 2.

Read the result as a direction, not a verdict:

| Drift pattern | Likely cause | Response |
|---------------|--------------|----------|
| Shorter sentences, lighter paragraphs, more fragments | Staged-emphasis formatting was applied | Re-join; see the rewrite playbook §4 |
| Fewer first-person words, no contractions | The draft is in report register | Ask what the author did, and write that in the first person |
| More dashes, more questions, more emoji | Drafting-tool defaults | Run the tell and emoji audits; these will have fired there too |
| Longer sentences only | A detailed post from a usually brief author | Usually fine; check the opening still fits before the fold |
| Everything in range, but it still sounds wrong | The difference is in content or humour | Outside what numbers can show; ask the author to read it aloud |

The sample draft drifts on six measures. The edited version drifts on one.

---

## 6. Rule versus habit: settling conflicts

| Situation | Decision | Reasoning |
|-----------|----------|-----------|
| Reduce-tier rule fires; fingerprint protects it | [PROVEN] Keep the text | This is the case the mechanism exists for |
| Rule fires; the habit is visible in past posts but below the protection threshold | [RECOMMENDED] Keep one or two instances, trim the rest to the author's own rate | The draft exaggerates a real habit |
| Rule fires; no trace of the habit in past posts | [PROVEN] Fix it | It arrived with the drafting tool |
| Author insists on a stock opener or closer | [RECOMMENDED] Explain once with `tell_rules.py --explain`, then respect the decision and note it in the profile | It is their name on the post |
| Remove-tier hit the author wants to keep | [PROVEN] Do not ship it | No exception; it is a visible error |
| Fingerprint was built from assisted posts and protects several rules | [RECOMMENDED] Rebuild from older, unassisted posts | The fingerprint is describing the tool |
| Author wants to change their style on purpose | [EXPERIMENTAL] Skip `--compare`, audit against the catalogue only, and rebuild the fingerprint after ten posts in the new style | The fingerprint describes the past |

---

## 7. Keeping the fingerprint honest

- **Rebuild every few months**, or after about ten new unassisted posts.
- **Never feed edited drafts back in.** Only posts as the author wrote and
  published them. Otherwise the fingerprint converges on the editor.
- **Keep the source file.** The JSON is derived; the posts are the record.
- **One fingerprint per person.** A company page written by four people has no
  single voice to measure; build one per regular writer or use none.
- **Store it with the profile.** `assets/voice_profile_template.md` has a
  section for the generated numbers next to the things only a person can say
  about the author.

---

## 8. What the fingerprint cannot do

- It cannot verify that the supplied posts were written by the author.
- It cannot detect borrowed ideas, only borrowed cadence.
- It does not work reliably on non-English text: the contraction, first-person
  and stop-word logic is English-only.
- It says nothing about whether the author's habits are good. An author whose
  every post opens with a stock phrase has a consistent fingerprint and a
  problem.
- It is not a likeness of the person. Two authors with the same medians can
  sound nothing alike. Use it to stop an edit doing damage, not to generate
  text "in their voice" from numbers alone.
