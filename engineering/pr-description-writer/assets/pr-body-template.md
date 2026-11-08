<!--
PR body template. Delete every comment before opening the PR; pr_body_lint.py
warns on leftovers. Keep the whole body under ~400 words: link out for detail.
-->

## Summary

<!-- One or two sentences: what changes for whom. Then, only if it saves reading,
ONE small picture: a diff-sketch of the shape, a call tree, a file tree, or a
mermaid sequence diagram. Pick the smallest view that makes the point. -->

## Why

<!-- The problem in the user's or operator's terms, plus the ticket link.
"BILL-412" alone is not a why. -->

## Evidence

<!-- Before and after, strongest available tier first:
screenshot or recording (UI) > test or command output (behaviour) > CI/staging run link > metrics.
Redact tokens, cookies, emails and customer IDs from anything pasted. -->

**Before:**

**After:**

## How to verify

<!-- Numbered steps a reviewer can repeat in under 10 minutes, with exact commands
and the expected result of each. "Tested locally" is not a step. -->

1.
2.
3.

## Merge risk

<!-- Door: two-way (revert is a full rollback) or one-way (revert does not undo
it: migrations, public API/contract changes, persisted formats, data deletion,
external side effects). Run scripts/risk_classifier.py --emit-section for a draft. -->

**Classification:**
**Blast radius:**
**Rollback plan:**
