---
title: Authoring Skills
---

# Authoring a New Skill

This guide covers how to create a new skill that follows the Claude Skills standard package structure.

## Skill Package Structure

Every skill follows this layout:

```
skill-name/
├── SKILL.md        # Master documentation (required)
├── scripts/        # Python CLI tools (recommended)
│   └── tool.py
├── references/     # Expert knowledge bases (optional)
│   └── guide.md
└── assets/         # User templates (optional)
    └── template.md
```

## Step 1: Create the SKILL.md

The SKILL.md is the heart of every skill. It must include YAML frontmatter:

```yaml
---
name: my-skill-name
description: >-
  One paragraph describing what this skill does and when to use it.
version: 1.0.0
license: MIT + Commons Clause
category: engineering          # Domain folder name
subdomain: my-subdomain       # Sub-category within the domain
tags:
  - relevant-tag
  - another-tag
tools:
  - scripts/my_tool.py
---
```

After the frontmatter, include:

1. **When to use** -- Clear trigger conditions
2. **Workflows** -- Step-by-step procedures
3. **Best practices** -- Domain expertise
4. **Tool reference** -- How to run each script

## Step 2: Write Python Tools

Tools should be self-contained CLI scripts using the standard library only.

```python
#!/usr/bin/env python3
"""Tool description -- what it does and what it outputs."""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    # Analysis logic here
    results = analyze(args.input)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print_human_readable(results)

if __name__ == "__main__":
    main()
```

**Tool requirements:**

- Standard library only (no pip dependencies if possible)
- Support both JSON and human-readable output
- Accept file/directory paths as arguments
- Exit with code 0 on success, non-zero on failure
- No LLM/ML calls (keeps skills portable and fast)

## Step 3: Add References (Optional)

Reference files in `references/` contain curated expert knowledge that the AI assistant reads for context. These are markdown files with frameworks, checklists, and domain expertise.

## Step 4: Add Templates (Optional)

Templates in `assets/` are ready-to-use deliverable templates that users customize. Examples: PRD template, audit report template, etc.

## Step 5: Validate Your Skill

Use the skill-tester to validate your package:

```bash
python engineering/skill-tester/scripts/skill_validator.py path/to/your-skill/
```

This checks:

- YAML frontmatter completeness
- Python script syntax and conventions
- File structure compliance
- Documentation quality

## Quality Checklist

- [ ] SKILL.md has valid YAML frontmatter
- [ ] Description is one clear paragraph
- [ ] At least one Python tool in `scripts/`
- [ ] Tools use standard library only
- [ ] Tools support `--format json` output
- [ ] Workflows are step-by-step and actionable
- [ ] Skill saves users 40%+ time on the task

See `standards/` in the repository for the complete authoring standards reference.
