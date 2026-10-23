#!/usr/bin/env python3
"""Detect a project's stack and generate a CI pipeline for it.

Reads manifests in the project root and generates cached install, lint, test, build and optional
Docker stages for GitHub Actions, GitLab CI, CircleCI or Jenkins. Writes a file only with --output.

Usage:
    python pipeline_generator.py <project-path>
    python pipeline_generator.py <project-path> --platform gitlab-ci --json
    python pipeline_generator.py <project-path> --output .github/workflows/ci.yml
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

PLATFORMS = {"github-actions": ".github/workflows/ci.yml", "gitlab-ci": ".gitlab-ci.yml",
             "circleci": ".circleci/config.yml", "jenkins": "Jenkinsfile"}
IMAGES = {"node": "node:{v}-bookworm-slim", "python": "python:{v}-slim", "go": "golang:{v}-bookworm",
          "rust": "rust:{v}-bookworm", "maven": "maven:3.9-eclipse-temurin-{v}", "gradle": "gradle:8.10-jdk{v}"}
DOCKER_IMAGE = "docker:27.3"
YAML_WORDS = ("true", "false", "yes", "no", "on", "off", "null", "~")
SAFE = re.compile(r"^[A-Za-z0-9_./@=+-][A-Za-z0-9_ ./@=+,-]*$")


def read(root: Path, name: str) -> str:
    """Return a small text file's content, or an empty string when absent."""
    path = root / name
    return path.read_text(encoding="utf-8", errors="replace")[:200_000] if path.is_file() else ""


def checked_version(raw: str, pattern: str, default: str, source: str, warnings: List[str]) -> str:
    """Accept a version string only if it fully matches pattern; otherwise warn and use the default."""
    ok = bool(re.fullmatch(pattern, raw))
    warnings += [f"Ignored unsupported version in {source} (accepted: Node 18-26, Python 3.8-3.14); "
                 f"using {default}."] if raw and not ok else []
    return raw if ok else default


def py_tool(tool: str, args: str, pm: str, run: str, declared: str, warnings: List[str]) -> str:
    """Return the command for a Python tool, installing it in the step when it is configured but not declared."""
    cmd = f"{run}{tool} {args}".strip()
    if re.search(rf"(?<![\w.-]){tool}(?![\w-])", declared):
        return cmd
    warnings.append(f"{tool} is configured but not declared as a dependency; the step installs it. Add it to your dev dependencies.")
    return {"uv": f"uv run --with {tool} {tool} {args}".strip(), "poetry": f"poetry run pip install {tool} && {cmd}"}.get(
        pm, f"pip install {tool} && {cmd}")


def detect_node(root: Path, warnings: List[str]) -> Dict:
    """Profile a Node project: package manager from the lockfile, steps from package.json scripts."""
    try:
        manifest = json.loads(read(root, "package.json") or "{}")
        scripts = manifest.get("scripts", {}) if isinstance(manifest, dict) else {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"package.json is not valid JSON ({exc.msg}, line {exc.lineno})")
    version = checked_version(read(root, ".nvmrc").strip().lstrip("v").split(".")[0], r"1[89]|2[0-6]", "22", ".nvmrc", warnings)
    if (root / "pnpm-lock.yaml").exists():
        pm, install = "pnpm", "pnpm install --frozen-lockfile"
    elif (root / "yarn.lock").exists():
        pm = "yarn"
        declared = str(manifest.get("packageManager", "")) if isinstance(manifest, dict) else ""
        berry = ((root / ".yarnrc.yml").exists() or bool(re.match(r"yarn@([2-9]|\d{2,})\.", declared))
                 or "__metadata:" in read(root, "yarn.lock")[:2000])  # Yarn 2+ lockfiles start with __metadata
        install = "yarn install --immutable" if berry else "yarn install --frozen-lockfile"
    else:
        pm, install = "npm", "npm ci"
        if not (root / "package-lock.json").exists():
            install = "npm install"
            warnings.append("No lockfile found: installs are not reproducible. Commit package-lock.json and use npm ci.")
    run, has_lock = ("npm run" if pm == "npm" else pm), install != "npm install"
    steps = {k: f"{run} {k}" for k in ("lint", "test", "build") if k in scripts}
    warnings += [f"package.json has no '{k}' script, so the pipeline has no {k} step." for k in ("lint", "test") if k not in scripts]
    prefix = "corepack enable && " if pm != "npm" else ""
    cache_var, cache_dir = {"pnpm": ("npm_config_store_dir", ".pnpm-store"), "yarn": ("YARN_CACHE_FOLDER", ".yarn-cache")}.get(
        pm, ("npm_config_cache", ".npm"))
    return {"language": "node", "version": version, "package_manager": pm, "image": IMAGES["node"].format(v=version),
            "lockfile": {"pnpm": "pnpm-lock.yaml", "yarn": "yarn.lock"}.get(pm, "package-lock.json" if has_lock else "package.json"),
            "has_lockfile": has_lock, "install": prefix + install, "cache_env": {cache_var: cache_dir},
            "cache_paths": [cache_dir], **steps}


def detect_python(root: Path, warnings: List[str]) -> Dict:
    """Profile a Python project: uv, poetry or pip, with ruff/flake8 and pytest when configured."""
    pyproject = read(root, "pyproject.toml")
    reqs = read(root, "requirements.txt") + read(root, "requirements-dev.txt")
    blob = pyproject + reqs + read(root, "setup.cfg")
    declared = reqs + "\n".join(line for line in pyproject.splitlines() if not line.lstrip().startswith("["))
    version = checked_version(".".join(read(root, ".python-version").strip().split(".")[:2]), r"3\.([89]|1[0-4])", "3.12",
                              ".python-version", warnings)
    if (root / "uv.lock").exists():
        pm, install, run, lock = "uv", "pip install uv && uv sync --frozen", "uv run ", "uv.lock"
    elif (root / "poetry.lock").exists():
        pm, install, run, lock = "poetry", "pip install poetry && poetry install --no-interaction", "poetry run ", "poetry.lock"
    else:
        pm, run, lock = "pip", "python -m ", "requirements.txt" if reqs else "pyproject.toml"
        install = " && ".join(["pip install -r requirements.txt" if read(root, "requirements.txt") else "pip install -e ."]
                              + (["pip install -r requirements-dev.txt"] if read(root, "requirements-dev.txt") else []))
    profile = {"language": "python", "version": version, "package_manager": pm, "image": IMAGES["python"].format(v=version),
               "lockfile": lock, "cache_glob": "requirements*.txt" if pm == "pip" and reqs else lock, "install": install,
               "cache_env": {"PIP_CACHE_DIR": ".pip-cache", "UV_CACHE_DIR": ".uv-cache"},
               "cache_paths": [".pip-cache", ".uv-cache"]}
    if "ruff" in blob or (root / "ruff.toml").exists():
        profile["lint"] = py_tool("ruff", "check .", pm, run, declared, warnings)
    elif "flake8" in blob or (root / ".flake8").exists():
        profile["lint"] = py_tool("flake8", ".", pm, run, declared, warnings)
    else:
        warnings.append("No ruff or flake8 configuration found, so the pipeline has no lint step.")
    if "pytest" in blob or (root / "tests").is_dir() or (root / "pytest.ini").exists():
        profile["test"] = py_tool("pytest", "", pm, run, declared, warnings)
    else:
        warnings.append("No pytest configuration or tests/ directory found, so the pipeline has no test step.")
    if "[build-system]" in pyproject:
        profile["build"] = "uv build" if pm == "uv" else ("poetry build" if pm == "poetry" else "pip install build && python -m build")
    return profile


def detect(root: Path) -> Dict:
    """Detect the primary stack in priority order and return its pipeline profile."""
    warnings: List[str] = []
    found = [n for n, f in (("node", "package.json"), ("python", "pyproject.toml"), ("python", "requirements.txt"),
                            ("go", "go.mod"), ("rust", "Cargo.toml"), ("java", "pom.xml"), ("java", "build.gradle"),
                            ("java", "build.gradle.kts")) if (root / f).exists()]
    if not found:
        raise ValueError(f"no supported manifest found in {root} (package.json, pyproject.toml, requirements.txt, "
                         "go.mod, Cargo.toml, pom.xml, build.gradle)")
    lang = found[0]
    if len(set(found)) > 1:
        warnings.append(f"Several stacks found ({', '.join(sorted(set(found)))}); generated for {lang}. Run once per stack if needed.")
    if lang == "node":
        p = detect_node(root, warnings)
    elif lang == "python":
        p = detect_python(root, warnings)
    elif lang == "go":
        m = re.search(r"^go (\d+\.\d+)", read(root, "go.mod"), re.M)
        v = m.group(1) if m else "1.23"
        lint = "golangci-lint run" if any((root / f).exists() for f in (".golangci.yml", ".golangci.yaml")) else "go vet ./..."
        p = {"language": "go", "version": v, "package_manager": "go modules", "image": IMAGES["go"].format(v=v),
             "lockfile": "go.sum" if (root / "go.sum").exists() else "go.mod", "install": "go mod download", "lint": lint,
             "test": "go test -race ./...", "build": "go build ./...",
             "cache_env": {"GOMODCACHE": ".go/pkg/mod", "GOCACHE": ".go/cache"}, "cache_paths": [".go"]}
        warnings += ["golangci-lint is not in the golang image; install it in the lint step or use "
                     "golangci/golangci-lint-action."] if lint.startswith("golangci") else []
    elif lang == "rust":
        p = {"language": "rust", "version": "1.82", "package_manager": "cargo", "image": IMAGES["rust"].format(v="1.82"),
             "lockfile": "Cargo.lock" if (root / "Cargo.lock").exists() else "Cargo.toml",
             "install": "rustup component add clippy rustfmt && cargo fetch --locked",
             "lint": "cargo fmt --check && cargo clippy --all-targets -- -D warnings", "test": "cargo test --locked",
             "build": "cargo build --release --locked", "cache_env": {"CARGO_HOME": ".cargo"}, "cache_paths": [".cargo", "target"]}
    else:
        gradle = not (root / "pom.xml").exists()
        tool = ("./gradlew" if (root / "gradlew").exists() else "gradle") if gradle else "mvn -B"
        p = {"language": "java", "version": "21", "package_manager": "gradle" if gradle else "maven",
             "image": IMAGES["gradle" if gradle else "maven"].format(v="21"),
             "lockfile": "build.gradle.kts" if (root / "build.gradle.kts").exists() else ("build.gradle" if gradle else "pom.xml"),
             "install": f"{tool} dependencies" if gradle else f"{tool} dependency:go-offline",
             "lint": f"{tool} check -x test" if gradle else f"{tool} validate", "test": f"{tool} test",
             "build": f"{tool} assemble" if gradle else f"{tool} package -DskipTests",
             "cache_env": {"GRADLE_USER_HOME": ".gradle"} if gradle else {"MAVEN_OPTS": "-Dmaven.repo.local=.m2/repository"},
             "cache_paths": [".gradle"] if gradle else [".m2/repository"]}
    p["docker"] = (root / "Dockerfile").exists()
    p["warnings"] = warnings
    return p


def yaml_dump(obj, indent: int = 0) -> str:
    """Serialise dicts, lists and scalars to block-style YAML (quoted where needed)."""
    pad, out = "  " * indent, []
    def scalar(v) -> str:
        if isinstance(v, (bool, int, float)):
            return str(v).lower() if isinstance(v, bool) else str(v)
        plain = SAFE.match(str(v)) and not re.fullmatch(r"[\d.]+", str(v)) and str(v).lower() not in YAML_WORDS
        return str(v) if plain else json.dumps(str(v))
    items = obj.items() if isinstance(obj, dict) else enumerate(obj)
    for k, v in items:
        lead = f"{pad}{k}:" if isinstance(obj, dict) else f"{pad}-"
        if isinstance(v, (dict, list)) and v:
            if isinstance(obj, list) and isinstance(v, dict):
                first, *rest = yaml_dump(v, indent + 1).splitlines()
                out.append(f"{pad}- {first.strip()}")
                out.extend(rest)
            else:
                out.append(lead)
                out.append(yaml_dump(v, indent + 1).rstrip("\n"))
        else:
            out.append(f"{lead} {scalar(v) if not isinstance(v, (dict, list)) else ('{}' if isinstance(v, dict) else '[]')}")
    return "\n".join(out) + "\n"


def stages(p: Dict) -> List[tuple]:
    """Return (name, command) pairs for lint, test and build, in fail-fast order."""
    return [(k, p[k]) for k in ("lint", "test", "build") if p.get(k)]


def github(p: Dict, name: str) -> str:
    """Build a GitHub Actions workflow with read-only token, caching and pinned major versions."""
    lang, v = p["language"], p["version"]
    setup: List[Dict] = [{"uses": "actions/checkout@v4"}]
    if lang == "node":
        pm = p["package_manager"]
        setup += [{"uses": "pnpm/action-setup@v4"}] if pm == "pnpm" else ([{"run": "corepack enable"}] if pm == "yarn" else [])
        cache = {"cache": pm} if p["has_lockfile"] else {}  # setup-node fails on cache without a lockfile
        setup.append({"uses": "actions/setup-node@v4", "with": {"node-version": v, **cache}})
    elif lang == "python":
        setup.append({"uses": "actions/setup-python@v5",
                      "with": {"python-version": v, "cache": "pip", "cache-dependency-path": p["cache_glob"]}})
    elif lang == "go":
        setup.append({"uses": "actions/setup-go@v5", "with": {"go-version-file": "go.mod", "cache": True}})
    elif lang == "rust":
        setup += [{"uses": "dtolnay/rust-toolchain@stable", "with": {"components": "clippy, rustfmt"}},
                  {"uses": "Swatinem/rust-cache@v2"}]
    else:
        setup.append({"uses": "actions/setup-java@v4",
                      "with": {"distribution": "temurin", "java-version": v, "cache": p["package_manager"]}})
    install = p["install"].replace("rustup component add clippy rustfmt && ", "")  # the toolchain action adds them
    install = install if p["package_manager"] == "yarn" else install.replace("corepack enable && ", "")
    steps = setup + [{"name": "Install", "run": install}] + [{"name": n.title(), "run": c} for n, c in stages(p)]
    jobs: Dict = {"ci": {"runs-on": "ubuntu-24.04", "timeout-minutes": 20, "steps": steps}}
    if p["docker"]:
        jobs["docker"] = {"needs": "ci", "runs-on": "ubuntu-24.04", "timeout-minutes": 20, "steps": [
            {"uses": "actions/checkout@v4"}, {"uses": "docker/setup-buildx-action@v3"},
            {"uses": "docker/build-push-action@v6", "with": {"context": ".", "push": False, "tags": f"{name}:${{{{ github.sha }}}}",
                                                             "cache-from": "type=gha", "cache-to": "type=gha,mode=max"}}]}
    wf = {"name": "CI", "on": {"push": {"branches": ["main"]}, "pull_request": {}},
          "permissions": {"contents": "read"},
          "concurrency": {"group": "ci-${{ github.ref }}", "cancel-in-progress": True}, "jobs": jobs}
    return yaml_dump(wf)


def gitlab(p: Dict, name: str) -> str:
    """Build a .gitlab-ci.yml with lockfile-keyed cache and a Docker-in-Docker build job."""
    cfg: Dict = {"workflow": {"rules": [{"if": "$CI_PIPELINE_SOURCE == \"merge_request_event\""},
                                        {"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}]},
                 "stages": ["install"] + [n for n, _ in stages(p)] + (["docker"] if p["docker"] else []),
                 "default": {"image": p["image"], "interruptible": True,
                             "cache": {"key": {"files": [p["lockfile"]]}, "paths": p["cache_paths"], "policy": "pull"}},
                 "variables": {k: v if v.startswith("-") else f"$CI_PROJECT_DIR/{v}" for k, v in p["cache_env"].items()},
                 "install": {"stage": "install", "script": [p["install"]],
                             "cache": {"key": {"files": [p["lockfile"]]}, "paths": p["cache_paths"], "policy": "pull-push"}}}
    for n, c in stages(p):
        cfg[n] = {"stage": n, "script": [p["install"], c]}
    if p["docker"]:
        cfg["docker-build"] = {"stage": "docker", "image": DOCKER_IMAGE, "services": [f"{DOCKER_IMAGE}-dind"],
                               "variables": {"DOCKER_TLS_CERTDIR": "/certs"}, "cache": [],
                               "script": [f"docker build -t {name}:$CI_COMMIT_SHORT_SHA ."]}
    return yaml_dump(cfg)


def circleci(p: Dict, name: str) -> str:
    """Build a CircleCI 2.1 config with checksum-keyed restore/save cache."""
    key = f"deps-v1-{{{{ checksum \"{p['lockfile']}\" }}}}"
    git = "command -v git >/dev/null || (apt-get update && apt-get install -y --no-install-recommends git openssh-client ca-certificates)"
    steps: List = [{"run": {"name": "Ensure git (slim images lack it)", "command": git}}, "checkout",
                   {"restore_cache": {"keys": [key]}}, {"run": {"name": "Install", "command": p["install"]}},
                   {"save_cache": {"key": key, "paths": p["cache_paths"]}}]
    steps += [{"run": {"name": n.title(), "command": c}} for n, c in stages(p)]
    jobs: Dict = {"ci": {"docker": [{"image": p["image"]}], "environment": p["cache_env"],
                         "resource_class": "medium", "steps": steps}}
    wf_jobs: List = ["ci"]
    if p["docker"]:
        jobs["docker-build"] = {"docker": [{"image": "cimg/base:current"}], "steps": [
            "checkout", {"setup_remote_docker": {"docker_layer_caching": False}},
            {"run": {"name": "Docker build", "command": f"docker build -t {name}:$CIRCLE_SHA1 ."}}]}
        wf_jobs.append({"docker-build": {"requires": ["ci"]}})
    return yaml_dump({"version": 2.1, "jobs": jobs, "workflows": {"ci": {"jobs": wf_jobs}}})


def jenkins(p: Dict, name: str) -> str:
    """Build a declarative Jenkinsfile running inside the stack's pinned image."""
    cache = dict(p["cache_env"], **({"HOME": "."} if p["language"] == "python" else {}))  # pip --user fallback needs a writable HOME
    env = "\n".join(f"        {k} = \"{v}\"" if v.startswith("-") else f"        {k} = \"${{WORKSPACE}}/{v}\"".replace("/.\"", "\"")
                    for k, v in cache.items())
    body = [("Install", p["install"])] + [(n.title(), c) for n, c in stages(p)]
    st = "".join(f"        stage('{n}') {{\n            steps {{ sh '{c}' }}\n        }}\n" for n, c in body)
    if p["docker"]:
        st += (f"        stage('Docker build') {{\n            agent any\n"
               f"            steps {{ sh 'docker build -t {name}:${{GIT_COMMIT}} .' }}\n        }}\n")
    return (f"pipeline {{\n    agent {{ docker {{ image '{p['image']}' }} }}\n    options {{\n"
            f"        timeout(time: 20, unit: 'MINUTES')\n        disableConcurrentBuilds(abortPrevious: true)\n    }}\n"
            f"    environment {{\n{env}\n    }}\n    stages {{\n{st}    }}\n}}\n")


def main() -> None:
    """Parse arguments, detect the stack, render the pipeline and optionally write it."""
    ap = argparse.ArgumentParser(description="Detect a project's stack and generate a CI pipeline config.")
    ap.add_argument("project", help="path to the project root")
    ap.add_argument("--platform", choices=sorted(PLATFORMS), default="github-actions", help="CI platform (default: github-actions)")
    ap.add_argument("--no-docker", action="store_true", help="omit the Docker build job even when a Dockerfile exists")
    ap.add_argument("--output", "-o", help="write the pipeline to this file (relative paths resolve against the project)")
    ap.add_argument("--force", action="store_true", help="overwrite --output if it already exists")
    ap.add_argument("--json", action="store_true", help="print a JSON report instead of text")
    ap.add_argument("--verbose", "-v", action="store_true", help="also print install and cache details")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    try:
        if not root.is_dir():
            raise ValueError(f"project path is not a directory: {args.project}")
        p = detect(root)
        p["docker"] = p["docker"] and not args.no_docker
        name = re.sub(r"[^a-z0-9-]+", "-", root.name.lower()).strip("-") or "app"
        text = {"github-actions": github, "gitlab-ci": gitlab, "circleci": circleci, "jenkins": jenkins}[args.platform](p, name)
        written: Optional[str] = None
        if args.output:
            out = Path(args.output) if Path(args.output).is_absolute() else root / args.output
            if out.exists() and not args.force:
                raise ValueError(f"{out} already exists; rerun with --force to overwrite")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            written = str(out)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    stack = {k: p.get(k) for k in ("language", "version", "package_manager", "image", "lockfile", "install",
                                   "lint", "test", "build", "docker")}
    if args.json:
        print(json.dumps({"platform": args.platform, "default_path": PLATFORMS[args.platform], "stack": stack,
                          "warnings": p["warnings"], "written": written, "pipeline": text}, indent=2))
        return
    print(f"Detected: {stack['language']} {stack['version']} ({stack['package_manager']}), Docker: {'yes' if stack['docker'] else 'no'}")
    print("Stages: install, " + ", ".join([n for n, _ in stages(p)] + (["docker"] if stack["docker"] else [])))
    if args.verbose:
        print(f"Install: {stack['install']}\nCache key: {stack['lockfile']}  Image: {stack['image']}")
    for w in p["warnings"]:
        print(f"Warning: {w}")
    print(f"Wrote {written}" if written else f"\n# {PLATFORMS[args.platform]}\n{text}", end="" if written is None else "\n")


if __name__ == "__main__":
    main()
