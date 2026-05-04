# Gmail Filter Recipes

Filters route incoming email automatically so you process less. Below are filter recipes mapped to the action buckets in this skill.

To create: Gmail → Settings → Filters and Blocked Addresses → Create new filter.

---

## Auto-Archive Receipts

Subject contains: `(receipt OR invoice OR "order confirmed" OR "payment received" OR "thank you for your order" OR "your order")`

**Action:** Skip Inbox, Apply label "Receipts", Mark as read

---

## Auto-Archive Calendar Invites

From: `(calendar-notification@google.com)` OR has-attachment:ics

**Action:** Skip Inbox, Apply label "Calendar"

---

## Auto-Label Newsletters / Marketing

From: contains `(newsletter OR marketing OR no-reply OR noreply)` OR has the words `unsubscribe`

**Action:** Skip Inbox, Apply label "Newsletters", Mark as read

---

## Auto-Delete Repeated Spammy Senders

After unsubscribing fails:

From: `[specific sender]`

**Action:** Delete it

---

## Star Time-Sensitive

Subject contains: `(urgent OR ASAP OR "action required" OR deadline)`

**Action:** Star it, Apply label "Today"

---

## Auto-Forward to Task Tool

For senders that always send tasks (e.g., your manager's tasking emails):

From: `[manager email]` AND Subject contains: `(action OR task OR todo OR please)`

**Action:** Forward to: `[your-task-tool-inbox-address]`

---

## Filter for Mentioned-By-Name

Has the words: `[your first name]` OR `[your last name]`

**Action:** Star it (often catches "Hi [your name]" direct asks)

---

## Mute Long Threads

For threads in CC where you don't need to follow:

To: `[your email]` AND not from: `[your email]` AND NOT direct address

**Action:** Skip Inbox (the thread continues but doesn't ping)

---

## Common Filter Mistakes

- **Filter that auto-deletes.** Use sparingly; sender patterns drift.
- **Single-keyword filter that catches too broadly.** Always combine with sender or other narrowing terms.
- **No periodic review.** Senders / patterns change. Quarterly review of filter list.
- **Over-engineering.** 5-15 filters work; 50+ create their own confusion.

---

## Outlook / Exchange equivalents

Same recipes work in Outlook via Rules. Logic is similar; UI varies.

For business email, your IT team may have policies on auto-forwarding (often blocked) and external auto-replies. Check before relying on auto-forward.
