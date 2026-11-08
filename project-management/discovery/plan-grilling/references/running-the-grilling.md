# Running the Grilling: Rounds, Logging, Stopping, Multi-Session Mode

This reference covers the mechanics: how to build the decision tree, how to cut
it into rounds, what to write down, when to stop, and how to stretch the same
discipline across several sessions to turn a fuzzy recurring workflow into a
spec someone else can build.

---

## 1. The decision tree

Every plan hides a tree. The root is the goal. Each answer opens the questions
that hang off it: once the goal is "stop missed exports", the next questions
are about who reads the export and what format must not change; once the
format is frozen, the rollback question becomes answerable; and so on.

Two properties matter:

- **Dependencies.** A question depends on another when a different answer to
  the first would change, or remove, the second. Record that as `depends_on`.
- **Settledness.** A question is settled when it is answered, or when it is
  stated as an assumption the decision-maker accepted (or, for a fact, that the
  agent verified and sourced). Asked-but-unanswered and deferred questions are
  not settled.

The **frontier** is the set of open questions whose prerequisites are all
settled. Those are the only questions worth asking right now. Anything else
asks the user to answer a hypothetical: "assuming you pick per-seat pricing,
what happens at seat 11?" invites an answer that may be thrown away next round.

## 2. Rounds

A round is one batch of frontier questions, sent together, answered together.

1. Recompute the frontier from the log (`question_log_checker.py --stage round`
   prints it as "Next round", ordered so the questions that unblock the most
   others come first).
2. Resolve every **fact** on the frontier yourself first. Read the repository,
   the data, the documentation. Log each with its source. Facts that turn out to
   be unfindable become unknowns.
3. Draft each **decision** with a recommended answer and a one-line reason.
   Word it so "yes" accepts the recommendation.
4. Cap a round at about five decisions. More than that and answers get shorter
   and less considered. If the frontier is larger, send the five that unblock the
   most.
5. Send the round. Number the questions so the user can reply "1 yes, 2 no —
   because…, 3 yes".
6. Log every answer verbatim. Then recompute the frontier: answers open new
   questions and sometimes make queued ones irrelevant (mark those `deferred`
   with reason "superseded by Q7", or delete them before they are asked).

### Round format

```
Round 3 — 4 questions (unblocks 6 more)

Q7. Shadow-run old and new exporters for 7 nights before cutover?
    Recommended: yes — cut over after 7 identical diffs.
    Why: the format is frozen (Q3), so a byte diff is a complete test.

Q8. Does the payments platform team own the exporter after cutover?
    Recommended: yes — it sits next to their invoicing service.
```

### Pace

- Do not wait on a slow fact lookup to send the rest of the round. A pending
  lookup only blocks the questions that depend on it.
- If the user answers a question that was not asked ("and by the way we also
  need SSO"), log it as a new question with its category and settle it — do not
  let it slip into the conversation unlogged.
- If an answer contradicts an earlier one, stop and surface the conflict
  before continuing: "Q9 says read-only after 7 days; Q4 said no access loss
  ever. Which holds?"

## 3. What the log must hold

| Field | Why |
|-------|-----|
| `id`, `question` | Reference in rounds and in the decisions list |
| `category` | Coverage check across the taxonomy |
| `kind` | Fact (agent answers) or decision (user answers) |
| `depends_on` | Frontier computation and order checking |
| `round` | Proves no question was asked before its prerequisites |
| `recommended` | Every decision put to the user carries the agent's pick |
| `answer` | Verbatim; paraphrase drifts |
| `status` | open, asked, answered, deferred, assumed |
| `resolved_by` | `agent` for facts looked up; `user` for anything the user said |
| `source` | Where an agent-resolved fact came from |
| `confirmed` | True when the user accepted an assumption |
| `owner`, `reason` | Required for every deferral |

Keep a human-readable copy (`assets/question_log_template.md`) for the
decision-maker and the JSON copy for the gate. They hold the same content.

## 4. When to stop

Stop when **all** of these hold:

1. The frontier is empty and nothing is blocked.
2. Every core category has at least one settled question.
3. No decision is recorded as an assumption without the user's confirmation.
4. Every deferral has an owner and a reason, and none of them sits on the route
   to the goal.
5. You can read the "Decisions so far" list back and the decision-maker agrees
   it is the plan.

Run `question_log_checker.py --stage final`. Exit 0 means the mechanical part of
the stop criteria holds; point 5 is a conversation, not a check.

### Stop early when

- The remaining questions are all two-way doors with cheap reversal. Record the
  recommended answers as confirmed assumptions in one batch ("Accept all
  remaining recommendations? yes/no") and stop.
- The user says they want to start. Close the log with the open questions listed
  as deferred, owner = the user, and say plainly which branches are unvisited.

### Do not stop when

- The goal is still two goals.
- A one-way door step (data migration, contract, public announcement) has no
  reversibility or failure-mode question settled.
- The user is answering with "whatever you think" to decisions that are not
  two-way doors. That is a sign they are tired, not that the tree is resolved;
  offer to pause and resume.

## 5. Facts: how to look them up

Before asking the user anything, search where facts live:

| Fact type | Where to look |
|-----------|---------------|
| Current behaviour of a system | The code, config, tests |
| Usage numbers | Analytics, logs, database counts |
| Existing commitments | Contracts, docs, tickets, roadmap |
| Constraints from other teams | Their docs, their interface definitions |
| Prior decisions | ADRs, decision logs, closed tickets |

Log every fact with its `source`. A fact without a source is an assumption, and
the checker warns about it.

## 6. Multi-session mode: fuzzy workflow → implementable spec

Use multi-session mode when the subject is a **recurring** workflow the user
wants to hand off — to a script, an agent, a teammate — and it is not yet
written down. One sitting rarely gets there: the user needs to watch the
workflow happen once or twice between sessions to answer accurately.

### The spec's sections

| Section | Settled when |
|---------|--------------|
| Trigger | The exact event or cadence (with time and timezone) is named, plus what looks like a trigger but is not |
| Inputs | Every input has a source and an example |
| Steps | Each step has one actor (agent, human, script) and a concrete action |
| Human checkpoints | Each states the decision asked and the brief shown; or the workflow is marked autonomous with a reason |
| Outputs | Each has a destination and a reader |
| Failure handling | What happens on a failed step and who hears about it |
| Done definition | Each criterion can be checked by someone who was not in the grilling |
| Vocabulary | The user's own terms are pinned down |

### Session structure

1. **Session 1 — the world.** Before specifying anything, learn the user's
   tools, channels and vocabulary. Record terms in the spec's Vocabulary
   section. Draft the trigger and outputs only.
2. **Between sessions** — the user runs the workflow by hand once and notes
   what they actually did. This is the most valuable input in the whole mode.
3. **Session 2 — the steps.** Walk the notes step by step. For each step: who
   does it, what they read, what they produce. Identify the judgment calls; those
   are checkpoint candidates.
4. **Session 3 — checkpoints and failure.** Push each checkpoint as late as it
   can go, so the human is asked once, with everything prepared, and reads a
   brief rather than raw output. Settle failure handling and the done
   definition.
5. **Gate.** Run `workflow_spec_checker.py`. Exit 0 means no open questions,
   every step has an actor, every checkpoint has a decision and a brief, every
   output has a destination, and the done definition is testable.

### Resuming a session

Open the question log and the spec. Recompute the frontier. Start the session
with a three-line recap — what was decided, what is open, what the user was
going to observe in between — then send the first round. Never re-ask a settled
question; if the user's view has changed, log a new question that supersedes the
old one and mark the old one deferred with reason "superseded".

### Checkpoint placement

| Placement | Effect |
|-----------|--------|
| Early (after step 1 of 6) | Human asked before anything is prepared; likely asked again later |
| Late (after the brief is written) | Human asked once, with the full picture; fast review |
| None, with reason | Autonomous; acceptable when every failure is cheap and reversible |
| None, no reason | A gap. The checker fails it. |

## 7. Worked example (compressed)

**Plan:** replace a nightly cron export with a queue-driven exporter.

- **Round 1** (frontier = no-dependency questions): goal (stop misses vs.
  real-time?), constraints (freeze the CSV format?), ownership (payments
  platform?). Users question resolved by the agent from bucket access logs.
- **Round 2:** success (30 days, zero misses?), failure modes (page on-call
  after two failures?), reversibility (keep cron deployable for 14 days?).
- **Round 3:** sequencing (shadow-run 7 nights, diff, then cut over?) — only
  answerable once reversibility and success were settled. One unknown (move to
  an API push?) deferred with an owner.
- **Gate:** `question_log_checker.py --input assets/sample_question_log.json`
  exits 0. The decisions list is read back; the plan is agreed.

The flawed sample (`assets/sample_question_log_flawed.json`) shows the common
failures: a goal answered "both", a fact put to the user and guessed, a decision
asked before its prerequisite, a decision silently assumed, a cycle, a
dangling dependency and a deferral without an owner. The checker exits 1 on it.
