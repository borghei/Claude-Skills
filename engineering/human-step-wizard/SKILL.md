---
name: human-step-wizard
description: >
  Generate an interactive, resumable bash wizard that walks a person through
  steps only a human can do. Use when a task needs dashboard credentials, DNS or
  change approval, key rotation, or a manual traffic cutover.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: developer-tooling
  updated: 2026-11-08
  tags: [wizard, bash, human-in-the-loop, credentials, cutover, runbook-automation]
---

# Human Step Wizard

Some steps in an otherwise automated task need a person: creating a token in a
dashboard, approving a DNS change, rotating a key the agent must never see,
cutting traffic over at a moment someone chose. The usual hand-off is a
paragraph of instructions in chat, which the human skims, half-follows, and
reports back on from memory. This skill replaces that paragraph with a
**generated bash wizard**: one step at a time, the exact link to open, hidden
prompts for secrets, format validation on every pasted value, checks that
confirm the step really happened, a typed confirmation before anything
irreversible, and progress saved so the human can stop and resume.

The agent writes a small JSON spec; the tools validate it and generate the
script. This is distinct from `engineering/runbook-generator`, which produces
static operational documentation. A wizard is executable, interactive and
tied to one concrete task.

## When to use this skill

- **Credentials only a human can create**: first admin token, OAuth app, API
  keys behind MFA, values the agent must not see
- **Approvals and authority**: DNS changes, change tickets, spending, accepting terms
- **Rotations**: roll a secret, deploy it, verify, revoke the old one
- **Cutovers**: DNS, load balancer, database primary, feature launch at a chosen time
- **Onboarding setup**: a new developer wiring up a dozen third-party accounts
  into `.env` and CI secrets

Not for steps the agent can perform itself; do those directly.

## Clarify First

The procedure, not the script, is the hard part, and its details live with the
human. Settle the inputs below before writing the spec. When one is missing or
vague and would change the result, ask about it; when it wouldn't, use a
sensible default and say which one you used.

- **The step list and which step is irreversible:** this sets the order (gather
  and verify everything before the point of no return) and where the typed
  confirmation goes.
- **Where each value goes:** env file, CI secret, both, or nowhere. Values a
  later check or the application needs must be stored, and secrets must not be
  stored more widely than they are used.
- **Exact dashboard paths:** if the agent is not sure of the current UI, it asks
  or links the page instead of inventing menu names.
- **How to verify each step from outside:** a `dig`, `curl`, `gh` or `test`
  command that proves the outcome; without it, the wizard trusts the Enter key.

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, generate from what you
know and state your assumptions at the top of your reply.

## Quick Start

```bash
# 1. Validate the spec (exit 1 on errors)
python3 engineering/human-step-wizard/scripts/wizard_spec_validate.py \
  --spec engineering/human-step-wizard/assets/sample_wizard_spec.json

# 2. Generate the wizard (runs bash -n on the output)
python3 engineering/human-step-wizard/scripts/wizard_generate.py \
  --spec engineering/human-step-wizard/assets/sample_wizard_spec.json --out scripts/cutover-wizard.sh

# 3. Hand it to the human
./scripts/cutover-wizard.sh          # --list, --from STEP, --reset, --help
```

## Tools Overview

| Tool | Purpose | Exit codes |
|------|---------|------------|
| `scripts/wizard_spec_validate.py` | Check ids, names, reserved variables, POSIX-ERE patterns, use-before-capture in checks, unquoted expansions, `eval`/`source`, irreversible steps without rollback or checks, unused secrets | `0` valid, `1` errors (or warnings with `--strict`), `2` unreadable or invalid JSON |
| `scripts/wizard_generate.py` | Validate, then emit one self-contained bash script: header, runtime, one function per step. Every spec string is single-quoted; output is `bash -n` checked | `0` written and syntax-checked, `1` spec errors or failed `bash -n`, `2` usage or I/O error |
| `assets/wizard_runtime.sh` | The runtime embedded in every wizard: prompts, hidden input, ERE validation, env-file upsert, checks with retry, irreversible confirmation, resume state, audit log | n/a (embedded) |

Both tools take `--format text|json`. The generator also takes `--stdout` to
print the script and `--force` to overwrite an existing file.

### Generated wizard behaviour

| Feature | Behaviour |
|---------|-----------|
| Progress | `==== Step 3/6: title ====`; `--list` shows done/pending |
| Resume | Finished step ids in `.wizard-state/<slug>.done`; stored values reloaded on restart |
| Secrets | `read -s`, never echoed or logged; env file written with mode 0600 |
| Validation | Anchored ERE per input, 3 attempts, then abort with progress kept |
| Checks | Spec commands run with captured values exported; failure offers retry/abort (and skip if allowed) |
| Irreversible | Rollback shown first; the human must type the step id |
| Safety | `set -euo pipefail`; refuses to run without a TTY unless `WIZARD_ALLOW_NONINTERACTIVE=1` |

## Workflows

### Workflow 1: Hand a human step to a person [RECOMMENDED]

1. Do every step the agent can do first. Collect what remains and confirm the
   list, order and irreversible step with the user.
2. For each human step, write the navigation path, the value(s) produced, where
   each value goes, and a command that proves the step happened.
3. Write the spec (start from `assets/sample_wizard_spec.json`).
4. Validate with `--strict`; fix every error and justify every remaining warning.
5. Generate the script. Add the env file to `.gitignore`.
6. Tell the human the command, the time it takes, any waiting periods, and which
   step is irreversible. Wait for them; do not run it yourself.

```bash
python3 engineering/human-step-wizard/scripts/wizard_spec_validate.py \
  --spec engineering/human-step-wizard/assets/sample_wizard_spec.json --strict --format json
python3 engineering/human-step-wizard/scripts/wizard_generate.py \
  --spec engineering/human-step-wizard/assets/sample_wizard_spec.json --stdout > /tmp/wizard.sh
bash -n /tmp/wizard.sh && echo syntax-ok
```

### Workflow 2: Verify a wizard before hand-off

The agent cannot complete the wizard (it blocks on human input), so it validates
the script statically and with a scripted run in a scratch directory:

1. `bash -n` (the generator already did) and `shellcheck -S warning` if installed.
2. Copy the spec, replace network checks with local ones (`test -n "$VAR"`),
   generate, and pipe answers in, including a hostile value such as
   `$(touch PWNED)`.
3. Verify that the env file holds the literal values, that no `PWNED` file
   appeared, that `--list` shows the right progress after an abort, and that a
   re-run resumes at the right step.

```bash
printf '%s\n' 'first-answer' 'abc' 'step-id' '' | \
  WIZARD_ALLOW_NONINTERACTIVE=1 WIZARD_STATE_DIR=./state bash wizard.sh
```

### Workflow 3: Fix a rejected spec

```bash
python3 engineering/human-step-wizard/scripts/wizard_spec_validate.py \
  --spec engineering/human-step-wizard/assets/sample_wizard_spec_flawed.json
```

The flawed sample fails on purpose (exit 1) with eight errors: a non-slug
`slug`, a lowercase variable name, `eval` in a check, a value used before it is
captured, a duplicate step id, an irreversible step without rollback, a `\d`
pattern bash cannot match, and an input named `PATH`. Fix in that order:
naming errors first, because later rules depend on names resolving.

## Spec Format

```json
{
  "title": "Move api.example.com to the new load balancer",
  "slug": "api-lb-cutover",
  "env_file": ".env.cutover",
  "steps": [
    {
      "id": "cutover-dns",
      "title": "Point api.example.com at the new load balancer",
      "instructions": ["DNS -> Records -> api.example.com (A) -> Edit.", "Set the new address and save."],
      "url": "https://dash.dns-provider.example/example.com/dns/records",
      "inputs": [{"name": "NEW_LB_IP", "prompt": "New IPv4", "pattern": "^([0-9]{1,3}\\.){3}[0-9]{1,3}$", "store": "env"}],
      "checks": [{"description": "DNS returns the new address", "command": "dig +short api.example.com A | grep -qxF \"$NEW_LB_IP\""}],
      "irreversible": true,
      "rollback": "Set the A record back to OLD_LB_IP from .env.cutover; 60 s TTL.",
      "pause": true,
      "allow_skip": false
    }
  ]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `title`, `slug` | yes | Slug names the state files; lowercase and dashes |
| `env_file` | no (`.env`) | Relative path; captured `store: env` values go here, mode 0600 |
| `steps[].id`, `title`, `instructions` | yes | Id is the resume key: do not rename after first use |
| `url` | no | Printed; opened only with `WIZARD_OPEN_URLS=1` |
| `inputs[]` | no | `name` UPPER_SNAKE, `prompt`, `secret`, `pattern` (anchored ERE), `store` env/none |
| `checks[]` | no | `description`, `command` (fixed shell text; quote `"$VARS"`) |
| `irreversible` + `rollback` | no | Typed confirmation and rollback shown before instructions |
| `pause` | no | Defaults to true when a step has no inputs |
| `allow_skip` | no | Lets the human skip a failing check (logged) |

## Anti-Patterns

### The Chat Runbook
**Mistake:** Pasting ten numbered steps into the chat and asking the human to "let me know when done".
**Why it happens:** It is the fastest thing for the agent to produce.
**Instead:** Generate a wizard. The human sees one step at a time, values are captured and validated where they are produced, and the agent gets a verifiable result instead of "done, I think".

### The Trust-the-Enter-Key Wizard
**Mistake:** Steps with a pause and no check, so pressing Enter marks them done.
**Why it happens:** Writing a check means knowing how to observe the outcome, which takes thought.
**Instead:** Attach a check that observes the world from outside (`dig`, `curl`, `gh secret list`, `test -s`). The validator warns on irreversible steps without one.

### The Late Rollback Data
**Mistake:** Asking the human to change the DNS record without first capturing the old address.
**Why it happens:** Rollback feels like a separate concern from the forward path.
**Instead:** Capture rollback inputs in an earlier step and store them, so the rollback text can point at a saved value.

### The PCRE Pattern
**Mistake:** Validating with `^\d+$` or `(?:...)`, copied from a Python or JavaScript regex.
**Why it happens:** Most regex knowledge is PCRE; bash's `[[ =~ ]]` silently uses POSIX ERE.
**Instead:** Use `[0-9]`, `[A-Za-z0-9_]`, `[[:space:]]`, plain groups. The validator rejects PCRE-only syntax because the human would be told their correct value is wrong.

### The Sourced Env File
**Mistake:** Hand-editing the generated script to `source .env` or `eval` a captured value.
**Why it happens:** It is the shortest way to load variables.
**Instead:** Regenerate from the spec. The runtime parses the env file and assigns only declared names; a pasted `$(...)` stays text.

## Verification Checklist

- [ ] Spec validates with `--strict` (or each warning has a stated reason)
- [ ] Every value a later check or the application needs has `store: env`
- [ ] Every irreversible step has rollback text that names the saved old value
- [ ] Generated script passes `bash -n` (and `shellcheck -S warning` when available)
- [ ] Scripted run in a scratch dir: hostile input stays literal, resume works
- [ ] Env file path is gitignored; the human knows which step is irreversible

## Reference Documentation

| File | Contents |
|------|----------|
| `references/human-step-design.md` | What is human-only, cutting steps, writing instructions, input naming and ERE patterns, check catalog, irreversible steps, resumability, hand-off message |
| `references/bash-wizard-safety.md` | Threat model, the nine generator guarantees (strict mode, quoting, `printf -v`, ERE, env upsert without sed, parse-not-source, TTY guard, value-free logs, interrupts), pre-handoff verification, review checklist |

## Files

| File | Purpose |
|------|---------|
| `scripts/wizard_spec_validate.py` | Spec validator (gate) |
| `scripts/wizard_generate.py` | Spec to bash generator with built-in `bash -n` |
| `assets/wizard_runtime.sh` | Runtime library embedded in every generated wizard |
| `assets/sample_wizard_spec.json` | Six-step DNS cutover: scoped token, TTL, capture, smoke test, irreversible cutover, close-out |
| `assets/sample_wizard_spec_flawed.json` | Deliberately failing spec (exit 1, eight errors) |

## Scope & Limitations

**In Scope:**
- Interactive bash wizards for human-only steps, generated from a validated spec.
- Validation, resumable progress, hidden secret entry, env-file storage, outside-in checks.

**Out of Scope:**
- Static runbooks and on-call documentation.
- Performing the human steps or driving dashboards through a browser.
- Writing to CI secret stores directly; add a check such as `gh secret list` or
  an instruction line that tells the human which command to run.

**Important Caveats:**
- Requires bash 3.2+ (macOS default works) and a terminal. Windows needs WSL or Git Bash.
- Check commands are the spec author's code and run with the human's
  permissions; review them like any script.
- The env file holds secrets in plain text with mode 0600; keep it out of git
  and delete it when the task is finished.
