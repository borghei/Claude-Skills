import kleur from "kleur";
import { loadManifest } from "../manifest.js";
import { log, truncate } from "../ui.js";

export async function searchCommand(query, options) {
  const manifest = await loadManifest();
  const q = query.toLowerCase();

  const matches = manifest.skills
    .map((s) => {
      let score = 0;
      if (s.name.toLowerCase() === q) score += 100;
      else if (s.name.toLowerCase().includes(q)) score += 50;
      if (Array.isArray(s.tags) && s.tags.some((t) => t.toLowerCase().includes(q))) score += 20;
      if ((s.description || "").toLowerCase().includes(q)) score += 10;
      if (s.domain.toLowerCase().includes(q)) score += 5;
      return { s, score };
    })
    .filter((m) => m.score > 0)
    .sort((a, b) => b.score - a.score);

  if (options.json) {
    process.stdout.write(JSON.stringify(matches.map((m) => m.s), null, 2) + "\n");
    return;
  }

  if (matches.length === 0) {
    log.warn(`No skills match "${query}".`);
    log.dim(`Try \`claude-skills list\` to see everything available.`);
    return;
  }

  log.header(`Found ${matches.length} skill${matches.length === 1 ? "" : "s"} for "${query}"`);
  for (const { s } of matches) {
    process.stdout.write(
      `  ${kleur.cyan(s.name.padEnd(32))} ${kleur.dim(s.domain.padEnd(20))} ${truncate(
        s.description,
        60,
      )}\n`,
    );
  }
}
