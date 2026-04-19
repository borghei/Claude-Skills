import { rm } from "node:fs/promises";
import { resolve } from "node:path";
import { loadLockfile, saveLockfile, removeInstall } from "../lockfile.js";
import { log } from "../ui.js";

export async function removeCommand(skillName) {
  const lockfile = await loadLockfile();
  const record = lockfile.installed[skillName];

  if (!record) {
    log.error(`${skillName} is not installed here.`);
    process.exit(1);
  }

  await rm(resolve(process.cwd(), record.path), { recursive: true, force: true });
  removeInstall(lockfile, skillName);
  await saveLockfile(lockfile);
  log.success(`Removed ${skillName} from ${record.path}`);
}
