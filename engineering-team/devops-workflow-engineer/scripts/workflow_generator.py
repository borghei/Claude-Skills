#!/usr/bin/env python3
"""
GitHub Actions Workflow Generator

Generates production-ready GitHub Actions workflow YAML files from templates.
Supports CI, CD, release, security-scan, and docs-check workflow types.

Usage:
    python workflow_generator.py --type ci --language python --test-framework pytest
    python workflow_generator.py --type cd --language node --deploy-target kubernetes
    python workflow_generator.py --type security-scan --language python
    python workflow_generator.py --type release --language python
    python workflow_generator.py --type docs-check
    python workflow_generator.py --type ci --language python --format json
"""

import argparse
import json
import sys
import textwrap
from datetime import datetime


# ---------------------------------------------------------------------------
# Template data
# ---------------------------------------------------------------------------

LANGUAGE_CONFIGS = {
    "python": {
        "setup_action": "actions/setup-python@v5",
        "setup_key": "python-version",
        "default_version": "3.12",
        "matrix_versions": ["3.10", "3.11", "3.12"],
        "cache_type": "pip",
        "install_cmd": "pip install -r requirements.txt",
        "lint_cmd": "ruff check . && ruff format --check .",
        "lint_packages": "pip install ruff",
        "build_cmd": "python -m build",
        "default_test_framework": "pytest",
        "test_frameworks": {
            "pytest": {
                "install": "pip install pytest pytest-cov",
                "run": "pytest --cov=src --cov-report=xml --junitxml=results.xml",
            },
            "unittest": {
                "install": "",
                "run": "python -m unittest discover -s tests -v",
            },
        },
        "audit_cmd": "pip install pip-audit && pip-audit -r requirements.txt",
        "publish_cmd": "twine upload dist/*",
    },
    "node": {
        "setup_action": "actions/setup-node@v4",
        "setup_key": "node-version",
        "default_version": "20",
        "matrix_versions": ["18", "20", "22"],
        "cache_type": "npm",
        "install_cmd": "npm ci",
        "lint_cmd": "npm run lint",
        "lint_packages": "",
        "build_cmd": "npm run build",
        "default_test_framework": "jest",
        "test_frameworks": {
            "jest": {
                "install": "",
                "run": "npm test -- --coverage --ci",
            },
            "vitest": {
                "install": "",
                "run": "npx vitest run --coverage",
            },
            "mocha": {
                "install": "",
                "run": "npx mocha --recursive",
            },
        },
        "audit_cmd": "npm audit --audit-level=high",
        "publish_cmd": "npm publish",
    },
    "go": {
        "setup_action": "actions/setup-go@v5",
        "setup_key": "go-version",
        "default_version": "1.22",
        "matrix_versions": ["1.21", "1.22"],
        "cache_type": "",
        "install_cmd": "go mod download",
        "lint_cmd": "go vet ./...",
        "lint_packages": "",
        "build_cmd": "go build ./...",
        "default_test_framework": "gotest",
        "test_frameworks": {
            "gotest": {
                "install": "",
                "run": "go test -v -race -coverprofile=coverage.out ./...",
            },
        },
        "audit_cmd": "go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...",
        "publish_cmd": "",
    },
    "rust": {
        "setup_action": "dtolnay/rust-toolchain@stable",
        "setup_key": "toolchain",
        "default_version": "stable",
        "matrix_versions": ["stable", "beta"],
        "cache_type": "",
        "install_cmd": "",
        "lint_cmd": "cargo clippy -- -D warnings",
        "lint_packages": "",
        "build_cmd": "cargo build --release",
        "default_test_framework": "cargo",
        "test_frameworks": {
            "cargo": {
                "install": "",
                "run": "cargo test --verbose",
            },
        },
        "audit_cmd": "cargo install cargo-audit && cargo audit",
        "publish_cmd": "cargo publish",
    },
}

DEPLOY_TARGETS = {
    "kubernetes": {
        "name": "Kubernetes",
        "deploy_steps": textwrap.dedent("""\
            - name: Set up kubectl
              uses: azure/setup-kubectl@v4

            - name: Configure kubeconfig
              run: |
                echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config

            - name: Deploy to ${{ inputs.environment }}
              run: |
                kubectl set image deployment/${{ env.APP_NAME }} \\
                  app=${{ env.REGISTRY }}/${{ env.APP_NAME }}:${{ inputs.image_tag }} \\
                  -n ${{ inputs.environment }}
                kubectl rollout status deployment/${{ env.APP_NAME }} \\
                  -n ${{ inputs.environment }} --timeout=300s"""),
    },
    "docker-compose": {
        "name": "Docker Compose",
        "deploy_steps": textwrap.dedent("""\
            - name: Deploy via SSH
              uses: appleboy/ssh-action@v1
              with:
                host: ${{ secrets.DEPLOY_HOST }}
                username: ${{ secrets.DEPLOY_USER }}
                key: ${{ secrets.DEPLOY_SSH_KEY }}
                script: |
                  cd /opt/${{ env.APP_NAME }}
                  docker compose pull
                  docker compose up -d --remove-orphans
                  docker compose exec -T app ./health-check.sh"""),
    },
    "aws-ecs": {
        "name": "AWS ECS",
        "deploy_steps": textwrap.dedent("""\
            - name: Configure AWS credentials
              uses: aws-actions/configure-aws-credentials@v4
              with:
                role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
                aws-region: ${{ vars.AWS_REGION }}

            - name: Deploy to ECS
              run: |
                aws ecs update-service \\
                  --cluster ${{ vars.ECS_CLUSTER }} \\
                  --service ${{ env.APP_NAME }}-${{ inputs.environment }} \\
                  --force-new-deployment
                aws ecs wait services-stable \\
                  --cluster ${{ vars.ECS_CLUSTER }} \\
                  --services ${{ env.APP_NAME }}-${{ inputs.environment }}"""),
    },
    "static": {
        "name": "Static Site (S3/CloudFront or Pages)",
        "deploy_steps": textwrap.dedent("""\
            - name: Deploy to GitHub Pages
              uses: actions/deploy-pages@v4
              with:
                token: ${{ secrets.GITHUB_TOKEN }}"""),
    },
}


# ---------------------------------------------------------------------------
# Workflow generators
# ---------------------------------------------------------------------------


def _header(name, triggers, permissions=None, concurrency=True):
    """Generate the workflow header."""
    lines = [f"name: {name}", ""]
    lines.append("on:")
    for trigger, config in triggers.items():
        if config is None:
            lines.append(f"  {trigger}:")
        elif isinstance(config, dict):
            lines.append(f"  {trigger}:")
            for k, v in config.items():
                if isinstance(v, list):
                    lines.append(f"    {k}:")
                    for item in v:
                        lines.append(f"      - '{item}'")
                else:
                    lines.append(f"    {k}: {v}")
        else:
            lines.append(f"  {trigger}: {config}")
    lines.append("")

    if permissions:
        lines.append("permissions:")
        for perm, level in permissions.items():
            lines.append(f"  {perm}: {level}")
        lines.append("")

    if concurrency:
        lines.append("concurrency:")
        lines.append("  group: ${{ github.workflow }}-${{ github.ref }}")
        lines.append("  cancel-in-progress: true")
        lines.append("")

    return "\n".join(lines)


def generate_ci(lang_key, test_framework, output_format):
    """Generate a CI workflow."""
    lang = LANGUAGE_CONFIGS.get(lang_key)
    if not lang:
        return {"error": f"Unsupported language: {lang_key}. Supported: {', '.join(LANGUAGE_CONFIGS)}"}

    tf_key = test_framework or lang["default_test_framework"]
    tf = lang["test_frameworks"].get(tf_key)
    if not tf:
        available = ", ".join(lang["test_frameworks"].keys())
        return {"error": f"Unsupported test framework '{tf_key}' for {lang_key}. Available: {available}"}

    header = _header(
        name=f"CI ({lang_key})",
        triggers={
            "push": {"branches": ["main", "dev"]},
            "pull_request": {"branches": ["main"]},
        },
        permissions={"contents": "read"},
    )

    # Lint job
    lint_steps = [
        "    steps:",
        "      - uses: actions/checkout@v4",
    ]
    if lang["setup_action"]:
        lint_steps.append(f"      - uses: {lang['setup_action']}")
        lint_steps.append("        with:")
        lint_steps.append(f"          {lang['setup_key']}: '{lang['default_version']}'")
        if lang["cache_type"]:
            lint_steps.append(f"          cache: {lang['cache_type']}")
    if lang["lint_packages"]:
        lint_steps.append(f"      - name: Install lint tools")
        lint_steps.append(f"        run: {lang['lint_packages']}")
    lint_steps.append("      - name: Lint")
    lint_steps.append(f"        run: {lang['lint_cmd']}")

    lint_job = "\n".join([
        "  lint:",
        "    runs-on: ubuntu-latest",
        "    timeout-minutes: 5",
    ] + lint_steps)

    # Test job
    versions_yaml = "\n".join(f"          - '{v}'" for v in lang["matrix_versions"])
    test_steps = [
        "    steps:",
        "      - uses: actions/checkout@v4",
        f"      - uses: {lang['setup_action']}",
        "        with:",
        f"          {lang['setup_key']}: ${{{{ matrix.version }}}}",
    ]
    if lang["cache_type"]:
        test_steps.append(f"          cache: {lang['cache_type']}")
    if lang["install_cmd"]:
        test_steps.append("      - name: Install dependencies")
        test_steps.append(f"        run: {lang['install_cmd']}")
    if tf["install"]:
        test_steps.append("      - name: Install test framework")
        test_steps.append(f"        run: {tf['install']}")
    test_steps.append("      - name: Run tests")
    test_steps.append(f"        run: {tf['run']}")
    test_steps.extend([
        "      - uses: actions/upload-artifact@v4",
        "        if: always()",
        "        with:",
        "          name: test-results-${{ matrix.version }}",
        "          path: |",
        "            results.xml",
        "            coverage.xml",
        "            coverage.out",
        "          retention-days: 7",
    ])

    test_job = "\n".join([
        "  test:",
        "    needs: lint",
        "    runs-on: ubuntu-latest",
        "    timeout-minutes: 15",
        "    strategy:",
        "      fail-fast: false",
        "      matrix:",
        "        version:",
        versions_yaml,
    ] + test_steps)

    # Build job
    build_steps = [
        "    steps:",
        "      - uses: actions/checkout@v4",
        f"      - uses: {lang['setup_action']}",
        "        with:",
        f"          {lang['setup_key']}: '{lang['default_version']}'",
    ]
    if lang["cache_type"]:
        build_steps.append(f"          cache: {lang['cache_type']}")
    if lang["install_cmd"]:
        build_steps.append("      - name: Install dependencies")
        build_steps.append(f"        run: {lang['install_cmd']}")
    if lang["build_cmd"]:
        build_steps.append("      - name: Build")
        build_steps.append(f"        run: {lang['build_cmd']}")

    build_job = "\n".join([
        "  build:",
        "    needs: lint",
        "    runs-on: ubuntu-latest",
        "    timeout-minutes: 10",
    ] + build_steps)

    workflow = header + "jobs:\n" + lint_job + "\n\n" + test_job + "\n\n" + build_job + "\n"

    if output_format == "json":
        return {
            "workflow_type": "ci",
            "language": lang_key,
            "test_framework": tf_key,
            "yaml": workflow,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return workflow


def generate_cd(lang_key, deploy_target, output_format):
    """Generate a CD workflow."""
    lang = LANGUAGE_CONFIGS.get(lang_key)
    if not lang:
        return {"error": f"Unsupported language: {lang_key}. Supported: {', '.join(LANGUAGE_CONFIGS)}"}

    target_key = deploy_target or "kubernetes"
    target = DEPLOY_TARGETS.get(target_key)
    if not target:
        return {"error": f"Unsupported deploy target '{target_key}'. Available: {', '.join(DEPLOY_TARGETS)}"}

    header = _header(
        name=f"CD ({lang_key} -> {target['name']})",
        triggers={
            "workflow_dispatch": {
                "inputs": None,
            },
            "push": {"branches": ["main"]},
        },
        permissions={"contents": "read", "packages": "write", "id-token": "write"},
        concurrency=True,
    )

    # Override the trigger section for workflow_dispatch with inputs
    # We need to manually craft this since our helper is simplified
    header_lines = header.split("\n")
    new_header_lines = []
    skip_until_next_trigger = False
    for line in header_lines:
        if "workflow_dispatch:" in line:
            new_header_lines.append("  workflow_dispatch:")
            new_header_lines.append("    inputs:")
            new_header_lines.append("      environment:")
            new_header_lines.append("        description: 'Target environment'")
            new_header_lines.append("        required: true")
            new_header_lines.append("        type: choice")
            new_header_lines.append("        options:")
            new_header_lines.append("          - dev")
            new_header_lines.append("          - staging")
            new_header_lines.append("          - production")
            new_header_lines.append("        default: staging")
            skip_until_next_trigger = True
            continue
        if skip_until_next_trigger:
            if line.startswith("  ") and ":" in line and not line.startswith("    "):
                skip_until_next_trigger = False
            elif line == "" or not line.startswith("  "):
                skip_until_next_trigger = False
            else:
                continue
        new_header_lines.append(line)
    header = "\n".join(new_header_lines)

    env_block = textwrap.dedent("""\
        env:
          REGISTRY: ghcr.io/${{ github.repository_owner }}
          APP_NAME: ${{ github.event.repository.name }}

    """)

    # Build job
    build_job = textwrap.dedent(f"""\
      build:
        runs-on: ubuntu-latest
        timeout-minutes: 15
        outputs:
          image_tag: ${{{{ github.sha }}}}
        steps:
          - uses: actions/checkout@v4

          - name: Log in to Container Registry
            uses: docker/login-action@v3
            with:
              registry: ghcr.io
              username: ${{{{ github.actor }}}}
              password: ${{{{ secrets.GITHUB_TOKEN }}}}

          - name: Build and push Docker image
            uses: docker/build-push-action@v5
            with:
              context: .
              push: true
              tags: |
                ${{{{ env.REGISTRY }}}}/${{{{ env.APP_NAME }}}}:${{{{ github.sha }}}}
                ${{{{ env.REGISTRY }}}}/${{{{ env.APP_NAME }}}}:latest
              cache-from: type=gha
              cache-to: type=gha,mode=max
    """)

    # Deploy job
    deploy_steps_indented = textwrap.indent(target["deploy_steps"], "        ")
    deploy_job = textwrap.dedent(f"""\
      deploy:
        needs: build
        runs-on: ubuntu-latest
        timeout-minutes: 15
        environment: ${{{{ inputs.environment || 'staging' }}}}
        steps:
          - uses: actions/checkout@v4

    {deploy_steps_indented}

          - name: Verify deployment
            run: |
              echo "Deployed ${{{{ env.APP_NAME }}}} (${{{{ github.sha }}}}) to ${{{{ inputs.environment || 'staging' }}}}"
              # Add health check URL verification here
              # curl -sf "${{{{ vars.HEALTH_CHECK_URL }}}}/health" || exit 1
    """)

    workflow = header + env_block + "jobs:\n" + build_job + "\n" + deploy_job

    if output_format == "json":
        return {
            "workflow_type": "cd",
            "language": lang_key,
            "deploy_target": target_key,
            "yaml": workflow,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return workflow


def generate_security_scan(lang_key, output_format):
    """Generate a security scanning workflow."""
    lang = LANGUAGE_CONFIGS.get(lang_key)
    if not lang:
        return {"error": f"Unsupported language: {lang_key}. Supported: {', '.join(LANGUAGE_CONFIGS)}"}

    header = _header(
        name=f"Security Scan ({lang_key})",
        triggers={
            "push": {"branches": ["main"]},
            "pull_request": {"branches": ["main"]},
            "schedule": None,
        },
        permissions={"contents": "read", "security-events": "write"},
        concurrency=True,
    )

    # Fix the schedule section
    header = header.replace("  schedule:\n", "  schedule:\n    - cron: '0 6 * * 1'\n")

    audit_cmd = lang["audit_cmd"]

    jobs = textwrap.dedent(f"""\
    jobs:
      dependency-audit:
        runs-on: ubuntu-latest
        timeout-minutes: 10
        steps:
          - uses: actions/checkout@v4

          - uses: {lang["setup_action"]}
            with:
              {lang["setup_key"]}: '{lang["default_version"]}'

          - name: Install dependencies
            run: {lang["install_cmd"] if lang["install_cmd"] else "echo 'No install step needed'"}

          - name: Dependency audit
            run: {audit_cmd}

      codeql:
        runs-on: ubuntu-latest
        timeout-minutes: 15
        permissions:
          security-events: write
          contents: read
        steps:
          - uses: actions/checkout@v4

          - name: Initialize CodeQL
            uses: github/codeql-action/init@v3
            with:
              languages: {lang_key if lang_key != 'node' else 'javascript'}

          - name: Autobuild
            uses: github/codeql-action/autobuild@v3

          - name: Perform CodeQL Analysis
            uses: github/codeql-action/analyze@v3

      secrets-scan:
        runs-on: ubuntu-latest
        timeout-minutes: 5
        steps:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0

          - name: Scan for secrets
            uses: trufflesecurity/trufflehog@main
            with:
              extra_args: --only-verified
    """)

    workflow = header + jobs

    if output_format == "json":
        return {
            "workflow_type": "security-scan",
            "language": lang_key,
            "yaml": workflow,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return workflow


def generate_release(lang_key, output_format):
    """Generate a release workflow."""
    lang = LANGUAGE_CONFIGS.get(lang_key)
    if not lang:
        return {"error": f"Unsupported language: {lang_key}. Supported: {', '.join(LANGUAGE_CONFIGS)}"}

    header = _header(
        name=f"Release ({lang_key})",
        triggers={
            "release": {"types": ["published"]},
        },
        permissions={"contents": "write", "packages": "write", "id-token": "write"},
        concurrency=False,
    )

    publish_step = ""
    if lang["publish_cmd"]:
        publish_step = textwrap.dedent(f"""\

          - name: Publish package
            run: {lang["publish_cmd"]}
            env:
              TWINE_USERNAME: __token__
              TWINE_PASSWORD: ${{{{ secrets.PYPI_TOKEN }}}}
    """)

    jobs = textwrap.dedent(f"""\
    jobs:
      release:
        runs-on: ubuntu-latest
        timeout-minutes: 15
        steps:
          - uses: actions/checkout@v4

          - uses: {lang["setup_action"]}
            with:
              {lang["setup_key"]}: '{lang["default_version"]}'

          - name: Install dependencies
            run: {lang["install_cmd"] if lang["install_cmd"] else "echo 'No install step needed'"}

          - name: Build
            run: {lang["build_cmd"] if lang["build_cmd"] else "echo 'No build step needed'"}{publish_step}
          - name: Upload release assets
            uses: softprops/action-gh-release@v2
            with:
              files: |
                dist/*
                build/*
              generate_release_notes: true
    """)

    workflow = header + jobs

    if output_format == "json":
        return {
            "workflow_type": "release",
            "language": lang_key,
            "yaml": workflow,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return workflow


def generate_docs_check(output_format):
    """Generate a documentation check workflow."""
    header = _header(
        name="Documentation Check",
        triggers={
            "pull_request": {"paths": ["docs/**", "*.md", "**/*.md"]},
        },
        permissions={"contents": "read", "pull-requests": "write"},
    )

    jobs = textwrap.dedent("""\
    jobs:
      check-docs:
        runs-on: ubuntu-latest
        timeout-minutes: 5
        steps:
          - uses: actions/checkout@v4

          - name: Check for broken links
            uses: lycheeverse/lychee-action@v1
            with:
              args: --verbose --no-progress '**/*.md'
              fail: true

          - name: Lint markdown
            run: |
              npm install -g markdownlint-cli
              markdownlint '**/*.md' --ignore node_modules

          - name: Check spelling
            uses: streetsidesoftware/cspell-action@v6
            with:
              files: '**/*.md'
              strict: false

          - name: Verify README sections
            run: |
              for file in $(find . -name 'README.md' -not -path '*/node_modules/*'); do
                echo "Checking $file..."
                if ! grep -q '## ' "$file"; then
                  echo "WARNING: $file has no H2 sections"
                fi
              done
    """)

    workflow = header + jobs

    if output_format == "json":
        return {
            "workflow_type": "docs-check",
            "yaml": workflow,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return workflow


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub Actions workflow YAML from templates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s --type ci --language python --test-framework pytest
              %(prog)s --type cd --language node --deploy-target kubernetes
              %(prog)s --type security-scan --language python
              %(prog)s --type release --language go
              %(prog)s --type docs-check
              %(prog)s --type ci --language python --format json
        """),
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["ci", "cd", "release", "security-scan", "docs-check"],
        help="Type of workflow to generate.",
    )
    parser.add_argument(
        "--language",
        choices=list(LANGUAGE_CONFIGS.keys()),
        help="Programming language (required for ci, cd, release, security-scan).",
    )
    parser.add_argument(
        "--test-framework",
        help="Test framework override (default depends on language).",
    )
    parser.add_argument(
        "--deploy-target",
        choices=list(DEPLOY_TARGETS.keys()),
        default="kubernetes",
        help="Deployment target for CD workflows (default: kubernetes).",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml).",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file instead of stdout.",
    )

    args = parser.parse_args()

    # Validate language requirement
    if args.type in ("ci", "cd", "release", "security-scan") and not args.language:
        parser.error(f"--language is required for --type {args.type}")

    # Generate
    generators = {
        "ci": lambda: generate_ci(args.language, args.test_framework, args.format),
        "cd": lambda: generate_cd(args.language, args.deploy_target, args.format),
        "release": lambda: generate_release(args.language, args.format),
        "security-scan": lambda: generate_security_scan(args.language, args.format),
        "docs-check": lambda: generate_docs_check(args.format),
    }

    result = generators[args.type]()

    # Handle errors
    if isinstance(result, dict) and "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if isinstance(result, dict):
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Workflow written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
