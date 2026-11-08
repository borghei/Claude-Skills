# Tracer-Bullet Slicing

A tracer bullet is the thinnest piece of a feature that runs end to end through every layer
it needs — storage, service, interface, tests — and can be demonstrated working. The first
one proves the path exists; each later one widens it. A spec sliced this way produces
tickets that each land something real, instead of a stack of layer tickets that only work
once the last one merges.

This reference covers how to slice, how to declare blocking links, the exceptions where
vertical slicing does not fit, and the ticket format `ticket_graph_validator.py` checks.

## The slicing rules

1. **Every slice crosses every layer its behaviour touches.** "Store saved searches" is a layer. "Save the current search and see it in the Saved list" is a slice: it needs a table, an endpoint, a button and a test, and when it merges a person can use it.
2. **Every slice is demoable or verifiable on its own.** If the only way to check the ticket is to wait for another ticket, it is not a slice.
3. **The first slice is the thinnest possible path.** Hard-code what you can, skip options, take the happy path. Its job is to force every layer to exist and talk to the next one. Widen later.
4. **Each slice fits in one working session.** For a coding agent that means one fresh context window: the ticket, the relevant spec lines and the files it touches, with room to debug. For a person, a day or two. Anything bigger hides a second slice.
5. **Prefactoring comes first.** When the existing code makes the change awkward, a small refactor ticket with no behaviour change goes at the front of the graph, so the slices after it are easy. Make the change easy, then make the change.

## Finding the slices

Start from the spec's user-visible behaviours, not from the architecture.

1. List each behaviour as one sentence a user could check: "I can rename a saved search."
2. Order them by dependency in the product, not the code: you cannot run a saved search before you can save one.
3. Take the first behaviour and strip it to the narrowest version that still runs through all layers. That is ticket one (after any prefactor).
4. For each remaining behaviour, ask what it needs that does not exist yet. That is its blocking link.
5. Split any slice whose estimate exceeds the team's limit (default three days) using the usual levers: happy path before error paths, one input type before many, one role before all roles, manual before automatic.

## Blocking links

Each ticket declares the tickets that must finish before it can start. Only real gates
count: a ticket blocks another when the second cannot be built or verified without the
first's code. "It would be nicer to do it after" is ordering preference, not a block.

- **Prefer few links.** Every unnecessary link narrows the frontier and serialises work that could run in parallel.
- **No cycles.** If A needs B and B needs A, the slice boundaries are wrong — usually a shared piece that should be its own ticket at the front.
- **Watch the bottleneck.** A ticket that blocks half the graph is the critical item. Land it first, keep it thin, or split it.
- **Use the tracker's native link** where it has one (Jira "is blocked by", Linear "blocked by", GitHub sub-issues and dependencies). Where it does not, put "Blocked by: #12, #14" in the ticket body. For local planning, one markdown file per ticket, numbered in dependency order, with the blockers listed at the top.

The **frontier** is every ticket whose blockers are all done. Work is always picked from the
frontier; when a ticket closes, the frontier is recomputed. The validator prints the graph
as waves — wave 1 is the starting frontier, and the number of waves is the critical path.

## Exceptions to vertical slicing

Some work cannot land green as a thin vertical slice. Name it as an exception so it does not
pass for a slice.

| Kind | When | Shape |
|------|------|-------|
| `prefactor` | The existing code makes the slices awkward | One no-behaviour-change ticket at the front; existing tests prove it |
| `expand` / `migrate` / `contract` | A wide mechanical change (renaming a column, retyping a shared symbol) breaks too many call sites at once | Expand: add the new form beside the old. Migrate: move callers in batches, each its own ticket blocked by the expand. Contract: remove the old form, blocked by every migrate batch |
| `spike` | An unknown makes the slice impossible to estimate | Time-boxed question with a written answer as its deliverable; the real slice is blocked by it |
| `integrate` | Migrate batches cannot stay green alone | Batches share an integration branch; a final integrate-and-verify ticket blocked by all of them is where green is promised |

The validator skips the horizontal-slice warning for tickets marked with one of these kinds.

## The ticket format

```json
{
  "feature": "Saved searches",
  "layers": ["db", "api", "ui", "tests"],
  "tickets": [
    {
      "id": "T2",
      "kind": "slice",
      "title": "Save the current search under a name and see it in the Saved list",
      "layers": ["db", "api", "ui", "tests"],
      "blocked_by": ["T1"],
      "demoable": true,
      "estimated_days": 2,
      "acceptance": ["Saving 'Open bugs' shows it at the top of the Saved list after reload"]
    }
  ]
}
```

- `layers` at the top lists the layers the feature touches; per ticket it lists the layers that ticket touches.
- `kind` defaults to `slice`. Use an exception kind only for the cases above.
- `acceptance` is required. A ticket with no acceptance criteria cannot be closed honestly.

Ticket body, when published to a tracker:

- **What it delivers:** the behaviour, from the user's side, not a list of layer changes.
- **Blocked by:** ticket references, or "nothing — can start now".
- **Acceptance criteria:** checkable statements.
- **Spec lines:** the requirement IDs or quoted spec lines this ticket implements.

## Review the breakdown before publishing

Show the proposed list — title, blocked by, what it delivers — and ask three things before
creating anything in the tracker:

- Is the granularity right, or are some tickets too thick or too thin?
- Does each blocking link reflect a real gate?
- Should any tickets merge or split?

Iterate until the breakdown is approved, then publish in dependency order so later tickets
can reference earlier ones by their real identifiers. Do not close or edit the parent issue
or epic while doing so.

## Worked example: horizontal versus tracer-bullet

**Horizontal plan (avoid):**
1. Create saved-search tables.
2. Build saved-search API.
3. Build Saved list UI.
4. Write tests.

Nothing is usable until ticket 4, integration bugs appear at the end, and tickets 2 and 3
cannot be verified on their own.

**Tracer-bullet plan:**
1. Prefactor: extract the query builder (no behaviour change).
2. Save the current search and see it in the Saved list (all layers, happy path). Blocked by 1.
3. Run a saved search from the list. Blocked by 2.
4. Rename and delete a saved search. Blocked by 2.
5. Share a saved search with a teammate. Blocked by 2.
6. Email on new results. Blocked by 3.

After ticket 2 merges, a user can save a search. Tickets 3, 4 and 5 can then run in parallel.
`assets/sample_tracer_tickets.json` is this plan with two deliberate defects added — a
horizontal "create all tables" ticket and a slice without acceptance criteria — so the
validator's warnings and errors are visible.
