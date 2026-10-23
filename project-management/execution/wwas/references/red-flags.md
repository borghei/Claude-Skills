# Red Flags: WWAS (Why-What-Acceptance)

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every WWAS-formatted backlog item before it enters refinement. Each red flag has bad and good quoted examples.

---

## Red Flag 1: WHY = Feature Wishlist

**Symptom.** The "WHY" section reads "because users have been asking for it" or "because Sales requested it".
**Why it's bad.** A request is not a why. The actual WHY connects the work to a customer outcome or business metric. Without it, the team builds because someone asked, not because it moves the world -- and the team cannot decide between the request and a different request that scores higher.
**Bad example:**
> "WHY: Several enterprise prospects asked for bulk-edit during sales demos."
**Good example:**
> "WHY: Enterprise admins spend ~12 min / day editing candidate records one at a time (n=8 customer observations, Q1 2026). Bulk-edit reduces this to <2 min, addressing the #2 churn-survey complaint ('repetitive work'). Expected metric movement: drop NPS detractor share from 18% to 12% in enterprise segment."
**How to catch it.** WHY contains 'asked for it', 'requested by', 'wants' -- without a customer outcome -- = rewrite.

---

## Red Flag 2: No Acceptance Criteria

**Symptom.** WWAS items have a WHY and a WHAT, but the Acceptance section is empty or says 'TBD'.
**Why it's bad.** Without acceptance, 'done' is undefined. The team will declare victory at different points; QA will retest; reviewers will keep adding scope. The whole purpose of WWAS is the testable spec.
**Bad example:**
> "WHY: ... (reasonable)
> WHAT: Add a bulk-edit feature for candidates.
> ACCEPTANCE: TBD."
**Good example:**
> "ACCEPTANCE (Given / When / Then):
> 1. Given a recruiter has 5+ candidates selected, when she clicks Bulk-Edit, then a dialog appears showing the 3 editable fields (status, tag, assignee).
> 2. Given the dialog is open, when she sets a status and clicks Apply, then the status updates for all selected candidates within 3 seconds, and an audit log entry is created per candidate.
> 3. Given any of the candidates fail validation, when the operation runs, then a partial-success message lists the failures and no successful updates are rolled back.
> 4. Given the recruiter lacks edit rights on some selected candidates, when she opens Bulk-Edit, then those candidates are listed as skipped before she applies anything.
> 5. Performance: bulk-edit of up to 200 candidates completes in <5 sec p95."
**How to catch it.** Fewer than 4 observable acceptance criteria = not ready for sprint. `invest_gate_checker.py` fails the Estimable gate below 4.

---

## Red Flag 3: WHAT That Specifies Implementation

**Symptom.** "WHAT: Add a React modal component that calls /v2/candidates/bulk POST endpoint."
**Why it's bad.** WHAT is the *user-visible behavior*, not the implementation. Specifying tech choices locks engineering into a solution before design, and conflates the problem with one solution. It also makes the item less reusable as a spec.
**Bad example:**
> "WHAT: A React component with a Material-UI modal that wraps a multi-select state. Calls /v2/candidates/bulk POST endpoint with the selected IDs."
**Good example:**
> "WHAT: When a recruiter selects 2+ candidates, she can apply one of three changes (status, tag, assignee) to all of them at once, with the same audit, undo, and validation behavior as single-record edits."
**How to catch it.** WHAT mentions specific component libraries, frameworks, endpoints, or database tables = rewrite.

---

## Red Flag 4: WHY That Stops at the Output

**Symptom.** "WHY: To launch bulk-edit." -- circular reasoning.
**Why it's bad.** The WHY must terminate in a customer outcome or business metric, not in the feature itself. Circular WHY signals the team has skipped the discovery step and is justifying the work by its own existence.
**Bad example:**
> "WHY: Because we need to ship bulk-edit this quarter."
**Good example:**
> "WHY: <customer outcome>. Bulk-edit is one bet on that outcome; alternatives include (a) auto-status-update via webhook (cheaper), (b) batch import (existing). Bulk-edit chosen because customer interviews showed direct-manipulation preference (n=14, Q1)."
**How to catch it.** WHY mentions the feature itself = rewrite to terminate in outcome.

---

## Red Flag 5: Acceptance Criteria as a Test Script

**Symptom.** Acceptance has 47 bullets covering every button click and pixel offset.
**Why it's bad.** Acceptance is the *what*, not the *how to test*. Over-specification locks design, makes the criteria brittle (every small change requires updating ACs), and crowds out the meaningful behavior.
**Bad example:**
> "47 ACs covering: 'button is blue', 'modal centered', 'X icon top-right', 'tab order is left-to-right'..."
**Good example:**
> "5 ACs covering the meaningful behaviors (validation, partial-success, performance, audit log, undo). Visual / micro-interaction details live in the design spec linked from the ticket, not in ACs."
**How to catch it.** AC count > 8 = over-specified; consolidate.

---

## Red Flag 6: WHY Without a Hypothesis or Confidence

**Symptom.** WHY is a confident assertion of impact, with no acknowledgment of risk or alternatives.
**Why it's bad.** Every WHY is a *bet*. Acting as if it is a certainty means the team will not measure whether the bet paid off, and will not de-prioritize when evidence disconfirms.
**Bad example:**
> "WHY: Bulk-edit will increase recruiter productivity by 30%."
**Good example:**
> "WHY: We hypothesize bulk-edit will reduce candidate-edit time by 80% for admins doing >20 edits / week (~15% of recruiters). Confidence: MEDIUM (based on 8 observations). Measure post-launch via the candidate-edit-event log; abandon further investment if reduction is < 50%."
**How to catch it.** WHY without a hypothesis or post-launch measurement = bet is unframed.

---

## Red Flag 7: Items That Are Just Restatements of the Title

**Symptom.** Title: "Bulk-edit candidates". WHY: "Allow bulk-edit of candidates". WHAT: "Bulk-edit candidates". ACCEPTANCE: "Bulk-edit works".
**Why it's bad.** The WWAS structure exists to force clarity. Tautological items defeat the purpose -- they look complete but transmit no information. The team treats them as if they are spec'd, and discovers the missing detail mid-sprint.
**Bad example:**
> "Title: Bulk-edit candidates.
> WHY: To allow bulk-edit.
> WHAT: Bulk-edit feature.
> ACCEPTANCE: The bulk-edit feature works."
**Good example:**
> "[See the well-formed example in Red Flag 1 + 2 above for a non-tautological WWAS.]"
**How to catch it.** WHY + WHAT + ACCEPTANCE collectively repeat the title with no new content = reject in refinement.

---

## Red Flag 8: Single-Persona Assumption

**Symptom.** WHY mentions 'the user' generically; the feature actually affects 3 personas differently.
**Why it's bad.** Generic 'user' hides differential impact. The bulk-edit feature might delight admins, confuse end-users, and break the auditor's workflow. Without persona-specific framing, the team optimizes for whichever persona the PM happened to have in mind.
**Bad example:**
> "WHY: Users want bulk-edit."
**Good example:**
> "WHY: Bulk-edit serves the *admin* persona (saves 10 min / day; primary win). For *standard recruiters* it is invisible (they have < 5 candidates per day; no impact). For *auditors* it requires a per-candidate audit entry (compliance) -- captured in AC4. We are not building bulk-edit for end-candidates."
**How to catch it.** WHY uses 'users' or 'people' = enumerate personas with differential impact.

---

## Red Flag 9: WHAT That Carries an Implicit Migration

**Symptom.** WHAT describes new behavior; ACCEPTANCE describes new behavior; neither addresses existing data or workflows.
**Why it's bad.** Most features have a migration tail (existing records, deprecated flows, in-flight states). Skipping this in WWAS means the team builds the new behavior and discovers the migration burden in sprint 3.
**Bad example:**
> "WHAT: Recruiters can bulk-tag candidates.
> ACCEPTANCE: ... (focused on new tagging flow only.)"
**Good example:**
> "WHAT: Recruiters can bulk-tag candidates.
> ACCEPTANCE includes AC5: 'Given the candidate has legacy single-tag metadata, when bulk-tagging is applied, then the legacy field is preserved and the new tags appear additively in the new structure. No data loss.'
> Migration plan linked: `confluence://MIGRATIONS/bulk-tag-2026q2`."
**How to catch it.** WWAS does not mention existing data / workflows = ask the engineering reviewer to scan for migration before approving.

---

## Red Flag 10: WWAS Items That Reference Other Untracked WWAS Items

**Symptom.** "ACCEPTANCE: works the same way as [some other feature]." But that other feature is also an undocumented WWAS in flight.
**Why it's bad.** Acceptance criteria that reference other in-flight specs cascade ambiguity. When one moves, the other breaks. Dependencies become invisible until a sprint slips.
**Bad example:**
> "ACCEPTANCE: 'Behaves like the single-edit flow', where the single-edit flow is also being redesigned."
**Good example:**
> "ACCEPTANCE: explicit behaviors written out. If a behavior is intentionally shared with another flow, the shared spec is extracted into a separate referenced doc, both items cite the doc, and the doc is versioned. Cross-WWAS dependencies are tracked in `dependency-map`."
**How to catch it.** ACs reference 'same as X' / 'behaves like Y' = inline the behavior or extract a shared spec.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | WHY = wishlist | WHY connects to a customer outcome or metric |
| 2 | No ACs | At least 4 observable acceptance criteria? |
| 3 | WHAT specifies implementation | No component libs / endpoints in WHAT |
| 4 | WHY stops at the output | WHY terminates in outcome, not feature |
| 5 | AC as test script | AC count <= 8 |
| 6 | WHY without hypothesis | Confidence + post-launch measurement noted |
| 7 | Tautological items | WWAS adds info beyond the title |
| 8 | Single-persona assumption | Enumerate personas + differential impact |
| 9 | Implicit migration | Existing data / workflows addressed |
| 10 | Cross-WWAS references | Shared specs extracted + versioned |

## Related Reading

- `SKILL.md` -- the WWAS format
- `references/wwas-template.md` -- the template
- Sibling skill: `execution/backlog-refinement/` -- INVEST + DoR / DoD on each WWAS
- Sibling skill: `execution/story-splitting/` -- splitting an over-large WWAS
- Sibling skill: `execution/job-stories/` -- JTBD alternative format
- Sibling skill: `discovery/identify-assumptions/` -- the hypothesis behind every WHY
- Sibling skill: `execution/create-prd/` -- WWAS items roll up into PRDs
