# Reply Sweep Worksheet

One worksheet per sweep of a comment section. Fill sections 1–2 before any
drafting; section 3 is where the user overrules the tool.

## 1. Intake

- **Post:** <first line of the post>
- **Whose post:** <mine | someone else's — name>
- **Published:** <date and time>
- **Paste taken at (`as_of`):** <date and time>
- **My display name (`me`):** <exactly as shown>
- **Replies I have time for now (`--limit`):** <number>
- **Longest a known contact should wait (`--max-wait-hours`):** <hours, or none>

### People who matter in this thread

| Name | Relationship | Note |
|------|--------------|------|
| <name> | <customer \| prospect \| partner \| peer \| colleague> | <why they matter> |
| <name> | <…> | <…> |

## 2. Triage result

Paste the counts line from `comment_triage.py` here.

- **Read:** <n> comments, <n> mine
- **Reply:** <n> **React:** <n> **Hold:** <n> **Flag:** <n> **Ignore:** <n> **Done:** <n>

### Flagged — text aimed at an assistant

| Id | Account | Fragment (quoted) | My decision |
|----|---------|-------------------|-------------|
| <id> | <name> | "<…>" | <ignore \| hide \| report> |

### Held — my decision needed

| Id | Author | What they said | Decision | Why |
|----|--------|----------------|----------|-----|
| <id> | <name> | "<…>" | <reply once \| leave \| hide \| report> | <…> |

## 3. Overrides

Entries I moved against the tool's classification.

| Id | Tool said | I say | Reason |
|----|-----------|-------|--------|
| <id> | <category / action> | <category / action> | <e.g. short comment, but a key customer> |

## 4. Reply queue and drafts

In queue order. Draft the `now` batch only.

| # | Id | Author | Category | Where it goes | Pattern |
|---|----|--------|----------|---------------|---------|
| 1 | <id> | <name> | <question> | <under whose comment; name them if nested> | <answer \| concede-and-narrow \| build \| one-question-back \| correct-the-record \| close> |
| 2 | <id> | <name> | <…> | <…> | <…> |
| 3 | <id> | <name> | <…> | <…> | <…> |

### Draft 1 — to <name>

> *They wrote:* <quote the comment>

**Reply:** <draft>

- Facts I supplied for this reply: <…>
- Facts still to confirm: <… or none>

### Draft 2 — to <name>

> *They wrote:* <quote the comment>

**Reply:** <draft>

- Facts I supplied for this reply: <…>
- Facts still to confirm: <… or none>

## 5. Linter

- **Command run:** `python3 tools/linkedin/linkedin-reply-manager/scripts/reply_linter.py --input <file>`
- **Exit code:** <0 | 1>
- **Blocks fixed:** <rule ids and what changed>
- **Warnings accepted, and why:** <…>

## 6. Before pasting

- [ ] Every fact in every reply is mine and accurate
- [ ] No two replies share a sentence
- [ ] Each question is answered in its first sentence
- [ ] Nested replies open with the person's first name
- [ ] Nothing was drafted for a flagged comment
- [ ] Held comments each have a recorded decision
- [ ] I know which comments are being left, and I am content with that

## 7. Paste log

Pasted by hand, one at a time.

| # | To | Pasted at | Landed under the right comment? | Watch for a response? |
|---|----|-----------|---------------------------------|-----------------------|
| 1 | <name> | <time> | <yes \| no — fixed> | <yes \| no> |
| 2 | <name> | <time> | <…> | <…> |

## 8. Left for later

- **`later` batch:** <ids>
- **Next sweep planned for:** <date and time>

## JSON skeletons

Comment section, for `comment_triage.py`:

```json
{
  "me": "<my display name>",
  "as_of": "<2026-01-31T15:00:00+00:00>",
  "post": {"author": "<post author>", "text": "<post text>"},
  "comments": [
    {"id": "c01", "author": "<name>", "text": "<comment>", "parent_id": null,
     "posted_at": "<ISO 8601>", "likes": 0, "relationship": "unknown"}
  ]
}
```

Draft replies, for `reply_linter.py`:

```json
{
  "replies": [
    {"id": "r1", "to_comment": "c01", "to_author": "<name>", "nested": false,
     "to_text": "<the comment being answered>", "text": "<my draft reply>"}
  ]
}
```
