# Supply Chain and Release Companion

Tier: focused, full.

## Select this companion when

The repository contains the machinery that turns source into something
shipped: dependency manifests and resolvers, code generators, CI workflow
definitions, build scripts, container build files, release and signing steps,
auto-update logic, or a plugin and extension system.

The question throughout is who can change what ends up running, and with whose
authority. Vulnerabilities inside third-party packages are a dependency-audit
matter; this file is about the target's own handling of inputs and authority.

## Ground rules

```text
- Read workflow, build, and release definitions as code that runs with
  credentials. Identify the trigger, who can cause it, what it checks out,
  and which secrets and permissions are present at each step.
- A finding needs an actor (outside contributor, low-privilege maintainer,
  compromised dependency, plugin author), the step they influence, and what
  they gain: code in a release, a secret, write access, a signed artifact.
- Do not run workflows, publish, sign, or contact a registry. Evidence comes
  from the definitions in the repository and from rendering or linting them
  locally.
- Repository settings, branch protection, environment approvals, and registry
  configuration that are not in source are unknown. If the defect depends on
  one, it is needs_validation with that setting as the blocker.
- An unpinned version is a hardening note unless you can show the path from
  that mutability to code running with authority.
```

## Hunting classes

### Dependency source and name confusion

The resolver can be made to fetch a package from an unintended source: an
internal name resolvable from a public registry, several indexes with no
priority rule, scoped names missing a registry mapping, a typo-adjacent name,
or a dependency pulled from a branch or URL someone else controls.

### Mutable build inputs

Anything fetched at build time by a reference that can change: tags, branches,
`latest`, unpinned base images, install scripts piped from a URL, actions or
shared pipeline steps referenced by a moving tag, lockfiles absent or ignored
by the install command actually used.

### Generated code without provenance

Checked-in generated files, vendored copies, or minified bundles that the
build does not regenerate or verify, so reviewed source and shipped code can
differ. Also generators that run with network or file access during the build.

### Build context leakage

Secrets, credentials, version-control metadata, or local config copied into an
image layer, an artifact, a source map, or a published package because ignore
rules or copy steps are too broad.

### Outsider code running with pipeline authority

A workflow that runs on events an outsider can trigger and both checks out
their code and holds secrets or write permission. Look at each trigger type,
what ref is checked out, and whether install or test steps execute
contributor-controlled scripts before any gate.

### Workflow expression and command injection

Event fields an outsider controls — titles, branch names, labels, comment
bodies, file names — interpolated into a shell step, a script, or an
environment file. The fix is passing them as data, so the finding is the
interpolation into an interpreter.

### Shared caches, artifacts, and workspaces

Caches or artifacts written by a low-trust job and read by a privileged one;
cache keys an outsider can predict or collide; self-hosted runners that keep
state between jobs from different trust levels.

### Over-privileged automation identity

Tokens, deploy keys, or cloud roles granted to a job that needs less:
repository-wide write for a lint job, long-lived secrets where a short-lived
identity exists, one credential shared across environments.

### Artifact substitution between build and release

The thing tested is not provably the thing published: rebuild at release
time, promotion by mutable name, artifacts fetched without digest
verification, a gap between stages where a lower-trust job can replace the
file.

### Release approval and signing gaps

Who can cut a release, and is that enforced in the pipeline definition? Signing
keys reachable from ordinary jobs, signing that happens before checks finish,
signatures produced but never verified by the consumer, provenance not bound
to the source commit.

### Update metadata and rollback

For a self-updating client: update manifests fetched without authentication of
their content, version comparison that accepts an older release, a signature
checked on the package but not on the metadata that selects it, and fallback
to an unverified channel on error.

### Plugin and extension privilege

Third-party code loaded into the product: what it can reach by default, how
its identity and version are verified, whether an update can widen its
permissions without consent, and whether one plugin can affect another or the
host's secrets.

## Cross-cutting moves

- For each job, list trigger, actor, checked-out ref, secrets in scope, and
  token permissions. The dangerous combination is outsider-triggered, with
  outsider code, with authority.
- Follow one artifact from commit to consumer and note every point where it is
  identified by name instead of by digest.
- Check the unhappy paths of verification: missing signature, unreachable key
  server, expired certificate.
- Compare the documented release process with what the definitions enforce.
- Look at composite steps, reusable workflows, and scripts called from the
  pipeline; the injection is often one level down.

## Evidence bar

- Confirmed needs the definition text that grants the authority, the input the
  actor controls, and a local demonstration where one is possible: the
  rendered command line, a linter or dry-run result, a resolver run against
  local fixtures.
- Anything that depends on hosted settings not present in the repository is
  `needs_validation`, with an owner check naming the exact setting.
- Never demonstrate by triggering a real pipeline, publishing a package, or
  registering a name.
- Severity reflects what the actor obtains: release integrity and signing
  authority rank above a read-only secret, which ranks above a cache nuisance.
