# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is the **universal AI skills library** — reusable, production-ready skill packages that bundle domain expertise, best practices, analysis tools, and strategic frameworks. Works with every major AI coding assistant: Claude Code, Cursor, Copilot, Codex, Gemini CLI, Windsurf, Cline, Aider, Goose, and more.

**Current Scope:** 343 production-ready skills across 17 domains with 786 Python automation tools, 76 AI agents (including 8 personas), 26 slash commands, 21 compound sub-skills, and 8 CI/CD workflows. **Project Management is the most-used domain (66 skills: discovery, delivery, career growth, strategy frameworks, GTM, modern AI/growth PM, integrations).**

**Key Distinction**: This is NOT a traditional application. It's a library of skill packages meant to be extracted and deployed by users into their AI coding workflows.

## Navigation Map

This repository uses **modular documentation**. For domain-specific guidance, see:

| Domain | CLAUDE.md Location | Focus |
|--------|-------------------|-------|
| **Agent Development** | [agents/CLAUDE.md](agents/CLAUDE.md) | cs-* agent creation, YAML frontmatter, relative paths |
| **Marketing Skills** | [marketing/CLAUDE.md](marketing/CLAUDE.md) | Content creation, SEO, demand gen, campaign analytics Python tools |
| **Product Team** | [product-team/CLAUDE.md](product-team/CLAUDE.md) | 13 skills: RICE, OKRs, UX research, product analytics, Apple HIG, research synthesis, spec-to-repo, roadmap communication |
| **Engineering** | [engineering/CLAUDE.md](engineering/CLAUDE.md) | Scaffolding, fullstack, AI/ML, data tools |
| **C-Level Advisory** | [c-level-advisor/CLAUDE.md](c-level-advisor/CLAUDE.md) | 31 skills: CEO/CTO/CFO/CMO/CRO/CPO/COO/CHRO/CISO + Tier 2 (CAIO, CDO, CCO, GC, VPE) advisors |
| **Project Management** ★ | [project-management/CLAUDE.md](project-management/CLAUDE.md) | **66 PM skills (most-used domain):** discovery, execution, career growth, strategy-frameworks/ (BMC, lean canvas, SWOT, Porter's, Ansoff), gtm/ (GTM strategy, ICP), Jira / Linear / Notion / Confluence integration |
| **RA/QM Compliance** | [ra-qm-team/CLAUDE.md](ra-qm-team/CLAUDE.md) | 27 skills: ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2, DORA, NIST CSF, PCI-DSS, CCPA, ISO 42001, infrastructure auditing — plus 6 audit-prep playbooks |
| **Business & Growth** | [business-growth/CLAUDE.md](business-growth/CLAUDE.md) | Customer success, sales engineering, revenue operations |
| **Finance** | [finance/CLAUDE.md](finance/CLAUDE.md) | Financial analysis, DCF valuation, budgeting, forecasting |
| **Data Analytics** | [data-analytics/CLAUDE.md](data-analytics/CLAUDE.md) | Data analysis, BI, ML ops, analytics engineering |
| **HR Operations** | [hr-operations/CLAUDE.md](hr-operations/CLAUDE.md) | Talent acquisition, people analytics, HR business partner |
| **Sales Success** | [sales-success/CLAUDE.md](sales-success/CLAUDE.md) | Account executive, sales ops, solutions architect |
| **Legal (Experimental)** | [legal/CLAUDE.md](legal/CLAUDE.md) | 17 skills: contract review, NDA, privacy, DPIA, breach response, risk assessment, mediation |
| **Personal Productivity** | [personal-productivity/CLAUDE.md](personal-productivity/CLAUDE.md) | 10 skills: resume, lead-research, meeting-insights, naming, invoices, email triage, calendar prep, investor update, pitch deck, weekly review |
| **Documents** | [documents/CLAUDE.md](documents/CLAUDE.md) | 4 skills: docx, pdf, pptx, xlsx audit (stdlib-only OOXML parsing) |
| **Vertical Advisors** | [vertical-advisors/CLAUDE.md](vertical-advisors/CLAUDE.md) | 7 skills: fintech, healthtech, edtech, ecommerce, proptech, climate-tech, marketplace strategic advisors |
| **Research** | [research/CLAUDE.md](research/CLAUDE.md) | 4 skills: litreview (systematic reviews), grants (proposal architecture), patent (prior art + landscape), dossier (intelligence briefings) |
| **Standards Library** | [standards/CLAUDE.md](standards/CLAUDE.md) | Communication, quality, git, security standards |
| **Templates** | [templates/CLAUDE.md](templates/CLAUDE.md) | Template system usage |

**Current Sprint:** See [documentation/delivery/sprint-11-05-2025/](documentation/delivery/sprint-11-05-2025/) for active sprint context and progress.

## Architecture Overview

### Repository Structure

```
claude-code-skills/
├── .claude/
│   ├── agents/                # 6 Claude Code subagents (code-reviewer, qa, docs, etc.)
│   └── commands/              # 26 slash commands (git, review, prd, tdd, rice, retro, etc.)
├── .gemini/                   # Gemini CLI support (skills-index.json + 20 skill wrappers)
├── .github/
│   ├── workflows/             # 6 CI/CD workflows (pages, enforce-pr, security, review, etc.)
│   └── copilot-instructions.md # GitHub Copilot config
├── agents/
│   ├── (domain dirs)/         # 26 cs-* prefixed skill agents
│   └── personas/              # 7 cross-domain personas (startup-cto, solo-founder, etc.)
├── engineering/               # 82 engineering skills + 3 compound sub-skill systems
├── marketing/                 # 39 marketing skills + Python tools (incl. aeo)
├── product-team/              # 13 product skills + Python tools (Tier 2: product-analytics, apple-hig-expert, research-summarizer, spec-to-repo, roadmap-communicator)
├── project-management/        # 66 PM skills (most-used domain) — role-based, discovery/, execution/, career/, strategy-frameworks/ (Tier 3), gtm/ (Tier 3), linear-expert, notion-pm
├── c-level-advisor/           # 31 C-level advisory skills + Python tools (Tier 2: CAIO, CDO, CCO, GC, VPE advisors)
├── research/                  # 4 research skills (Tier 2) — litreview, grants, patent, dossier
├── ra-qm-team/                # 27 RA/QM compliance skills (incl. audit-prep/ subfolder)
├── business-growth/           # 20 business & growth skills (incl. commercial: deal-desk, channel-economics, partnerships-architect, commercial-policy)
├── data-analytics/            # 5 data analytics skills + Python tools
├── hr-operations/             # 4 HR operations skills + Python tools
├── sales-success/             # 5 sales success skills + Python tools
├── finance/                   # 3 finance skills + Python tools
├── legal/                     # 17 legal skills (EXPERIMENTAL) + 34 Python tools
├── personal-productivity/     # 10 personal-productivity skills (resume, leads, meetings, naming, invoices, email triage, calendar prep, investor update, pitch deck, weekly review)
├── documents/                 # 4 document automation skills (docx, pdf, pptx, xlsx) — stdlib only
├── vertical-advisors/         # 7 vertical advisor skills (fintech, healthtech, edtech, ecommerce, proptech, climate-tech, marketplace)
├── standards/                 # 7 standards (+ orchestration protocol, skill authoring standard)
├── templates/                 # Reusable templates + 12 sample GitHub workflows
├── documentation/             # Implementation plans, sprints, delivery
├── AGENTS.md                  # Universal agent config (Codex, Aider, Jules, etc.)
├── GEMINI.md                  # Gemini CLI instructions
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

**Phase 1-4 Complete:** 245 production-ready skills deployed
- Engineering (76 skills incl. 3 compound sub-skill systems), Marketing (38), Product (8), PM (54), C-Level (26), RA/QM & Compliance (21), Legal (17 — EXPERIMENTAL), Data Analytics (5), HR (4), Sales (5), Business Growth (16), Finance (3), Personal Productivity (10), Documents (4), Vertical Advisors (7)
- 653 Python automation tools, 317+ reference guides
- 32 AI agents (6 .claude/agents + 19 domain agents + 7 personas)
- 26 slash commands, 21 compound sub-skills, 6 active CI/CD workflows + 12 templates
- 18 compliance frameworks covered (SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS, EU AI Act, NIS2, DORA, NIST CSF 2.0, CCPA, ISO 42001, ISO 13485, ISO 14971, MDR, FDA, 21 CFR Part 11, IEC 62304, IEC 62443)
- Cross-platform support (Claude Code + OpenAI Codex + Gemini CLI + Cursor + VS Code)
- Persona system (7 cross-domain personas) + Orchestration Protocol (4 patterns)
- Skill Authoring Standard (10 formal patterns)

**Next Priorities:**
- **Phase 5 (Q2 2026):** Per-skill installation system, automatic updates, ClawHub publishing
- **Phase 6 (Q3 2026):** 250+ skills - blockchain, web3, advanced analytics, specialized mobile

**Target:** 250+ skills by Q3 2026

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

**Last Updated:** June 2026
**Version:** 4.10.0
**Status:** 343 skills, 68 cs-* agents (+ 8 personas), 26 commands, 21 sub-skills, 17 domains (incl. workflow meta-skills), Gemini CLI support. Engineering domain adds 4 AI-modernization skills (extended-thinking-architect, batch-api-orchestrator, computer-use-automation, agentic-evaluation-framework) + memory-tool/context-editing/reasoning-effort/caching upgrades to context-engine, llm-cost-optimizer, agent-workflow-designer, mcp-server-builder. Cross-platform surface unified — one `build_manifest.py` run regenerates `cli/skills.json`, `registry.json`, `.gemini/skills-index.json`, and the website catalog `skills.json`; all 17 domains install as Claude Code plugins; Cursor `.cursor/rules/*.mdc` added. PM domain expanded to 66 skills with career track, AI/ML PRD, activation funnels, feature flags, post-mortems, customer feedback triage, pricing PRDs, Linear/Notion/Productboard integrations, strategy frameworks (BMC/lean/SWOT/Porter's/Ansoff), and GTM (gtm-strategy/ICP).
- **Recent Tier-3 additions (May 2026):** 12 PM skills in new subfolders `strategy-frameworks/` (business-model-canvas, lean-canvas, swot-analysis, porters-five-forces, ansoff-matrix) and `gtm/` (gtm-strategy, ideal-customer-profile), plus discovery additions (opportunity-solution-tree, metrics-dashboard) and execution additions (stakeholder-map, test-scenarios, sprint-plan). 12 stdlib Python validators, ~12K lines.
- **Recent Tier-2 additions (May 2026):** 5 C-suite advisors (chief-ai-officer-advisor, chief-data-officer-advisor, chief-customer-officer-advisor, general-counsel-advisor, vpe-advisor); 5 product skills (product-analytics, apple-hig-expert, research-summarizer, spec-to-repo, roadmap-communicator); new `research/` domain with 4 skills (litreview, grants, patent, dossier). 14 deep skills, 42 stdlib Python scripts, ~24K lines.
- **Tier-1 additions (Apr 2026):** 6 engineering skills (feature-flags-architect, chaos-engineering, kubernetes-operator, azure-cloud-architect, gcp-cloud-architect, data-quality-auditor); 4 commercial skills in business-growth (deal-desk, channel-economics, partnerships-architect, commercial-policy); 6 audit-prep playbooks in ra-qm-team/audit-prep/ (soc2/gdpr/fda-qsr/ai-act/aims/compliance-readiness); 1 marketing skill (aeo).
- Domains: `personal-productivity/` (10 skills), `documents/` (4 skills, stdlib OOXML), `vertical-advisors/` (7 skills), `research/` (4 skills — Tier 2)
- Vertical advisors: fintech, healthtech, edtech, ecommerce, proptech, climate-tech, marketplace — strategic, not implementation
- Expanded `agents/`: cs-* agents across engineering (23), c-level (12), marketing (8), business-growth (3), hr (2), product (3), compliance (2), vertical (7), root (4)
