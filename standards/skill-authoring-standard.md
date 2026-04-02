---
name: skill-authoring-standard
description: Formal standard for creating high-quality, consistent skills
version: 1.0.0
updated: 2026-04-02
---

# Skill Authoring Standard

## Overview

Every skill is a product. Users extract a folder, drop it into their workflow, and expect it to work immediately. This standard codifies the 10 patterns that every skill must follow to ensure consistent quality across the library.

**Who this is for:** Anyone creating or modifying skills. Read this before writing your first SKILL.md.

## Pattern 1: Context-First Design

**Every SKILL.md must open with a description that tells AI assistants when to activate this skill.**

AI assistants scan skill descriptions to decide relevance. Vague openings mean the skill never activates when needed.

### Requirements

- First 3 lines: clear, specific description of what the skill does
- Include trigger phrases (words a user would say when they need this skill)
- Specify target audience

### Good vs Bad

```markdown
# GOOD: Senior Architect Skill
System design and architecture decision-making for teams building production software.
Activate when: designing new systems, evaluating architecture tradeoffs, reviewing
technical proposals, planning migrations, or making build-vs-buy decisions.
Target: Engineering leads, CTOs, senior developers making structural decisions.

# BAD: Senior Architect Skill
This skill helps with architecture.
# Fails because "helps with architecture" matches everything and nothing.
```

## Pattern 2: YAML Frontmatter Schema

**Every SKILL.md must begin with structured YAML frontmatter.**

Frontmatter enables programmatic discovery, catalog generation, and filtering.

### Required Fields

```yaml
---
name: skill-name-here
description: One-line description (under 120 characters)
license: MIT
metadata:
  version: 1.0.0
  author: Author Name
  category: Primary category (e.g., Engineering, Marketing, Compliance)
  domain: Specific domain (e.g., frontend, seo, iso-13485)
  updated: YYYY-MM-DD
  tags:
    - tag1
    - tag2
    - tag3
---
```

### Field Rules

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Lowercase, hyphenated, matches folder name |
| `description` | Yes | Under 120 characters, no jargon |
| `license` | Yes | Must be `MIT` unless explicitly approved otherwise |
| `metadata.version` | Yes | Semantic versioning (MAJOR.MINOR.PATCH) |
| `metadata.author` | Yes | Full name or team name |
| `metadata.category` | Yes | Must match a top-level directory name |
| `metadata.domain` | Yes | Specific subdomain within the category |
| `metadata.updated` | Yes | ISO 8601 date format |
| `metadata.tags` | Yes | 3-8 tags, lowercase, relevant to discovery |

## Pattern 3: Line Limits

**SKILL.md should be under 500 lines. If longer, split into references/.**

Long files degrade AI assistant performance. Context windows are finite.

### Rules

| File | Maximum Lines | Purpose |
|------|---------------|---------|
| SKILL.md | 500 | Workflows, quick-reference, activation context |
| references/*.md | 800 per file | Deep knowledge, detailed frameworks, standards |
| scripts/*.py | 300 per file | Automation tools |
| assets/* | No limit | User templates, examples |

### Splitting Strategy

When SKILL.md exceeds 500 lines:

1. **Keep in SKILL.md:** Workflows, decision trees, quick-reference tables, activation context
2. **Move to references/:** Detailed frameworks, exhaustive checklists, background theory, regulatory text
3. **Link, don't duplicate:** SKILL.md references the detailed file with a relative path

### Example

A 1,200-line SKILL.md becomes: SKILL.md (380 lines with workflows) + `references/technical-seo-checklist.md` (600 lines) + `references/ranking-factors.md` (700 lines). Deep content moves to references, SKILL.md keeps workflows and decision trees.

## Pattern 4: Opinionated Recommendations

**Skills must take a position. "Use X because Y" is always better than "You could use X or Y."**

Users activate skills for expert guidance, not a menu of options. A skill that lists five approaches without recommending one has failed its purpose.

### Rules

1. **State the recommendation first**, then explain why
2. **Acknowledge alternatives briefly** — one sentence maximum
3. **Provide the escape hatch** — when the recommendation does not apply

### Good Example

```markdown
## Database Selection

**Use PostgreSQL for your primary datastore.** It handles relational data, JSON documents,
full-text search, and geospatial queries in a single system, eliminating the operational
burden of multiple databases.

Alternative: Use DynamoDB if your access patterns are exclusively key-value lookups at
massive scale (>100K requests/second) and you can accept eventual consistency.
```

### Bad Example

```markdown
## Database Selection
There are many options: PostgreSQL, MySQL, MongoDB, DynamoDB, Redis.
Choose the one that best fits your needs.
# Zero guidance — a user learns nothing they couldn't find in a 30-second web search.
```

## Pattern 5: Anti-Patterns Section

**Every skill must include a dedicated section documenting common mistakes to avoid.**

### Requirements

- Minimum 3 anti-patterns per skill
- Each entry includes: the mistake, why it happens, and what to do instead
- Must come from real-world experience, not theoretical concerns

### Format

```markdown
## Anti-Patterns

### [Name of Anti-Pattern]
**Mistake:** [What people do wrong]
**Why it happens:** [Root cause — usually sounds reasonable on the surface]
**Instead:** [What to do instead, with specific guidance]
```

### Example

```markdown
### The Premature Microservice
**Mistake:** Splitting a monolith into microservices before understanding domain boundaries.
**Why it happens:** Teams read about microservices at scale and assume they need them from day one.
**Instead:** Start with a well-structured monolith. Extract services only when you have clear
domain boundaries, independent scaling needs, and a team large enough to own each service.
```

## Pattern 6: Confidence Tagging

**Mark every recommendation with a confidence level.**

### Confidence Levels

| Tag | Meaning | When to Use |
|-----|---------|-------------|
| **[PROVEN]** | Battle-tested across many projects and teams | Industry-standard practices, well-established patterns |
| **[RECOMMENDED]** | Strong evidence from multiple sources | Best practices with broad (but not universal) support |
| **[EXPERIMENTAL]** | Promising approach, limited validation | Emerging patterns, new frameworks, novel combinations |

### Usage Rules

1. Tag at the section or recommendation level, not every sentence
2. Default to **[RECOMMENDED]** when unsure — most guidance falls here
3. **[PROVEN]** requires the author to have seen it work in 3+ real projects
4. **[EXPERIMENTAL]** must include a risk note explaining what could go wrong

### Example

```markdown
### [PROVEN] HTTP Cache Headers — battle-tested, no downsides when configured correctly
### [RECOMMENDED] Redis Application Cache — strong evidence for read-heavy workloads
### [EXPERIMENTAL] Edge-Side Includes — promising but CDN support varies; include risk note
```

## Pattern 7: Tool Design Standards

**Python scripts must follow strict design constraints to maintain portability and speed.**

### Requirements

| Constraint | Rule |
|------------|------|
| Dependencies | Standard library only. If an external package is essential, document it in SKILL.md. |
| Interface | `argparse` CLI with `--help` that fully documents all options |
| Output | Support both JSON (`--format json`) and human-readable (default) output |
| Line count | 150-300 lines per script. Under 150 suggests missing functionality. Over 300 suggests the script should be split. |
| ML/LLM calls | Prohibited. Scripts must be deterministic and fast. |
| Error handling | All exceptions caught with actionable error messages |
| Type hints | Required for all function signatures |
| Docstrings | Required for all public functions |

### Script Structure

Every script must follow this structure:

1. **Shebang + docstring** with one-line description and usage
2. **Standard library imports only** (`argparse`, `json`, `sys`, `pathlib`, `typing`)
3. **`main()` function** with argparse, try/except, and sys.exit on error
4. **Analysis function(s)** with type hints and docstrings
5. **`output()` function** supporting both JSON and human-readable formats
6. **`if __name__ == "__main__": main()`** guard

## Pattern 8: Reference Architecture

**Every skill must follow the standard directory structure.**

### Required Structure

```
skill-name/
├── SKILL.md              # Master documentation (under 500 lines)
├── scripts/              # Python CLI tools
│   ├── tool_one.py       # Each tool is self-contained
│   └── tool_two.py
├── references/           # Deep knowledge bases
│   ├── framework.md      # Detailed frameworks and models
│   └── checklist.md      # Exhaustive checklists
└── assets/               # User-facing templates
    ├── template.md       # Report templates
    └── example.yaml      # Configuration examples
```

### Role of Each Directory

| Directory | Contains | Audience |
|-----------|----------|----------|
| `SKILL.md` | Workflows, decision trees, activation context | AI assistants and users |
| `scripts/` | Automation tools that execute analysis | Users running tools locally |
| `references/` | Deep domain knowledge, standards, checklists | AI assistants needing detailed context |
| `assets/` | Templates users customize for their projects | Users producing deliverables |

### Rules

Knowledge flows: `references/` informs `SKILL.md` workflows, executed via `scripts/`, applied using `assets/` templates.

1. **SKILL.md is the entry point** — must be self-sufficient for basic use
2. **references/, scripts/, assets/ are optional** — include only when needed
3. **No nested subdirectories** — keep the structure flat within each directory

## Pattern 9: Self-Contained Packaging

**Each skill must be deployable independently with zero dependencies on other skills.**

### Rules

1. **No cross-skill imports** — scripts must not import from other skill directories
2. **No cross-skill references** — SKILL.md must not require reading another skill's documentation to be useful
3. **Duplicate rather than depend** — if two skills need the same utility function, each skill gets its own copy
4. **Standards are the exception** — skills may reference files in `standards/` since those apply universally

### Validation Test

Copy the skill folder to an empty directory. SKILL.md must be readable, all scripts must execute, all relative paths must resolve, and no references to external files should break.

### Acceptable Dependencies

- Python standard library (always available)
- Files within the same skill directory (by definition self-contained)
- Standards library (`standards/`) for universal guidelines
- External packages documented in SKILL.md with install instructions

## Pattern 10: Quality Threshold

**Each skill must save users 40%+ time while improving consistency by 30%+.**

If a skill does not clear this bar, it should not be published.

### How to Measure

- **Time savings:** Estimate the task duration without vs with the skill. Must cut total time by 40%+.
- **Consistency:** Identify key quality dimensions (completeness, accuracy, thoroughness). Must improve at least one by 30%+.

### Examples

| Skill | Without Skill | With Skill | Time Savings | Consistency Gain |
|-------|---------------|------------|--------------|------------------|
| Code Review | 45 min manual review | 15 min guided review | 67% | Catches 40% more issues |
| SEO Audit | 3 hours crawl + analyze | 1 hour structured audit | 67% | Covers 50% more factors |
| PRD Writing | 4 hours from scratch | 2 hours with templates | 50% | 35% more complete |

### Skills That Fail This Bar

- **Information-only skills** that just list facts without workflows or tools
- **Thin wrapper skills** that add a few bullet points to a generic process
- **Copy-paste skills** that repackage freely available documentation without adding structure

## Checklist

Use this checklist before publishing any skill.

- [ ] YAML frontmatter with all required fields; `name` matches directory name (P2)
- [ ] SKILL.md under 500 lines (P3)
- [ ] First 3 lines provide clear activation context (P1)
- [ ] Recommendations are opinionated with rationale (P4)
- [ ] Anti-patterns section with 3+ entries (P5)
- [ ] Confidence tags on key recommendations (P6)
- [ ] Python scripts: argparse, JSON + text output, stdlib only, 150-300 lines (P7)
- [ ] Directory structure follows standard layout (P8)
- [ ] Self-contained: no cross-skill deps, all paths resolve (P9)
- [ ] Time savings 40%+, consistency improvement 30%+ (P10)

## Examples

### Common Mistakes

| Mistake | Pattern Violated | Fix |
|---------|-----------------|-----|
| SKILL.md is 900 lines | Pattern 3 (Line Limits) | Split deep content into references/ |
| No frontmatter | Pattern 2 (YAML Schema) | Add required YAML block |
| "You could use X or Y" | Pattern 4 (Opinionated) | Pick one and explain why |
| Script requires `pip install numpy pandas scikit-learn` | Pattern 7 (Tool Design) | Rewrite with standard library |
| Skill imports from `../other-skill/scripts/` | Pattern 9 (Self-Contained) | Copy the needed function locally |
| No anti-patterns section | Pattern 5 (Anti-Patterns) | Add 3+ real-world mistakes |

---

**Last Updated:** April 2, 2026
**Version:** 1.0.0
**Status:** Active standard for all skill authors
