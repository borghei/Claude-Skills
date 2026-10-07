# Post Brief: {working title}

Fill this in with the author before any drafting. Leave a material field blank
if the author does not have it; a blank is information. When complete, copy the
answers into the JSON shape at the bottom and run `scripts/angle_picker.py`.

- **Author:** {name, role, company}
- **Brief taken by:** {name}
- **Date:** {YYYY-MM-DD}
- **Intended posting week:** {week of …}

## 1. The post in one line

**Topic:** {what the post is about, in the author's own words}

**Why now:** {what happened recently that makes this worth posting}

## 2. Goal (choose one)

- [ ] **conversation** — replies from people who have done the same thing
- [ ] **saves** — something a reader will want to come back to and use
- [ ] **reshares** — a claim or a credit others will pass on
- [ ] **inbound** — the right people getting in touch afterwards

If two are ticked, the brief is not finished. Which one would the author give
up last?

## 3. Audience

**Who exactly:** {role, seniority, kind of company. One sentence.}

**What they already know about this:** {…}

**What they probably believe that this post touches:** {…}

## 4. Material inventory

Write what the author actually has. Exact words and exact numbers. If a field
would need inventing, leave it empty.

| Field | What to capture | The author's answer |
|-------|-----------------|---------------------|
| `figure` | One precise number and what it counts | {…} |
| `dated_event` | What happened, on what date, and what it cost | {…} |
| `scene` | A moment: where, who was there, what was said or seen | {…} |
| `changed_belief` | Something they believed and no longer do | {…} |
| `opposing_view` | Common advice they disagree with, and for which case | {…} |
| `before_after` | Before figure, after figure, time span, same measure | {…} |
| `quote` | Someone's exact words, and who said them | {…} |
| `rule` | A rule they or the team keep | {…} |
| `sample_count` | How many of something they examined, and the pattern | {…} |
| `question_received` | A question they were really asked, and by whom (role) | {…} |
| `person_to_credit` | Who did a specific thing, and what it was | {…} |
| `term` | A term the audience uses loosely | {…} |
| `prediction` | What they expect, by when, and what would prove them wrong | {…} |
| `steps` | Three or more steps or checks they actually follow | {1. … 2. … 3. …} |

**How was each figure measured?** {source, period, who can confirm it}

## 5. The part that did not work

**What went wrong, cost more than expected, or is still unsolved?** {…}

**What would the author warn someone about before they copied this?** {…}

## 6. Constraints

- **Must include:** {…}
- **Must not name or reveal:** {clients, colleagues, figures, projects}
- **People who may be named:** {name: confirmed on date}
- **People to describe by role only:** {…}
- **Needs sign-off from:** {comms / legal / manager / nobody}
- **Length:** {short / standard / long / no preference}
- **Link to include, if any:** {URL; body or first comment?}
- **Hashtags the author wants:** {up to three, or none}

## 7. Voice

- **Voice profile on file?** {yes: path / no}
- **Two past posts that sound like them:** {first lines}
- **Words they use for the key things in this post:** {e.g. "all-hands", not "town hall"}
- **Anything they never say:** {…}

## 8. After drafting

- [ ] Picker run; top options offered to the author
- [ ] Pattern chosen by the author: {slug}
- [ ] Draft passes `scripts/post_gate.py`
- [ ] Every figure, name and quote checked against section 4
- [ ] Author has read the draft aloud
- [ ] Sign-off received from: {…}

## JSON for the picker

```json
{
  "topic": "{topic}",
  "goal": "{conversation | saves | reshares | inbound}",
  "audience": "{audience}",
  "author": "{author}",
  "length": "{short | standard | long}",
  "material": {
    "figure": "",
    "dated_event": "",
    "scene": "",
    "changed_belief": "",
    "opposing_view": "",
    "before_after": "",
    "quote": "",
    "rule": "",
    "sample_count": "",
    "question_received": "",
    "person_to_credit": "",
    "term": "",
    "prediction": "",
    "steps": []
  },
  "must_include": [],
  "must_avoid": []
}
```
