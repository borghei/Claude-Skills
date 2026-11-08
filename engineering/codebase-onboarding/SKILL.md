---
name: codebase-onboarding
description: >
  Gathers facts about a codebase (stack, layers, entry points, setup gaps) and turns them into
  onboarding docs: architecture overview, file map, setup guide, debugging guide. Use when
  onboarding engineers or re-documenting after a refactor.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: developer-experience
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: markdown, notion, confluence
  tags:
    - onboarding
    - documentation
    - architecture
    - runbooks
    - developer-experience
---
# Codebase Onboarding

Analyze any codebase and generate production-quality onboarding documentation tailored to the audience. Produces architecture overviews with system diagrams, annotated key file maps, step-by-step local setup guides, common developer task runbooks, debugging guides with real error solutions, and contribution guidelines. Supports Markdown, Notion, and Confluence output formats.

## Core Capabilities

- **Architecture analysis** — tech stack identification from manifests/lockfiles, system boundary mapping, Mermaid data-flow diagrams, dependency graphs, module ownership.
- **Key file annotation** — surface the 20 most important files and why they matter; mark entry points, config hubs, shared utilities, and files dangerous to modify without coordination.
- **Setup guide generation** — prerequisites with exact versions, `git clone`-to-tests steps, env-var docs, infra setup (Docker/DB/cache), and a verification checklist.
- **Task runbooks** — add an API endpoint, run/write tests, create & apply migrations, deploy to staging/production, add a dependency safely.
- **Debugging guide** — common errors with exact messages and fixes, log locations by environment, diagnostic SQL/CLI queries, local reproduction of production issues.
- **Audience-aware output** — tailored additions for junior developers, senior engineers, and contractors; Markdown / Notion / Confluence formats.

**Keywords:** codebase onboarding, developer experience, documentation, architecture overview, setup guide, debugging guide, contribution guidelines, code walkthrough, new hire onboarding

## When to Use

- Onboarding a new team member (junior, senior, or contractor)
- After a major refactor that made existing docs stale
- Before open-sourcing a project
- Creating a team wiki page for a service you own
- Self-documenting before a long vacation or team transition
- Preparing for a compliance audit that requires documentation

## Clarify First

Before generating the docs, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target codebase path:** which project to analyze (the input all three scripts scan).
- **Audience:** junior developer, senior engineer, or contractor (tailors which sections appear and at what depth).
- **Where the docs live:** repo Markdown, Notion or Confluence (changes headings, links and how much goes in one page).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

The scripts gather facts. `onboarding_generator.py --format markdown` turns them into a draft guide:
sections the repo can answer (README summary, stack, declared run commands, env variables, entry
points, layout) are filled in, and everything it cannot know is a `> **TODO (owner):**` line. The
finished guide is yours: replace every TODO from reading the code and asking the owners, using the
templates in `references/documentation-templates.md`.

```bash
# 1. Facts report: stack, frameworks, entry points, key files, file-type spread
#    (manifests first; without one it counts source files by extension)
python scripts/onboarding_generator.py /path/to/project
#    Draft guide with TODO placeholders (sample: package.json scripts, .env keys, README summary)
python scripts/onboarding_generator.py assets/sample_project --format markdown > /tmp/ONBOARDING.md

# 2. Architecture patterns and layers by directory, with dependency hints
python scripts/architecture_mapper.py /path/to/project --json

# 3. Setup completeness: README, .env template, lockfile, CI, lint config, tests, licence; 0-100 score
python scripts/setup_validator.py /path/to/project
```

## Tools Overview

| Tool | Gives you | Use it for |
|------|-----------|------------|
| `onboarding_generator.py` | Stack, frameworks, entry points, key files, top-level dirs, package.json scripts, Makefile targets, env-template keys, README summary; `--format text\|json\|markdown` | The draft guide (`markdown`) and the key file map |
| `architecture_mapper.py` | Detected pattern (monorepo, microservices, MVC, layered) and per-directory layer roles | The architecture overview and its diagram |
| `setup_validator.py` | Pass/warn/fail on README, .env template, lockfile, CI, lint config, tests, CONTRIBUTING and LICENSE, with fixes and a health score | The setup guide, and the gaps to fix before the guide is honest |

All take a directory (default `.`) and `--json`. **Exit codes:** `0` report printed; `2` the
directory does not exist. A low setup score does not change the exit code.

For an ordered reading path through the code (stop-by-stop tour), use `engineering/code-tour`
instead; this skill produces the reference documents a newcomer keeps open.

**Done when:**
1. No `TODO (owner)` line is left in the guide.
2. A newcomer can go from clone to a passing local test run using only the setup guide (try it in a clean checkout or container).
3. Every path in the key file map exists, and every command in the docs ran as written.
4. The architecture overview names the real entry points and data stores, checked against the code, not only the scripts' heuristics.
5. Setup gaps that `setup_validator.py` reports are fixed or listed as known issues.

## Anti-Patterns

### Docs from heuristics alone
**Mistake:** Pasting the scripts' output as the onboarding guide.
**Why it happens:** It looks complete and took seconds.
**Instead:** Use the output as a checklist of facts to confirm, then read the entry points and write the guide in plain language.

### A setup guide nobody ran
**Mistake:** Setup steps written from memory, missing the one environment variable everyone already has.
**Why it happens:** The author's machine has been set up for years.
**Instead:** Follow the guide in a clean container or fresh checkout and fix every step that fails.

### Listing every file
**Mistake:** A key file map with two hundred entries.
**Why it happens:** Completeness feels safer than choosing.
**Instead:** List the ten to twenty files a newcomer touches in the first week, each with one line on why it matters.

## Files

- `scripts/onboarding_generator.py`, `scripts/architecture_mapper.py`, `scripts/setup_validator.py` — the three fact-gathering CLIs above.
- `assets/sample_project/` — small Node service (package.json scripts, `.env.example`, README) for the draft-guide demo.
- `references/` — fact-gathering commands and pattern table, document templates, quality checklist.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/fact-gathering-and-patterns.md](references/fact-gathering-and-patterns.md)** — the Phase 1 fact-gathering shell commands and the Phase 2 architecture-pattern classification table. Read when analyzing a codebase before writing docs.
- **[references/documentation-templates.md](references/documentation-templates.md)** — the architecture overview, key file map, local setup, and debugging guide templates plus audience-specific (junior/senior/contractor) additions. Read when generating the actual onboarding documents.
- **[references/quality-and-best-practices.md](references/quality-and-best-practices.md)** — quality verification checklist, common pitfalls, best practices, a troubleshooting matrix, and success criteria. Read before shipping onboarding docs.

## Scope & Limitations

**This skill covers:**
- Generating architecture overviews, key file maps, setup guides, task runbooks, and debugging guides from codebase analysis
- Audience-aware documentation tailored for junior developers, senior engineers, and contractors
- Markdown documents that paste cleanly into Notion or Confluence
- Quality verification checklists and freshness audit processes

**This skill does NOT cover:**
- Automated API reference generation from code annotations — see `engineering/changelog-generator` for release-oriented docs or `engineering/api-design-reviewer` for API quality
- Continuous documentation pipelines or CI-triggered doc builds — see `engineering/ci-cd-pipeline-builder` for pipeline automation
- Security-focused documentation such as threat models or access control matrices — see `engineering/skill-security-auditor` for security auditing
- Runbook generation for incident response and production operations — see `engineering/runbook-generator` for operational runbooks

## See Also

- `engineering/code-tour` — a guided, ordered walk through the code for a first read.
- `engineering/runbook-generator` — production runbooks beyond onboarding tasks.
- `engineering/ci-cd-pipeline-builder` — fix CI gaps that `setup_validator.py` reports.
