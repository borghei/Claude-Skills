import kleur from "kleur";
import { access, rm } from "node:fs/promises";
import { relative } from "node:path";
import { findSkill } from "../manifest.js";
import { detectTarget, getTarget, getInstallPath, TARGET_NAMES } from "../detect.js";
import { downloadSkill } from "../download.js";
import { loadLockfile, saveLockfile, recordInstall } from "../lockfile.js";
import { log, formatSize } from "../ui.js";

async function pathExists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

export async function addCommand(skillName, options) {
  const skill = await findSkill(skillName);

  let target;
  if (options.to) {
    target = getTarget(options.to);
  } else {
    target = await detectTarget();
    if (!target) {
      log.error(
        `Couldn't detect an AI assistant in this directory.\n  Re-run with --to <${TARGET_NAMES.join("|")}>\n  Or cd into a project that has one of: .claude/, .cursor/, .codex/, .gemini/, .cursorrules, .windsurfrules, .clinerules, .goosehints, AGENTS.md`,
      );
      process.exit(1);
    }
  }

  const installPath = options.dir
    ? options.dir
    : getInstallPath(target, skill.name);

  if (await pathExists(installPath)) {
    if (!options.force) {
      log.warn(`${skill.name} is already installed at ${relative(process.cwd(), installPath)}`);
      log.dim("Re-run with --force to overwrite.");
      process.exit(1);
    }
    await rm(installPath, { recursive: true, force: true });
  }

  log.header(`Installing ${kleur.cyan(skill.name)}`);
  log.dim(`  target:  ${target.name}`);
  log.dim(`  path:    ${relative(process.cwd(), installPath) || "."}`);
  log.dim(`  size:    ${formatSize(skill.size_bytes)} · ${skill.files.length} files`);
  log.info("");

  await downloadSkill(skill, installPath, (file, done, total) => {
    process.stdout.write(
      `\r  ${kleur.dim(`[${done}/${total}]`)} ${file.padEnd(60).slice(0, 60)}`,
    );
  });
  process.stdout.write("\r" + " ".repeat(80) + "\r");

  const lockfile = await loadLockfile();
  recordInstall(lockfile, skill, target, relative(process.cwd(), installPath));
  await saveLockfile(lockfile);

  log.success(`Installed ${skill.name}`);
  log.info("");
  printNextSteps(target, skill);
}

function printNextSteps(target, skill) {
  const instructions = {
    claude: `In Claude Code: the skill's auto-discovered. Reference it like "use the ${skill.name} skill".`,
    codex: `In Codex CLI: reference "${skill.name}" in your AGENTS.md or invoke directly.`,
    gemini: `In Gemini CLI: the skill's in .gemini/skills/ and auto-discovered on next run.`,
    cursor: `In Cursor: restart the editor to pick up the new rule. Reference "${skill.name}" in chat.`,
    copilot: `In Copilot: the skill's been placed in .github/skills/. Reference it in your prompts.`,
    windsurf: `In Windsurf: add a reference to .ai-skills/${skill.name}/SKILL.md in your .windsurfrules file.`,
    cline: `In Cline: add a reference to .ai-skills/${skill.name}/SKILL.md in your .clinerules file.`,
    aider: `In Aider: pass the SKILL.md as a file: aider --read .ai-skills/${skill.name}/SKILL.md`,
    goose: `In Goose: add a reference to .ai-skills/${skill.name}/SKILL.md in your .goosehints file.`,
  };
  const tip = instructions[target.name];
  if (tip) log.dim(`Next: ${tip}`);
}
