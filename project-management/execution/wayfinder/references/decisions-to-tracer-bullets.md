# From Resolved Decisions to Tracer-Bullet Tickets

A decision map produces answers. Answers do not ship. This reference covers the
conversion step: turning each resolved decision into thin, end-to-end implementation
tickets that can be built, demoed and verified one at a time.

## 1. What a tracer bullet is

A tracer-bullet ticket delivers a narrow path through **every layer the behaviour
needs**, all the way to something a person can observe. It is thin in breadth and
complete in depth.

| | Tracer bullet (vertical) | Layer ticket (horizontal) |
|--|--------------------------|---------------------------|
| Shape | One behaviour, every layer | One layer, many behaviours |
| Done means | Someone can demo it | Code exists in one layer |
| Integration risk | Paid on day one | Deferred to the end |
| Feedback | Immediate, from real use | None until all layers meet |
| Can be reprioritised | Yes, each slice stands alone | No, layers depend on each other |

The reason to slice vertically is not tidiness. It is that integration is where the
surprises live, and a vertical slice forces integration on the first ticket instead
of the last. When the first slice works, the architecture has been proven end to end
at small scale.

## 2. When a decision is ready to convert

Convert a resolved decision when:

- the resolution names a choice concrete enough to build against;
- every other decision the build depends on is also resolved;
- the result would be demoable on its own.

Some resolutions convert immediately ("meter on seat-hours" plus "provider rates
usage" together give the first slice). Others never produce code ("we will not
support offline edits on shared devices") and are marked `no_build: true`. Others
must wait for a sibling decision; leave them resolved and unconverted, and the
validator will keep a gentle warning on them until you act.

Never convert a decision that is still open. An implementation ticket that depends on
an open decision is a bet that the decision goes a particular way. The validator
treats this as an error because it is the most common source of thrown-away work.

## 3. Writing the slice

For each slice, write:

1. **A title that names a behaviour.** "One workspace's seat-hours appear at the
   provider", not "Build metering API".
2. **Derived from.** The decision ids it puts into effect. This is the traceability
   that lets someone ask "why does this exist?" and get an answer.
3. **Layers crossed.** List them explicitly. A list with one entry is the signal that
   the slice is horizontal.
4. **Demo.** What someone will run or look at. If you cannot write it, the slice does
   not end anywhere observable.
5. **Acceptance criteria.** Observable statements with numbers or concrete examples.
   Cover the happy path, one failure path, and any idempotency or retry behaviour.
6. **Blocked by.** Only the tickets that genuinely gate it.
7. **Estimate.** Three days or fewer. Larger slices hide a second behaviour.
8. **Out of scope for this slice.** The adjacent work that will be tempting mid-build.

### Testable criteria

| Untestable | Testable |
|-----------|----------|
| "Metering works correctly" | "An hour with 2 active seats reports exactly 2 seat-hours" |
| "Handles errors properly" | "A failed provider call is retried 3 times then logged with workspace_id" |
| "Fast enough" | "Hourly aggregation for 10k workspaces completes in under 5 minutes" |
| "Report looks good" | "Rows with variance above 0.5% are highlighted" |

The slice checker flags vague wording (works, properly, correctly, as expected, etc.)
as warnings. They are warnings rather than errors because sometimes the word is
used precisely; read each one.

### Describe behaviour, not files

Implementation tickets often sit for days or weeks before someone picks them up. File
paths, line numbers and function names drift in that time. Describe interfaces,
contracts and observable behaviour; let the implementer find the code. The one
exception is a schema or type shape that a prototype already settled, which can be
quoted because it *is* the decision.

## 4. Choosing the first slice

The first slice should be the one that proves the riskiest integration with the least
scope. Ask:

- Which layer has never talked to which other layer before?
- Which external system have we not yet called in anger?
- Which assumption, if wrong, would invalidate the most later slices?

The first slice through the billing example touched event capture, the aggregation
job, the provider client and an integration test, for one workspace and one hour.
Nothing about invoices, dunning or reporting: those are later slices that reuse the
path the first one proved.

## 5. Slicing patterns

When a slice is too big, cut along one of these lines:

| Cut by | Example |
|--------|---------|
| One entity first | One workspace, then all workspaces |
| One happy path first | Successful collection, then failed collection |
| Manual before automated | Finance runs the report by hand, then it is scheduled |
| Read before write | Show usage, then let users change their plan |
| Simple rule first | Flat seat-hour price, then tiers |
| One channel first | Email notification, then in-app |

Each cut must still cross every layer. "One workspace" is a valid cut; "database
only" is not.

## 6. The exception: wide mechanical refactors

Some changes cannot be sliced vertically because they are one mechanical edit that
fans out across hundreds of call sites: renaming a widely used field, changing the
type of a shared identifier, moving a module. Making the edit in one go breaks every
caller at once, and no vertical slice can land with the build green.

Sequence these as **expand, migrate, contract**:

1. **Expand.** Add the new form beside the old. Both work. Nothing breaks. One ticket.
2. **Migrate.** Move callers to the new form in batches sized so each batch lands with
   the suite passing (per package, per directory, per service). One ticket per batch,
   each blocked by the expand ticket. Batches can run in parallel.
3. **Contract.** Remove the old form once nothing uses it. One ticket, blocked by
   every migrate batch.

The slice checker enforces exactly this: one expand per refactor group, every migrate
blocked by the expand, the contract blocked by every migrate. A contract that can run
before a migrate batch would delete the old form under live callers.

If even individual migrate batches cannot stay green alone (because callers are
tightly coupled), keep the same sequence on a shared integration branch and add a
final integrate-and-verify ticket blocked by every batch. Only that final ticket
promises a green build.

Place the refactor before the slices that need the new form: in the billing sample,
the first tracer bullet is blocked by the contract ticket so that new metering code is
written only against `workspace_id`.

## 7. Ordering the implementation tickets

Run `decision_map_validator.py`. Its dependency order covers decisions and
implementation together, using Kahn's algorithm with ties broken by id so the order is
stable from run to run. The frontier shows what can be picked up now.

For implementation work, prefer:

1. Refactor expand tickets (they unblock everything that follows).
2. The first tracer bullet (it proves the path).
3. Slices that reuse the proven path, in order of risk retired per day of effort.
4. Contract tickets as soon as their migrate batches are done, so the old form does
   not linger.

## 8. Review before handing out

Before tickets go to a team or a coding agent, check:

- [ ] Every implementation ticket has `derived_from` pointing at resolved decisions.
- [ ] No ticket is blocked by, or built on, an open decision.
- [ ] Every slice lists two or more layers, a demo and testable criteria.
- [ ] No slice is over three days.
- [ ] Every refactor group has one expand, at least one migrate, one contract, with the
      blocking links in the right direction.
- [ ] Both tools exit 0.

Ask the people who will build the slices whether the granularity feels right and
whether each blocking edge is real. Adjust and re-run the tools. A breakdown nobody
on the building side has read is a plan only on paper.
