# Flow Metrics Reference Guide

A practical reference for Kanban flow metrics: lead time, cycle time, throughput, WIP, and aging WIP. Built on Daniel Vacanti's body of work and David Anderson's Kanban methodology. Companion to `flow_metrics.py`.

---

## 1. Why Flow Metrics

Story-point velocity is a measure of a team's *commitment*, not its delivery. It is highly gameable, sensitive to estimation drift, and meaningless across teams. Flow metrics measure actual delivery behavior using only event timestamps already in your tracker. They are:

- **Atomic.** One completed item = one. No estimation bias.
- **Comparable.** Throughput and cycle time mean the same thing across teams.
- **Diagnostic.** When delivery slows, flow metrics tell you *where* (which step in the workflow is the bottleneck).
- **Forecasting-ready.** Cycle time distributions feed Monte Carlo forecasts directly.

The four metrics are governed by **Little's Law**:

```
Average Cycle Time = Average WIP / Average Throughput
```

Practical implication: reducing WIP is the most reliable way to reduce cycle time. Estimation accuracy is a distant second.

---

## 2. The Workflow Model

Every work item moves through a defined workflow:

```
Backlog -> Ready -> In Progress -> In Review -> Done
```

The exact state names vary by tracker and team. What matters is identifying three boundaries:

| Boundary | Meaning | Common State Names |
|----------|---------|---------------------|
| **Commitment point** | The team agrees to do this item | `Ready`, `To Do`, `Selected for Development` |
| **Start of active work** | Someone begins working on it | `In Progress`, `In Development` |
| **Delivery point** | The item ships / is accepted | `Done`, `Closed`, `Deployed`, `Accepted` |

The choice of boundaries determines the metrics:

- **Lead time** = `Delivery point` - `Commitment point`
- **Cycle time** = `Delivery point` - `Start of active work`

If your team has a long "Ready" queue (commitment to start), lead time will be much larger than cycle time. That gap is the queueing delay, often the biggest opportunity for improvement.

---

## 3. Lead Time

The customer-perceived elapsed time from commitment to delivery.

### How to Read It

Report as a **distribution**, not a single number:

| Percentile | Meaning |
|------------|---------|
| **50th (median)** | Half of items finish in this time or less |
| **85th** | The "service level expectation" -- a defensible commitment to stakeholders |
| **95th** | Worst-case for planning; outliers above this need investigation |

A stakeholder asking "when will it be done?" deserves the 85th-percentile answer, not the average. The average over-promises because the distribution is right-skewed (a few items take very long).

### Common Failures

- **Reporting average lead time only.** Hides the skew; promises overshoot reality.
- **Stale backlog inflating lead time.** Items "committed" months ago that nobody is actually working on. Either close them or measure lead time only for items committed in the last N months.
- **Mixing types.** Bugs, features, and spikes have very different lead times. Filter or split before reporting.

---

## 4. Cycle Time

The team-perceived elapsed time from start of active work to delivery.

### How to Read It

Same distribution rules as lead time. The 85th percentile is the practical "how long do things take us?" answer.

### What Increases Cycle Time

The four big drivers (in observed-impact order):

1. **High WIP.** Little's Law makes this mechanical.
2. **Cross-team dependencies.** Waiting on another team's review or deployment.
3. **Large items.** Stories that should have been split (see `story-splitting/`).
4. **Context switching.** Engineers juggling multiple items simultaneously.

### Cycle Time vs Estimation Accuracy

Teams that improve cycle time by reducing WIP and splitting work see predictability improvements much larger than teams that improve estimation accuracy. Vacanti's recommendation: stop estimating story points and instead split work into uniform-ish sizes (most teams converge on 1-3 days per item) and use throughput as the planning unit.

---

## 5. Throughput

Items completed per unit time. Most useful at the week or sprint level.

### How to Read It

| Window | Use |
|--------|-----|
| Per week | Operational dashboard |
| Per sprint | Sprint review baseline |
| Rolling 6-8 weeks | Trend reporting |
| Per quarter | Capacity planning |

### Throughput vs Velocity

| | Throughput | Story-Point Velocity |
|---|---|---|
| Counts | Completed items | Story points completed |
| Estimation needed | No | Yes |
| Comparable across teams | Yes (with type filter) | No |
| Useful for Monte Carlo | Yes | Yes (but noisier) |
| Gameable | Low (visible count) | High (point inflation) |

### Monte Carlo Forecasting

Given a throughput distribution from N past sprints, you can answer "how likely is it that we finish X items by sprint Y?" with a Monte Carlo simulation:

1. Sample N throughput values from history (with replacement).
2. Sum the samples across the forecast horizon.
3. Check the percentile of "X items completed."
4. Repeat 10,000+ times.

The result: "There is a 90% chance we deliver 30 items in the next 6 weeks; a 50% chance we deliver 40." This is far more useful than "our velocity is 35."

(For Monte Carlo specifically, hand off to `scrum-master/velocity_analyzer.py`. This skill produces the input distribution.)

---

## 6. Work-In-Progress (WIP)

The count of items currently in flight.

### Why WIP Matters

From Little's Law, WIP and cycle time are mechanically linked. Doubling WIP doubles cycle time (with throughput held constant). This is not a metaphor -- it is queueing theory.

### Setting WIP Limits

A practical starting point: WIP limit per state = team size + a small buffer. Tighten over time as the team gets comfortable finishing-before-starting.

A common refinement (Anderson): explicit WIP limits per state, displayed on the board. When a state is at capacity, no new items enter -- forcing the team to swarm on what is there and finish it.

### WIP Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| No WIP limits | Multitasking everywhere; cycle time creep | Set per-state limits at current median |
| Hidden WIP | Items in "In Progress" that nobody is actively working on | Aging WIP review; close or restart |
| Per-person WIP limits | One person dominating two items; team feels productive | WIP is a *team* limit, not a per-person limit |
| Limit busted "just this once" | Limits routinely ignored | Either lower limits or stop pretending they matter |

---

## 7. Aging WIP

The most actionable flow metric. A list of every currently-in-flight item with its age (days since start).

### How to Use Aging WIP

In daily standup, ask only one question per aging item: "What is the plan today to move this forward?"

Items older than the team's 85th-percentile cycle time are statistical outliers. They almost always:

- Have an unresolved dependency.
- Are larger than they should be (and should be split).
- Are blocked by a decision that nobody is pushing on.
- Have been quietly abandoned and need to be closed.

### Aging WIP Report Format

| ID | Title | Age (days) | Status | Assignee | Days over 85th %ile |
|----|-------|-----------:|--------|----------|--------------------:|
| ENG-201 | OAuth migration | 18 | In Progress | (any) | +7 |
| ENG-198 | Mobile push fix | 14 | In Review | (any) | +3 |

Run this report at the start of every standup. Most teams find this single change improves cycle time more than any tooling investment.

---

## 8. Cumulative Flow Diagram (CFD)

A stacked-area chart showing the count of items in each workflow state over time.

```
^  Cumulative Items
|
|        Done /////////
|        ////////////
|       /////////
|      / In Review ----
|     /  ----
|    /  In Progress ...
|   /  ...
|  /  Ready - - -
| /  - - -
|/__________________> Time
```

### What to Look For

- **Parallel bands.** Healthy flow: bands grow at roughly the same rate.
- **Widening "In Progress" band.** WIP is growing; cycle time will follow.
- **Flat "Done" band.** Delivery has stalled; debug upstream.
- **Sudden vertical jumps.** Status transitions logged in batch, not real time.
- **Bands crossing each other.** Items moving backwards through the workflow (a churn signal).

### CFD vs Burndown

| | Cumulative Flow Diagram | Burndown |
|---|---|---|
| Time horizon | Multi-sprint, multi-month | Single sprint |
| Question answered | Where is work accumulating? | Are we tracking toward the commitment? |
| Useful for | Process improvement, bottleneck detection | Sprint operational management |

Both are useful; they answer different questions.

---

## 9. Tracker-Specific Export Tips

### Jira

Use the `jira-python` library or the REST API:

```bash
# Pseudocode (Jira Cloud, as of September 2026)
# 1) Find the issues -- enhanced JQL search, token pagination
GET /rest/api/3/search/jql?jql=project=ENG AND updated >= -90d&fields=key,created,resolutiondate&maxResults=100
#    repeat with &nextPageToken=<token> until the response has no nextPageToken

# 2) Pull full status history in bulk (up to 1000 issues per request)
POST /rest/api/3/changelog/bulkfetch
{"issueIdsOrKeys": ["ENG-1", "ENG-2"], "fieldIds": ["status"]}
#    paginate with nextPageToken
```

The legacy `/rest/api/3/search` (and `/rest/api/2/search`) endpoint is deprecated and being removed (Atlassian changelog CHANGE-2046). The replacement returns no `total`, has no `startAt`, and returns only `id` unless you list `fields` explicitly. `expand=changelog` on search returns only *recent* updates, so use the changelog endpoints above for complete cycle-time history. Queries must be bounded (include a restriction such as a project or date). See the [Issue search](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/) and [Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/) API reference.

Map each `issueChangeLogs[].changeHistories[].items` entry with `field == "status"` (its `fromString` -> `toString`, timestamped by the history's `created`) to `status_history` in the input JSON.

### Linear

Use Linear's GraphQL API:

```graphql
query {
  issues(first: 200, filter: { team: { key: { eq: "ENG" } } }) {
    nodes {
      identifier title createdAt
      history { nodes { fromState { name } toState { name } createdAt } }
    }
  }
}
```

Map `history.nodes` -> `status_history`.

### GitHub Projects

Less straightforward (no built-in status history); requires reading project field updates via the GraphQL API. The `events` endpoint of the issues API offers `labeled` / `unlabeled` events that approximate status if your team uses labels-as-status.

---

## 10. Common Reporting Cadences

| Cadence | Audience | Artifacts |
|---------|----------|-----------|
| **Daily standup** | Team | Aging WIP report |
| **Weekly** | Team + lead | Throughput trend, cycle-time distribution snapshot |
| **Per sprint review** | Team + stakeholders | CFD for the sprint, week-over-week throughput |
| **Quarterly** | Leadership | Rolling 12-week throughput, cycle-time stability, dependency-correlated delays |

---

## 11. Anti-Patterns to Avoid

| Anti-Pattern | Why It Backfires |
|--------------|------------------|
| Per-person cycle time | Punishes collaboration; encourages individual silos |
| Throughput target ("hit 10/week") | Encourages closing items that are not actually done; "scope-cutting to finish" |
| Cycle time SLA without WIP limit | Mathematically impossible per Little's Law |
| Reporting averages only | Hides skew; over-promises delivery |
| Mixing types in one number | Bugs and features have different distributions; combined numbers mislead |
| Tracking cycle time only for completed items | Survivorship bias; ignores items that are still in flight and aging |

---

## 12. References

- Vacanti, Daniel S. *Actionable Agile Metrics for Predictability*. ActionableAgile Press, 2015.
- Vacanti, Daniel S. *When Will It Be Done?* ActionableAgile Press, 2020.
- Anderson, David J. *Kanban: Successful Evolutionary Change for Your Technology Business*. Blue Hole Press, 2010.
- Little, John D. C. "A Proof for the Queuing Formula: L = λW." Operations Research, 9(3), 1961.
- Reinertsen, Donald G. *The Principles of Product Development Flow*. Celeritas, 2009.
