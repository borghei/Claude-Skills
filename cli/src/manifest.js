import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const BUNDLED_PATH = resolve(__dirname, "..", "skills.json");

// The live catalog is the same file the repo's manifest workflow keeps current on
// main, so new skills reach the CLI without an npm release. The bundled copy is
// the fallback when offline or when the fetch fails.
const DEFAULT_CATALOG_URL =
  "https://raw.githubusercontent.com/borghei/Claude-Skills/main/cli/skills.json";
const CACHE_TTL_MS = 60 * 60 * 1000;
const FETCH_TIMEOUT_MS = 5000;

let cached = null;

function catalogUrl() {
  return process.env.CLAUDE_SKILLS_CATALOG_URL || DEFAULT_CATALOG_URL;
}

function cacheFile() {
  const base =
    process.env.CLAUDE_SKILLS_CACHE_DIR ||
    join(process.env.XDG_CACHE_HOME || join(homedir(), ".cache"), "claude-skills");
  return join(base, "skills.json");
}

function isOffline() {
  return ["1", "true"].includes(String(process.env.CLAUDE_SKILLS_OFFLINE).toLowerCase());
}

// Skill names become directory names on install, so a fetched catalog with a
// name that could escape the install directory is rejected outright.
const SAFE_NAME = /^[a-z0-9][a-z0-9._-]*$/i;

function isValidManifest(m) {
  return Boolean(
    m &&
      Array.isArray(m.skills) &&
      m.skills.length > 0 &&
      m.schema_version &&
      m.skills.every((s) => typeof s?.name === "string" && SAFE_NAME.test(s.name) && !s.name.includes("..")),
  );
}

async function readJson(path) {
  try {
    const m = JSON.parse(await readFile(path, "utf8"));
    return isValidManifest(m) ? m : null;
  } catch {
    return null;
  }
}

// The bundled copy is the last resort, so it fails loudly instead of returning null.
async function readBundled() {
  const m = JSON.parse(await readFile(BUNDLED_PATH, "utf8"));
  if (!isValidManifest(m)) {
    throw new Error(`Bundled skill catalog is invalid: ${BUNDLED_PATH}. Reinstall @borghei/claude-skills.`);
  }
  return m;
}

async function readCache({ freshOnly }) {
  const path = cacheFile();
  try {
    const { mtimeMs } = await stat(path);
    if (freshOnly && Date.now() - mtimeMs > CACHE_TTL_MS) return null;
  } catch {
    return null;
  }
  return readJson(path);
}

async function fetchRemote() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(catalogUrl(), { signal: controller.signal });
    if (!res.ok) return null;
    const m = await res.json();
    return isValidManifest(m) ? m : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

async function writeCache(manifest) {
  try {
    const path = cacheFile();
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, JSON.stringify(manifest));
  } catch {
    // A read-only home directory must not break the command.
  }
}

// Resolution order: fresh cache → live catalog → stale cache → bundled copy.
// Set CLAUDE_SKILLS_OFFLINE=1 to use only the bundled copy.
export async function loadManifest() {
  if (cached) return cached;
  if (isOffline()) {
    cached = await readBundled();
    return cached;
  }
  cached = await readCache({ freshOnly: true });
  if (cached) return cached;

  const remote = await fetchRemote();
  if (remote) {
    await writeCache(remote);
    cached = remote;
    return cached;
  }
  cached = (await readCache({ freshOnly: false })) || (await readBundled());
  return cached;
}

// Test hook: forget the in-process copy so the next load re-resolves.
export function resetManifestCache() {
  cached = null;
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
