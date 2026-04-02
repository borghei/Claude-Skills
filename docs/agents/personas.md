---
title: Personas
---

# Personas

7 cross-functional personas that combine skills from multiple domains into a single professional role. Unlike task agents (which focus on one function), personas think holistically about problems.

## Available Personas

| Persona | Domains | Description |
|---|---|---|
| **Startup CTO** | Engineering + C-Level + Product | Technical co-founder perspective. Balances architecture decisions with business constraints, hiring, and product strategy. |
| **Solo Founder** | C-Level + Business + Marketing + Product | Wears every hat. Covers strategy, product, marketing, sales, and finance for early-stage solo operators. |
| **Product Manager** | Product + Engineering + Marketing | Bridges technical and business. Handles roadmap, prioritization, user research, and go-to-market. |
| **Growth Marketer** | Marketing + Business + Data | Data-driven growth. Covers experimentation, funnel optimization, content, paid ads, and analytics. |
| **Content Strategist** | Marketing + SEO + Brand | Content-first marketing. Plans editorial strategy, SEO, brand voice, and content production workflows. |
| **DevOps Engineer** | Engineering (DevOps + Security + Cloud) | Infrastructure and reliability. Covers CI/CD, containers, IaC, monitoring, and incident response. |
| **Finance Lead** | Finance + C-Level (CFO) + Business | Financial operations. Covers modeling, forecasting, unit economics, fundraising, and board reporting. |

## How Personas Differ from Task Agents

| | Task Agents | Personas |
|---|---|---|
| **Scope** | Single domain | Cross-domain |
| **Output** | Structured report | Holistic advice |
| **Best for** | Specific tasks | Strategic questions |
| **Example** | "Audit this code for security" | "Should we build or buy this feature?" |

## Activating a Persona

Use the `/persona` slash command in Claude Code:

```
> /persona startup-cto
```

Or reference the persona file directly:

```
Load agents/personas/startup-cto.md and advise on this technical decision
```

## Persona Files

All persona definitions live in `agents/personas/`:

```
agents/personas/
├── startup-cto.md
├── solo-founder.md
├── product-manager.md
├── growth-marketer.md
├── content-strategist.md
├── devops-engineer.md
└── finance-lead.md
```

Each file defines:

- **Identity** -- Role description and expertise areas
- **Skill dependencies** -- Which skills the persona draws from
- **Decision frameworks** -- How the persona approaches problems
- **Communication style** -- Tone, detail level, and output format
