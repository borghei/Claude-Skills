---
title: Standards
---

# Standards Library

The `standards/` directory contains best-practice standards used across all skills. These define quality bars for communication, code, documentation, and security.

## Available Standards

| Standard | File | Purpose |
|---|---|---|
| **Communication** | `standards/communication/` | Writing style, tone, clarity guidelines for all skill outputs |
| **Quality** | `standards/quality/` | Quality gates, review checklists, acceptance criteria |
| **Git Workflow** | `standards/git/git-workflow-standards.md` | Conventional commits, branch naming, PR templates |
| **Documentation** | `standards/documentation/` | Documentation structure, formatting, completeness criteria |
| **Security** | `standards/security/` | Security review standards, vulnerability classification |

## Git Workflow Standards

### Conventional Commits

All commits follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

feat(agents): implement cs-ceo-advisor
fix(tool): correct DCF calculation logic
docs(workflow): update branch strategy
chore(deps): update Python dependencies
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`

### Branch Strategy

```
feature/topic-name → dev → main (PR only)
```

- **Main:** Protected. Requires PR approval. No direct pushes.
- **Dev:** Integration branch. PRs recommended.
- **Feature:** Short-lived branches for individual tasks.

## Skill Quality Standards

Every skill must meet these criteria:

1. **Actionable** -- Workflows are step-by-step, not generic advice
2. **Measurable** -- Tools produce scored/quantified output
3. **Self-contained** -- No dependencies on other skills
4. **40% time savings** -- Each skill should save at least 40% time on the task
5. **30% quality improvement** -- Outputs should be 30%+ better than manual work

## Applying Standards

Standards are referenced automatically by agents and skills. You can also apply them directly:

```
Follow standards/git/git-workflow-standards.md for all commits in this session.
```

See the full standards files in the [standards/ directory](https://github.com/borghei/Claude-Skills/tree/main/standards).
