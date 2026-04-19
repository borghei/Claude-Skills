import kleur from "kleur";
import { loadManifest } from "../manifest.js";
import { log, truncate } from "../ui.js";

export async function listCommand(options) {
  const manifest = await loadManifest();
  let skills = manifest.skills;

  if (options.domain) {
    skills = skills.filter((s) => s.domain === options.domain);
    if (skills.length === 0) {
      log.error(`No skills found in domain "${options.domain}".`);
      process.exit(1);
    }
  }

  if (options.json) {
    process.stdout.write(JSON.stringify(skills, null, 2) + "\n");
    return;
  }

  const byDomain = new Map();
  for (const s of skills) {
    if (!byDomain.has(s.domain)) byDomain.set(s.domain, []);
    byDomain.get(s.domain).push(s);
  }

  for (const [domain, domainSkills] of [...byDomain.entries()].sort()) {
    log.header(`${domain} (${domainSkills.length})`);
    for (const s of domainSkills) {
      process.stdout.write(
        `  ${kleur.cyan(s.name.padEnd(32))} ${kleur.dim(truncate(s.description, 70))}\n`,
      );
    }
  }

  log.info("");
  log.dim(
    `${skills.length} skill${skills.length === 1 ? "" : "s"} across ${byDomain.size} domain${
      byDomain.size === 1 ? "" : "s"
    }`,
  );
}
