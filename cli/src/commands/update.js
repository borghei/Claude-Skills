import kleur from "kleur";
import { findSkill } from "../manifest.js";
import { downloadSkill } from "../download.js";
import { loadLockfile, saveLockfile, recordInstall } from "../lockfile.js";
import { getTarget } from "../detect.js";
import { log } from "../ui.js";
import { rm } from "node:fs/promises";
import { resolve } from "node:path";

export async function updateCommand(skillName) {
  const lockfile = await loadLockfile();
  const installed = lockfile.installed;

  if (Object.keys(installed).length === 0) {
    log.warn("No skills are installed here.");
    return;
  }

  const toUpdate = skillName
    ? { [skillName]: installed[skillName] }
    : installed;

  if (skillName && !installed[skillName]) {
    log.error(`${skillName} is not installed here.`);
    process.exit(1);
  }

  for (const [name, record] of Object.entries(toUpdate)) {
    const latest = await findSkill(name);
    if (latest.version === record.version) {
      log.dim(`${name}: already at ${record.version}`);
      continue;
    }

    log.info(`${kleur.cyan(name)}: ${record.version} → ${latest.version}`);
    const installPath = resolve(process.cwd(), record.path);
    await rm(installPath, { recursive: true, force: true });
    await downloadSkill(latest, installPath);
    const target = getTarget(record.target);
    recordInstall(lockfile, latest, target, record.path);
  }

  await saveLockfile(lockfile);
  log.success("Update complete.");
}
