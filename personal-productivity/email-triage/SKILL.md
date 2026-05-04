---
name: email-triage
description: >
  Classify a batch of email subjects/snippets into action categories
  (reply now / reply later / archive / delete / unsubscribe), and surface
  unsubscribe candidates and recurring senders. Use after a busy week,
  when running inbox-zero, or when the user mentions inbox triage,
  email overload, unsubscribe, or inbox zero.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: inbox
  updated: 2026-05-04
  python-tools: email_classifier.py
  tech-stack: email, productivity
---

# Email Triage

Classify a batch of email subjects + senders into action buckets and surface inbox-zero candidates.

---

## Keywords

email, inbox, inbox zero, triage, unsubscribe, mailing list, mailbox, gmail, outlook, productivity

---

## Quick Start

1. Export inbox to CSV with columns: `subject,sender,snippet,received_at`
2. Run: `python scripts/email_classifier.py inbox.csv`
3. Review action buckets; act on each in order

---

## Core Workflows

### Workflow 1: Weekly Inbox Triage
1. Export the past week's inbox
2. Run classifier
3. Action in order: reply-now → reply-later (move to follow-up folder) → archive → unsubscribe → delete
4. Apply Gmail filters (see `assets/gmail_filter_template.md`) so future similar emails route automatically

**Time Estimate:** 30-45 minutes for a busy week.

### Workflow 2: Unsubscribe Pass
1. Run classifier; review unsubscribe candidates
2. Unsubscribe in batch (most senders honor unsubscribe links within ~10 days)
3. For senders that don't honor, set Gmail filter to auto-delete

**Time Estimate:** 15 minutes per pass.

### Workflow 3: Inbox-Zero Reset
1. Apply the full inbox-zero method from `references/inbox_zero_method.md`
2. Move every email older than 30 days to archive (you'll find 1% later via search)
3. Triage the remaining recent emails using the classifier

**Time Estimate:** 1-2 hours one-time; then 20 min/week to maintain.

---

## Tools

### email_classifier.py

Classifies email rows into action buckets using rule-based pattern matching on sender domain, subject line, and snippet.

```bash
python scripts/email_classifier.py inbox.csv
python scripts/email_classifier.py inbox.csv --json
```

Action buckets:
- **reply_now** — direct addressing, time-sensitive language, named-person sender
- **reply_later** — informational threads, longer non-urgent
- **archive** — receipts, confirmations, completed transactions
- **unsubscribe** — newsletters, marketing, promotional
- **delete** — spam patterns, low-signal senders
- **review** — couldn't classify confidently

---

## Reference Guides

- **`references/inbox_zero_method.md`** — Method, daily routine, common pitfalls

---

## Templates

- **`assets/gmail_filter_template.md`** — Common Gmail filter recipes for the action buckets above

---

## Best Practices

- **The 2-minute rule:** if a reply takes < 2 minutes, do it now.
- **Don't archive instead of unsubscribing.** Recurring senders compound — kill the source.
- **Process in batches.** Constant inbox checking destroys focus more than email itself.
- **Inbox is not a to-do list.** Move action items to a real task tool.
