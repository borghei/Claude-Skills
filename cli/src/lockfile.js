import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const LOCKFILE_NAME = ".claude-skills.json";

export async function loadLockfile(cwd = process.cwd()) {
  try {
    const raw = await readFile(join(cwd, LOCKFILE_NAME), "utf8");
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === "ENOENT") {
      return { version: 1, installed: {} };
    }
    throw err;
  }
}

export async function saveLockfile(lockfile, cwd = process.cwd()) {
  const path = join(cwd, LOCKFILE_NAME);
  await writeFile(path, JSON.stringify(lockfile, null, 2) + "\n", "utf8");
}

export function recordInstall(lockfile, skill, target, installPath) {
  lockfile.installed[skill.name] = {
    version: skill.version,
    domain: skill.domain,
    target: target.name,
    path: installPath,
    files: skill.files,
    installed_at: new Date().toISOString(),
  };
  return lockfile;
}

export function removeInstall(lockfile, skillName) {
  delete lockfile.installed[skillName];
  return lockfile;
}
