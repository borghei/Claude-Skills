# Agents

Claude Skills includes two types of agents: **built-in subagents** (`.claude/agents/`) for autonomous code workflows, and **role-based agents** (`agents/`) that combine multiple skills into specialized personas.

---

## Built-In Subagents (6)

Located in `.claude/agents/`. Invoke with `/agents/name` in Claude Code.

| Agent | What It Does | Invoke With |
|-------|-------------|-------------|
| **code-reviewer** | Scores code across 5 categories (1-10), flags bugs, security holes, performance issues | `/agents/code-reviewer` |
| **security-auditor** | OWASP Top 10 audit, secrets scanning, infrastructure security checks | `/agents/security-auditor` |
| **qa-engineer** | Test coverage analysis, bug hunting, test generation, quality metrics | `/agents/qa-engineer` |
| **doc-generator** | Generates README, API docs, architecture docs, changelog entries from code | `/agents/doc-generator` |
| **changelog-manager** | Builds Keep a Changelog entries from git history, determines semver | `/agents/changelog-manager` |
| **git-workflow** | Conventional commits, branch strategy, PR creation, release workflow | `/agents/git-workflow` |

---

## Role-Based Agents (19)

Located in `agents/`. These are specialized AI personas that orchestrate multiple skills with domain-specific behavior. Each agent file defines the persona, tools, and workflows the agent uses.

### Engineering (6)

| Agent | Role | File |
|-------|------|------|
| **cs-tech-lead** | Technical leadership, architecture reviews, team mentoring | `agents/engineering/cs-tech-lead.md` |
| **cs-engineering-director** | Engineering management, hiring, process optimization | `agents/engineering/cs-engineering-director.md` |
| **cs-architecture-reviewer** | Architecture review, system design validation | `agents/engineering/cs-architecture-reviewer.md` |
| **cs-code-auditor** | Deep code audit, quality analysis, refactoring recommendations | `agents/engineering/cs-code-auditor.md` |
| **cs-doc-writer** | Technical documentation, API docs, architecture guides | `agents/engineering/cs-doc-writer.md` |
| **cs-security-engineer** | Security engineering, threat modeling, vulnerability assessment | `agents/engineering/cs-security-engineer.md` |

### C-Level (3)

| Agent | Role | File |
|-------|------|------|
| **cs-ceo-advisor** | Strategic planning, board governance, investor relations | `agents/c-level/cs-ceo-advisor.md` |
| **cs-cto-advisor** | Technical strategy, architecture decisions, engineering leadership | `agents/c-level/cs-cto-advisor.md` |
| **cs-cfo-advisor** | Financial planning, fundraising, unit economics | `agents/c-level/cs-cfo-advisor.md` |

### Compliance (2)

| Agent | Role | File |
|-------|------|------|
| **cs-compliance-auditor** | Multi-framework compliance audit across 18 standards (SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS, EU AI Act, NIS2, DORA, NIST CSF 2.0, CCPA) | `agents/compliance/cs-compliance-auditor.md` |
| **cs-ciso-advisor** | Security strategy, risk quantification, compliance roadmap | `agents/compliance/cs-ciso-advisor.md` |

### Marketing (3)

| Agent | Role | File |
|-------|------|------|
| **cs-content-creator** | Content strategy, brand voice, SEO optimization | `agents/marketing/cs-content-creator.md` |
| **cs-demand-gen-specialist** | Demand generation, paid media, lead nurturing | `agents/marketing/cs-demand-gen-specialist.md` |
| **cs-seo-analyst** | Technical SEO, keyword research, analytics | `agents/marketing/cs-seo-analyst.md` |

### Product (1)

| Agent | Role | File |
|-------|------|------|
| **cs-product-manager** | Product strategy, roadmap planning, user research | `agents/product/cs-product-manager.md` |

### Cross-Functional (4)

| Agent | Role | File |
|-------|------|------|
| **cs-cmo-advisor** | Marketing leadership, brand strategy, demand generation | `agents/cs-cmo-advisor.md` |
| **cs-design-lead** | Design leadership, design systems, UX strategy | `agents/cs-design-lead.md` |
| **cs-growth-lead** | Growth strategy, experimentation, product-led growth | `agents/cs-growth-lead.md` |
| **cs-privacy-officer** | Data privacy, GDPR/CCPA compliance, privacy engineering | `agents/cs-privacy-officer.md` |

---

## How Agents Orchestrate Skills

Agents combine multiple skills to handle complex, multi-step workflows. When you invoke an agent, it:

1. **Activates its persona** with role-specific expertise and communication style
2. **Selects relevant skills** from its domain based on the task
3. **Runs Python tools** from those skills to gather data and produce analysis
4. **Synthesizes results** into structured, actionable output

### Example Workflow: Engineering Director

When asked to "review our engineering health," the `cs-engineering-director` agent might:

1. Run `code_quality_analyzer.py` across key services (from `senior-fullstack`)
2. Analyze test coverage patterns (from `senior-qa`)
3. Check dependency health (from `dependency-auditor`)
4. Review CI/CD pipeline efficiency (from `devops-workflow-engineer`)
5. Produce a consolidated engineering health report with recommendations

### Example Workflow: Compliance Auditor

When asked to "audit SOC 2 readiness," the `cs-compliance-auditor` agent might:

1. Run infrastructure security checks (from `infrastructure-compliance-auditor`)
2. Evaluate access control policies (from `soc2-compliance-expert`)
3. Check encryption and secrets management (from `information-security-manager-iso27001`)
4. Cross-reference findings against SOC 2 Trust Services Criteria
5. Produce a gap analysis with remediation priorities
