# GEMINI.md

Instructions for Google Gemini CLI when working with the Claude Skills Library.

## Project Overview

This is the **Universal AI Skills Library** -- 203 production-ready skill packages across 13 domains with 559 Python automation tools. Each skill bundles domain expertise, best practices, analysis tools, and strategic frameworks into self-contained packages.

**This is NOT a traditional application.** It is a library of skill packages meant to be extracted and deployed into your AI coding workflows.

## How to Use Skills with Gemini CLI

### 1. Browse Available Skills

Open `.gemini/skills-index.json` to see all 203 skills with descriptions, domains, tools, and tags. Each entry points to a full `SKILL.md` documentation file.

### 2. Activate a Skill

To use a skill, read its `SKILL.md` file. Every skill follows this structure:

```
skill-name/
  SKILL.md        -- Master documentation and workflows
  scripts/        -- Python CLI tools (no external dependencies)
  references/     -- Expert knowledge bases
  assets/         -- User templates
```

Tell Gemini: "Read `engineering/senior-architect/SKILL.md` and use it as your guide for this task."

### 3. Run Python Tools

Skills include deterministic Python scripts (standard library only, no ML/LLM calls). Run them directly:

```bash
python3 engineering/code-reviewer/scripts/code_quality_checker.py --path ./src
python3 marketing/seo-specialist/scripts/keyword_analyzer.py --url https://example.com
python3 finance/financial-analyst/scripts/dcf_valuation.py --input data.json
```

### 4. Combine Skills

Skills are composable. For example, combine `senior-architect` + `code-reviewer` + `senior-qa` for a full engineering review pipeline.

## Skill Domains

| Domain | Count | Description |
|--------|-------|-------------|
| engineering | 60 | Architecture, backend, frontend, DevOps, security, QA, CI/CD |
| marketing | 35 | Content, SEO, ads, email, social, analytics, brand |
| c-level-advisor | 26 | CEO, CTO, CFO, COO, CMO, CISO strategic advisory |
| project-management | 22 | Agile, PM, Scrum, Jira, Confluence, discovery, execution |
| ra-qm-team | 21 | ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIST, PCI-DSS |
| business-growth | 16 | CRO, pricing, referrals, competitive analysis, revenue ops |
| product-team | 8 | Product management, design systems, UX research, A/B testing |
| data-analytics | 5 | Data analysis, BI, data science, ML ops, analytics engineering |
| sales-success | 5 | Account executive, sales ops, solutions architect |
| hr-operations | 4 | Talent acquisition, people analytics, HR business partner |
| finance | 1 | Financial analysis, DCF valuation, budgeting, forecasting |

## Skill Activation Patterns

Use these patterns when asking Gemini to work with skills:

**Architecture review:** "Load `engineering/senior-architect/SKILL.md` and evaluate this system design."

**Code quality:** "Use the code-reviewer skill at `engineering/code-reviewer/SKILL.md` to review this PR."

**SEO audit:** "Follow the workflow in `marketing/seo-audit/SKILL.md` to audit this site."

**Compliance check:** "Read `ra-qm-team/soc2-compliance-expert/SKILL.md` and assess our SOC 2 readiness."

**Strategic planning:** "Use `c-level-advisor/ceo-advisor/SKILL.md` to evaluate this business decision."

**Sprint planning:** "Follow `project-management/scrum-master/SKILL.md` for our sprint retrospective."

## Quick Reference

- **Skill wrappers:** `.gemini/skills/` -- Short summaries of the top 20 skills for quick discovery
- **Full index:** `.gemini/skills-index.json` -- All 203 skills with metadata
- **Install to your project:** Run `scripts/gemini-install.sh` to copy Gemini config files

## Key Principles

1. **Skills are self-contained** -- no dependencies between skills
2. **Python tools use standard library only** -- no pip install required
3. **Algorithm over AI** -- scripts use deterministic analysis, not LLM calls
4. **Documentation-driven** -- each SKILL.md is the single source of truth
5. **Template-heavy** -- ready-to-use templates you customize for your context

## Repository Structure

```
claude-code-skills/
  .gemini/                  -- Gemini CLI configuration
    skills-index.json       -- Full skill catalog (203 skills)
    skills/                 -- Top 20 skill wrappers for quick access
  engineering/              -- 60 skills + 191 Python tools
  marketing/                -- 35 skills + 106 Python tools
  c-level-advisor/          -- 26 skills + 73 Python tools
  project-management/       -- 22 skills + 53 Python tools
  ra-qm-team/              -- 21 skills + 38 Python tools
  business-growth/          -- 16 skills + 48 Python tools
  product-team/             -- 8 skills + 15 Python tools
  data-analytics/           -- 5 skills + 16 Python tools
  sales-success/            -- 5 skills + 15 Python tools
  hr-operations/            -- 4 skills + 12 Python tools
  finance/                  -- 1 skill + 4 Python tools
  standards/                -- Communication, quality, git, security standards
  templates/                -- Reusable templates + 12 sample GitHub workflows
```
