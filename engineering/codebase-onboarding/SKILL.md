---
name: codebase-onboarding
description: >
  Analyze a codebase and generate onboarding docs: architecture overviews, file maps, setup
  guides, runbooks, and debugging guides. Use when onboarding new team members, open-sourcing,
  or documenting after a major refactor.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: developer-experience
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: markdown, notion, confluence
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

Before generating the docs, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target codebase path** — which project to analyze (the input all three scripts scan)
- [ ] **Audience** — junior developer, senior engineer, or contractor (tailors which sections appear and at what depth)
- [ ] **Output format** — Markdown, Notion, or Confluence (sets the generated document format)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `architecture_mapper.py` | Analyze project structure and generate a high-level architecture map | `python scripts/architecture_mapper.py /path/to/project --json` |
| `onboarding_generator.py` | Scan a project directory and generate an onboarding guide | `python scripts/onboarding_generator.py /path/to/project --json` |
| `setup_validator.py` | Validate a project's development setup completeness | `python scripts/setup_validator.py /path/to/project --json` |

All tools accept an optional `directory` argument (default: current directory) and `--json` for machine-readable output.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/fact-gathering-and-patterns.md](references/fact-gathering-and-patterns.md)** — the Phase 1 fact-gathering shell commands and the Phase 2 architecture-pattern classification table. Read when analyzing a codebase before writing docs.
- **[references/documentation-templates.md](references/documentation-templates.md)** — the architecture overview, key file map, local setup, and debugging guide templates plus audience-specific (junior/senior/contractor) additions. Read when generating the actual onboarding documents.
- **[references/quality-and-best-practices.md](references/quality-and-best-practices.md)** — quality verification checklist, common pitfalls, best practices, a troubleshooting matrix, and success criteria. Read before shipping onboarding docs.

## Scope & Limitations

**This skill covers:**
- Generating architecture overviews, key file maps, setup guides, task runbooks, and debugging guides from codebase analysis
- Audience-aware documentation tailored for junior developers, senior engineers, and contractors
- Output in Markdown, Notion, and Confluence formats
- Quality verification checklists and freshness audit processes

**This skill does NOT cover:**
- Automated API reference generation from code annotations — see `engineering/changelog-generator` for release-oriented docs or `engineering/api-design-reviewer` for API quality
- Continuous documentation pipelines or CI-triggered doc builds — see `engineering/ci-cd-pipeline-builder` for pipeline automation
- Security-focused documentation such as threat models or access control matrices — see `engineering/skill-security-auditor` for security auditing
- Runbook generation for incident response and production operations — see `engineering/runbook-generator` for operational runbooks

## Integration Points

| Skill | Integration | Data Flow |
|-------|------------|-----------|
| `engineering/runbook-generator` | Onboarding task runbooks can seed operational runbooks for production incident response | Onboarding runbook templates → Runbook Generator for ops-grade expansion |
| `engineering/api-design-reviewer` | API route analysis from Phase 1 feeds into API design quality reviews | Discovered API endpoints → API Design Reviewer for consistency checks |
| `engineering/database-schema-designer` | Database schema files identified during key file mapping inform schema design reviews | Schema file paths and ORM type → Schema Designer for migration planning |
| `engineering/tech-debt-tracker` | Technical debt items surfaced during architecture analysis should be logged for tracking | Architecture analysis findings → Tech Debt Tracker backlog entries |
| `engineering/ci-cd-pipeline-builder` | CI/CD config discovered in Phase 1 can be validated and improved by the pipeline builder | CI config paths and workflow list → Pipeline Builder for optimization |
| `engineering/dependency-auditor` | Dependency counts and lockfiles gathered in Phase 1 feed directly into security and license audits | Package manifests and lockfiles → Dependency Auditor for vulnerability scanning |
