---
title: Slash Commands
---

# Slash Commands

26 slash commands available in Claude Code for common workflows. These live in `.claude/commands/` and are invoked with the `/` prefix.

## Git Commands

| Command | Description |
|---|---|
| `/git:cm` | Stage working tree changes and create a Conventional Commit (no push) |
| `/git:cp` | Stage, commit, and push the current branch following git governance rules |
| `/git:pr` | Create a pull request from the current branch |

## Quality Gates

| Command | Description |
|---|---|
| `/review` | Run the local review gate before pushing -- checks code quality, linting, and tests |
| `/security-scan` | Run the security scan gate -- checks for vulnerabilities, secrets, and unsafe patterns |

## Product & Strategy

| Command | Description |
|---|---|
| `/prd` | Create a Product Requirements Document from scratch |
| `/code-to-prd` | Reverse-engineer a PRD from existing code |
| `/user-story` | Create well-structured user stories with acceptance criteria |
| `/rice` | RICE-score features or tasks for prioritization |
| `/okr` | Create or review OKRs (Objectives and Key Results) |
| `/competitive-matrix` | Build a competitive analysis matrix comparing products |
| `/saas-health` | Generate a SaaS health dashboard with key business metrics |
| `/financial-health` | Assess financial health of a SaaS business |

## Engineering & DevOps

| Command | Description |
|---|---|
| `/pipeline` | Design or review a CI/CD pipeline for the current project |
| `/tdd` | Guide a Test-Driven Development workflow for the current task |
| `/focused-fix` | Apply a focused, minimal-change bugfix with minimal blast radius |
| `/tech-debt` | Scan and prioritize technical debt in the codebase |
| `/project-health` | Assess overall project health across code quality, tests, docs, and activity |
| `/a11y-audit` | Run an accessibility audit for WCAG compliance |
| `/plugin-audit` | Audit installed plugins, extensions, and dependencies for security |
| `/seo-auditor` | Run an SEO audit on web content and HTML files |

## Sprint & Retrospectives

| Command | Description |
|---|---|
| `/sprint-plan` | Plan a sprint by analyzing backlog, estimating capacity, and selecting work |
| `/sprint-health` | Check current sprint health and identify risks |
| `/retro` | Run a sprint retrospective with data-driven insights from git history |
| `/changelog` | Generate a changelog from git history since the last tag or release |

## Cross-Domain

| Command | Description |
|---|---|
| `/persona` | Activate a cross-domain persona for the current session |

## Using Commands

In Claude Code, type `/` followed by the command name:

```
> /review
> /git:pr
> /sprint-health
```

Some commands accept arguments:

```
> /rice "Add dark mode" "Implement API rate limiting" "Build mobile app"
> /persona startup-cto
> /tdd Write tests for the auth module
```

!!! note "Claude Code only"
    Slash commands are a Claude Code feature. For other platforms, invoke the equivalent skill directly by referencing its SKILL.md path.
