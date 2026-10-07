# Pre-Publish Gate

What `scripts/post_gate.py` checks, why each check has the level it has, what
the tool cannot check, and how to tune it.

The gate is the last step before the author pastes the text into the composer.
It is a mechanical check on a text file. It does not publish, schedule or
contact anything.

Thresholds are editorial heuristics. Platform numbers are current as of
writing and must be verified in the product; both are command-line options so
that a change in the platform is a change in a flag, not in the script.

## Contents

1. Levels and the verdict
2. The fifteen checks
3. Platform mechanics and their caveats
4. Manual checks the tool cannot do
5. Tuning
6. Reading a failing report
7. What the gate is not

---

## 1. Levels and the verdict

| Level | Meaning | Effect |
|-------|---------|--------|
| **block** | A visible error, or a line that undermines the whole post | Any one fails the gate |
| **warn** | Likely to cost readers; sometimes justified | More than `--max-warnings` (default 3) fails the gate |
| **note** | Worth a glance | No effect |

Exit codes: 0 passed, 1 failed, 2 bad input.

A draft with three warnings passes. That is intended: a deliberate long
opening, a link that is the point of the post and a fourth hashtag can each be
a reasonable choice. Four such choices in one draft is a pattern worth a second
look.

---

## 2. The fifteen checks

### Opening (first non-empty line)

| ID | Check | Level | Fires when | Rationale |
|----|-------|-------|------------|-----------|
| PG-01 | Opening runs past the fold | warn | First line longer than `--fold-chars` | Text after the cut is seen only by readers who expand. A long first line is acceptable if its first clause carries the point |
| PG-02 | Stock opening phrase | block | "In today's…", "I'm excited to…", "Let's talk about…", "Have you ever…", "Unpopular opinion" and similar | Recognised before it is read; no fact can follow fast enough to recover |
| PG-03 | Opening in capitals | block | Over 70% of letters in the first line are upper case | Reads as shouting |
| PG-04 | Opens on a question to the reader | warn | First line ends with a question mark | Asks for attention before giving a reason. A reported question usually ends with a full stop and does not fire |
| PG-05 | Opening teases without content | warn | Six words or fewer with no numeral and no proper noun | "This changed everything." tells the reader nothing about whether the post concerns them |

### Body

| ID | Check | Level | Fires when | Rationale |
|----|-------|-------|------------|-----------|
| PG-06 | Over the character limit | block | Longer than `--max-chars` | The composer will refuse it or cut it |
| PG-07 | Very short | note | Shorter than `--min-chars` | Fine for announcements; otherwise evidence may be missing |
| PG-08 | Placeholder or markup left in | block | `[link]`, `[Your Company]`, `{name}`, `XX`, `TK`, `**bold**`, a pound-sign heading | A visible slot or literal asterisks; the most avoidable public mistake |
| PG-09 | Dense paragraph | warn | Any paragraph over 70 words | Hard to read on a phone; usually two beats sharing a paragraph |
| PG-10 | Too many hashtags | warn | More than three | They are labels; a row of six reads as reach-seeking |
| PG-11 | Link in the body | warn | A URL appears and `--allow-links` is not set | A widely followed practice is to put links in the first comment. Its effect is unverified, so this is a warning with an override, not a rule |
| PG-12 | Nothing only the author could know | block / note | **Block** when two or more of these are missing: a numeral, a named person, company or place, a first-person word. **Note** when one is missing | A post with none of them could carry anyone's name |
| PG-13 | Machine-sounding habits | warn | Two or more of: contrast frame, question-and-answer bridge, announced candor, stock vocabulary | A spot check only. A full audit is a separate job for a dedicated editing pass |
| PG-14 | Exclamation marks | note | More than two | Enthusiasm asserted in punctuation |

### Close (last two prose lines, ignoring a hashtag line)

| ID | Check | Level | Fires when | Rationale |
|----|-------|-------|------------|-----------|
| PG-15 | Stock closing line | block | "What do you think?", "Thoughts?", "Agree?", "Tag someone…", "Repost if…", "Follow for more", "Let that sink in", "Comment X below" | A generic ask draws generic replies and marks the post as engagement-seeking |

The gate does not require a closing question. A post that ends on its last
fact passes.

---

## 3. Platform mechanics and their caveats

| Assumption | Default | Confidence | If it changes |
|------------|---------|------------|---------------|
| Post length limit | 3,000 characters | Current as of writing; verify in the product | `--max-chars N` |
| Characters shown before truncation | 140 | A deliberately conservative estimate for a phone. Desktop shows noticeably more, and the cut depends on line breaks, device and app version | `--fold-chars N` |
| Markdown is not rendered | Asterisks and pound signs appear literally | Current as of writing | Remove the markup patterns from `PLACEHOLDER` in the script |
| How character count is computed | The tool counts Unicode code points after trimming | The composer may count some emoji or line breaks differently | Leave a margin of a few dozen characters near the limit |

**On the fold.** Nobody outside the platform knows the exact cut, and it moves.
The useful discipline does not depend on the number: put the point in the first
clause. If the author previews the post on their own phone and sees more room,
raise `--fold-chars` to what they observe.

**On everything else.** This skill makes no claim about how the feed ranks
posts: not about posting times, link placement, hashtag counts, edits after
publishing, or format preferences. Advice of that kind circulates widely and is
rarely checkable. Where the gate encodes a common practice (links, hashtags)
it does so as a warning the author can override, and says so in the message.

---

## 4. Manual checks the tool cannot do

Run through these after the gate passes. The agent should verify each one
against the brief and report any it cannot confirm.

### Facts

- [ ] Every figure in the draft appears in the brief with the same value and unit.
- [ ] Every figure says what it counts and over what period.
- [ ] Every quote is word for word as supplied.
- [ ] Every date is right, and "last week" will still be true on the day of posting.
- [ ] No claim in the draft is stronger than the one the author made.

### People

- [ ] Everyone named has agreed to be named, or the brief says they may be.
- [ ] Anyone in `must_avoid` is absent, including by obvious description.
- [ ] A cost or failure that fell on someone else is described by role only.
- [ ] Credit is given for the specific act, to the person who did it.

### Reading

- [ ] The opening still makes sense when cut off mid-sentence.
- [ ] The second line adds something and does not restate.
- [ ] The post contains a cost, exception or open question.
- [ ] Each paragraph would be missed if deleted.
- [ ] The author has read it aloud and nothing made them wince.

### Employer and legal

- [ ] No unreleased numbers, client names or internal project names.
- [ ] Anything about a regulated product, a financial result or a personnel
      matter has been seen by whoever needs to see it.
- [ ] If the post discloses a commercial relationship, it says so plainly.

---

## 5. Tuning

| Situation | Setting | Why |
|-----------|---------|-----|
| Author consistently writes two-clause openings that front-load the point | `--fold-chars 200` | Stops PG-01 firing on openings that work |
| The link is the purpose of the post (a job advert, a report) | `--allow-links` | The warning is a heuristic, not a rule |
| Company page with stricter standards | `--max-warnings 1` | Fewer judgment calls allowed through |
| Announcements and credits | `--min-chars 120` | Removes the "very short" note |
| Checking a batch in a script | `--format json` and read `passed` | Stable machine output |

Do not weaken the blockers. If PG-12 keeps firing, the fix is to get a fact
from the author, not to lower the bar.

### Using it in a loop

```bash
for draft in drafts/*.txt; do
  python3 scripts/post_gate.py --input "$draft" --format json > "${draft%.txt}.gate.json" \
    || echo "needs work: $draft"
done
```

Exit code 2 means the file could not be read; treat it as a broken input, not
as a failed draft.

---

## 6. Reading a failing report

The sample draft produces:

```
Verdict: FAIL - 2 blocker(s), 3 warning(s) (limit 3), 0 note(s)
[BLOCK] PG-08 Placeholder or markup left in      seen: [link]
[BLOCK] PG-15 Stock closing line                 seen: What do you think?
[WARN ] PG-01 Opening runs past the fold         seen: 202 characters; the feed cuts near 140
[WARN ] PG-09 Dense paragraph                    seen: 1 paragraph(s) over 70 words
[WARN ] PG-10 Too many hashtags                  seen: 6
```

Work it in this order:

1. **PG-08.** Either the author supplies the link (and it moves to the first
   comment, or `--allow-links` is used), or the sentence goes.
2. **PG-15.** Write a question from the brief's goal. This draft's goal is
   conversation, so: what broke for others who tried the same thing?
3. **PG-01.** The date and the mistake are in paragraph two. Promote them.
4. **PG-09.** The long paragraph holds three beats: the cost, the bad
   fortnight, the replacement. Split at each, and turn the three replacement
   steps into a numbered list.
5. **PG-10.** Keep the two hashtags that name the subject.

The revised sample is the result. Note that fixing PG-01 and PG-09 improved the
post far more than fixing the two blockers; the blockers were merely the errors
that could not be allowed out.

---

## 7. What the gate is not

- **Not a quality score.** A dull, accurate, well-formatted post passes.
- **Not a style audit.** PG-13 looks for four habits. A complete catalogue with
  tiers, allowances and voice protection is a separate concern.
- **Not a fact-checker.** It cannot know whether 62 is the right number.
- **Not a prediction.** Passing says nothing about how many people will see or
  respond to the post.
- **Not a substitute for the author reading it.** The last check is always a
  person.
