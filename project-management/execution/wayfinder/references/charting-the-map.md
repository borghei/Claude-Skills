# Charting and Working a Decision Map

This reference covers the first two thirds of wayfinding: turning a large, foggy
piece of work into a map of decision tickets, and then working that map one
decision at a time. Converting resolved decisions into implementation tickets is
covered in `decisions-to-tracer-bullets.md`.

## 1. When a map is the right tool

A decision map earns its overhead when three things are true at once:

1. **The work is bigger than one sitting.** It will span several working sessions,
   several people, or several sprints. If one focused session could plan and finish
   it, a map is ceremony.
2. **The route is not visible.** You can describe where you want to end up, but you
   cannot yet list the build steps because they depend on choices nobody has made.
3. **Those choices block each other.** Some answers cannot be given until other
   answers exist. If every open question is independent, a simple checklist does the
   job.

Signals that you need one:

- Estimates for the work range across an order of magnitude ("two weeks or three
  months, depending").
- Every planning conversation re-opens the same three questions.
- Engineers are writing code that may be thrown away because "we'll decide later".
- A ticket titled "Investigate X" has been open for a month.

Signals that you do not:

- The open questions can all be answered in one meeting.
- The work is already decided and only needs sequencing across teams (a dependency
  map of committed work is the right tool for that).
- The work is a user journey that needs release slicing (a story map fits better).

## 2. Writing the destination

The destination is the single most important line on the map. It fixes scope, so it
decides what counts as fog (in scope, not yet sharp) and what counts as out of scope
(beyond the destination). Write it before any ticket.

A good destination is:

| Property | Test | Example |
|----------|------|---------|
| Observable | Could a stranger check whether it is true? | "Every invoice reconciles to the ledger within 0.5%" |
| End state, not activity | Does it describe a world, not work? | "is billed per seat-hour", not "build metering" |
| Bounded | Does it exclude something tempting? | "new self-serve workspaces" (legacy excluded) |
| One sentence or two | Can it be read at the start of every session? | — |

The destination can also be a decision or a spec rather than a shipped change:
"A signed-off data-retention policy that legal and engineering both accept" is a
valid destination. A map whose destination is a decision ends when that decision is
made and recorded; there are no implementation tickets.

Common destination failures:

- **Activity framing.** "Explore offline mode." There is no point at which exploring
  is done, so the map never closes.
- **Solution baked in.** "Ship the Kafka-based sync pipeline." The choice of Kafka was
  one of the decisions the map should have contained.
- **Unbounded.** "Modernise billing." Everything is in scope, so nothing is out of
  scope, and the fog list grows forever.

When stakeholders disagree on the destination, stop. Do not chart tickets. Resolve
the destination as its own decision first, usually as a short written proposal with
two or three candidate destinations and the trade-offs between them.

## 3. Finding the decisions

Fan out breadth-first across the whole problem before going deep on any thread. The
aim of the first charting session is coverage, not answers. Useful prompts:

- **Unknown facts.** What do we not know that would change what we build? (limits,
  volumes, costs, vendor capabilities, legal constraints)
- **Forks.** Where are there two or more plausible approaches with different costs?
- **Ownership.** Which choices belong to someone outside the team (finance, legal,
  security, a platform team)?
- **Irreversibility.** Which choices are expensive to undo (data model, public API,
  pricing, contracts)? These deserve tickets even when the answer seems obvious.
- **Presentation.** Where will people need to see something before they can choose?
- **Prerequisites.** What access, data or environment must exist before anyone can
  even evaluate the options?

Each answer that survives becomes either a ticket, a fog item, or an out-of-scope
line. Use the sharpness test below to decide which.

## 4. Ticket, fog, or out of scope

| You can... | And it is... | It becomes |
|------------|--------------|------------|
| State the question precisely now | Inside the destination | A decision ticket (even if blocked) |
| Sense the question but not phrase it | Inside the destination | A fog line, noting what it hangs on |
| Phrase it or not | Beyond the destination | An out-of-scope line with a reason |

The test for ticket versus fog is **whether you can state the question sharply, not
whether you can answer it**. A sharp but blocked question is still a ticket; the
blocking link is what keeps it off the frontier.

Do not slice fog into ticket-sized pieces in advance. Fog is coarser than tickets: a
single fog line may later become three tickets, or none, once the answers ahead of it
are known. Pre-slicing produces tickets built on guesses, which then have to be
rewritten.

Marking something out of scope narrows the work; it does not add a ticket to the map. Nothing in that list is ever promoted to a build ticket.
If one comes back, the destination has changed, and that is a new effort or an
explicit redraw of the map, not a quiet addition.

## 5. Ticket types

Every decision ticket has exactly one type. The type tells whoever picks it up how
it gets resolved.

| Type | Resolved by | Needs a human in the loop? | Typical length |
|------|-------------|---------------------------|----------------|
| research | Reading docs, data, code, vendor APIs; reporting a fact | No, can be delegated | Hours |
| prototype | Making a rough concrete artefact people react to | Yes, the reaction is the point | Half a day |
| discussion | A person with authority choosing between options | Yes, always | One session |
| enabling-task | Doing prerequisite work so another decision becomes possible | Sometimes | Hours to a day |

Rules that keep types honest:

- A **research** ticket returns a fact, not a choice. If the researcher ends up
  choosing, split the ticket: research for the fact, discussion for the choice.
- A **discussion** ticket needs at least two real options, including "do nothing" when
  that is genuine. A discussion with one option is a decree; record it as resolved.
- A **prototype** ticket also needs options: the prototype exists to compare them.
- An **enabling-task** must name the decision it unblocks. Work that unblocks nothing
  on the map is implementation work wearing the wrong label.
- Nobody may answer their own discussion ticket on behalf of the owner. An agent or
  analyst can prepare the options and a recommendation; the owner makes the call.

## 6. Owners and decide-by dates

The owner is the person who makes the call, not the person who does the research.
For a pricing decision the researcher might be an analyst and the owner the head of
product. A ticket with no owner will sit on the frontier until someone notices it has
been there for weeks.

Decide-by dates exist to expose the cost of delay. Write next to the date what slips
if it is missed ("T1 cannot start; launch moves a week"). A decide-by date that has
passed is a warning in `decision_map_validator.py` when run with `--today`; treat a
run of overdue tickets as a signal that the owners are wrong or overloaded, not that
the dates were optimistic.

## 7. Blocking links

Draw a blocking link only when one question genuinely cannot be answered without the
other's answer. Over-linking collapses the frontier: everything waits on everything
and nothing is takeable. Under-linking causes rework: a decision made before its
prerequisite gets reopened.

Test each link by asking: "If the blocker came back with its *least* likely answer,
would this ticket's options change?" If not, remove the link.

Create tickets first and wire links in a second pass. Trackers need ids before
tickets can reference each other, and writing placeholder references produces links
to unrelated issues.

Cycles mean two questions have been drawn as each other's prerequisite. They are
almost always one of three things:

1. **Two halves of one decision.** Merge them into a single ticket.
2. **A missing fact both depend on.** Extract a research ticket that both are blocked by.
3. **A wrong link.** Apply the least-likely-answer test and drop the weaker edge.

The validator reports every cycle as a closed path so you can see which edge to cut.

## 8. Working the map

Each working session:

1. **Load the map page**, not every ticket. The decisions-so-far index gives the
   low-resolution view; open individual tickets only as needed.
2. **Run the validator.** Fix any error before taking work. An error means the map is
   lying about what is takeable.
3. **Take one frontier ticket.** The frontier is every open, unclaimed ticket whose
   blockers are all closed. Decisions come before implementation in the tool output
   because an unmade decision ripples further than an unbuilt slice.
4. **Claim it** before doing anything else, so a parallel session does not take it too.
5. **Resolve it** according to its type.
6. **Record the resolution on the ticket**: chosen option, reason, rejected options,
   consequences, and what would make you revisit it. Close the ticket.
7. **Add one line to Decisions so far**: title, link, one-clause gist.
8. **Update the map**: graduate fog that is now sharp into tickets (and delete it from
   the fog list), open newly surfaced tickets, rule anything now beyond the destination
   out of scope, and convert the resolution into implementation tickets where it is ready.

Resolve one decision per session. A session that tries to settle several decisions
usually settles the first and quietly assumes the rest. Research tickets are the
exception: several can run in parallel because none of them chooses anything.

## 9. Parallel sessions

When several people or agents work the same map:

- The claim (assignee plus `claimed` status) is the lock. An open, unassigned ticket
  is free; anything else is taken.
- Expect the map to change under you. Reload it before recording a resolution.
- Never edit another session's claimed ticket. Comment on it instead.
- Keep the decisions-so-far index append-only; reordering it causes merge pain and
  destroys the record of the route actually walked.

## 10. Worked example (abridged)

**Destination:** "New self-serve workspaces are billed per active seat-hour through
the new metering pipeline, and every invoice reconciles to the ledger within 0.5%
before month-end close."

First charting session produced:

| Id | Type | Question | Blocked by |
|----|------|----------|-----------|
| D1 | discussion | What unit do we meter and bill on? | — |
| D2 | research | Do we rate usage ourselves or send it to the provider to rate? | D1 |
| D3 | discussion | Which identifier keys usage records, given account_id is overloaded? | — |
| D4 | prototype | How should seat-hour usage appear on the invoice? | D2 |
| D5 | discussion | What happens when a usage invoice fails to collect? | D2 |
| D6 | enabling-task | Can we get a provider sandbox with metered prices? | D2 |

Fog: proration on mid-cycle plan changes (hangs on D2 and D5); who receives usage
alerts. Out of scope: migrating legacy flat-rate customers; multi-currency invoicing.

After three sessions D1, D2 and D3 were resolved, the D3 answer became a four-ticket
expand-migrate-contract refactor, and D1+D2 became the first tracer bullet. The full
JSON is in `assets/sample_decision_map_clean.json`.

## 11. Closing the map

The map is finished when:

- the destination is reached (or, for a decision-destination, the decision is made);
- the frontier is empty and no fog remains;
- every resolved decision either has implementation tickets or is marked as needing
  none (`no_build: true`);
- the decisions-so-far index reads as a coherent account of how the route was found.

Archive the map rather than deleting it. Six months later, the index is the fastest
way for someone to learn why the system is shaped the way it is.
