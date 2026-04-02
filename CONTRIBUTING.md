# Contributing to Claude Skills

Welcome, and thank you for considering a contribution. Claude Skills is a universal AI skills library -- reusable, production-ready skill packages that bundle domain expertise, best practices, analysis tools, and strategic frameworks. It works with every major AI coding assistant: Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, and more.

We value contributions of all kinds:

- **New skills** -- Add a skill to an existing domain or propose a new domain.
- **Skill improvements** -- Sharpen workflows, add examples, fix anti-patterns.
- **Python tools** -- Build new CLI automation scripts for existing skills.
- **Bug fixes** -- Fix broken paths, incorrect calculations, or logic errors.
- **Documentation** -- Improve SKILL.md files, references, or standards.
- **Translations** -- Localize skills or documentation for non-English audiences.

---

## Getting Started

### 1. Fork and Clone

```bash
gh repo fork <owner>/Claude-Skills --clone
cd Claude-Skills
```

### 2. Branch from dev

All work branches from `dev`. Direct pushes to `main` are blocked by branch protection.

```bash
git checkout dev
git pull origin dev
git checkout -b <branch-name>
```

### 3. Branch Naming

Use one of these prefixes:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New skill or tool | `feature/engineering-terraform-skill` |
| `fix/` | Bug fix | `fix/seo-keyword-density-calc` |
| `docs/` | Documentation only | `docs/marketing-skill-examples` |

---

## Creating a New Skill

### Skill Package Structure

Every skill lives inside a domain directory and follows this layout:

```
<domain>/<skill-name>/
├── SKILL.md              # Master documentation (required)
├── scripts/              # Python CLI tools (required if adding tools)
│   └── tool_name.py
├── references/           # Expert knowledge bases
│   └── domain-guide.md
└── assets/               # User-facing templates
    └── template.md
```

### Authoring Workflow

1. Read the [Skill Authoring Standard](standards/skill-authoring-standard.md) before writing anything.
2. Create the directory structure under the appropriate domain folder.
3. Write `SKILL.md` following the patterns in the authoring standard.
4. Add Python tools in `scripts/` and reference material in `references/`.
5. Validate quality (see requirements below).

Knowledge flows from `references/` into `SKILL.md` workflows, executed via `scripts/`, and applied using `assets/` templates. Keep this pipeline intact.

---

## Skill Quality Requirements

Every skill must meet these standards before it can be merged.

### SKILL.md Requirements

1. **YAML frontmatter** -- Include all required fields: `name`, `description`, `version`, `updated`, `domain`, `tags`.
2. **Trigger clause** -- The description must contain a "Use when..." sentence that tells AI assistants when to activate the skill.
3. **Third-person agent voice** -- Write as instructions to an AI agent ("The agent analyzes..."), not as a tutorial ("You should analyze...").
4. **Numbered workflow steps** -- Every workflow must use numbered steps with explicit validation checkpoints (e.g., "Validate: confirm output contains at least 3 recommendations").
5. **Anti-patterns section** -- List at least 3 things the skill should never do.
6. **Length limits** -- Under 500 lines and 3,000 words. Skills that exceed this should be split.
7. **Concrete examples** -- Include examples with realistic data, not placeholder text. "Acme Corp Q3 revenue of $2.4M" beats "Company X revenue of $N".

### Quality Score

If the quality scorer is available, run it against your skill:

```bash
python scripts/skill_quality_scorer.py <domain>/<skill-name>
```

Target a score of **70 or higher**. Skills below 70 will be sent back for revision.

---

## Python Tool Standards

Python tools are the executable backbone of each skill. Every script must follow these rules.

### Hard Requirements

| Rule | Detail |
|------|--------|
| Standard library only | Zero `pip install` dependencies. Use `os`, `json`, `argparse`, `csv`, `pathlib`, etc. |
| argparse CLI | Every tool must define `--help` with a clear description of purpose and arguments. |
| Dual output format | Support `--format json` and `--format human` (default: human). |
| Compiles cleanly | Must pass `python -m py_compile <file>`. |
| No ML/LLM calls | No imports of `openai`, `anthropic`, `transformers`, or similar. Skills stay portable and fast. |
| 150-300 lines | Real logic, not boilerplate. Tools under 150 lines likely lack substance; over 300 should be split. |

### Integration Testing

If the integration test runner is available, run it before submitting:

```bash
python scripts/integration_test_runner.py --skill <domain>/<skill-name>
```

### Example Tool Skeleton

```python
#!/usr/bin/env python3
"""Brief description of what this tool does."""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        description="One-line description shown in --help"
    )
    parser.add_argument("input", help="Path to input file or data source")
    parser.add_argument(
        "--format",
        choices=["json", "human"],
        default="human",
        help="Output format (default: human)",
    )
    args = parser.parse_args()

    result = analyze(args.input)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


def analyze(input_path):
    """Core logic goes here. Returns a dict."""
    # Real analysis, no stubs
    return {"status": "ok"}


def print_human(result):
    """Readable console output."""
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
```

---

## Pull Request Process

### Before Opening a PR

1. **Commit with conventional commits.** Format: `<type>(<domain>): <description>`

   ```bash
   feat(engineering): add terraform-skill with 3 automation tools
   fix(marketing): correct CTR calculation in campaign-analyzer
   docs(product-team): add RICE scoring examples
   ```

2. **Run the review gate:**

   ```bash
   /review
   ```

3. **Run the security scan:**

   ```bash
   /security-scan
   ```

4. **Verify compilation of all Python tools:**

   ```bash
   python -m py_compile <domain>/<skill-name>/scripts/*.py
   ```

### Opening the PR

- Target the **dev** branch. Never open a PR directly to `main`.
- One skill per PR unless skills are tightly coupled (e.g., a skill and its companion agent).
- Use this PR description template:

```markdown
## What this skill does
<1-2 sentences>

## Tools added
- `tool_name.py` -- brief description
- `other_tool.py` -- brief description

## Quality score
<score> / 100

## Checklist
- [ ] YAML frontmatter complete
- [ ] "Use when..." trigger clause present
- [ ] Numbered workflows with validation checkpoints
- [ ] Anti-patterns section included
- [ ] Python tools compile cleanly
- [ ] Integration tests pass
- [ ] No secrets or credentials committed
```

---

## Skill Review Criteria

Reviewers evaluate every skill against these questions:

1. **Does it save users 40%+ time?** The skill must demonstrably reduce effort compared to doing the work manually or with generic AI prompting.
2. **Is it opinionated?** Good skills take positions and recommend specific approaches. They do not just list options and say "it depends."
3. **Is it self-contained?** No dependencies on other skills. A user must be able to extract the skill folder and use it in isolation.
4. **Are examples concrete and realistic?** Real company names, plausible numbers, specific scenarios. No "Company X" or "lorem ipsum."
5. **Would a senior professional find it useful?** The skill must encode genuine domain expertise, not surface-level summaries.

A skill that fails on any of these criteria will be sent back with specific feedback.

---

## Code of Conduct

We are committed to providing a welcoming and respectful environment for everyone.

- Be respectful and constructive in all interactions.
- Focus feedback on the work, not the person.
- Assume good intent. Ask clarifying questions before criticizing.
- No harassment, discrimination, or personal attacks of any kind.

If a `CODE_OF_CONDUCT.md` exists in the repository root, it takes precedence over this summary.

---

## Recognition

- All contributors are acknowledged in release notes.
- Significant contributors (3+ merged skills or major improvements) are listed in the project README.
- Skill authors are credited in the YAML frontmatter `author` field of the skills they create.

---

## Quick Reference Checklist

Use this checklist before submitting any PR:

```
[ ] Branched from dev (not main)
[ ] Branch name follows convention (feature/, fix/, docs/)
[ ] Conventional commit messages used
[ ] SKILL.md has YAML frontmatter with all required fields
[ ] "Use when..." trigger clause in description
[ ] Third-person agent voice throughout
[ ] Numbered workflow steps with validation checkpoints
[ ] Anti-patterns section with 3+ entries
[ ] Under 500 lines / 3,000 words
[ ] Concrete examples with realistic data
[ ] Python tools use standard library only
[ ] Python tools have argparse with --help
[ ] Python tools support --format json and --format human
[ ] All Python files pass py_compile
[ ] No secrets, API keys, or credentials
[ ] /review gate passed
[ ] /security-scan passed
[ ] PR targets dev branch
[ ] One skill per PR
```

---

**Questions?** Open a GitHub issue with the `question` label, or start a discussion in the repository's Discussions tab.
