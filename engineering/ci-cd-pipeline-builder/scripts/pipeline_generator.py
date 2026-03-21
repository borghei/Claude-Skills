#!/usr/bin/env python3
"""Generate CI/CD pipeline YAML from detected project stack signals.

Scans a project directory for lockfiles, manifests, Dockerfiles, and
framework configs, then generates an appropriate GitHub Actions or
GitLab CI pipeline with caching, testing, and deployment stages.

Usage:
    python pipeline_generator.py /path/to/project
    python pipeline_generator.py . --platform gitlab
    python pipeline_generator.py . --platform github --deploy --json
"""

import argparse
import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Stack detection
# ---------------------------------------------------------------------------

STACK_SIGNALS = [
    # (file_or_glob, language, package_manager, framework_hint)
    ("package-lock.json",   "node",   "npm",    None),
    ("pnpm-lock.yaml",      "node",   "pnpm",   None),
    ("yarn.lock",            "node",   "yarn",   None),
    ("bun.lockb",            "node",   "bun",    None),
    ("requirements.txt",     "python", "pip",    None),
    ("Pipfile",              "python", "pipenv", None),
    ("poetry.lock",          "python", "poetry", None),
    ("uv.lock",             "python", "uv",     None),
    ("pyproject.toml",       "python", None,     None),
    ("go.mod",               "go",     "go",     None),
    ("Cargo.lock",           "rust",   "cargo",  None),
    ("Gemfile.lock",         "ruby",   "bundler", None),
    ("composer.lock",        "php",    "composer", None),
]

FRAMEWORK_SIGNALS = [
    ("next.config.js",      "nextjs"),
    ("next.config.ts",      "nextjs"),
    ("next.config.mjs",     "nextjs"),
    ("nuxt.config.ts",      "nuxt"),
    ("nuxt.config.js",      "nuxt"),
    ("angular.json",        "angular"),
    ("svelte.config.js",    "sveltekit"),
    ("vite.config.ts",      "vite"),
    ("vite.config.js",      "vite"),
]

INFRA_SIGNALS = [
    ("Dockerfile",          "docker"),
    ("docker-compose.yml",  "docker-compose"),
    ("docker-compose.yaml", "docker-compose"),
]


def detect_stack(project_dir):
    """Detect project stack from filesystem signals."""
    root = Path(project_dir)
    detected = {
        "language": None,
        "package_manager": None,
        "framework": None,
        "has_docker": False,
        "has_docker_compose": False,
        "has_tests": False,
    }

    for filename, lang, pm, _fw in STACK_SIGNALS:
        if (root / filename).exists():
            if detected["language"] is None:
                detected["language"] = lang
            if pm and detected["package_manager"] is None:
                detected["package_manager"] = pm

    for filename, fw in FRAMEWORK_SIGNALS:
        if (root / filename).exists():
            detected["framework"] = fw
            break

    for filename, kind in INFRA_SIGNALS:
        if (root / filename).exists():
            if kind == "docker":
                detected["has_docker"] = True
            elif kind == "docker-compose":
                detected["has_docker_compose"] = True

    # Detect test presence
    test_indicators = [
        "tests", "test", "__tests__", "spec",
        "pytest.ini", "jest.config.js", "jest.config.ts",
        "vitest.config.ts", "vitest.config.js",
    ]
    for indicator in test_indicators:
        if (root / indicator).exists():
            detected["has_tests"] = True
            break

    return detected


# ---------------------------------------------------------------------------
# Pipeline templates (GitHub Actions)
# ---------------------------------------------------------------------------

def _github_node(stack, deploy):
    pm = stack["package_manager"] or "npm"
    install_cmd = {
        "npm": "npm ci",
        "pnpm": "pnpm install --frozen-lockfile",
        "yarn": "yarn install --frozen-lockfile",
        "bun": "bun install --frozen-lockfile",
    }.get(pm, "npm ci")

    setup_steps = "      - uses: actions/checkout@v4\n"
    if pm == "pnpm":
        setup_steps += "      - uses: pnpm/action-setup@v4\n        with:\n          version: '9'\n"
    setup_steps += (
        "      - uses: actions/setup-node@v4\n"
        "        with:\n"
        f"          node-version: '20'\n"
    )
    if pm in ("npm", "pnpm", "yarn"):
        setup_steps += f"          cache: '{pm}'\n"
    setup_steps += f"      - run: {install_cmd}\n"

    jobs = f"""  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
{setup_steps}      - run: npx eslint . || true

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: lint
    steps:
{setup_steps}      - run: {"npx vitest run" if stack.get("framework") in ("vite", "nextjs", "sveltekit") else "npm test"}
"""

    if stack["has_docker"]:
        jobs += f"""
  build-image:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: test
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: app:${{{{ github.sha }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""
    else:
        jobs += f"""
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: test
    steps:
{setup_steps}      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 3
"""

    if deploy:
        jobs += """
  deploy-staging:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: [build]
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment:
      name: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: echo "Add your staging deploy command here"
        env:
          DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}

  deploy-production:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: deploy-staging
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment:
      name: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: echo "Add your production deploy command here"
        env:
          DEPLOY_TOKEN: ${{ secrets.PROD_DEPLOY_TOKEN }}
"""

    return _github_wrapper(jobs)


def _github_python(stack, deploy):
    pm = stack["package_manager"] or "pip"
    install_block = {
        "pip": "      - run: pip install -r requirements.txt",
        "poetry": "      - run: pip install poetry && poetry install --no-interaction",
        "uv": "      - uses: astral-sh/setup-uv@v4\n      - run: uv sync --frozen",
        "pipenv": "      - run: pip install pipenv && pipenv install --deploy",
    }.get(pm, "      - run: pip install -r requirements.txt")

    setup_steps = (
        "      - uses: actions/checkout@v4\n"
        "      - uses: actions/setup-python@v5\n"
        "        with:\n"
        "          python-version: '3.12'\n"
    )
    if pm != "uv":
        setup_steps += install_block + "\n"
    else:
        setup_steps = "      - uses: actions/checkout@v4\n" + install_block + "\n"

    test_cmd = "uv run pytest -v" if pm == "uv" else "pytest -v"
    lint_cmd = "uv run ruff check ." if pm == "uv" else "ruff check . || true"

    jobs = f"""  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
{setup_steps}      - run: {lint_cmd}

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: lint
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
{install_block}
      - run: {test_cmd}
"""

    if stack["has_docker"]:
        jobs += """
  build-image:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: test
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""

    if deploy:
        jobs += """
  deploy-staging:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: [test]
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment:
      name: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: echo "Add your staging deploy command here"

  deploy-production:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: deploy-staging
    runs-on: ubuntu-latest
    timeout-minutes: 10
    environment:
      name: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: echo "Add your production deploy command here"
"""

    return _github_wrapper(jobs)


def _github_go(stack, deploy):
    jobs = """  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go vet ./...

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go test -race -coverprofile=coverage.out ./...

  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go build -o bin/app ./...
      - uses: actions/upload-artifact@v4
        with:
          name: binary
          path: bin/
          retention-days: 3
"""
    return _github_wrapper(jobs)


def _github_wrapper(jobs_block):
    return f"""name: CI/CD

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
{jobs_block}"""


def _github_generic():
    return _github_wrapper("""  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: echo "Configure your build steps here"
      - name: Test
        run: echo "Configure your test steps here"
""")


# ---------------------------------------------------------------------------
# Pipeline templates (GitLab CI)
# ---------------------------------------------------------------------------

def _gitlab_node(stack, deploy):
    pm = stack["package_manager"] or "npm"
    install = {"npm": "npm ci", "pnpm": "corepack enable && pnpm install --frozen-lockfile",
               "yarn": "yarn install --frozen-lockfile", "bun": "bun install"}.get(pm, "npm ci")
    cache_path = {"npm": "node_modules/", "pnpm": ".pnpm-store/\n      - node_modules/",
                  "yarn": "node_modules/", "bun": "node_modules/"}.get(pm, "node_modules/")

    deploy_block = ""
    if deploy:
        deploy_block = """
deploy_staging:
  stage: deploy
  environment:
    name: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  script:
    - echo "Add staging deploy command"

deploy_production:
  stage: deploy
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
  needs: [deploy_staging]
  script:
    - echo "Add production deploy command"
"""

    return f"""stages:
  - validate
  - test
  - build
  - deploy

default:
  image: node:20

cache:
  key: ${{CI_COMMIT_REF_SLUG}}
  paths:
    - {cache_path}

lint:
  stage: validate
  before_script:
    - {install}
  script:
    - npx eslint . || true
  timeout: 10m

test:
  stage: test
  before_script:
    - {install}
  script:
    - npm test
  timeout: 15m

build:
  stage: build
  before_script:
    - {install}
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour
{deploy_block}"""


def _gitlab_python(stack, deploy):
    pm = stack["package_manager"] or "pip"
    install = {"pip": "pip install -r requirements.txt",
               "uv": "pip install uv && uv sync --frozen",
               "poetry": "pip install poetry && poetry install"}.get(pm, "pip install -r requirements.txt")

    return f"""stages:
  - validate
  - test
  - build
  - deploy

default:
  image: python:3.12

cache:
  key: ${{CI_COMMIT_REF_SLUG}}
  paths:
    - .cache/pip/

lint:
  stage: validate
  before_script:
    - {install}
  script:
    - ruff check . || true
  timeout: 10m

test:
  stage: test
  before_script:
    - {install}
  script:
    - pytest -v
  timeout: 15m
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.11", "3.12", "3.13"]
"""


# ---------------------------------------------------------------------------
# Generator dispatch
# ---------------------------------------------------------------------------

GENERATORS = {
    ("github", "node"):   _github_node,
    ("github", "python"): _github_python,
    ("github", "go"):     _github_go,
    ("gitlab", "node"):   _gitlab_node,
    ("gitlab", "python"): _gitlab_python,
}


def generate_pipeline(project_dir, platform="github", deploy=False):
    """Generate a CI/CD pipeline for the given project."""
    stack = detect_stack(project_dir)
    lang = stack["language"]

    gen_fn = GENERATORS.get((platform, lang))
    if gen_fn:
        yaml_content = gen_fn(stack, deploy)
    elif platform == "github":
        yaml_content = _github_generic()
    else:
        yaml_content = "# Could not detect stack. Add pipeline configuration manually.\n"

    return {
        "stack": stack,
        "platform": platform,
        "yaml": yaml_content,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate CI/CD pipeline YAML from project stack detection.",
        epilog="Examples:\n"
               "  %(prog)s /path/to/project\n"
               "  %(prog)s . --platform gitlab --deploy\n"
               "  %(prog)s . --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_dir", nargs="?", default=".",
                        help="Project directory to scan (default: current directory)")
    parser.add_argument("--platform", choices=["github", "gitlab"],
                        default="github", help="Target CI platform (default: github)")
    parser.add_argument("--deploy", action="store_true",
                        help="Include deployment stages (staging + production)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON (includes detected stack info)")
    parser.add_argument("--detect-only", action="store_true",
                        help="Only detect stack, do not generate pipeline")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    if args.detect_only:
        stack = detect_stack(project_dir)
        if args.json_output:
            print(json.dumps({"project_dir": project_dir, "stack": stack}, indent=2))
        else:
            print(f"Project: {project_dir}")
            print(f"Language:        {stack['language'] or 'unknown'}")
            print(f"Package Manager: {stack['package_manager'] or 'unknown'}")
            print(f"Framework:       {stack['framework'] or 'none'}")
            print(f"Docker:          {'yes' if stack['has_docker'] else 'no'}")
            print(f"Tests detected:  {'yes' if stack['has_tests'] else 'no'}")
        sys.exit(0)

    result = generate_pipeline(project_dir, platform=args.platform, deploy=args.deploy)

    if args.json_output:
        print(json.dumps({
            "project_dir": project_dir,
            "stack": result["stack"],
            "platform": result["platform"],
            "yaml": result["yaml"],
        }, indent=2))
    else:
        print(f"# Detected stack: {result['stack']['language'] or 'unknown'}"
              f" / {result['stack']['package_manager'] or 'unknown'}"
              f" / {result['stack']['framework'] or 'none'}")
        print(f"# Platform: {result['platform']}")
        print(f"# Docker: {'yes' if result['stack']['has_docker'] else 'no'}")
        print()
        print(result["yaml"])

    sys.exit(0)


if __name__ == "__main__":
    main()
