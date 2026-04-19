# Bundles

Five curated plugin bundles. Each one groups 6-9 flagship skills from a single domain and ships as an installable Claude Code plugin.

## Install

```bash
/plugin marketplace add borghei/Claude-Skills
/plugin install engineering-skills@claude-skills
```

Swap in any of the 5 bundle names:

| Bundle | Skills | Focus |
|---|---|---|
| [engineering-skills](engineering-skills/) | 8 | Fullstack, DevOps, security, Docker, Terraform, MCP, RAG, code review |
| [compliance-skills](compliance-skills/) | 9 | ISO 27001, SOC 2, GDPR, EU AI Act, NIS2, DORA, ISO 13485, MDR, FDA |
| [c-level-skills](c-level-skills/) | 7 | CEO, CTO, CFO, CISO, CMO advisors plus board work |
| [marketing-skills](marketing-skills/) | 6 | Content, SEO, demand gen, analytics, landing pages, X growth |
| [product-skills](product-skills/) | 6 | Product management, strategy, UX research, design systems |

## Alternate install paths

**Universal CLI** (works across Cursor, Codex, Gemini CLI, Copilot, Windsurf, Cline, Aider, Goose):

```bash
npx @borghei/claude-skills add senior-fullstack
```

The CLI installs individual skills. Bundles are the Claude Code path; the universal CLI lets you cherry-pick.

## Why bundles

Bundles exist for two reasons:
1. **Discoverability.** Five named kits give teams a mental shortcut. "We need the compliance kit" beats "we need ISO 27001 + SOC 2 + GDPR + ...".
2. **Update surface.** One plugin version bump ships every skill in the bundle. No drift between related skills.

Skills inside bundles are symlinks to the canonical skill directories in the root of this repo. Editing a skill in `engineering/senior-fullstack/` instantly updates every bundle that includes it.
