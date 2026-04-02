---
title: Task Agents
---

# Task Agents

19 specialized `cs-*` agents organized by domain. Each agent combines multiple skills into a focused workflow.

## Engineering Agents

| Agent | Role | Skills Used |
|---|---|---|
| **cs-tech-lead** | Architecture reviews, code quality, team mentoring | senior-architect, code-reviewer, senior-fullstack |
| **cs-engineering-director** | Engineering management, hiring, process optimization | interview-system-designer, senior-devops, observability-designer |
| **cs-code-auditor** | Deep code quality and security audits | code-reviewer, senior-security, tech-debt-tracker |
| **cs-architecture-reviewer** | System design review and ADR generation | senior-architect, database-designer, migration-architect |
| **cs-security-engineer** | Application security assessment and remediation | senior-security, senior-secops, dependency-auditor |
| **cs-doc-writer** | Technical documentation generation | codebase-onboarding, doc-drift-detector, changelog-generator |

## C-Level Agents

| Agent | Role | Skills Used |
|---|---|---|
| **cs-ceo-advisor** | Strategic planning, board governance, organizational development | ceo-advisor, strategic-alignment, org-health-diagnostic |
| **cs-cto-advisor** | Technical strategy, engineering leadership, architecture decisions | cto-advisor, tech-stack-evaluator, senior-architect |
| **cs-cfo-advisor** | Financial planning, fundraising, investor reporting | cfo-advisor, financial-analyst, saas-metrics-coach |

## Compliance Agents

| Agent | Role | Skills Used |
|---|---|---|
| **cs-compliance-auditor** | 18-framework compliance audit | soc2-compliance-expert, gdpr-dsgvo-expert, iso42001-ai-management |
| **cs-ciso-advisor** | Security strategy, risk quantification, incident response | ciso-advisor, information-security-manager-iso27001, nist-csf-specialist |

## Marketing Agents

| Agent | Role | Skills Used |
|---|---|---|
| **cs-content-creator** | Blog posts, landing pages, social content with brand voice | content-creator, copywriting, seo-specialist |
| **cs-demand-gen-specialist** | Campaign planning, lead generation, funnel optimization | marketing-demand-acquisition, paid-ads, campaign-analytics |
| **cs-seo-analyst** | Technical SEO audits, keyword research, content optimization | seo-audit, site-architecture, schema-markup |

## Product Agent

| Agent | Role | Skills Used |
|---|---|---|
| **cs-product-manager** | Roadmap planning, user research, feature prioritization | product-manager-toolkit, ux-researcher-designer, ab-test-setup |

## Additional Agents

These agents live in the `agents/` root directory:

| Agent | Role |
|---|---|
| **cs-cmo-advisor** | Marketing leadership and brand strategy |
| **cs-design-lead** | Design system leadership and UX strategy |
| **cs-growth-lead** | Growth marketing and experimentation |
| **cs-privacy-officer** | Privacy compliance across GDPR, CCPA, and other frameworks |

## Invoking an Agent

=== "Claude Code"

    ```
    > /agents/cs-tech-lead Review the architecture of the payments service
    ```

=== "Direct Reference"

    ```
    Load agents/engineering/cs-tech-lead.md and review this codebase
    ```

Each agent's `.md` file contains its complete configuration, skill dependencies, and workflow instructions.
