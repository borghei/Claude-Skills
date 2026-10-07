# Swipe File: {owner}

A log of saved posts analysed for their opening pattern. One entry per post.
Run `scripts/hook_classifier.py` on the pasted texts, then correct and complete
each entry by hand. Keep the full post texts in a separate `---`-separated file
so the classifier can be re-run.

- **Owner:** {name}
- **Posts file:** {path to the pasted texts}
- **Last classified:** {YYYY-MM-DD}
- **Fold estimate used:** {140} characters (verify in the product)

## Pattern tally

Paste from `hook_classifier.py --input {file} --summary-only`, then add the
hand-corrected count.

| Pattern | Tool count | After correction | Reusable? |
|---------|-----------|------------------|-----------|
| receipt | {n} | {n} | yes |
| dated-error | {n} | {n} | yes |
| cold-scene | {n} | {n} | yes |
| belief-flip | {n} | {n} | yes |
| counter-position | {n} | {n} | yes |
| gap | {n} | {n} | yes |
| borrowed-line | {n} | {n} | yes |
| house-rule | {n} | {n} | yes |
| field-count | {n} | {n} | yes |
| asked-question | {n} | {n} | yes |
| credit | {n} | {n} | yes |
| plain-definition | {n} | {n} | yes |
| dated-bet | {n} | {n} | yes |
| list-promise | {n} | {n} | yes |
| direct-question | {n} | {n} | study only |
| announcement | {n} | {n} | study only |
| teaser | {n} | {n} | study only |
| command | {n} | {n} | study only |
| unclassified | {n} | {n} | study by hand |

**What the mix says:** {one or two sentences: what dominates, what is missing}

**Patterns to look for next:** {…}

---

## Entries

Copy this block for each saved post.

### {label: author's role, date saved}

- **Source:** {own post / someone else's}
- **Why I saved it (written at the time):** {one sentence}

**Opening**

> {first line, as written}

**Second line**

> {second line, as written}

| Field | Value |
|-------|-------|
| Pattern (tool) | {slug}, confidence {0.00} ({band}) |
| Runner-up | {slug or none} |
| Pattern (after reading) | {slug, or blend of two, or unclassified} |
| Cues that fired | {…} |
| Opening length | {n} characters |
| Body shape | {numbered list / story paragraphs / …} |
| Close | {question / statement / postscript / stock ask} |

**Tool template**

```
{template as printed by the classifier}
```

**Abstract template**

```
{roles and moves only; none of the source's nouns}
```

**Craft notes**

- {what the opening does well inside the pattern}
- {where the first concrete detail lands}
- {how the body pays off the opening}

**Material required to use it:** {from the pattern's reuse note}

**Do I have that material?** {yes: what / no / not yet}

**Cautions from the source (do not inherit):** {…}

**Reuse status:** {reusable / study only / own post}

**Used on:** {date and post, or "not yet"}

---

## Templates ready to use

Entries above where the material is in hand. This is the list to open when
there is a post to write.

| Pattern | Abstract template | My material | From entry |
|---------|-------------------|-------------|------------|
| {slug} | {template} | {the figure / date / quote} | {label} |

## Reuse log

Check before reusing a pattern, so the same one does not appear three posts
running.

| Date posted | Pattern | Opening used |
|-------------|---------|--------------|
| {YYYY-MM-DD} | {slug} | {first line} |

## Saved for something other than the opening

| Label | What I actually admired |
|-------|-------------------------|
| {label} | {the subject / the candour of the turn / the author} |
