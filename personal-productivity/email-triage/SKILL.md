---
name: email-triage
description: >
  Classify a batch of emails into action categories (reply now, reply later,
  archive, delete, unsubscribe) and surface unsubscribe candidates. Use after
  a busy week, running inbox zero, or triaging email overload.
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

## Clarify First

Before triaging, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Inbox export fields** — subject, sender, snippet drive classification accuracy; missing columns degrade the buckets
- [ ] **Priority / VIP senders** — who always routes to reply_now regardless of content
- [ ] **Unsubscribe tolerance** — purge all marketing vs keep newsletters you value; sets how aggressive the unsubscribe/delete buckets are

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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
