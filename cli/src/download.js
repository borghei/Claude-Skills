import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

const RAW_BASE = "https://raw.githubusercontent.com/borghei/Claude-Skills/main";

export async function downloadSkill(skill, destDir, onProgress) {
  await mkdir(destDir, { recursive: true });
  const results = [];

  for (const file of skill.files) {
    const url = `${RAW_BASE}/${skill.path}/${file}`;
    const destPath = resolve(join(destDir, file));

    if (!destPath.startsWith(resolve(destDir))) {
      throw new Error(`Refusing to write outside destination: ${file}`);
    }

    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Failed to fetch ${file}: HTTP ${res.status}`);
    }
    const buf = Buffer.from(await res.arrayBuffer());
    await mkdir(dirname(destPath), { recursive: true });
    await writeFile(destPath, buf);
    results.push(file);
    if (onProgress) onProgress(file, results.length, skill.files.length);
  }

  return results;
}
