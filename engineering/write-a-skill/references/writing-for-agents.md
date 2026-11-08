# Writing for Agents

Everything in a skill package, and every steering file in a repository, is read by a model
before it is read by a person. That reader is fast, literal and short on attention: it pays
for every token in its context window, and it treats each line as something to act on. This
reference covers three decisions that follow from that: who may invoke a skill, when a skill
should do nothing but call other skills, and how to write the always-loaded files
(`AGENTS.md`, `CLAUDE.md` and their equivalents).

---

## 1. Who invokes the skill

A skill can be reached two ways: the model decides to load it because its description
matches the task, or the user calls it by name (a slash command). Most skills should allow
both. Some should allow only the second.

### User-only skills: `disable-model-invocation: true`

In Claude Code, adding `disable-model-invocation: true` to a skill's frontmatter stops the
model from loading the skill on its own. The skill still appears as a command the user can
run. Other platforms have their own switch, or none; where none exists, the description
should say "Run only when the user asks for it by name."

```yaml
---
name: release-notes
description: Draft release notes from merged PRs since the last tag. Run only when the user asks.
disable-model-invocation: true
license: MIT + Commons Clause
metadata:
  ...
---
```

Make a skill user-only when any of these is true:

| Signal | Why model invocation is wrong | Example |
|--------|-------------------------------|---------|
| It has side effects the user must choose | The model would trigger them on a loose match | Publish, deploy, open tickets, send messages |
| It is a ritual with a time the user picks | The model cannot know when the moment has come | Retrospective, end-of-day handoff, weekly review |
| It is costly | Long multi-agent runs, paid APIs, big context loads | Deep review, full audit |
| Its description would collide | Its trigger words overlap a model-invocable skill's | A "quick review" next to a full review skill |

Two consequences of the switch:

- **The description stops being a trigger and becomes a label.** Write it for the person scanning the command list: what it does, in one line. The `Use when` clause still helps catalog search in this library, so keep it short.
- **Nothing will run it unless someone remembers to.** If the skill matters, put a one-line pointer in the steering file ("After a messy session, run `/session-retro`") or wire it into a command the user already runs.

The linter checks that the field, when present, is `true` or `false`.

### Model-invocable skills

Everything else. Here the description is the only thing that decides whether the skill is
ever used, so it carries the trigger words a user would actually type, as covered in the
authoring playbook.

---

## 2. Thin composing skills

A composing skill contains no domain knowledge of its own. It names a sequence of other
skills, states what passes between them, and defines when the sequence is done. Example: a
"ship a feature" skill that runs spec capture, ticket slicing, the implementation loop and a
two-axis review, in that order.

### When a composing skill earns its place

- The same sequence of skills is run often, in the same order.
- The handoff between them needs a rule nobody remembers ("the review uses the spec from step 1, not the ticket text").
- People skip a step when they run the sequence by hand.

If the sequence is run rarely or varies every time, a short list in the steering file does
the same job for less.

### How to write one

1. **Name each step by skill and say what it must produce.** "Run the spec skill; done when the spec lints clean." The completion condition is the most important line in each step.
2. **Pass artifacts by pointer, not by copy.** "Use the spec at `docs/specs/<feature>.md`" rather than pasting the spec into the next step. Pointers stay current; copies drift.
3. **Keep the steps' own instructions out.** The composing skill does not restate how to write a spec. If it did, there would be two versions of that procedure to keep in sync.
4. **Say where each step runs** when it matters: in the current session, in a fresh sub-agent, or in a background session. Steps that must not see each other's context (an implementer and its reviewer) say so.
5. **Stop on a failed step.** State what happens when a step's completion condition is not met — usually "stop and report", not "continue".

### Packaging note for this library

Library skills must stay self-contained (Pattern 9): a skill may not depend on another
skill's files. A composing skill therefore refers to other skills **by name only**, as
instructions to the agent ("invoke the `tdd-guide` skill"), never by importing scripts or
requiring the reader to open another skill's files to make sense of it. If the named skill
is missing, the composing skill should still read as a usable checklist. Keep composing
skills in a user's own setup or a plugin when they depend on skills outside this library.

---

## 3. Writing steering files

`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/*.mdc` and the like are loaded into
context at the start of every session, and often kept there for the whole session. Each
line costs tokens and attention on every turn whether or not it is relevant. Write them like
a pre-flight checklist, not like documentation.

### Style rules

- **Short, imperative lines.** "Run tests with `make test`." One instruction or fact per line.
- **Lead with the situation.** "Database changes: write a migration in `db/migrations/`; never edit `schema.sql`." The agent scans for the case it is in.
- **Say what to do, not only what to avoid.** A bare prohibition still puts the forbidden action in front of the agent. Pair any "never" with the alternative.
- **No filler.** Drop "please", "make sure to", "it is important to", "always remember", "as an AI". They change nothing.
- **Point instead of paste.** Long procedures go in a doc or a skill; the steering file holds one line saying when to read it. The wording of that line decides whether the agent follows it, so name the trigger precisely.
- **Do not restate the environment.** Script names, flags and directory layout are one command away. Copies of them go stale. Write what looking cannot reveal: the unwritten convention, the reason, the trap.
- **Put review rules where the reviewer reads them.** The agent writing code carries the most context. Style and design rules that a reviewer can check against a diff belong in the standards document, not in the always-loaded file.
- **Prefer a check to a sentence.** A rule with a fixed shape (a banned import, a required header) becomes a lint rule or hook. It is enforced every time and costs no context.
- **Prune on every edit.** When adding a line, look for one to delete. Lines that never change the agent's behaviour are pure cost.

### Size

There is no fixed limit, but a useful test is whether a newcomer could read the whole file
in two minutes. Past that, split by directory (a per-directory steering file loads only when
work happens there) or move procedures into skills.

### Before and after

```markdown
<!-- Before -->
## Testing
It's really important that you always make sure to run the complete test suite before
you consider any task finished. We use pytest, but please note that you need to set the
PYTHONPATH first, otherwise imports will fail. You can find more about our testing
philosophy in the docs folder.

<!-- After -->
## Testing
- Run `make test` before reporting done (bare `pytest` fails: needs `PYTHONPATH=src`).
- Writing new tests: read `docs/testing.md` first.
```

The rewrite is a third of the length, carries the same facts, and gives the agent the exact
command and the exact condition for opening the doc.

### The same rules apply to SKILL.md

A SKILL.md body is loaded when the skill triggers, so it is cheaper than a steering file but
still read in full. The same habits apply: steps the agent follows in order, each with a
clear done condition; reference material pushed to `references/` behind a pointer that says
when to read it; one concept's rules kept together under one heading; no restating what a
script's `--help` already says.
