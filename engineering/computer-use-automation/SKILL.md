---
name: computer-use-automation
description: >
  This skill should be used when the user asks to "build a computer-use agent",
  "automate a GUI with an AI agent", "when to use computer use vs an API",
  "make browser automation reliable", or "design screenshot-driven agent actions".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  updated: 2026-06-29
  tags: [computer-use, browser-automation, agents, gui, reliability]
---

# Computer Use Automation

> **Category:** Engineering
> **Domain:** AI Agents

## Overview

The **Computer Use Automation** skill helps you design AI agents that operate a graphical interface the way a person does — take a screenshot, reason about what is on screen, then click, type, scroll, or navigate, and repeat. It covers the core perception→reason→action loop, the decision of when computer-use is the right tool versus a structured API/MCP tool (prefer a real API whenever one exists; reach for computer-use only for GUIs with no programmatic surface), reliability patterns (grounding every action in the *current* screenshot, verifying after each step, recovering from misclicks), safety guardrails (confirmation gates for destructive actions, sandboxing, avoiding blocking dialogs), and how to evaluate a computer-use agent. It is model-agnostic — the patterns apply to any computer-use-capable model and any GUI tool surface.

## Clarify First

Before designing or auditing a computer-use agent, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Does a real API/MCP tool exist?** — whether the target exposes an API, SDK, CLI, or MCP server, or is GUI-only (the single biggest factor; if a real API exists, prefer it and skip computer-use)
- [ ] **Task & risk** — what the agent must accomplish and whether any step is destructive or irreversible (delete, send, pay, submit), which sets the confirmation gates and sandboxing
- [ ] **Which tool** — advise on tool choice for a target, or lint a planned action sequence for safety (selects `tool_choice_advisor.py` vs `action_safety_linter.py`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Decide computer-use vs API/MCP for a target
python scripts/tool_choice_advisor.py --api-exists no --gui-stability high --volume low --json

# Lint a planned action sequence for safety/reliability gaps
python scripts/action_safety_linter.py --file planned_actions.json

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

## Workflows

### Decide and Design a Computer-Use Agent
1. Run `tool_choice_advisor.py` with the target's API/MCP availability, GUI stability, and volume — if it says "use API/MCP," stop and build against the real interface instead.
2. If computer-use is justified, draft the action plan as the screenshot→reason→action loop: each step re-grounds on a fresh screenshot before acting.
3. Add a verification observation after every state-changing action (read back the resulting screen, not the intent).
4. Insert confirmation gates before any destructive/irreversible step and choose a sandbox (throwaway profile, test account, isolated VM/container).

### Audit a Planned Action Sequence
1. Express the plan as a JSON/text list of actions (`type`, `target`, optional `verified`/`confirmed`).
2. Run `action_safety_linter.py --file plan.json` to flag risky verbs, unverified state changes, ungated destructive actions, and dialog-triggering patterns.
3. Resolve each finding — add verification steps, add confirmation gates, replace blocking-dialog flows.
4. Re-run until clean, then dry-run in the sandbox before any real target.

## Reference Documentation

- [Computer Use Patterns](references/computer-use-patterns.md) - The action loop; computer-use vs structured-tool decision matrix; reliability patterns (grounding, verification, recovery); safety guardrails (confirmation gates, sandboxing, blocking dialogs); evaluation approach; and common failure modes.

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
