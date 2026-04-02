---
title: Customization
---

# Customizing Skills for Your Stack

Skills are designed to be customized. Here is how to adapt them to your specific technology stack, team conventions, and business context.

## Customization Levels

### Level 1: Context Injection (No Changes)

Pass your project context alongside the skill. The AI assistant adapts automatically.

```
Use engineering/senior-fullstack/SKILL.md to review this project.
Our stack: Next.js 14, Prisma, PostgreSQL, deployed on Vercel.
```

This is the simplest approach and works well for most use cases.

### Level 2: CLAUDE.md Configuration

Add stack-specific instructions to your `CLAUDE.md` that override skill defaults:

```markdown
## Stack Context
- Frontend: React 18 + TypeScript + Tailwind
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Testing: Pytest + Playwright
- Deployment: AWS ECS + Terraform

## Skill Overrides
When using senior-fullstack, prefer FastAPI patterns over Express.
When using senior-qa, generate Pytest tests (not Jest).
```

### Level 3: Fork and Edit

Copy a skill into your project and modify it:

```bash
cp -r engineering/senior-fullstack/ .claude/skills/fullstack/
# Edit .claude/skills/fullstack/SKILL.md with your conventions
```

Changes you might make:

- Add your team's specific coding standards
- Remove frameworks you don't use
- Add internal tool references
- Customize output formats

### Level 4: Compose New Skills

Combine parts of multiple skills into a custom skill:

```markdown
---
name: my-team-review
description: Custom code review combining security and quality checks
version: 1.0.0
---

# My Team Review Skill

## Workflow
1. Run code quality check (from code-reviewer)
2. Run security scan (from senior-security)
3. Check test coverage (from senior-qa)
4. Output unified report in our team format
```

## Customizing Python Tools

Tools accept arguments that adapt their behavior:

```bash
# Different output formats
python scripts/analyzer.py . --format json
python scripts/analyzer.py . --format text

# Filter by severity
python scripts/scanner.py . --min-severity high
```

To permanently change a tool's defaults, edit the script's `argparse` defaults or wrap it in a shell alias.

## Team-Wide Configuration

For consistent customization across a team:

1. Fork the Claude-Skills repository
2. Add a `team/` directory with your overrides
3. Update `CLAUDE.md` to reference your fork
4. Share via git submodule or internal package registry

!!! warning "Keep upstream compatibility"
    When customizing, try to extend rather than replace. This makes it easier to pull upstream updates without merge conflicts.
