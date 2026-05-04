# Insight Extraction Patterns

Heuristic patterns for pulling structured outcomes from messy meeting transcripts. The analyzer applies these automatically; this guide explains them so you can verify and override.

---

## Decisions

A decision is **a choice that closes a question** — past or future, but no longer open. Trigger phrases:

- "we decided…"
- "we agreed…"
- "we'll go with…" / "let's go with…"
- "decision is…" / "the call is…"
- "sign-off" / "sign off"
- "final call on…"

**False positives to watch for:**
- "We decided last quarter…" (this is a *prior* decision, not a new one — note it but mark as historical)
- "I think we should decide…" (still open, not closed)

---

## Action Items

An action item has three parts: **what, who, when**. The analyzer guesses owner and due date heuristically — verify both.

### What — trigger phrases
- "I'll / we'll / I will / we will…"
- "I need to…" / "we should…"
- "follow up", "circle back", "sync"
- "next step is…" / "action item is…"

### Who — owner heuristic
- "**I'll** send the draft." → owner = current speaker
- "**Priya will** review by Friday." → owner = Priya
- "**We'll** ship Monday." → owner = team

### When — due date heuristic
- "by tomorrow / today" → tomorrow / today
- "by Friday" → next Friday
- "by next week" → next week
- "EOD / EOW / COB" → end of day / week / business
- "by 5/12" → that date

**False positives to watch for:**
- "If we ship, then…" (conditional, not committed)
- "I might send the draft" (uncommitted)

---

## Open Questions

Anything ending in `?` is captured. Plus explicit triggers like "open question", "still TBD".

**Triage:**
- Move questions to a parking-lot doc if they need follow-up research
- If a question got answered later in the same meeting, mark closed
- Keep unanswered questions in the recap so they have an owner

---

## Risks

Risk markers:

- "risk", "concern", "blocker", "blocked on"
- "worried about / that"
- "if X (slips/fails/breaks)…"

**Risk vs. concern triage:**

| Pattern | Treat as |
|---------|----------|
| Has owner + mitigation | Risk (track) |
| Has owner, no mitigation | Risk (urgent — needs mitigation plan) |
| No owner | Concern (raise in next meeting; not a tracked risk yet) |

---

## Pains (customer interviews)

Phrases that surface a problem worth solving:

- "painful", "frustrating", "struggle"
- "hard to / difficult to"
- "takes too long", "wastes time"
- "wish we could…", "I hate when…"

**Triangulation:** A pain mentioned by 1 customer is a hypothesis. Same pain across 3+ customers is a signal. Same pain across 5+ in your ICP is product roadmap material.

---

## Quotes

Verbatim sentences over 12 words from a named speaker. Use them to:

- Source customer language for marketing copy (don't paraphrase customer pain — quote it)
- Anchor user-story authoring with real wording
- Build voice-of-customer dashboards over time

---

## Triangulation Across Multiple Interviews

After 5+ interviews:

1. Tag each insight by ICP segment, role, company size
2. Cluster pains — frequency × severity = priority
3. Look for *anti-signals*: pains expected but not mentioned (often more telling than what is mentioned)
4. Promote a pain to "validated problem" only if it appears across interviews unprompted (you can hear yourself in their answer = leading question, not validation)

---

## Quality Checklist Before Sending Recap

- [ ] Every action item has owner + due date (or explicitly "TBD — will assign by EOD")
- [ ] Decisions are phrased as decided, not as proposals
- [ ] Open questions have someone on the hook to drive resolution
- [ ] Risks have either a mitigation plan or an owner to draft one
- [ ] No quote is paraphrased — verbatim or removed
