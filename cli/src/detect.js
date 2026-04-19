import { access } from "node:fs/promises";
import { join } from "node:path";

const TARGETS = [
  { name: "claude", markers: [".claude"], installDir: ".claude/skills" },
  { name: "codex", markers: [".codex", "AGENTS.md"], installDir: ".codex/skills" },
  { name: "gemini", markers: [".gemini", "GEMINI.md"], installDir: ".gemini/skills" },
  { name: "cursor", markers: [".cursor", ".cursorrules"], installDir: ".cursor/rules" },
  { name: "copilot", markers: [".github/copilot-instructions.md"], installDir: ".github/skills" },
  { name: "windsurf", markers: [".windsurfrules"], installDir: ".ai-skills" },
  { name: "cline", markers: [".clinerules"], installDir: ".ai-skills" },
  { name: "aider", markers: [".aider.conf.yml", ".aiderignore"], installDir: ".ai-skills" },
  { name: "goose", markers: [".goosehints"], installDir: ".ai-skills" },
];

export const TARGET_NAMES = TARGETS.map((t) => t.name);

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

export async function detectTarget(cwd = process.cwd()) {
  for (const target of TARGETS) {
    for (const marker of target.markers) {
      if (await exists(join(cwd, marker))) {
        return target;
      }
    }
  }
  return null;
}

export function getTarget(name) {
  const target = TARGETS.find((t) => t.name === name);
  if (!target) {
    throw new Error(
      `Unknown target "${name}". Valid: ${TARGET_NAMES.join(", ")}`,
    );
  }
  return target;
}

export function getInstallPath(target, skillName, cwd = process.cwd()) {
  return join(cwd, target.installDir, skillName);
}
