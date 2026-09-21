# Changelog — @borghei/claude-skills (CLI)

All notable changes to the npm CLI. The skills library itself is versioned separately in the root [CHANGELOG.md](../CHANGELOG.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-22

### Added

- Live skill catalog: `list`, `search`, `info` and `add` read the current catalog from the repository's `main` branch, so new skills are available without an npm release. The catalog is cached for an hour and falls back to the bundled copy when offline.
- `CLAUDE_SKILLS_OFFLINE`, `CLAUDE_SKILLS_CACHE_DIR` and `CLAUDE_SKILLS_CATALOG_URL` environment variables.

### Changed

- Bundled catalog updated from 229 to 372 skills, including the files added to existing skills since 0.1.0.

### Fixed

- `add --dir <path>` no longer requires a detected AI assistant, as documented.

### Security

- A fetched catalog is rejected if any skill name could escape the install directory.

## [0.1.0] - 2026-04-19

- Initial release: `list`, `search`, `info`, `add`, `update`, `remove`, `create`; target detection for 9 AI assistants; lockfile.
