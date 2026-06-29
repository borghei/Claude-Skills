---
title: Claude Skills — Universal AI Skills Library
---

# Claude Skills

**The universal AI skills library for every coding assistant.**

Production-ready skill packages that bundle domain expertise, best practices, analysis tools, and strategic frameworks. Works with Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, Jules, and RooCode.

<div class="stats" markdown>
<div class="stat">
<div class="number">224</div>
<div class="label">Skills</div>
</div>
<div class="stat">
<div class="number">613</div>
<div class="label">Python Tools</div>
</div>
<div class="stat">
<div class="number">13</div>
<div class="label">Domains</div>
</div>
<div class="stat">
<div class="number">25</div>
<div class="label">Agents</div>
</div>
<div class="stat">
<div class="number">10</div>
<div class="label">Platforms</div>
</div>
</div>

---

## Quick Install

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills

# Browse skills
ls engineering/ marketing/ product-team/ c-level-advisor/

# Run a Python tool directly
python engineering/senior-fullstack/scripts/code_quality_analyzer.py /path/to/project

# Install a skill to your project
python scripts/skill-installer.py install senior-fullstack --agent claude
```

See [Installation](getting-started/installation.md) for per-skill install, auto-update setup, and platform-specific instructions.

---

## Domains

<div class="grid" markdown>

<div class="card" markdown>
### :material-cog: Engineering
**82 skills** &middot; 248+ tools

Fullstack, DevOps, security, mobile, ML, cloud (AWS/Azure/GCP), MCP servers, CI/CD, observability, chaos engineering, feature flags, kubernetes operators, data quality.

[:octicons-arrow-right-24: Browse skills](skills/engineering.md)
</div>

<div class="card" markdown>
### :material-bullhorn: Marketing
**39 skills** &middot; 118+ tools

Content, SEO, AEO, demand gen, paid ads, CRO, email, social, brand, analytics.

[:octicons-arrow-right-24: Browse skills](skills/marketing.md)
</div>

<div class="card" markdown>
### :material-account-tie: C-Level Advisory
**31 skills** &middot; 88+ tools

CEO, CTO, CFO, CMO, CRO, CPO, COO, CHRO, CISO, plus CAIO, CDO, CCO, GC, VPE advisors and board governance.

[:octicons-arrow-right-24: Browse skills](skills/c-level.md)
</div>

<div class="card" markdown>
### :material-shield-check: Compliance
**27 skills** &middot; 50+ tools

ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2, DORA, NIST CSF, PCI-DSS, plus 6 audit-prep playbooks.

[:octicons-arrow-right-24: Browse skills](skills/compliance.md)
</div>

<div class="card" markdown>
### :material-clipboard-check: ★ Project Management
**66 skills** &middot; 82+ tools &middot; *most-used domain*

PRDs (incl. AI features), OKRs, NSM, roadmaps, retros, story splitting, post-mortems, activation funnels, feature flags, career growth, strategy frameworks (BMC/Lean/SWOT/Porter's/Ansoff), GTM. Jira / Linear / Notion / Productboard / Confluence.

[:octicons-arrow-right-24: Browse skills](skills/project-management.md)
</div>

<div class="card" markdown>
### :material-palette-outline: Product Team
**13 skills** &middot; 30+ tools

UX research, design systems, A/B tests, product strategy, product analytics, Apple HIG, research synthesis, spec-to-repo, roadmap communication.

[:octicons-arrow-right-24: Browse skills](skills/product.md)
</div>

<div class="card" markdown>
### :material-chart-line: Business & Sales
**28 skills** &middot; 85+ tools

CRO, churn prevention, pricing, referral programs, MEDDIC, pipeline, finance, plus deal-desk, channel-economics, partnerships-architect, commercial-policy.

[:octicons-arrow-right-24: Browse skills](skills/business.md)
</div>

<div class="card" markdown>
### :material-magnify: Research
**4 skills** &middot; 12 tools &middot; *new domain*

Literature review (PRISMA), grant proposals (NIH/NSF/SBIR), patent landscape, intelligence dossiers.

[:octicons-arrow-right-24: Browse skills](skills/research.md)
</div>

<div class="card" markdown>
### :material-database: Data & HR
**9 skills** &middot; 28 tools

SQL, ML ops, dbt, BI, talent acquisition, people analytics, operations.

[:octicons-arrow-right-24: Browse skills](skills/other.md)
</div>

</div>

---

## What You Get

| | |
|---|---|
| **339 Skills** | Production-ready expertise across 17 professional domains. Project Management is the most-used (66 skills). |
| **720+ Python Tools** | CLI scripts for code quality, SEO, DCF valuation, compliance auditing, flow metrics, status updates, activation funnels, feedback triage -- all standard library, no ML dependencies |
| **25 Role-Based Agents** | Specialized AI personas (Tech Lead, CFO, CISO, Compliance Auditor, etc.) that orchestrate multiple skills |
| **6 Subagents** | Autonomous Claude Code agents for code review, security audit, QA, docs, changelog, and git workflows |
| **12 CI/CD Workflows** | Ready-to-use GitHub Actions for quality gates, release drafting, skill validation |
| **10 Platforms** | Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, Jules, RooCode |

---

## Usage Examples

**Run a Python tool:**

```bash
python engineering/claude-code-mastery/scripts/claudemd_optimizer.py CLAUDE.md
```

```
CLAUDE.md Optimization Report
  Score: 72/100 | Lines: 142 | Tokens: ~1,850 (9.3% of budget)
  Missing: Code Style, Testing Strategy
  Redundancy: 3 issues found (-120 tokens)
```

**Use a subagent:**

```
> /agents/code-reviewer Review the last commit for security issues
```

```
Code Review: 7/10 | 1 critical (SQL injection), 1 high (missing auth), 1 N+1 query
```

---

## License

**MIT + Commons Clause** -- Free for open-source, personal, education, and internal business use. Cannot be sold or repackaged as a paid product. See [LICENSE](https://github.com/borghei/Claude-Skills/blob/main/LICENSE) for full terms.
