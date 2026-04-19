import kleur from "kleur";
import { findSkill } from "../manifest.js";
import { log, formatSize } from "../ui.js";

export async function infoCommand(name, options) {
  const skill = await findSkill(name);

  if (options.json) {
    process.stdout.write(JSON.stringify(skill, null, 2) + "\n");
    return;
  }

  log.header(skill.name);
  process.stdout.write(`  ${kleur.dim("domain:")}      ${skill.domain}\n`);
  process.stdout.write(`  ${kleur.dim("version:")}     ${skill.version}\n`);
  if (skill.updated) process.stdout.write(`  ${kleur.dim("updated:")}     ${skill.updated}\n`);
  if (skill.author) process.stdout.write(`  ${kleur.dim("author:")}      ${skill.author}\n`);
  process.stdout.write(`  ${kleur.dim("path:")}        ${skill.path}\n`);
  process.stdout.write(`  ${kleur.dim("size:")}        ${formatSize(skill.size_bytes)}\n`);
  process.stdout.write(`  ${kleur.dim("files:")}       ${skill.files.length}\n`);

  const parts = [];
  if (skill.has_scripts) parts.push("scripts");
  if (skill.has_references) parts.push("references");
  if (skill.has_assets) parts.push("assets");
  if (parts.length) process.stdout.write(`  ${kleur.dim("includes:")}    ${parts.join(", ")}\n`);

  if (Array.isArray(skill.tags) && skill.tags.length) {
    process.stdout.write(`  ${kleur.dim("tags:")}        ${skill.tags.join(", ")}\n`);
  }

  if (skill.description) {
    log.info("");
    process.stdout.write(`${skill.description}\n`);
  }

  log.info("");
  log.dim(`Install with: claude-skills add ${skill.name}`);
}
