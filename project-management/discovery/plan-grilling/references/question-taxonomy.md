# Question Taxonomy for Plan Grilling

A grilling fails in one of two ways: it asks the wrong questions, or it asks the
right ones in the wrong order. This reference covers the first problem. Each of
the nine categories below names what it is for, the questions that usually pay
off, the answers that should make you dig further, and the questions that
usually come after it. Use it to draft rounds and to see which branches of the
tree have never been visited.

The seven **core** categories (goal, users, constraints, failure modes,
reversibility, sequencing, unknowns) must each carry at least one settled
question before a grilling can close; `question_log_checker.py` treats a missing
core category as a gate failure. **Success** and **ownership** are strongly
recommended and the checker warns when they are absent.

---

## 1. Goal

**Purpose:** pin down the outcome the plan exists to produce. Every later
answer is judged against it, so it is almost always the first round.

**Questions that pay off**

- What changes in the world when this is done, and for whom?
- If only half of this ships, which half must it be?
- What would make you call this a success even if the plan as written is abandoned?
- Is this the goal, or the first step towards a bigger goal? What is the bigger one?
- What are you explicitly *not* trying to achieve?

**Answers that should make you dig**

- "Both" or "all of the above" — two goals compete for every later trade-off.
  Force a ranking: "When they conflict, which wins?"
- An output instead of an outcome ("ship the dashboard"). Ask what the
  dashboard is for until you reach a behaviour or a number.
- A goal phrased as a solution ("migrate to the queue"). Ask what problem the
  queue removes.

**Usually unlocks:** success, users, constraints.

---

## 2. Users

**Purpose:** identify who is affected, who uses the result and who pays the
cost of change. Many plans name one user and silently harm a second.

**Questions that pay off**

- Who touches the result every day? Who touches it once a quarter?
- Who loses something when this ships (a report, a workaround, a habit)?
- How many of each are there? (A fact — look it up.)
- Which user's needs win when two conflict?
- Who will notice first if it breaks?

**Answers that should make you dig**

- "Everyone." There is always a primary user; name them.
- A number given from memory ("maybe 400?"). Facts belong to the agent: find the
  real figure before the next round.

**Usually unlocks:** constraints, failure modes, success.

---

## 3. Constraints

**Purpose:** list what cannot change — budgets, deadlines, contracts, formats,
regulation, headcount, systems that must keep working.

**Questions that pay off**

- What has to stay byte-identical, API-compatible or contractually unchanged?
- What is the hard deadline, and what happens on the day after it?
- What is the budget ceiling, in money and in people-weeks?
- Which approvals are mandatory, and how long do they take?
- What technology or vendor choices are already fixed?

**Answers that should make you dig**

- A deadline with no consequence attached. A deadline nobody pays for missing is
  a preference; treat it as such.
- "No constraints." Ask about the systems downstream; they are constraints.

**Usually unlocks:** sequencing, reversibility.

---

## 4. Success

**Purpose:** agree how anyone will know the goal was met, before work starts.

**Questions that pay off**

- What number moves, by how much, measured where, by when?
- What is the minimum result that still counts as success?
- What would tell us early (in days, not months) that we are off track?
- Who signs off that it worked?

**Answers that should make you dig**

- Unmeasurable words: "better", "smoother", "faster". Ask "faster than what,
  measured how?"
- A metric nobody currently collects. Then collecting it is a step in the plan.

**Usually unlocks:** failure modes, sequencing.

---

## 5. Failure modes

**Purpose:** walk the specific ways the plan breaks and decide, now, what
happens in each. This is not a full risk workshop; it is enough to make the
design decisions that failure forces.

**Questions that pay off**

- What happens when the main dependency is down for an hour? For a day?
- What happens on bad input, partial input, duplicate input?
- Who is told when it fails, how, and how fast?
- What is the blast radius of the worst plausible mistake?
- What failure would be silent — wrong but not erroring?

**Answers that should make you dig**

- "That won't happen." Ask what happened last time something similar did.
- Alerting with no recipient or no deadline.

**Usually unlocks:** reversibility, sequencing.

---

## 6. Reversibility

**Purpose:** sort decisions into one-way and two-way doors, because they deserve
different amounts of grilling. A two-way door can be decided fast and revisited;
a one-way door needs the full tree.

**Questions that pay off**

- If this turns out wrong in a month, what does undoing it cost?
- Which step destroys or migrates data, contracts or public promises?
- Can the old path stay deployable while the new one proves itself?
- What is the latest point at which we can still back out cheaply?

**Answers that should make you dig**

- "We can always roll back" with no rollback ever rehearsed.
- Any data migration described as reversible without a tested reverse script.

**Usually unlocks:** sequencing (one-way steps go last, behind evidence).

---

## 7. Sequencing

**Purpose:** decide the order of work so the riskiest unknowns are retired first
and one-way doors come after the evidence that justifies them.

**Questions that pay off**

- What is the thinnest version that proves the riskiest assumption?
- What must be true before the first irreversible step?
- What can run in parallel, and what genuinely blocks what?
- Is there a shadow or parallel-run phase, and what ends it?

**Answers that should make you dig**

- A sequence that does all the easy work first and the risky part last.
- Steps ordered by team availability rather than by dependency.

**Usually unlocks:** ownership.

---

## 8. Ownership

**Purpose:** name who decides, who builds, who runs it afterwards and who is
woken up. Plans without an owner for the "afterwards" become orphans.

**Questions that pay off**

- Who has final say when two stakeholders disagree?
- Who owns this in production six months from now?
- Who maintains the documentation and the runbook?

**Answers that should make you dig**

- A team name with no person. Ask for the person.
- "We'll figure it out after launch."

---

## 9. Unknowns

**Purpose:** list what nobody knows yet and decide, per item, whether to find
out now, defer with an owner, or accept the risk explicitly. Unknowns left
unlisted become assumptions nobody chose.

**Questions that pay off**

- What are we assuming that we have not checked?
- Which unknown, if it went the wrong way, would change the plan?
- What is the cheapest way to turn that unknown into a fact?
- Which unknowns can safely wait until after the first release?

**Answers that should make you dig**

- An empty list. Every non-trivial plan has unknowns; ask about the parts the
  team has not built before.

---

## Facts versus decisions

Every question is one of two kinds, and the kind decides who answers it.

| Kind | Example | Who answers | How |
|------|---------|-------------|-----|
| **Fact** | "How many accounts have 2–9 seats?" | The agent | Read the code, the data, the docs, the logs. Log the source. |
| **Decision** | "Do we price per seat or flat?" | The decision-maker | Put it to them with a recommended answer. |

Rules of thumb:

- If the answer exists somewhere the agent can reach, it is a fact. Asking the
  user for it wastes their attention and invites a guess.
- If two reasonable people could give different answers and both be right, it
  is a decision.
- A fact the agent cannot find becomes an **unknown**, not a question for the
  user — unless the user is the only place it exists (their preference, their
  plan, their calendar).
- Never record a decision as an "assumption" without the decision-maker
  confirming it. That is the agent deciding on the user's behalf.

---

## Writing a good question

| Property | Good | Bad |
|----------|------|-----|
| One idea | "Do we page on-call after two failures?" | "How should we handle failures and alerts and retries?" |
| Carries a recommendation | "...? Recommended: yes, page before 05:30." | "...?" |
| "Yes" accepts the recommendation | "Keep the CSV schema frozen?" | "Should we change the CSV schema or not?" |
| Answerable now | Prerequisites settled | Depends on an answer not given yet |
| Concrete | "Grace period of 7 days, then read-only?" | "What about edge cases?" |

The recommendation is not a leading trick. It shows the decision-maker the
agent's reasoning, lets them accept with one word when they agree, and turns a
disagreement into a precise correction rather than an essay.

---

## Category-to-category dependency map

The usual order in which categories unlock each other. Use it to draft the
first two rounds; after that, the actual answers decide the order.

```
goal ──► users ──► constraints ──► reversibility ──► sequencing ──► ownership
  │         │            │                ▲
  └► success └► failure_modes ────────────┘
unknowns: raised in every round, resolved or deferred before closing
```

Round 1 usually contains goal, the first users question, and any hard
constraint already visible. Ownership questions with no prerequisites can join
round 1 too.
