# CI/CD Pipeline Guide

Read this when designing a pipeline, reviewing one, or adapting what `scripts/pipeline_generator.py` produced.

## Stage Order

Run the cheapest checks first so a broken change fails in minutes, not after a 15-minute build.

| Order | Stage | Typical time | Fails on |
|-------|-------|--------------|----------|
| 1 | Install (cached) | 10-60 s | Lockfile drift, unreachable registry |
| 2 | Lint and format check | 10-60 s | Style, static errors, type errors |
| 3 | Unit tests | 1-5 min | Logic regressions |
| 4 | Build | 1-5 min | Compile errors, bundling |
| 5 | Container build | 1-5 min | Dockerfile errors, base image issues |
| 6 | Integration / e2e tests | 5-15 min | Contract and wiring problems |
| 7 | Deploy to staging, smoke test | 2-10 min | Config, migrations, infra |
| 8 | Promote to production (gated) | n/a | Approval, change freeze |

The generator emits stages 1 to 5. Stages 6 to 8 depend on the user's environments and registry, so add them by hand once the build is green.

## Install and Caching

- Install from the lockfile, never from ranges: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable` (Berry) or `--frozen-lockfile` (v1), `uv sync --frozen`, `poetry install`, `cargo fetch --locked`, `go mod download`.
- Key the cache on the lockfile hash. A key that never changes serves stale dependencies; a key that changes every run never hits.
- Cache the package manager's download cache, not `node_modules` or a virtualenv. Download caches are portable across runner images; installed trees are not.
- A missing lockfile is a finding in itself. The generator falls back to `npm install` and warns.

| Stack | Cache directory | Key file |
|-------|-----------------|----------|
| npm | `~/.npm` (`npm_config_cache`) | `package-lock.json` |
| pnpm | store dir (`npm_config_store_dir`) | `pnpm-lock.yaml` |
| yarn | `YARN_CACHE_FOLDER` | `yarn.lock` |
| pip / uv | `PIP_CACHE_DIR`, `UV_CACHE_DIR` | `requirements.txt`, `uv.lock` |
| Go | `GOMODCACHE`, `GOCACHE` | `go.sum` |
| Cargo | `CARGO_HOME`, `target/` | `Cargo.lock` |
| Maven / Gradle | `.m2/repository`, `GRADLE_USER_HOME` | `pom.xml`, `build.gradle(.kts)` |

On GitHub Actions the `setup-*` actions handle the cache (`cache: npm`, `cache: pip`, `go-version-file`). `setup-node` fails when `cache` is set and there is no lockfile, so the generator drops the cache in that case; `setup-python` looks for `requirements.txt` by default, so the generator sets `cache-dependency-path` to the file it actually found (`requirements*.txt`, `pyproject.toml`, `uv.lock` or `poetry.lock`). On GitLab, CircleCI and Jenkins the cache directories must sit inside the project directory, which is why the generator sets them to workspace-relative paths.

## Platform Notes

| Concern | GitHub Actions | GitLab CI | CircleCI | Jenkins |
|---------|----------------|-----------|-----------|---------|
| File | `.github/workflows/*.yml` | `.gitlab-ci.yml` | `.circleci/config.yml` | `Jenkinsfile` |
| Runtime | `setup-*` action on a VM | job `image:` | executor `docker:` image | `agent { docker { image } }` |
| Cache | built into `setup-*`, `actions/cache` | `cache:key:files` | `restore_cache` / `save_cache` with `checksum` | volume or plugin; keep caches in the workspace |
| Docker build | Buildx action, `type=gha` layer cache | Docker-in-Docker service | `setup_remote_docker` | agent with a Docker socket |
| Secrets | repository or environment secrets | masked, protected variables | contexts | credentials binding |
| Approval gate | `environment:` with required reviewers | `when: manual` + protected environment | `type: approval` job | `input` step |

Yarn 2 and later (Berry) is detected from `.yarnrc.yml`, a `packageManager` of `yarn@2` or above in `package.json`, or a `yarn.lock` that starts with `__metadata:`; Berry gets `yarn install --immutable`, Yarn 1 gets `--frozen-lockfile`. Yarn 2 and later is activated through Corepack. On GitHub the generated workflow runs `corepack enable` before `setup-node`, otherwise the runner's global Yarn 1 handles the install and rejects `--immutable`.

CircleCI's `checkout` step needs `git`, which the `-slim` Node and Python images do not include. The generated config installs `git` and `openssh-client` before `checkout` when they are missing, and runs the Docker build job on `cimg/base:current`. Switching the main job to a CircleCI convenience image (`cimg/node`, `cimg/python`) removes that step.

A lint or test tool that is configured (for example `[tool.ruff]` in `pyproject.toml`) but not declared as a dependency would not exist in CI. The generator then installs it inside the step (`pip install ruff && python -m ruff check .`, `uv run --with ruff ...`) and warns; the proper fix is to add it to the dev dependencies.

Jenkins Docker agents run as the Jenkins user, not root. `pip install` then falls back to a user install, so the generated Jenkinsfile sets `HOME` to the workspace and calls tools as `python -m pytest`.

## Security Defaults

- **Least privilege.** Set `permissions: contents: read` at the top of every GitHub workflow and widen per job only where needed (for example `packages: write` on the job that pushes to GHCR, `id-token: write` for OIDC to a cloud).
- **No secrets in the file.** Reference the platform's secret store. Prefer OIDC federation to a cloud over long-lived keys.
- **Pin what you run.** The generator deliberately uses major-version tags (`actions/checkout@v4`) and versioned images (`node:22-bookworm-slim`): they stay readable and pick up fixes, and it cannot look up commit SHAs offline. Tags are mutable, so for high-assurance repositories replace each third-party action with its full commit SHA (keep the tag as a comment) and let Dependabot or Renovate bump them.
- **Version files are validated.** `.nvmrc` is accepted for Node majors 18 to 26 and `.python-version` for Python 3.8 to 3.14. Anything else, including text that is not a plain version, is ignored with a warning and the default (Node 22, Python 3.12) is used, so a crafted file cannot inject text into an image name or Jenkinsfile and an impossible version does not produce a missing image.
- **Untrusted input.** Never interpolate `${{ github.event.* }}` fields (PR titles, branch names) straight into `run:`; pass them through `env:` and quote them. Avoid `pull_request_target` with a checkout of the PR head.
- **Fork PRs** get no secrets on GitHub by default. Keep it that way.

## Speed

- `concurrency` with `cancel-in-progress` (GitHub) or `interruptible: true` (GitLab) stops superseded runs on the same branch.
- Set a job timeout (the generator uses 20 minutes). A hung job otherwise burns hours of runner time.
- Run independent jobs in parallel: lint and tests do not need to wait for each other once install is cached.
- Use a test matrix only for versions you actually support.
- Copy dependency manifests before source in the Dockerfile so the dependency layer survives code changes.

## Build Once, Promote the Artifact

Build the image once, tag it with the commit SHA, and deploy that exact digest to staging and production. Rebuilding for production produces a different artifact from the one you tested. Never deploy `latest`.

## Review Checklist

- [ ] Lockfile committed and the install command refuses drift
- [ ] Cache keyed on the lockfile hash
- [ ] Lint and unit tests run before build and container stages
- [ ] Top-level `permissions` set to read-only (GitHub)
- [ ] No inline secrets, tokens or passwords
- [ ] Actions and images pinned to a version, never `latest`
- [ ] Job timeouts and concurrency cancellation set
- [ ] Production deploy behind an approval gate or protected environment
- [ ] The artifact deployed is the one that was built and tested
