# Map Health and Failure Modes

A decision map decays like any other plan. This reference gives the signals that a map
is healthy or stuck, the validator findings that map to each failure mode, and the
repair for each.

## 1. Health signals to track each session

| Signal | Healthy | Worry | How to read it |
|--------|---------|-------|----------------|
| Frontier width | 2-5 tickets | 0, or more than 10 | Zero means stalled; too many means links are missing or the map is a backlog in disguise |
| Decision latency (open to resolved) | Days | Weeks | Long latency points at the wrong owner or a missing prerequisite |
| Overdue decide-by dates | 0-1 | 3+ | A cluster means owners are overloaded or dates were invented |
| Fog list size | Shrinking over time | Growing every session | Growing fog means the destination is too broad |
| Decisions resolved per week | Steady | Zero for two weeks | The map has stopped being worked; ask why before adding more tickets |
| Resolved but unconverted decisions | Few, recent | Many, old | Planning is outrunning building, or decisions are vaguer than they look |
| Reopened decisions | Rare | Frequent | Decisions are being made before their prerequisites |

Run `decision_map_validator.py --today <date>` at the start of each session and paste
the counts into the map's health section. The trend matters more than any single
reading.

## 2. Validator findings and what they mean

| Finding | Severity | What it usually means | Repair |
|---------|----------|-----------------------|--------|
| no destination | error | The effort was charted before anyone agreed on the end state | Stop; resolve the destination first |
| blocking cycle | error | Two halves of one decision, a shared missing fact, or a wrong link | Merge, extract a research ticket, or drop the weaker edge |
| unknown blocker id | error | A ticket was deleted or mistyped; the dependent looks blocked forever | Fix the id or remove the link |
| decision has no owner | error | Nobody can make the call | Name the person with authority, not the researcher |
| fewer than 2 options | error | A discussion with one option is a decree, not a decision | Add the real alternatives (including "do nothing") or mark it resolved |
| resolved without resolution | error | The answer lived in a meeting and was not written down | Write chosen / why / rejected / consequences before anything else |
| built on / blocked by unresolved decision | error | Someone started building on a guess | Pause the implementation ticket or resolve the decision now |
| in progress while blocker open | error | Work started out of order | Either the link is wrong or the work is premature |
| orphan implementation ticket | error | Work that traces to no decision on the map | Link it, or move it off the map if it serves another effort |
| question not phrased as a question | warn | The ticket names a topic, not a decision | Rewrite as one sentence ending in "?" |
| isolated decision | warn | No links in or out; may not serve the destination | Confirm it belongs, link it, or rule it out of scope |
| resolved, not converted | warn | Planning ahead of building | Convert, or mark `no_build: true` |
| decide-by passed | warn | The decision is late | Escalate to the owner with what is slipping |
| claimed without claimant | warn | A lock nobody holds | Set `claimed_by` or return the ticket to open |
| frontier empty, work remains | warn | Everything open is blocked or the map is stuck | Look for cycles, unknown ids, or a missing enabling task |

## 3. Failure modes in practice

### The map that became a backlog

Symptoms: forty tickets, most of them implementation work, frontier of fifteen, no
fog. Cause: the planner charted every task they could imagine instead of only the
questions blocking the route. Repair: close or move every ticket that does not resolve
a decision or put a resolved decision into effect. A map holds questions and the
slices that follow from answered ones, not every chore.

### Fog that never clears

Symptoms: the fog list grows every session and nothing graduates. Cause: the
destination is too broad, so every resolution reveals more in-scope territory.
Repair: redraw the destination tighter and move the excess to out of scope with a
reason. If stakeholders resist, that disagreement is itself the first decision.

### The decision made in the corridor

Symptoms: a ticket closed as resolved with no resolution text, or a resolution like
"agreed in sync". Cause: the decision happened in conversation and nobody wrote it
down. Repair: the validator blocks this as an error. Write the chosen option, the
reason, and the rejected options before taking the next ticket. A decision nobody can
read later will be reopened.

### Building on hope

Symptoms: implementation tickets in progress that derive from open decisions.
Cause: pressure to show progress. Repair: either the decision is actually made (record
it) or the code is a prototype (move it to a prototype decision ticket and treat the
code as disposable). Do not let it become the default answer by inertia.

### The ownerless frontier

Symptoms: frontier tickets sit for weeks; nobody claims them. Cause: owners are
missing, or are people outside the team who do not know they own anything. Repair:
name owners at charting time and send each owner their tickets with the decide-by date
and the consequence of delay. A short structured questionnaire to an external owner
often resolves a ticket faster than a meeting.

### Too many links

Symptoms: frontier of zero or one even though most tickets are open; long chains in the
dependency order. Cause: every vague relationship drawn as a blocking link. Repair:
apply the least-likely-answer test to each link and remove the ones that do not change
options.

### The cycle hidden by a long chain

Symptoms: the validator reports a cycle of four or more tickets. Cause: each link
looked reasonable on its own. Repair: find the edge where the dependency is weakest
(often a "nice to know" research result) and cut it, or extract the shared missing fact
into its own research ticket that every member of the cycle depends on.

### Horizontal tickets after a good map

Symptoms: the decisions were made well, then the implementation tickets came out as
"database schema", "API endpoints", "UI screens". Cause: the conversion step was rushed
or done by habit. Repair: run `tracer_slice_checker.py`; every single-layer ticket is
an error. Re-slice around behaviours using the patterns in
`decisions-to-tracer-bullets.md`.

## 4. Cadence

| Effort size | Session cadence | Map review |
|-------------|-----------------|-----------|
| 2-4 weeks | One decision per day | End of each week |
| 1-3 months | Two to three decisions per week | Every two weeks with owners |
| Quarter+ | Weekly decision session per workstream | Monthly with sponsor; redraw destination if fog grows |

A map review is not a status meeting. Its agenda is: frontier, overdue decisions,
fog that is ready to graduate, anything that should move out of scope, and whether the
destination still holds.

## 5. When to abandon a map

Abandon or restart when:

- the destination has changed materially (start a new map, link the old one);
- two consecutive reviews show no resolved decisions and no clear reason;
- the remaining questions are all answerable in one meeting (hold the meeting, close
  the map, and convert what is left directly into implementation tickets).

Archive the abandoned map with a one-paragraph note on why. The decisions it did reach
are still valid input to whatever replaces it.
