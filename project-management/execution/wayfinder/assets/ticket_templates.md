# Wayfinding ticket templates

Two ticket shapes live on a map. Decision tickets resolve a question; implementation
tickets build something once the questions they depend on are answered. Copy the one
you need into your tracker. The JSON field names in brackets match what
`decision_map_validator.py` and `tracer_slice_checker.py` read.

---

## Decision ticket

**Title:** <the decision in a few words, e.g. "Unit of metering"> [`title`]

**Type:** research | prototype | discussion | enabling-task [`type`]

- *research* — a fact is missing; someone reads docs, data or an API and reports back.
- *prototype* — people need something concrete to react to before they can choose.
- *discussion* — the facts are in; a person with authority must choose.
- *enabling-task* — work that must happen before the decision is possible (get sandbox
  access, export a data sample). It decides nothing on its own.

**Question:** <one sentence ending in "?" — what exactly must be decided> [`question`]

**Options:** [`options`, at least two for discussion and prototype]

1. <option> — <main consequence>
2. <option> — <main consequence>
3. Do nothing / defer — <what that costs>

**Owner:** <the person who makes the call, not the person who researches it> [`owner`]

**Blocked by:** <ticket ids whose answers this question needs> [`blocked_by`]

**Decide by:** <YYYY-MM-DD and what slips if it is late> [`decide_by`]

**Status:** open | claimed | resolved | out-of-scope [`status`, `claimed_by` when claimed]

### Resolution (fill in when closing) [`resolution`]

- **Chosen:** <option>
- **Why:** <the reason that would survive a newcomer asking "why not the other one?">
- **Rejected:** <options not taken and the one-line reason each>
- **Consequences:** <what this unblocks, what fog it clears, what new tickets it opens>
- **Revisit if:** <the observation that would reopen it>

---

## Tracer-bullet implementation ticket

**Title:** <behaviour a person can observe, e.g. "One workspace's seat-hours appear at the provider"> [`title`]

**Derived from:** <resolved decision ids this ticket puts into effect> [`derived_from`]

**Blocked by:** <ticket ids that must be done first, or "none"> [`blocked_by`]

**Layers crossed:** <every layer the slice touches, e.g. capture → job → API client → test> [`layers`]

**Demo:** <what someone will run or look at to see it working> [`demo`]

**Acceptance criteria:** [`acceptance_criteria`]

- [ ] <observable, testable statement with a number or a concrete example>
- [ ] <edge case or failure path>

**Estimate:** <days, three or fewer — otherwise slice thinner> [`estimate_days`]

**Out of scope for this slice:** <the tempting adjacent work that belongs to a later slice>

---

## Wide refactor phase ticket (expand / migrate / contract)

Use only for a mechanical change that fans out across many callers (a rename, a type
change on a shared field). It cannot be a vertical slice, so it is sequenced instead.

**Title:** <phase verb + change> [`title`]

**Pattern:** expand | migrate | contract [`pattern`]

**Refactor group:** <one shared name for all phases> [`refactor_group`]

**Blocked by:**

- *expand*: nothing in the group.
- *migrate*: the expand ticket. One ticket per batch of callers.
- *contract*: every migrate ticket in the group.

**Acceptance criteria:**

- [ ] expand — new form exists beside the old; no caller changes; suite passes
- [ ] migrate — no caller in this batch uses the old form; suite passes after the batch
- [ ] contract — old form removed; a search for it returns zero hits
