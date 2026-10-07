---
name: security-audit
description: >
  Multi-agent source security audit with a coverage ledger, independently
  verified findings, and machine-checked records. Use when asked to audit a
  codebase, find vulnerabilities, or run a source-level pen test.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: application-security
  updated: 2026-10-07
  tags: [security-audit, vulnerability-research, multi-agent, code-review, appsec]
---

# Security Audit

A single pass over a codebase finds the bugs that pass happened to look at and
reports them with whatever confidence the reader had that day. This skill
replaces that with a process: a lead agent maps the target, writes down exactly
what will be examined, sends isolated hunters at each piece, has a different
agent try to disprove every claim, and only then writes a report — from records
that two validators have checked.

The output is a set of findings in three honest states: **confirmed** (traced
through source and reproduced locally), **needs validation** (a specific
hypothesis blocked on one named fact), and **rejected** (disproved, kept so it
is not raised again).

**Scope boundary.** This is a defensive, source-first audit of a repository. It
does **not** send traffic to deployed systems — that needs an engagement plan
from `red-team`. It does **not** produce a STRIDE threat model or scan for
secrets as its main job — that is `senior-security`. It does **not** query live
cloud accounts — that is `cloud-security`. It does **not** list dependency CVEs
— that is `dependency-auditor`. What lives here is finding, verifying, and
documenting boundary failures in the code itself.

## When to use this skill

- A request for a security audit, a vulnerability hunt, or a source-level pen test of a repository or one of its directories
- A release, acquisition, or customer review needs findings that stand up to scrutiny
- A previous audit produced a long list nobody trusts, and the real ones must be separated out
- A security-relevant change needs a scoped review of one subsystem or one diff
- A repeat audit should target what the last one deferred, blocked, or left out

## Two modes

- **Guidance mode** — a security question, a focused review of one file or
  finding, or triage. Use the relevant reference, answer in the conversation,
  create no files and no run directory.
- **Full audit mode** — the user explicitly wants the repository audited or
  pen-tested, or wants report files. Run all six phases.

If the request could be either, ask which before creating anything.

## Clarify First

Before a full audit, confirm these. Ask — do not assume:

- [ ] **Breadth tier** — decides which attack-class files are in play, and therefore cost and coverage. Offer all three:

  | Tier | Covers | Fits |
  |---|---|---|
  | `core` | The 9 core classes only | A first look, a small service, a tight budget |
  | `focused` | Core + web/auth, AI/LLM, supply chain, cloud | Most web and API products; the default |
  | `full` | Core + all 10 companions | High-stakes targets, native code, multi-tenant platforms, device apps |

- [ ] **Target and scope** — the repository root, and whether to audit all of it, named paths, or a diff between two refs
- [ ] **Output location** — a directory outside the target (default `~/security-audits/<repo>/run-<N>`)
- [ ] **Profile and budget** — `quick`, `standard`, or `deep`, and any cap on agent invocations

Stop rule: always ask the tier; ask the others only if the request leaves them
open. If the user says "just run it", use `focused`, `standard`, whole
repository, default output, no budget cap — and state those choices at the top
of the report.

A tier limits which companions are eligible. A boundary whose companion is
outside the tier is recorded as an `out_of_scope` unit and named in the report.
It is never silently skipped, and never counted as covered.

## Execution safety

These rules hold in both modes and are not negotiable by profile or budget.

- Reading source is always allowed. **Running target code** — builds, tests,
  fixtures, fuzzers, browsers, emulators — is allowed only inside an
  OS-enforced sandbox with no external network, an environment built from an
  explicit allowlist, a read-only target, writes confined to the agent's
  `scratch/`, and CPU, memory, process, file-size, disk, and time limits.
- If any of those controls is unavailable, nothing is executed. The lead is
  recorded as `needs_validation` with the missing control as its blocker.
- No deployed endpoints, external services, real accounts, real credentials,
  production data, shared queues, registries, or paid APIs. No dependency
  installation. No stress or volume testing.
- A local check stops at the first result that settles the question.
- The audit never edits the target repository. It describes fixes.
- Sandbox output is target-controlled. Only `promote_evidence.py` moves a file
  from `scratch/` to `evidence/`.

## The six phases

| # | Phase | Who | Output | Reference |
|---|---|---|---|---|
| 1 | Reconnaissance | 4 read-only scouts, then the lead | `architecture.md`, seeded `coverage-ledger.json` | `references/reconnaissance.md` |
| 2 | Coverage-led hunting | Hunters per unit, a critic per wave | Updated ledger, candidates | `references/hunting.md`, attack-class files |
| 3 | Candidate validation | One fresh verifier per candidate | A decided record per fingerprint | `references/validation-and-reporting.md` |
| 4 | Structured output | The lead | `findings.json`, both validators pass | same |
| 5 | Record verification | One fresh reader per record | Verified or independently re-checked records | same |
| 6 | Reporting | The lead | `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md` | same, `assets/report_template.md` |

Three rules of independence hold the process together: the lead is the only
writer of shared files; no agent validates a candidate it hunted; and no agent
sees another verifier's conclusion.

A run ends in exactly one of two states: every Phase 6 file is written and both
validators pass, or `run_status` is `incomplete` with the exact reason and the
gap is stated in the report's first paragraph.

## Workflows

### Workflow 1 — Full audit

1. Ask the tier, then create the run with `init`.
2. Launch the four scouts, write `architecture.md`, and seed the ledger — every
   unit ID derived with `coverage-id`. Validate the ledger.
3. Assign hunters wave by wave from `planned` units; update and re-validate the
   ledger after each result; run the coverage critic after each wave.
4. Promote any local-check output with `promote_evidence.py` before citing it.
5. Give each candidate to a fresh verifier, write `findings.json`, and run both
   validators.
6. Give each retained record to a fresh reader; re-validate after any change.
7. Pass the `--final` gate, paste the `summary` tables, and write the reports.

```bash
# 1. Create the run outside the target (asks nothing; pass what the user chose)
python3 engineering/security-audit/scripts/audit_run.py init \
  --target ~/code/app --tier focused --profile standard

# 2. After seeding units from reconnaissance, and after every ledger edit
python3 engineering/security-audit/scripts/validate_coverage_ledger.py \
  <run-dir>/coverage-ledger.json --metadata <run-dir>/run-metadata.json

# 3. After a hunter or verifier ran a local check
python3 engineering/security-audit/scripts/promote_evidence.py \
  --run-dir <run-dir> --agent-id hunter-03 --file result.txt

# 4. After writing findings.json, and after every replacement
python3 engineering/security-audit/scripts/validate_findings.py <run-dir>/findings.json

# 5. Final gate, then the coverage tables for REPORT.md
python3 engineering/security-audit/scripts/validate_coverage_ledger.py \
  <run-dir>/coverage-ledger.json --metadata <run-dir>/run-metadata.json \
  --findings <run-dir>/findings.json --run-dir <run-dir> --final
python3 engineering/security-audit/scripts/audit_run.py summary --run-dir <run-dir>
```

### Workflow 2 — Scoped or budgeted audit

```bash
python3 engineering/security-audit/scripts/audit_run.py init \
  --target ~/code/app --tier core --profile quick \
  --scope services/billing --budget 14

python3 engineering/security-audit/scripts/audit_run.py budget \
  --budget 14 --profile quick --units 9
```

`init` refuses a budget that cannot pay for reconnaissance, the critic, and one
verifier. `budget` reserves those first and reports how many units must be
`deferred`. A scoped, `quick`, or budget-limited run presents itself as a
partial pass.

### Workflow 3 — Repeat audit

Run `init` again on the same target. It lists prior runs; follow "Using prior
runs" in `references/reconnaissance.md` to carry unchanged confirmed records to
a fresh verifier, reopen every deferred, blocked, and out-of-scope unit, and
revalidate anything whose source changed. Repeat runs are how coverage grows —
plan for at least two on anything that matters.

## Decision frameworks

### Choosing a profile

| Profile | Units | Hunting loop | Review per candidate | Use when |
|---|---|---|---|---|
| `quick` | One per surface × boundary × class | One wave, one critic | One fresh verifier | [RECOMMENDED] Small targets, re-runs, a first look |
| `standard` | Split by subsystem | Waves until two critics are clean | Validator, then a separate record reader | [PROVEN] The default |
| `deep` | Split by subsystem and lifecycle mode | As standard, plus a second pass over re-checked units | As standard | [RECOMMENDED] High stakes or large targets |

Profiles change breadth and redundancy. They never lower the evidence bar.

### Severity calibration

| Severity | Anchor |
|---|---|
| **Critical** | Anyone on the network, with no account, can run code, read or rewrite the whole data store, or take over any user they choose |
| **High** | A named control is completely bypassed and it matters: signing in without credentials, one tenant reading or changing another's data, script planted for other users to run, a logged-in user running code, an anonymous request that halts a service others depend on |
| **Medium** | The boundary is genuinely crossed, but reach is small, the setup is unusual, or only a few resources are exposed |
| **Low** | Internal detail that is not secret leaks, or the attacker works hard for very little |
| **Informational** | True but nearly harmless alone; worth recording because another finding builds on it |

Only `confirmed` records get a severity, and `overall` cannot exceed the impact
that was demonstrated. A rating you cannot back with a one-sentence description
of the harm is too high.

### Confirmed, or needs validation?

| Situation | Verdict |
|---|---|
| Full trace in source and a bounded local result observed | `confirmed` |
| Full trace, but the result depends on a proxy, provider, or policy not in the repository | `needs_validation`, blocker named |
| Full trace, but no sandbox to run the check | `needs_validation`, missing control named |
| A layer visible in source prevents it | `rejected` |
| Good practice missing, nobody harmed | Hardening note — not a record |

## Anti-Patterns

### The checklist finding
**Mistake:** Reporting "missing rate limiting" or "cookie lacks a flag" as a vulnerability.
**Why it happens:** Deviations from a list are quick to spot and look like output.
**Instead:** Require an actor, a boundary, and a result. No victim means a hardening note.

### Grading your own homework
**Mistake:** The agent that found a candidate also confirms it, or a verifier is shown the previous verdict.
**Why it happens:** It saves an agent, and the finder already has the context loaded.
**Instead:** Every candidate goes to an agent that did not hunt it and is told to refute it. Refutation is the step that removes false positives; skipping it moves that work to whoever reads the report.

### Guessing the deployment
**Mistake:** "The load balancer probably strips that header" — or probably does not — decides the verdict.
**Why it happens:** The repository ends where the infrastructure begins, and a confident sentence reads better than an open question.
**Instead:** Record `needs_validation` with the exact fact and a check the owner can make in their own environment.

### Coverage by assertion
**Mistake:** The report says "authentication and authorization were reviewed" with no record of which paths.
**Why it happens:** Agents ran, tokens were spent, and it feels covered.
**Instead:** The ledger is the claim. A unit closes only with reviewed paths and checks; everything unreached is `deferred` or `out_of_scope` with a reason, and the report lists them.

### Severity by bug class
**Mistake:** Rating a finding high because it is called injection, or parking a guess as "low confidence, critical".
**Why it happens:** Class names carry reputations, and an alarming rating gets attention.
**Instead:** Rate what the reproduction showed. The findings validator rejects an overall severity above demonstrated impact, and a high or critical record held with low confidence.

### One run and done
**Mistake:** Treating a single clean pass as proof the code is sound.
**Why it happens:** The report looks finished.
**Instead:** Say what the run did not cover, and schedule a repeat run that starts from those gaps.

## Files

| File | Purpose |
|------|---------|
| `scripts/audit_run.py` | `init` a run directory outside the target; derive `coverage-id`s; split a `budget`; print the `summary` tables for the report |
| `scripts/validate_coverage_ledger.py` | Validates the ledger: derived IDs, order, state table, owned evidence, resolvable blocks, tier confinement, findings cross-links, `--final` gate |
| `scripts/validate_findings.py` | Validates `findings.json` against the schema plus ordering, path safety, trace shape, and severity rules |
| `scripts/promote_evidence.py` | The only path from `scratch/` to `evidence/`: no-follow, single-link regular files within byte limits, exclusive create |
| `scripts/ledger_rules.py` | Unit state table, evidence rules, and reopened-attempt rules behind the ledger validator; run it to print the table |
| `scripts/audit_common.py` | Shared vocabularies, tier definitions, ID and path rules; run it to print the contracts |
| `references/reconnaissance.md` | Phase 1: scout prompts, prior-run handling, architecture summary, ledger seeding, unit states |
| `references/hunting.md` | Phase 2: assignment order, hunter prompt, candidate gate, result format, coverage critic, stop rules |
| `references/validation-and-reporting.md` | Phases 3–6: verifier prompt, record fields, material replacements, report contents |
| `references/attack-classes.md` | The 9 core classes and the companion routing table |
| `references/web-protocol-and-auth.md` | Focused tier: HTTP framing, caches, sessions, tokens, OAuth/OIDC, SAML, MFA, passkeys, API keys, mTLS |
| `references/ai-and-llm.md` | Focused tier: indirect injection, memory, tool calls, approvals, MCP, output handling |
| `references/supply-chain-and-release.md` | Focused tier: dependency sources, CI workflows, artifacts, signing, updates, plugins |
| `references/cloud-and-deployment.md` | Focused tier: workload identity, exposure, containers, config precedence, secrets, storage, events |
| `references/client-side.md` | Full tier: DOM sinks, messaging, CORS, service workers, storage, state leaks, framing |
| `references/data-isolation-and-lifecycle.md` | Full tier: tenant scope, derived copies, export and restore, deletion, retention |
| `references/desktop-mobile-and-local-ipc.md` | Full tier: deep links, web-view bridges, local IPC, privileged helpers, device lifecycle |
| `references/memory-safety-and-binary.md` | Full tier: bounds, integers, lifetimes, FFI, loaders, JIT, kernel interfaces |
| `references/protocols-rpc-and-messaging.md` | Full tier: wire formats, RPC identity, brokers, replay and ordering |
| `references/resource-exhaustion-and-availability.md` | Full tier: amplification, accumulation, quotas, starvation, recovery |
| `assets/findings.schema.json` | JSON Schema for the three record verdicts |
| `assets/sample_findings.json` | One record of each verdict; passes the validator |
| `assets/sample_coverage_ledger.json` | Units in each state, including a reopened attempt; passes the validator |
| `assets/sample_run_metadata.json` | Run metadata as `init` writes it |
| `assets/report_template.md` | Layout for `REPORT.md` |
