import kleur from "kleur";

export const log = {
  info: (msg) => process.stdout.write(`${msg}\n`),
  success: (msg) => process.stdout.write(`${kleur.green("✓")} ${msg}\n`),
  warn: (msg) => process.stdout.write(`${kleur.yellow("!")} ${msg}\n`),
  error: (msg) => process.stderr.write(`${kleur.red("✗")} ${msg}\n`),
  dim: (msg) => process.stdout.write(`${kleur.dim(msg)}\n`),
  header: (msg) => process.stdout.write(`\n${kleur.bold(msg)}\n`),
};

export function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

export function truncate(text, max = 80) {
  if (!text) return "";
  return text.length <= max ? text : text.slice(0, max - 1) + "…";
}
