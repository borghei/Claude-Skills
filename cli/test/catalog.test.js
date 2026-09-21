import { test, beforeEach, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdtemp, readFile, utimes, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadManifest, resetManifestCache } from "../src/manifest.js";

const remote = {
  schema_version: "1.0.0",
  skill_count: 1,
  skills: [{ name: "remote-only-skill", domain: "test", description: "", tags: [], files: ["SKILL.md"], path: "x" }],
};

let body = JSON.stringify(remote);
let status = 200;
let hits = 0;
const server = createServer((req, res) => {
  hits += 1;
  res.writeHead(status, { "content-type": "application/json" });
  res.end(body);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const URL_OK = `http://127.0.0.1:${server.address().port}/skills.json`;
after(() => server.close());

beforeEach(async () => {
  resetManifestCache();
  body = JSON.stringify(remote);
  status = 200;
  hits = 0;
  delete process.env.CLAUDE_SKILLS_OFFLINE;
  process.env.CLAUDE_SKILLS_CATALOG_URL = URL_OK;
  process.env.CLAUDE_SKILLS_CACHE_DIR = await mkdtemp(join(tmpdir(), "cs-cache-"));
});

const cachePath = () => join(process.env.CLAUDE_SKILLS_CACHE_DIR, "skills.json");
const bundledCount = async () =>
  JSON.parse(await readFile(new URL("../skills.json", import.meta.url), "utf8")).skills.length;

test("uses the live catalog and writes the cache", async () => {
  const m = await loadManifest();
  assert.equal(m.skills[0].name, "remote-only-skill");
  assert.equal(JSON.parse(await readFile(cachePath(), "utf8")).skills[0].name, "remote-only-skill");
});

test("a fresh cache is used without a network call", async () => {
  await writeFile(cachePath(), JSON.stringify({ ...remote, skills: [{ ...remote.skills[0], name: "cached-skill" }] }));
  const m = await loadManifest();
  assert.equal(m.skills[0].name, "cached-skill");
  assert.equal(hits, 0);
});

test("a stale cache is refreshed from the network", async () => {
  await writeFile(cachePath(), JSON.stringify({ ...remote, skills: [{ ...remote.skills[0], name: "old" }] }));
  const past = new Date(Date.now() - 2 * 60 * 60 * 1000);
  await utimes(cachePath(), past, past);
  const m = await loadManifest();
  assert.equal(m.skills[0].name, "remote-only-skill");
  assert.equal(hits, 1);
});

test("falls back to a stale cache when the network fails", async () => {
  status = 500;
  await writeFile(cachePath(), JSON.stringify({ ...remote, skills: [{ ...remote.skills[0], name: "stale" }] }));
  const past = new Date(Date.now() - 2 * 60 * 60 * 1000);
  await utimes(cachePath(), past, past);
  const m = await loadManifest();
  assert.equal(m.skills[0].name, "stale");
});

test("falls back to the bundled catalog when the network fails and no cache exists", async () => {
  process.env.CLAUDE_SKILLS_CATALOG_URL = "http://127.0.0.1:9/unreachable.json";
  const m = await loadManifest();
  assert.equal(m.skills.length, await bundledCount());
});

test("rejects an invalid remote catalog", async () => {
  body = JSON.stringify({ skills: [] });
  const m = await loadManifest();
  assert.equal(m.skills.length, await bundledCount());
});

test("CLAUDE_SKILLS_OFFLINE=1 uses only the bundled catalog", async () => {
  process.env.CLAUDE_SKILLS_OFFLINE = "1";
  const m = await loadManifest();
  assert.equal(m.skills.length, await bundledCount());
  assert.equal(hits, 0);
});

test("rejects a catalog with a path-traversal skill name", async () => {
  body = JSON.stringify({ ...remote, skills: [{ ...remote.skills[0], name: "../../etc" }] });
  const m = await loadManifest();
  assert.equal(m.skills.length, await bundledCount());
});
