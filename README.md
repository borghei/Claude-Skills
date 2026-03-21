<p align="center">
  <img src="assets/header.svg" alt="Claude Skills" width="100%"/>
</p>

<h1 align="center">Claude Skills</h1>
<p align="center">The universal AI skills library for every coding assistant</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT_+_Commons_Clause-yellow.svg" alt="License"></a>
  <a href="#domains"><img src="https://img.shields.io/badge/Skills-204-brightgreen.svg" alt="204 Skills"></a>
  <a href="#domains"><img src="https://img.shields.io/badge/Python_Tools-559-blue.svg" alt="559 Tools"></a>
  <a href="https://claude.ai/code"><img src="https://img.shields.io/badge/Claude_Code-purple.svg" alt="Claude Code"></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-00D1FF.svg" alt="Cursor"></a>
  <a href="https://github.com/features/copilot"><img src="https://img.shields.io/badge/Copilot-000000.svg" alt="GitHub Copilot"></a>
  <a href="https://openai.com/codex"><img src="https://img.shields.io/badge/Codex-412991.svg" alt="OpenAI Codex"></a>
  <a href="https://codeium.com/windsurf"><img src="https://img.shields.io/badge/Windsurf-0EA5E9.svg" alt="Windsurf"></a>
  <a href="https://github.com/cline/cline"><img src="https://img.shields.io/badge/Cline-EC4899.svg" alt="Cline"></a>
  <a href="https://aider.chat"><img src="https://img.shields.io/badge/Aider-14B8A6.svg" alt="Aider"></a>
</p>

---

## What You Get

| | |
|---|---|
| **204 Skills** | Production-ready expertise across 13 professional domains |
| **559 Python Tools** | CLI scripts for code quality, SEO, DCF valuation, compliance auditing, and more -- all standard library, no ML dependencies |
| **19 Role-Based Agents** | Specialized AI personas (Tech Lead, CFO, CISO, Compliance Auditor, etc.) that orchestrate multiple skills |
| **6 Subagents** | Autonomous Claude Code agents for code review, security audit, QA, docs, changelog, and git workflows |
| **12 CI/CD Workflows** | Ready-to-use GitHub Actions for quality gates, release drafting, skill validation |
| **10 Platforms** | Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, Jules, RooCode |

---

## Quick Start

### Option A: Clone & Use

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

### Option B: Copy a Skill Manually

```bash
# Copy a skill folder into your project
cp -r engineering/senior-fullstack ~/.claude/skills/senior-fullstack

# Or paste any SKILL.md content directly into your AI assistant
```

See [INSTALLATION.md](INSTALLATION.md) for the full installation guide with auto-update configuration and per-agent details.

---

## Usage

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

See [docs/USAGE.md](docs/USAGE.md) for detailed examples across all tools and agents.

---

## Domains

| Domain | Skills | Tools | Focus |
|--------|--------|-------|-------|
| [Engineering](docs/SKILLS.md#engineering-28) | 28 | 77 | Fullstack, DevOps, security, mobile, ML, cloud |
| [Advanced Engineering](docs/SKILLS.md#advanced-engineering-33) | 33 | 33 | MCP servers, Playwright, CI/CD, SaaS, observability |
| [C-Level Advisory](docs/SKILLS.md#c-level-advisory-26) | 26 | 4 | CEO, CTO, CFO, CISO strategic decision-making |
| [Marketing](docs/SKILLS.md#marketing-35) | 35 | 6 | Content, SEO, demand gen, paid ads, CRO |
| [Product Team](docs/SKILLS.md#product-team-8) | 8 | 6 | RICE, OKRs, user stories, UX research, design systems |
| [Project Management](docs/SKILLS.md#project-management-23) | 23 | 14 | Scrum, discovery, execution, Atlassian, retros |
| [RA/QM & Compliance](docs/SKILLS.md#regulatory-affairs-quality-management--compliance-20) | 20 | 35 | ISO 13485, MDR, FDA, SOC 2, GDPR, EU AI Act, NIS2, DORA |
| [Business Growth](docs/SKILLS.md#business-growth-16) | 16 | 9 | CRO, churn prevention, pricing, referral programs |
| [Finance](docs/SKILLS.md#finance-1) | 1 | 4 | DCF valuation, ratio analysis, budgeting |
| [Data & Analytics](docs/SKILLS.md#data--analytics-5) | 5 | 4 | SQL, ML ops, dbt, business intelligence |
| [Sales & Success](docs/SKILLS.md#sales--success-5) | 5 | - | MEDDIC, pipeline management, solutions architecture |
| [HR & People](docs/SKILLS.md#hr--people-4) | 4 | - | Talent acquisition, people analytics, org design |
| [Standards](standards/) | 5 | - | Communication, quality, git, security standards |
| | **204** | **559** | |

See [docs/SKILLS.md](docs/SKILLS.md) for the complete skills reference with descriptions and tool counts.

---

## Agents

Claude Skills includes **19 role-based agents** that combine multiple skills into specialized AI personas, plus **6 built-in subagents** for autonomous code workflows.

Role-based agents act as domain experts. When you invoke one, it selects the right skills, runs relevant Python tools, and produces structured analysis.

| Agent | Domain | Role |
|-------|--------|------|
| **cs-tech-lead** | Engineering | Architecture reviews, team mentoring |
| **cs-engineering-director** | Engineering | Engineering management, hiring, process |
| **cs-ceo-advisor** | C-Level | Strategic planning, board governance |
| **cs-cto-advisor** | C-Level | Technical strategy, engineering leadership |
| **cs-cfo-advisor** | C-Level | Financial planning, fundraising |
| **cs-compliance-auditor** | Compliance | 18-framework audit (SOC 2, GDPR, HIPAA, etc.) |
| **cs-ciso-advisor** | Compliance | Security strategy, risk quantification |
| **cs-product-manager** | Product | Roadmap planning, user research |

See [docs/AGENTS.md](docs/AGENTS.md) for the full list of all 25 agents with descriptions and example workflows.

---

## Repository Structure

```
Claude-Skills/
├── .claude/              # Claude Code config
│   └── agents/           # 6 subagents (code-reviewer, qa-engineer, etc.)
├── agents/               # 19 role-based agents
│   ├── engineering/      # Tech lead, director, code auditor, etc.
│   ├── c-level/          # CEO, CTO, CFO advisors
│   ├── compliance/       # Compliance auditor, CISO advisor
│   ├── marketing/        # Content creator, demand gen, SEO
│   └── product/          # Product manager
├── engineering/          # 61 engineering skills + 177 Python tools
├── c-level-advisor/      # 26 C-level advisory skills
├── marketing/            # 35 marketing skills + 6 Python tools
├── product-team/         # 8 product skills + 6 Python tools
├── project-management/   # 23 PM skills + 14 Python tools
├── ra-qm-team/           # 20 compliance skills + 35 Python tools
├── business-growth/      # 16 growth skills + 9 Python tools
├── finance/              # 1 finance skill + 4 Python tools
├── data-analytics/       # 5 analytics skills + 4 Python tools
├── sales-success/        # 5 sales skills
├── hr-operations/        # 4 HR skills
├── standards/            # Best practices library
├── templates/            # Templates + 12 sample GitHub workflows
├── scripts/              # Skill installer + utilities
├── docs/                 # Extended documentation
└── CLAUDE.md             # Claude Code config
```

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Fork the repo, create a skill following the standard package structure, include Python tools and YAML frontmatter, and submit a PR.

---

## Contributors

| Contributor | GitHub |
|-------------|--------|
| Alan Pope | [@popey](https://github.com/popey) |
| Izzy | [@weemax](https://github.com/weemax) |

---

## License

**MIT + Commons Clause** -- Free for open-source, personal, education, and internal business use. Cannot be sold or repackaged as a paid product. See [LICENSE](LICENSE) for full terms.

---

<p align="center">
  <strong>204 skills. 559 tools. 13 domains. 19 agents. 10 platforms.</strong><br>
  <a href="https://borghei.me">borghei.me</a>
</p>

<p align="center">
  <a href="https://buymeacoffee.com/borghei"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee"></a>
</p>
