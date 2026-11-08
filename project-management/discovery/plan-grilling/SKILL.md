---
name: plan-grilling
description: >
  Interrogate a plan, design or idea one round of questions at a time until
  every decision is settled. Use when stress-testing a plan before building,
  when a design feels underspecified, or turning a fuzzy workflow into a spec.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-11-08
  python-tools: question_log_checker.py, workflow_spec_checker.py
  tech-stack: decision-trees, discovery-interviews, specification, question-logs
  tags:
    - grilling
    - decision-tree
    - plan-review
    - specification
    - discovery
---

# Plan Grilling

A plan hides a tree of decisions, most of them made by accident. This skill
makes them explicitly. The agent walks the tree in rounds, asks only questions whose
prerequisites are settled, attaches its own recommended answer to each, looks
facts up instead of asking for them, and logs everything until nothing is left
silently assumed.

## When to Use

- Before committing build effort to a plan, design or migration
- When a design "feels done" but nobody can list its decisions
- When a recurring workflow should be handed to a script, agent or teammate and is not yet written down (multi-session mode)

## Clarify First

What most shapes a grilling is what it is meant to settle. Settle the inputs below before the first round. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The subject:** the plan, design or workflow, in writing if it exists. The tree is built from it.
- **The decision-maker:** who answers decisions. A grilling answered by someone without authority settles nothing.
- **The destination:** a go/no-go, an agreed plan, or an implementable spec. It sets the stop criteria and whether multi-session mode applies.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Next round: the frontier, ordered by how many questions each unblocks
python3 project-management/discovery/plan-grilling/scripts/question_log_checker.py \
  --input project-management/discovery/plan-grilling/assets/sample_question_log.json --stage round
```

```bash
# Final gate before declaring the tree resolved (flawed sample exits 1)
python3 project-management/discovery/plan-grilling/scripts/question_log_checker.py \
  --input project-management/discovery/plan-grilling/assets/sample_question_log_flawed.json --format json
```

```bash
# Multi-session mode: is the workflow spec implementable?
python3 project-management/discovery/plan-grilling/scripts/workflow_spec_checker.py \
  --input project-management/discovery/plan-grilling/assets/sample_workflow_spec.json
```

## Tools Overview

| Tool | Checks |
|------|--------|
| `question_log_checker.py` | Category coverage, out-of-order questions, missing recommendations, unconfirmed assumed decisions, facts asked of the user, cycles, ownerless deferrals; prints the next round. `--stage final` also requires closure. |
| `workflow_spec_checker.py` | Trigger, steps with one actor, checkpoints with decision and brief, output destinations, testable done-criteria, no open questions. |

### Exit code contract

| Code | Meaning |
|------|---------|
| 0 | No error findings (warnings allowed) |
| 1 | Gate failed: at least one error finding |
| 2 | Bad input: missing file, invalid JSON, wrong shape |

## Workflow

1. **Build the tree.** [PROVEN] Draft questions across the taxonomy (goal, users, constraints, success, failure modes, reversibility, sequencing, ownership, unknowns). Record `depends_on` wherever one answer would change or remove another question.
2. **Split facts from decisions.** [PROVEN] Facts (how many users, what the code does) are the agent's job: look them up and log the source. Only decisions (the user's call) go to the user.
3. **Ask the frontier, one round at a time.** [RECOMMENDED] Run the checker with `--stage round`. Send at most five decisions, numbered, each with a recommended answer and a one-line reason, worded so "yes" accepts it. Never ask a question whose prerequisite is still open.
4. **Log verbatim and recompute.** Surface contradictions with earlier answers at once; defer superseded questions.
5. **Close the open ends.** Every unknown is resolved, deferred with an owner and reason, or accepted as an assumption the decision-maker confirmed.
6. **Run the quality gate.** [RECOMMENDED] `--stage final` must exit 0, then read the decisions back to the decision-maker; their agreement is the last checklist item.
7. **Multi-session mode.** [EXPERIMENTAL] For a recurring workflow: session 1 learns tools and vocabulary; the user runs it once by hand between sessions; later sessions settle steps, late checkpoints and failure handling. Validate with `workflow_spec_checker.py`. Risk: users describe the ideal workflow, not the real one, so insist on hand-run notes.

### Stop criteria

| Signal | Action |
|--------|--------|
| Frontier empty, gate exits 0, decisions read back and agreed | Stop: tree resolved |
| Only cheap two-way doors left, or user wants to start | Accept remaining recommendations or defer them to the user; list unvisited branches; stop |
| Goal still two goals, or a one-way door lacks failure/rollback answers | Do not stop |

## Anti-Patterns

### Asking the Whole Tree at Once
**Mistake:** Sending twenty questions in the first message, half of which depend on answers not yet given.
**Why it happens:** It feels thorough.
**Instead:** Ask only the frontier. Questions built on hypothetical answers get thrown away.

### Making the User Your Search Engine
**Mistake:** Asking "how many accounts have under ten seats?" and logging the guess.
**Why it happens:** Asking is faster than looking.
**Instead:** Resolve facts from code, data and docs, with a logged source.

### The Bare Question
**Mistake:** "How should we handle failures?" with no recommendation.
**Why it happens:** Offering an answer feels presumptuous.
**Instead:** Attach a recommended answer; agreement then costs one word.

### The Silent Assumption
**Mistake:** Filling an unanswered decision with the recommendation and moving on.
**Why it happens:** The user went quiet and momentum matters.
**Instead:** Get explicit confirmation; the checker fails unconfirmed assumed decisions.

### Grilling Without a Destination
**Mistake:** Questions continue indefinitely.
**Why it happens:** The destination was never set.
**Instead:** Fix it in Clarify First and stop on the criteria above.

## Files

| File | Purpose |
|------|---------|
| `scripts/question_log_checker.py` | Coverage, ordering, assumption and closure gate; prints the next round |
| `scripts/workflow_spec_checker.py` | Implementability gate for multi-session workflow specs |
| `assets/question_log_template.md`, `assets/workflow_spec_template.md` | Human-readable log and workflow spec templates |
| `assets/sample_question_log.json` / `_flawed.json` | Resolved grilling (exits 0) / out-of-order, assumed, cyclic log (exits 1) |
| `assets/sample_workflow_spec.json` / `_flawed.json` | Implementable spec (exits 0) / unready spec (exits 1) |

## Reference Documentation

- **[references/question-taxonomy.md](references/question-taxonomy.md)**: nine categories, probing questions, fact vs decision rules. Read when drafting rounds.
- **[references/running-the-grilling.md](references/running-the-grilling.md)**: frontier mechanics, round format, log fields, stop rules, multi-session mode, worked example. Read when running or resuming a session.

## Scope & Limitations

**In Scope:** building and walking a plan's decision tree in rounds; fact/decision separation; question logs with assumptions and deferrals; stop criteria; multi-session specification of recurring workflows.

**Out of Scope:**
- Imagining failure after launch and classifying risks (see `project-management/discovery/pre-mortem/`)
- Adversarial attack on a finished design or system (see `engineering/red-team/`)
- Mapping and testing assumptions with experiments (see `project-management/discovery/identify-assumptions/`)
- Breaking a large effort into decision tickets across many sessions (see `project-management/execution/wayfinder/`)

**Important Caveats:**
- The checkers verify the log's structure, not the quality of answers.
- `depends_on` and `round` are entered by hand; a wrong dependency gives a wrong frontier.
