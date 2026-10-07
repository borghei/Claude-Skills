# Voice Profile: {author name}

Fill this in once per author and keep it with their fingerprint file. Sections
1 and 2 come from `scripts/voice_fingerprint.py`; sections 3 to 6 can only come
from the author or someone who edits them regularly.

- **Profile owner:** {who maintains this file}
- **Last rebuilt:** {YYYY-MM-DD}
- **Source posts:** {path to the past-posts file} ({n} posts, dated {from} to {to})
- **Were any source posts drafted with assistance?** {no / yes: which, and why they were kept}

## 1. Measured habits

Paste from `voice_fingerprint.py --input {file}`.

| Measure | Median | Notes |
|---------|--------|-------|
| Post length (words) | {n} | |
| Opening line (characters) | {n} | |
| Words per sentence | {n} | |
| Sentence spread | {n} | |
| Words per paragraph | {n} | |
| First-person words per 100 | {n} | |
| Contractions per 100 | {n} | |
| Dashes per 100 words | {n} | |
| Fragments per post | {n} | |
| Triples per post | {n} | |
| Emoji per post | {n} | Use as `--usual` in the emoji audit |
| Closes on a question | {share} | |

Confidence label from the tool: {thin / usable / solid}

## 2. Protected rules

Rules the audit waives for this author, and why.

| Rule | Reason reported by the tool | Agreed with the author? |
|------|-----------------------------|-------------------------|
| {RD-xx} | {reason} | {yes / no / not asked} |

Rules the author has asked to keep **against** the tool's advice (record the
date and their reason):

- {rule id}: {reason}, {date}

## 3. Words and phrases

- **Says:** {words the author reaches for: e.g. "customers" not "users"}
- **Never says:** {words that are off-limits for this author, beyond the catalogue}
- **Spelling and style:** {British / American; numerals or words under ten; Oxford comma}
- **Names things as:** {how they refer to their company, team, product, role}

## 4. How they open and close

- **Typical opening:** {a figure / a date / a scene / a flat claim}
- **Would never open with:** {…}
- **Typical close:** {a question / the last fact / a postscript}
- **Asks for comments?** {never / sometimes, in these words: …}

## 5. Subjects and limits

- **Writes about:** {three or four subjects}
- **Will not write about:** {clients by name, salaries, politics, …}
- **People they may name without asking:** {…}
- **People or companies that must be described by role only:** {…}
- **Figures that must be checked with {whom} before publishing:** {…}

## 6. Things an editor should know

- **Humour:** {dry / none / self-deprecating; an example}
- **How they handle being wrong in public:** {…}
- **A post of theirs that sounds most like them:** {first line or link kept privately}
- **A past edit they rejected, and why:** {…}

## Gate settings for this author

```bash
python3 scripts/tell_audit.py --input {draft.txt} --voice {voice.json} --max-load {6}
python3 scripts/emoji_audit.py --input {draft.txt} --usual {n} --fail-under {60}
python3 scripts/voice_fingerprint.py --input {past_posts.txt} --compare {draft.txt} --max-drift {2}
```
