# Conversation Capture and the Implementation Loop

Two transitions sit at either end of a spec's life and are where most specs lose fidelity:
turning a discussion into a written spec, and turning the written spec into code. This
reference covers both. The middle — linting, IDs, coverage — is in
`spec-writing-guide.md` and `traceability-model.md`.

---

## Part 1 — From conversation to spec

Many features are not specified at a desk. They are settled in a chat thread, a design
call, a long back-and-forth with a coding agent, or a stakeholder meeting. By the time
someone says "let's write this up", the decisions exist, scattered across an hour of
discussion and mixed with ideas that were floated and dropped.

### What to extract

Read the whole conversation once before writing anything, and sort every substantive
statement into one of five bins.

| Bin | Test | Goes to |
|-----|------|---------|
| **Decision** | Someone proposed it and nobody objected, or it was explicitly agreed | A normative requirement (must/should/may) |
| **Constraint** | A limit stated as fact: a deadline, a platform, a budget, a regulation | Constraints section, or a requirement if it is testable |
| **Example** | A concrete scenario someone walked through ("if I export 10k rows…") | Acceptance criteria under the requirement it illustrates |
| **Deferred** | Raised and explicitly postponed ("not in v1", "later") | Out-of-scope list, word for word |
| **Open** | Raised and not settled, or settled differently by different people | Open questions, each with an owner |

Anything that fits no bin is discussion, not content. Leave it out.

### Rules for the draft

1. **Write decisions as one obligation per statement.** A conversation often agrees two things in one breath ("it should retry and log the failure"). That is two requirements.
2. **Keep the speaker's numbers.** If someone said "under two seconds", the requirement says 2 seconds, not "fast". If nobody gave a number for a quality the feature depends on, that is an open question, not an adjective.
3. **Do not resolve open questions silently.** A placeholder in a requirement (`TBD`) fails the linter by design. Put the question in the Open Questions section with the person who can answer it, and leave the requirement out until it is answered.
4. **Turn examples into acceptance criteria verbatim where possible.** A scenario the user described is the best acceptance test available, because it is the one they will check first.
5. **Quote deferrals exactly.** "Not in v1" and "never" are different scopes. The out-of-scope list is what stops the next session from building the deferred feature.
6. **Mark where a statement came from** when the conversation is long or has several participants: a timestamp, message link or speaker initials next to each requirement. It makes the read-back fast.

### Ask only about real gaps

The conversation already answered most questions. Re-asking them wastes the user's time
and signals that nobody listened. Ask only when an answer would change a requirement:
an obligation with no number, two participants who said different things, or a constraint
that conflicts with a decision. Batch those questions; do not drip them one at a time.

### Read it back

Before the spec is linted or shared, show the participants the list of requirements and
the out-of-scope list and ask one question: "Is anything here something we did not
decide?" Additions are cheap at this point and expensive after implementation starts.
Then run `spec_lint.py`; a captured spec usually fails first on unquantified adjectives,
because conversations are full of them.

### Capturing from an agent session

When the conversation is with a coding agent, the same bins apply, with two additions:

- **Decisions the agent made unilaterally are not decisions.** If the agent chose a library or a data shape and the user never confirmed it, list it as Open, not as a requirement.
- **Prefer the user's words over the agent's summary.** Agent summaries smooth away disagreement. Go back to what the user typed.

---

## Part 2 — Implementing from the spec

Once the spec is approved and broken into tickets with blocking links, the implementation
loop turns tickets into commits without letting the spec and the code drift apart.

### The frontier

Tickets with blocking links form a graph. At any moment the **frontier** is the set of
tickets whose blockers are all done. Work only on frontier tickets. When a ticket closes,
recompute the frontier; it may open one ticket or several. Several open tickets can be
worked in parallel by separate people or agents, each on its own branch or worktree.

### One ticket, one loop

For each frontier ticket:

1. **Load only what the ticket needs.** The ticket, the requirement IDs it covers, and the spec sections those IDs live in. A fresh session or sub-agent per ticket keeps earlier tickets' debugging out of the way.
2. **Write the failing test first.** Name or annotate it with the requirement ID (`# REQ-EXPORT-03`). Run it and see it fail for the expected reason. A test that passes before the code exists is testing nothing.
3. **Write the minimum code that makes it pass.** Annotate the implementation with the same ID.
4. **Run the gates.** The full test suite, then `spec_parse.py` against the baseline (no drift) and `trace_coverage.py` (the ticket's IDs now `covered`, no orphans).
5. **Refactor with the tests green.**
6. **Review the ticket's diff on two axes.** Does it follow the repo's standards, and does it do what the requirement says — no less, no more? Review with fresh eyes, not in the same breath as writing.
7. **Commit once per ticket.** The message names the ticket and the requirement IDs: `feat(export): stream rows to disk (TICKET-14, REQ-EXPORT-03)`. One commit per ticket makes each requirement's implementation easy to find, review and revert.
8. **Close the ticket and recompute the frontier.**

### When the spec turns out to be wrong

Implementation regularly discovers that a requirement is ambiguous, contradicts another,
or cannot be built as written. Stop on that ticket. Change the spec first — in the same
branch, so the spec change and the code change merge together — re-run the linter, update
the baseline, and only then continue. Coding around a wrong spec produces exactly the
drift the workflow exists to prevent.

### Finishing

The spec is implemented when every ticket is closed, `trace_coverage.py` reports every
mandatory requirement `covered` at the agreed floor, and a final review of the whole
branch against the spec finds no missing requirement and no unrequested behaviour. Close
the tickets the way the tracker expects (usually through the PR), not by hand.

### Common failures in the loop

| Failure | Symptom | Fix |
|---------|---------|-----|
| Batching tickets into one commit | Reverting one requirement reverts three | One commit per ticket, always |
| Writing tests after the code | Tests mirror the implementation, including its bugs | Red test first, every time |
| Working ahead of the frontier | Half-built ticket blocked on an unfinished one | Only pick tickets whose blockers are done |
| Silent spec fixes | Code and spec disagree after merge | Spec change lands in the same branch, before the code |
| Carrying context across tickets | Agent applies a workaround from ticket 3 to ticket 7 | Fresh session per ticket; point at commits instead of retelling |
