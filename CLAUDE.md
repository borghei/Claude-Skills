# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is the **universal AI skills library** — reusable, production-ready skill packages that bundle domain expertise, best practices, analysis tools, and strategic frameworks. Works with every major AI coding assistant: Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, and more.

**Current Scope:** 204 production-ready skills across 13 domains with 559 Python automation tools, 17 AI agents, and 12 sample CI/CD workflows.

**Key Distinction**: This is NOT a traditional application. It's a library of skill packages meant to be extracted and deployed by users into their AI coding workflows.

## Navigation Map

This repository uses **modular documentation**. For domain-specific guidance, see:

| Domain | CLAUDE.md Location | Focus |
|--------|-------------------|-------|
| **Agent Development** | [agents/CLAUDE.md](agents/CLAUDE.md) | cs-* agent creation, YAML frontmatter, relative paths |
| **Marketing Skills** | [marketing/CLAUDE.md](marketing/CLAUDE.md) | Content creation, SEO, demand gen, campaign analytics Python tools |
| **Product Team** | [product-team/CLAUDE.md](product-team/CLAUDE.md) | RICE, OKRs, user stories, UX research tools |
| **Engineering** | [engineering/CLAUDE.md](engineering/CLAUDE.md) | Scaffolding, fullstack, AI/ML, data tools |
| **C-Level Advisory** | [c-level-advisor/CLAUDE.md](c-level-advisor/CLAUDE.md) | CEO/CTO strategic decision-making |
| **Project Management** | [project-management/CLAUDE.md](project-management/CLAUDE.md) | 25 PM skills: discovery, execution, Atlassian MCP |
| **RA/QM Compliance** | [ra-qm-team/CLAUDE.md](ra-qm-team/CLAUDE.md) | 21 skills: ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2, DORA, NIST CSF, PCI-DSS, CCPA, ISO 42001, infrastructure auditing |
| **Business & Growth** | [business-growth/CLAUDE.md](business-growth/CLAUDE.md) | Customer success, sales engineering, revenue operations |
| **Finance** | [finance/CLAUDE.md](finance/CLAUDE.md) | Financial analysis, DCF valuation, budgeting, forecasting |
| **Data Analytics** | [data-analytics/CLAUDE.md](data-analytics/CLAUDE.md) | Data analysis, BI, ML ops, analytics engineering |
| **HR Operations** | [hr-operations/CLAUDE.md](hr-operations/CLAUDE.md) | Talent acquisition, people analytics, HR business partner |
| **Sales Success** | [sales-success/CLAUDE.md](sales-success/CLAUDE.md) | Account executive, sales ops, solutions architect |
| **Standards Library** | [standards/CLAUDE.md](standards/CLAUDE.md) | Communication, quality, git, security standards |
| **Templates** | [templates/CLAUDE.md](templates/CLAUDE.md) | Template system usage |

**Current Sprint:** See [documentation/delivery/sprint-11-05-2025/](documentation/delivery/sprint-11-05-2025/) for active sprint context and progress.

## Architecture Overview

### Repository Structure

```
claude-code-skills/
├── .claude/
│   ├── agents/                # 6 Claude Code subagents (code-reviewer, qa, docs, etc.)
│   └── commands/              # Slash commands (git:cm, git:cp, git:pr, review, security-scan)
├── .github/
│   └── copilot-instructions.md # GitHub Copilot config
├── agents/                    # cs-* prefixed skill agents
├── engineering/               # 61 engineering skills + 177 Python tools
├── marketing/           # 35 marketing skills + 106 Python tools
├── product-team/              # 8 product skills + 15 Python tools
├── project-management/        # 25 PM skills + 53 Python tools
├── c-level-advisor/           # 26 C-level advisory skills + 73 Python tools
├── ra-qm-team/                # 21 RA/QM compliance skills + 38 Python tools
├── business-growth/           # 17 business & growth skills + 48 Python tools
├── data-analytics/            # 5 data analytics skills + 16 Python tools
├── hr-operations/             # 4 HR operations skills + 12 Python tools
├── sales-success/             # 5 sales success skills + 15 Python tools
├── finance/                   # 1 finance skill + 4 Python tools
├── standards/                 # 5 standards library files
├── templates/                 # Reusable templates + 12 sample GitHub workflows
├── documentation/             # Implementation plans, sprints, delivery
├── AGENTS.md                  # Universal agent config (Codex, Aider, Jules, etc.)
├── .cursorrules               # Cursor AI config
├── .windsurfrules             # Windsurf config
├── .clinerules                # Cline config
└── .goosehints                # Goose config
```

### Skill Package Pattern

Each skill follows this structure:
```
skill-name/
├── SKILL.md              # Master documentation
├── scripts/              # Python CLI tools (no ML/LLM calls)
├── references/           # Expert knowledge bases
└── assets/               # User templates
```

**Design Philosophy**: Skills are self-contained packages. Each includes executable tools (Python scripts), knowledge bases (markdown references), and user-facing templates. Teams can extract a skill folder and use it immediately.

**Key Pattern**: Knowledge flows from `references/` → into `SKILL.md` workflows → executed via `scripts/` → applied using `assets/` templates.

## Git Workflow

**Branch Strategy:** feature → dev → main (PR only)

**Branch Protection Active:** Main branch requires PR approval. Direct pushes blocked.

### Quick Start

```bash
# 1. Always start from dev
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b feature/agents-{name}

# 3. Work and commit (conventional commits)
feat(agents): implement cs-{agent-name}
fix(tool): correct calculation logic
docs(workflow): update branch strategy

# 4. Push and create PR to dev
git push origin feature/agents-{name}
gh pr create --base dev --head feature/agents-{name}

# 5. After approval, PR merges to dev
# 6. Periodically, dev merges to main via PR
```

**Branch Protection Rules:**
- ✅ Main: Requires PR approval, no direct push
- ✅ Dev: Unprotected, but PRs recommended
- ✅ All: Conventional commits enforced

See [documentation/WORKFLOW.md](documentation/WORKFLOW.md) for complete workflow guide.
See [standards/git/git-workflow-standards.md](standards/git/git-workflow-standards.md) for commit standards.

## Development Environment

**No build system or test frameworks** - intentional design choice for portability.

**Python Scripts:**
- Use standard library only (minimal dependencies)
- CLI-first design for easy automation
- Support both JSON and human-readable output
- No ML/LLM calls (keeps skills portable and fast)

**If adding dependencies:**
- Keep scripts runnable with minimal setup (`pip install package` at most)
- Document all dependencies in SKILL.md
- Prefer standard library implementations

## Current Sprint

**Active Sprint:** sprint-11-05-2025 (Nov 5-19, 2025)
**Goal:** Skill-Agent Integration Phase 1-2
**Status:** ✅ COMPLETE - All 6 days finished, 5 agents deployed

**Deliverables:**
- 5 production agents: cs-content-creator, cs-demand-gen-specialist, cs-ceo-advisor, cs-cto-advisor, cs-product-manager
- 1 agent template for future development
- Modular documentation structure (main + 9 domain CLAUDE.md files)
- Branch protection and workflow documentation

**Progress Tracking:**
- [Sprint Plan](documentation/delivery/sprint-11-05-2025/plan.md) - Day-by-day execution plan
- [Sprint Context](documentation/delivery/sprint-11-05-2025/context.md) - Goals, scope, risks
- [Sprint Progress](documentation/delivery/sprint-11-05-2025/PROGRESS.md) - Real-time auto-updating tracker

## Roadmap

**Phase 1-3 Complete:** 204 production-ready skills deployed
- Engineering (28 + 12 POWERFUL + 22 new), Marketing (10 + 25 new), Product (8 + 1 new), PM (23), C-Level (5 + 18 new), RA/QM & Compliance (20), Data Analytics (5), HR (4), Sales (5), Business Growth (3 + 13 new), Finance (1)
- 559 Python automation tools, 230+ reference guides
- 17 AI agents (6 .claude/agents + 11 agents/), 12 sample CI/CD workflows
- 18 compliance frameworks covered (SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS, EU AI Act, NIS2, DORA, NIST CSF 2.0, CCPA, ISO 42001, ISO 13485, ISO 14971, MDR, FDA, 21 CFR Part 11, IEC 62304, IEC 62443)
- Cross-platform support (Claude Code + OpenAI Codex + Cursor + VS Code)

**Next Priorities:**
- **Phase 4 (Q2 2026):** Per-skill installation system, automatic updates, marketing expansion
- **Phase 5 (Q3 2026):** 120+ skills - blockchain, web3, advanced analytics, specialized mobile

**Target:** 130+ skills by Q3 2026

## Key Principles

1. **Skills are products** - Each skill deployable as standalone package
2. **Documentation-driven** - Success depends on clear, actionable docs
3. **Algorithm over AI** - Use deterministic analysis (code) vs LLM calls
4. **Template-heavy** - Provide ready-to-use templates users customize
5. **Platform-specific** - Specific best practices > generic advice

## Anti-Patterns to Avoid

- Creating dependencies between skills (keep each self-contained)
- Adding complex build systems or test frameworks (maintain simplicity)
- Generic advice (focus on specific, actionable frameworks)
- LLM calls in scripts (defeats portability and speed)
- Over-documenting file structure (skills are simple by design)

## Working with This Repository

**Creating New Skills:** Follow the appropriate domain's roadmap and CLAUDE.md guide (see Navigation Map above).

**Editing Existing Skills:** Maintain consistency across markdown files. Use the same voice, formatting, and structure patterns.

**Quality Standard:** Each skill should save users 40%+ time while improving consistency/quality by 30%+.

## Additional Resources

- **.gitignore:** Excludes .vscode/, .DS_Store, .env*, __pycache__/, node_modules/
- **Standards Library:** [standards/](standards/) - Communication, quality, git, documentation, security
- **Implementation Plans:** [documentation/implementation/](documentation/implementation/)
- **Sprint Delivery:** [documentation/delivery/](documentation/delivery/)

---

**Last Updated:** March 2026
**Version:** 3.0.0
**Status:** 204 skills, 559 Python tools, 17 agents, 12 workflows deployed
