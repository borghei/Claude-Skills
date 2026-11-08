---
name: computer-use-automation
description: >
  Decides when a GUI-driving (computer-use) agent beats an API and lints planned screen actions
  for missing confirmation, verification and grounding. Use when designing a computer-use agent
  or reviewing its action plan.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  updated: 2026-11-08
  tags: [computer-use, browser-automation, agents, gui, reliability]
---

# Computer Use Automation

> **Category:** Engineering
> **Domain:** AI Agents

## Overview

The **Computer Use Automation** skill helps you design AI agents that operate a graphical interface the way a person does — take a screenshot, reason about what is on screen, then click, type, scroll, or navigate, and repeat. It covers the core perception→reason→action loop, the decision of when computer-use is the right tool versus a structured API/MCP tool (prefer a real API whenever one exists; reach for computer-use only for GUIs with no programmatic surface), reliability patterns (grounding every action in the *current* screenshot, verifying after each step, recovering from misclicks), safety guardrails (confirmation gates for destructive actions, sandboxing, avoiding blocking dialogs), and how to evaluate a computer-use agent. It is model-agnostic — the patterns apply to any computer-use-capable model and any GUI tool surface.

## When to Use

- Deciding whether a task needs a screen-driving agent or can use an API, SDK, CLI or MCP tool.
- Designing the screenshot, act, verify loop and its guardrails for a GUI-only target.
- Reviewing a planned action sequence for ungated destructive steps and missing verification before a dry run.

## Clarify First

Before designing or auditing a computer-use agent, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Does a real API/MCP tool exist?:** whether the target exposes an API, SDK, CLI, or MCP server, or is GUI-only (the single biggest factor; if a real API exists, prefer it and skip computer-use).
- **Task & risk:** what the agent must accomplish and whether any step is destructive or irreversible (delete, send, pay, submit), which sets the confirmation gates and sandboxing.
- **Which tool:** advise on tool choice for a target, or lint a planned action sequence for safety (selects `tool_choice_advisor.py` vs `action_safety_linter.py`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Decide computer-use vs API/MCP for a target
python scripts/tool_choice_advisor.py --api-exists no --gui-stability high --volume low --json

# Lint a planned action sequence for safety/reliability gaps
python scripts/action_safety_linter.py --file assets/sample_plan_safe.json    # CLEAN, exit 0
python scripts/action_safety_linter.py --file assets/sample_plan_risky.json   # HIGH, exit 1

# Read actions from stdin and emit a markdown risk report
echo '[{"type":"click","target":"Delete"},{"type":"submit","target":"Confirm"}]' \
  | python scripts/action_safety_linter.py --format markdown
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `tool_choice_advisor.py` | Recommend computer-use vs structured API/MCP for a target, with rationale | `--api-exists`, `--gui-stability`, `--volume`, `--reversible`, `--json` |
| `action_safety_linter.py` | Scan a planned action list for destructive verbs, missing verification, missing confirmation gates, and dialog-triggering patterns | `--file`, `--format`, `--json` |

All scripts: Python 3 standard library only, argparse CLI, `--json` and human-readable output. Run `--help` for full usage.

**Action plan format.** A JSON list of objects with `type` (or its alias `action`): `screenshot`, `observe`, `verify`, `click`, `type`, `submit`, `navigate`, `upload`, ...; `target` (the visible label); optional `text` (what gets typed), `confirmed` (a human or explicit gate approved it) and `verified` (the step checks its own result). Plain text with one `<type> <target>` per line also works. An object with no `type` or `action` is rejected rather than silently passed.

**What the linter flags.** High: destructive verbs (delete, send, pay, submit...) without `confirmed`, state changes on a destructive step with no verification, and typed text that looks like a destructive command (`rm -rf`, `DROP TABLE`, `sudo`...). Medium: unverified state changes, typing into password or payment fields, actions that open native dialogs. Low: actions not preceded by a fresh screenshot.

**Exit codes.** `action_safety_linter.py`: `0` no high finding, `1` at least one high finding, `2` unreadable file or an action list it cannot parse. `tool_choice_advisor.py`: `0` recommendation printed, `2` invalid option value.

**Done when:**
1. The advisor's recommendation is recorded, and an API or MCP route was ruled out with a reason.
2. The linter shows no high findings on the final plan.
3. A sandbox dry run (throwaway profile, test account or VM) completed the task with every verification step passing.

## Workflows

### Decide and Design a Computer-Use Agent
1. Run `tool_choice_advisor.py` with the target's API/MCP availability, GUI stability, and volume — if it says "use API/MCP," stop and build against the real interface instead.
2. If computer-use is justified, draft the action plan as the screenshot→reason→action loop: each step re-grounds on a fresh screenshot before acting.
3. Add a verification observation after every state-changing action (read back the resulting screen, not the intent).
4. Insert confirmation gates before any destructive/irreversible step and choose a sandbox (throwaway profile, test account, isolated VM/container).

### Audit a Planned Action Sequence
1. Express the plan as a JSON/text list of actions (`type`, `target`, optional `text`, `verified`, `confirmed`).
2. Run `action_safety_linter.py --file plan.json` to flag risky verbs, unverified state changes, ungated destructive actions, and dialog-triggering patterns.
3. Resolve each finding — add verification steps, add confirmation gates, replace blocking-dialog flows.
4. Re-run until clean, then dry-run in the sandbox before any real target.

## Scope & Limitations

**In Scope:**
- Deciding between computer use and a structured API, SDK, CLI or MCP tool with `tool_choice_advisor.py`, based on API availability, GUI stability, volume and reversibility
- Linting a planned action list with `action_safety_linter.py` for destructive verbs, state changes with no verification, destructive steps with no confirmation gate, and patterns that open blocking dialogs
- Design patterns for the screenshot, reason and act loop: grounding each action in a fresh screenshot, verifying after each step and recovering from misclicks
- Safety guardrails, sandboxing choices and an evaluation approach from the computer-use patterns reference

**Out of Scope:**
- Running a computer-use agent, taking screenshots or controlling a desktop or browser
- Scripted browser automation and scraping with selectors (see `engineering/browser-automation/`)
- Building the MCP server or API that would replace a GUI flow (see `engineering/mcp-server-builder/`)
- Regression-testing an agent from recorded runs (see `engineering/agent-harness/`)

**Important Caveats:**
- The linter matches action types, target labels and typed text against fixed word lists and patterns. It cannot tell what a click does in a real interface, so an innocuous label on a destructive control will pass.
- The advisor applies fixed rules to a few coarse inputs. Its output is a starting recommendation, not a measured comparison.
- The skill is model-agnostic and names no vendor tool. Computer-use model support, action types and pricing change often and need checking against current provider documentation.
- A clean lint does not make an agent safe to run against production accounts. Dry-run in a sandbox first.

## Reference Documentation

- [Computer Use Patterns](references/computer-use-patterns.md) - The action loop; computer-use vs structured-tool decision matrix; reliability patterns (grounding, verification, recovery); safety guardrails (confirmation gates, sandboxing, blocking dialogs); evaluation approach; and common failure modes.

## Anti-Patterns

### Pixels when an API exists
**Mistake:** Driving a SaaS dashboard by screenshot when the product has a documented API.
**Why it happens:** Computer use demos well and needs no integration work up front.
**Instead:** Run `tool_choice_advisor.py` first. An API call is cheaper, faster and verifiable; reserve the GUI loop for targets with no programmatic surface.

### Acting on a stale screen
**Mistake:** Clicking coordinates taken from a screenshot several steps ago.
**Why it happens:** Re-capturing feels redundant when nothing seems to have changed.
**Instead:** Take a fresh screenshot before each action and target what is visible now. Layouts shift after every load, toast and modal.

### Trusting intent instead of result
**Mistake:** Marking a payment or send step done because the click was issued.
**Why it happens:** The agent's plan says the click happens, so the outcome is assumed.
**Instead:** Read the resulting screen (confirmation banner, new row, changed status) before moving on, and gate irreversible steps behind a human approval.

## Files

- `scripts/tool_choice_advisor.py`, `scripts/action_safety_linter.py` — the two CLIs above.
- `assets/sample_plan_safe.json` (clean plan) and `assets/sample_plan_risky.json` (destructive command, payment field, ungated delete).
- `references/computer-use-patterns.md` — action loop, decision matrix, reliability and safety patterns, evaluation.

## Common Patterns

### Ground Every Action in the Current Screenshot
- Never act on a stale screenshot or a remembered layout — re-capture before each action.
- Reference elements by what is visible now (label, position) rather than a cached coordinate from a prior turn.
- After acting, take a fresh screenshot and confirm the expected change actually happened before continuing.

### Gate Destructive Actions and Sandbox by Default
- Require an explicit confirmation step before delete, send, pay, submit, or any irreversible action.
- Run in a sandbox first: throwaway browser profile, test account, or isolated VM/container.
- Avoid flows that spawn blocking modal/native dialogs (file pickers, OS print dialogs) that the agent cannot see or dismiss; prefer paths that keep state on the page.

### Prefer the Real Interface When It Exists
- A documented API, SDK, CLI, or MCP tool is more reliable, cheaper, and more verifiable than pixels — use it.
- Reserve computer-use for genuinely GUI-only targets, one-off tasks, or bridging gaps an API does not cover.
- For high-volume or business-critical flows, the cost of computer-use flakiness usually justifies building or requesting an API.
