# INVEST and Story Splitting Guide

A deep reference on the INVEST criteria (Bill Wake), the 9 splitting patterns (Richard Lawrence), and the SPIDR alternative (Mike Cohn). Includes worked examples of horizontal-vs-vertical splits and refinement session structure.

---

## Part 1: INVEST in depth

INVEST was published by Bill Wake in 2003 (XP Magazine) as a checklist for "good stories." It is a heuristic for **form quality**, not for strategic substance. A 6/6 story can still be the wrong story to build -- pair INVEST with strategic checks from `prioritization-frameworks/` and `discovery/`.

### I -- Independent

**Definition:** The story can be developed, demoed, and shipped without waiting for another story to be completed first.

**Why it matters:** Coupled stories force ordering, create blocking dependencies, and ruin sprint flow. They also obscure value (you cannot demo the slice on its own).

**Common failures:**
- "Implement backend API" + "Implement frontend UI" -- the frontend cannot ship without the backend
- "Set up database schema" + "Build user profile" -- the second depends on the first
- "Feature flag the experiment" + "Build the experiment" -- coupled by intent

**Fix:** Vertical slicing (see Part 2). Replace coupled tasks with thin end-to-end slices that each deliver a sliver of user value.

**Sometimes acceptable dependencies:**
- A shared spike that resolves a technical unknown can block subsequent stories. Mark it explicitly and time-box.
- A platform foundation (auth, billing) that everything depends on. Sequence it explicitly and acknowledge.

### N -- Negotiable

**Definition:** The story describes WHAT to build and WHY, but not HOW. Implementation is open to the engineers.

**Why it matters:** Negotiability respects the team's expertise. When PMs prescribe implementation, they (1) take responsibility they cannot back up technically, and (2) prevent the team from finding a better solution.

**Common failures:**
- "Use Redis to cache..." (prescribes the technology)
- "Add a button at coordinates 240,180..." (prescribes the design)
- "Implement using event sourcing..." (prescribes the architecture)

**Fix:** Strip implementation language. Replace "Use Redis" with "Page load under 200ms p95." Replace "Add a button at coordinates..." with the user outcome and link to design.

**The 800-character rule of thumb:** Most negotiable WHATs fit in under 800 characters. Long WHATs typically smuggle in implementation specs.

### V -- Valuable

**Definition:** Delivers value to a user, a customer, or a business stakeholder. If the only beneficiary is the engineering team, it is a task, not a story.

**Why it matters:** Without value, the team is shipping motion. The PM should be able to answer "who benefits if this is the only thing we ship this quarter?"

**Common failures:**
- "Refactor the auth module" (no user benefit articulated)
- "Upgrade dependencies" (operational hygiene, not story)
- "Add unit tests for X" (engineering practice, not story)

**Fix for technical-debt stories:** Articulate the value chain. "Refactor auth to reduce login failure rate from 2.4% to <1%" is valuable. "Refactor auth" alone is not.

**Bona fide engineering tasks:** Some work is genuinely engineering hygiene with no user-facing outcome. Track these separately from feature stories (e.g., as "tech debt" tickets), not as user stories.

### E -- Estimable

**Definition:** The team can estimate effort with reasonable confidence -- typically within 2x.

**Why it matters:** Unestimable stories cannot be sequenced, budgeted, or committed to. They also signal that the team does not understand the work, which is the real problem.

**Common failures:**
- "Improve performance" (unclear what changes, unclear how to measure)
- "Add AI features" (unclear scope, unclear constraints)
- "Make it more delightful" (no testable outcome)

**Fix:** If the team cannot estimate, the story is too vague or too large. Run a spike (recipe 9 below), or split until each slice is sizeable.

**The "two engineers, 2x" test:** Have two engineers estimate independently. If their estimates differ by more than 2x, the story is not Estimable.

### S -- Small

**Definition:** Fits within one sprint. Most teams target 1-5 days of effort per story.

**Why it matters:** Small stories (1) flow through the system faster, (2) reduce work-in-progress risk, (3) provide more frequent demoable value, and (4) reduce the cost of being wrong.

**Common failures:**
- Stories estimated at 8+ days
- Stories that span multiple personas or use cases
- "Build the dashboard" (typically 3+ weeks)

**Fix:** Apply the 9 splitting patterns (Part 2). A 10-day story almost always has 2-3 vertical slices hiding inside it.

**Too small is also bad:** A 2-hour task is not a story; it is a task. Roll it up into a story with siblings, or attach it as a sub-task.

### T -- Testable

**Definition:** Acceptance criteria are observable and verifiable. Someone (QA, the PM, the user) can check whether the story is done.

**Why it matters:** Untestable stories produce ambiguous "done" decisions. They also block automation: if you cannot describe the test, you cannot write it.

**Common failures:**
- "The system is fast" (not testable -- how fast? on what?)
- "Users love the new flow" (not testable -- how measured?)
- "Works on all browsers" (vague -- which browsers, which OS)

**Fix:** Rewrite acceptance criteria as observable outcomes with concrete thresholds.

**Bad:** "Search is fast."
**Good:** "Search returns first result within 200ms p95 for queries over a 1M-record corpus."

---

## Part 2: Vertical Slicing

The single most important refinement habit is **slicing vertically, not horizontally**.

### Horizontal slicing (anti-pattern)

A horizontal slice cuts by layer:

```
Story: "Implement user dashboard"
  Slice 1: DB schema for dashboard
  Slice 2: API endpoints for dashboard data
  Slice 3: Frontend dashboard UI
  Slice 4: Caching layer
```

**Failures:**
- Slice 1 has no user value (no one benefits from a DB schema alone)
- Slices 2-4 depend on Slice 1 (violates Independent)
- The team cannot demo until Slice 3 is done
- If priorities shift after Slice 1, nothing has shipped

### Vertical slicing (correct pattern)

A vertical slice cuts by user outcome and goes through every layer:

```
Story: "Implement user dashboard"
  Slice 1: User can see their account name and current plan
  Slice 2: User can see their last 5 activity events
  Slice 3: User can see their usage vs. plan limit
  Slice 4: User can change their plan from the dashboard
```

**Benefits:**
- Each slice is independently demoable (Valuable + Independent)
- Each slice fits in a few days (Small)
- The team ships Slice 1 to get feedback before building Slice 4
- Priorities can shift between slices without waste

---

## Part 3: The 9 Lawrence Splitting Patterns

Richard Lawrence's flowchart (Agile for All) enumerates 9 reliable splits, applied in this priority order:

### 1. Workflow steps

The story spans a multi-step user process. Split by step.

**Example:** "Checkout" -> "Add item to cart" / "Enter payment" / "Confirm order" / "Send receipt"

### 2. Business rule variations

The story handles many business rules. Split by rule.

**Example:** "Apply discount" -> "Loyalty tier discount" / "Promo code discount" / "Volume pricing discount"

### 3. Happy path / unhappy paths

Error handling adds complexity. Ship the happy path first.

**Example:** "Submit application" -> "Submit valid application" / "Handle validation errors" / "Handle backend failures"

### 4. Input options / platforms

Multiple inputs or platforms. Split by channel.

**Example:** "Search products" -> "Search via keyword" / "Search via category filter" / "Search via voice"

### 5. Data types or parameters

Multiple data variations. Split by data type.

**Example:** "Export report" -> "Export as CSV" / "Export as PDF" / "Export as XLSX"

### 6. Operations (CRUD)

The story covers multiple operations on one resource. Split by operation.

**Example:** "Manage saved searches" -> "Create saved search" / "Edit saved search" / "Delete saved search"

### 7. Test scenarios / cases

The test plan reveals natural splits. Split by scenario.

**Example:** "Login" -> "Login with email + password" / "Login with Google SSO" / "Login with MFA enabled"

### 8. Defer performance / quality

The simple version works; performance optimization can ship later.

**Example:** "Search 10M records" -> "Search with current performance" (v1) / "Optimize search to <200ms p95" (v2)

### 9. Spike (last resort)

The team cannot estimate. Time-box an investigation, then re-split.

**Example:** "Integrate with X system" -> "Spike: prototype the X API integration (2 days)" -> [re-refine]

---

## Part 4: SPIDR (Mike Cohn's alternative)

Mike Cohn's mnemonic covers similar ground with five buckets:

| Letter | Bucket | Lawrence equivalent |
|--------|--------|---------------------|
| **S** | Spikes | Pattern 9 |
| **P** | Paths | Patterns 1, 3 |
| **I** | Interfaces | Pattern 4 |
| **D** | Data | Patterns 5 |
| **R** | Rules | Pattern 2 |

Use whichever taxonomy your team finds memorable. Both lead to the same kinds of vertical slices.

---

## Part 5: Worked split examples

### Example A: SSO login

**Original story (too large):**
> "Add Enterprise SSO so customers can log in with their company identity provider."

Estimated at 15 days. Fails INVEST-S.

**Split by Test Scenarios (Pattern 7):**

1. **SSO login with Okta** (4 days) -- SAML 2.0 flow, IdP-initiated only
2. **SSO login with Azure AD** (2 days) -- reuses SAML implementation
3. **SP-initiated SSO** (3 days) -- support login from our domain
4. **Just-in-time user provisioning** (3 days) -- auto-create users on first SSO
5. **SSO admin UI** (3 days) -- self-serve setup for IT admins

Each slice is independently shippable and demoable. Slice 1 alone gives Enterprise customers a usable login.

### Example B: Notifications

**Original story (too large):**
> "Implement notification system so users receive alerts about important events."

Estimated at 20+ days. Fails INVEST-S, INVEST-E (too vague to estimate), and possibly INVEST-V (which events?).

**Split by Input Options + Business Rules (Patterns 4 + 2):**

1. **In-app notification banner for billing failures** (3 days)
2. **In-app notification for new comments on my work** (2 days)
3. **Email notification for billing failures** (2 days)
4. **Email digest of daily activity** (4 days)
5. **Notification preferences UI** (3 days)
6. **Push notification (mobile)** (5 days) -- explicitly deferred

The team ships 1-2 first to start learning whether users engage. Push (slice 6) is deferred until in-app proves valuable.

### Example C: Dashboard

**Original story (horizontal anti-pattern):**

> "Build user dashboard."
> Sub-tasks: DB schema, API, UI, caching.

**Split vertically by data type (Pattern 5):**

1. **Dashboard shows account name and plan** (2 days)
2. **Dashboard shows last 5 activities** (3 days)
3. **Dashboard shows usage vs. plan limit** (3 days)
4. **Dashboard supports plan upgrade** (4 days)

Each slice is end-to-end. Each is demoable. Each delivers value alone.

---

## Part 6: Refinement session structure

### Standard 60-minute weekly refinement

| Time | Activity | Purpose |
|------|----------|---------|
| 0:00-0:05 | Review last week's refined stories | Continuity, catch any rework |
| 0:05-0:15 | Quick INVEST grade on 5-10 candidates | Triage; produce ready/refine/discovery buckets |
| 0:15-0:45 | Deep-refine 2-4 stories scoring 3-4 | Split, clarify, write acceptance criteria |
| 0:45-0:55 | Estimate refined stories | Planning Poker, t-shirt, or affinity |
| 0:55-1:00 | Confirm DoR pass and queue for sprint | Final gate |

### Anti-pattern: refining everything

If the team tries to deeply refine every story, the session runs 90+ minutes and produces few sprint-ready items. The fix: triage fast, deep-refine slow. Most stories should be either "promote" or "send back to discovery" in 60 seconds.

---

## Part 7: Tracer-Bullet Slicing

Vertical slicing says each slice should cross every layer. Tracer-bullet slicing adds an
order and a shape to the set of slices: the **first** slice is the thinnest possible path
through every layer, built to prove the path works, and every later slice widens that path.
It is the right splitting technique when a story or epic is new territory — a new
integration, a new data flow, a feature nobody on the team has built before — because the
riskiest unknown is usually whether the layers connect at all.

### How to cut a tracer bullet

1. **Write the end-to-end behaviour in one sentence a user could check.** "A user saves the current search and sees it in the Saved list."
2. **Strip everything optional.** One input type, the happy path, defaults instead of settings, no edge cases, minimal UI. Keep every layer: storage, service, interface and a test.
3. **Check it is demoable.** If the slice cannot be shown working on its own, it is a layer, not a tracer bullet.
4. **List the widening slices.** Each adds one dimension back: error handling, a second input type, permissions, performance. Most can then be split further with the Lawrence patterns (Part 3).
5. **Give each slice its blocking links.** A slice is blocked only by slices it cannot be built or verified without. Everything else can run in parallel once the tracer bullet lands.

### Example: saved searches

| # | Slice | Blocked by |
|---|-------|-----------|
| 1 | Save the current search under a name; it appears in the Saved list (happy path, all layers) | — |
| 2 | Run a saved search from the list | 1 |
| 3 | Rename or delete a saved search | 1 |
| 4 | Share a saved search with a teammate | 1 |
| 5 | Email me when a saved search has new results | 2 |

After slice 1, slices 2, 3 and 4 are all ready at once. A horizontal plan (tables, then API,
then UI, then tests) would have produced nothing usable until its last ticket.

### How it relates to INVEST

- **Independent:** the tracer bullet is the one deliberate dependency; after it lands, the widening slices are mostly independent of each other.
- **Valuable:** even the thinnest slice does something a user can see.
- **Small:** the first slice is small by construction; if it is not, more has to be stripped.
- **Testable:** the one-sentence behaviour is the first acceptance criterion.

### When not to use it

- **Well-trodden work.** When the team has built this shape many times, the path is not in doubt; split by the Lawrence patterns directly.
- **Wide mechanical changes** (renaming a field used everywhere). These cannot land green as a thin slice. Split them as expand (add the new form beside the old), migrate (move callers over in batches), contract (remove the old form), each its own ticket.
- **Pure research.** If the unknown is a question rather than a path, use a time-boxed spike (pattern 9) and slice after it answers.

### Red flags in a tracer-bullet split

- The first slice has a long acceptance list. It is not thin; strip it.
- A slice touches one layer only and is not an expand/migrate/contract step. It is horizontal.
- Every slice is blocked by the one before. The links are preferences, not gates; re-check which slices really need which.

---

## Further reading

- Bill Wake, "INVEST in Good Stories, and SMART Tasks" (XP Magazine 2003)
- Richard Lawrence, "Patterns for Splitting User Stories" (Agile for All)
- Mike Cohn, "User Stories Applied" (Addison-Wesley)
- Jeff Patton, "User Story Mapping" (O'Reilly)

---

**Last Updated:** 2026-05-21
