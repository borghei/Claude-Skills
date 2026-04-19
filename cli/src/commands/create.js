import { access, mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { log } from "../ui.js";

const SKILL_TEMPLATE = (name, domain) => `---
name: ${name}
description: >
  This skill should be used when the user asks to ... (describe trigger cases here).
license: MIT + Commons Clause
metadata:
  version: 0.1.0
  author: your-name
  category: ${domain}
  domain: ${domain}
  updated: ${new Date().toISOString().slice(0, 10)}
  tags: []
---

# ${name.split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ")}

> **Category:** ${domain[0].toUpperCase() + domain.slice(1)}

## Overview

One-paragraph summary of what this skill does and when to use it.

## Quick Start

\`\`\`bash
# Example invocation of the primary script
python scripts/main.py --help
\`\`\`

## When to Use This

- Trigger 1
- Trigger 2
- Trigger 3

## Workflow

1. Step one
2. Step two
3. Step three

## Scripts

- \`scripts/main.py\` — what it does

## References

- \`references/guide.md\` — expert knowledge base

## Assets

- \`assets/template.md\` — ready-to-use template
`;

const SCRIPT_TEMPLATE = `#!/usr/bin/env python3
"""Primary script for this skill. Replace with actual logic."""

import sys


def main(argv: list[str]) -> int:
    print("Replace this with the skill's real behavior.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
`;

export async function createCommand(name, options) {
  const domain = options.domain || "engineering";
  const skillDir = join(process.cwd(), name);

  try {
    await access(skillDir);
    log.error(`Directory "${name}" already exists. Pick another name.`);
    process.exit(1);
  } catch {}

  await mkdir(join(skillDir, "scripts"), { recursive: true });
  await mkdir(join(skillDir, "references"), { recursive: true });
  await mkdir(join(skillDir, "assets"), { recursive: true });

  await writeFile(join(skillDir, "SKILL.md"), SKILL_TEMPLATE(name, domain), "utf8");
  await writeFile(join(skillDir, "scripts", "main.py"), SCRIPT_TEMPLATE, "utf8");
  await writeFile(join(skillDir, "references", "guide.md"), `# ${name} — reference\n\nExpert knowledge base for this skill.\n`, "utf8");
  await writeFile(join(skillDir, "assets", "template.md"), `# ${name} — template\n\nReady-to-use template for this skill.\n`, "utf8");

  log.success(`Created ${name}/`);
  log.info("");
  log.dim("Next steps:");
  log.dim(`  1. Edit ${name}/SKILL.md and fill in the trigger description`);
  log.dim(`  2. Replace ${name}/scripts/main.py with real logic`);
  log.dim(`  3. Run the skill locally, iterate until it works`);
  log.dim(`  4. Submit a PR to github.com/borghei/Claude-Skills`);
}
