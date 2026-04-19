import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const MANIFEST_PATH = resolve(__dirname, "..", "skills.json");

let cached = null;

export async function loadManifest() {
  if (cached) return cached;
  const raw = await readFile(MANIFEST_PATH, "utf8");
  cached = JSON.parse(raw);
  return cached;
}

export async function findSkill(name) {
  const manifest = await loadManifest();
  const exact = manifest.skills.find((s) => s.name === name);
  if (exact) return exact;
  const partial = manifest.skills.filter((s) => s.name.includes(name));
  if (partial.length === 1) return partial[0];
  if (partial.length > 1) {
    const err = new Error(
      `"${name}" matches ${partial.length} skills. Be more specific:\n  ${partial
        .map((s) => s.name)
        .join("\n  ")}`,
    );
    err.code = "AMBIGUOUS_MATCH";
    throw err;
  }
  const err = new Error(`Skill not found: ${name}`);
  err.code = "NOT_FOUND";
  throw err;
}
