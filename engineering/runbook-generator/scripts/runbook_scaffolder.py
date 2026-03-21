#!/usr/bin/env python3
"""Runbook Scaffolder — Generate runbook markdown templates from service definitions.

Accepts a JSON service definition (via file or stdin) containing service name,
stack components, dependencies, and endpoints. Produces a production-grade
runbook markdown file with deployment steps, rollback procedures, monitoring
checks, escalation paths, and staleness tracking.

Usage:
    python runbook_scaffolder.py --input service.json
    python runbook_scaffolder.py --input service.json --output runbook.md
    cat service.json | python runbook_scaffolder.py --input -
    python runbook_scaffolder.py --input service.json --json
    python runbook_scaffolder.py --input service.json --type incident
"""

import argparse
import json
import sys
import textwrap
from datetime import date


RUNBOOK_TYPES = ["deployment", "incident", "database", "scaling", "monitoring"]

DEPLOY_COMMANDS = {
    "vercel": "vercel --prod",
    "fly": "fly deploy --app $APP_NAME",
    "kubernetes": "kubectl apply -f k8s/deployment.yaml",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --force-new-deployment",
    "heroku": "git push heroku main",
    "docker-compose": "docker-compose -f docker-compose.prod.yml up -d",
}

ROLLBACK_COMMANDS = {
    "vercel": "vercel rollback $PREVIOUS_DEPLOYMENT_URL",
    "fly": "fly releases --app $APP_NAME\nfly deploy --image $PREVIOUS_IMAGE",
    "kubernetes": "kubectl rollout undo deployment/$APP_NAME",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --task-definition $PREV_TASK_DEF",
    "heroku": "heroku rollback --app $APP_NAME",
    "docker-compose": "docker-compose -f docker-compose.prod.yml down\ndocker-compose -f docker-compose.prod.yml up -d --no-build",
}

DB_BACKUP_COMMANDS = {
    "postgresql": 'pg_dump $PROD_DB_URL --format=custom --compress=9 --file="backup-$(date +%Y%m%d-%H%M%S).dump"',
    "mysql": 'mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > "backup-$(date +%Y%m%d-%H%M%S).sql"',
    "mongodb": 'mongodump --uri="$MONGO_URI" --out="backup-$(date +%Y%m%d-%H%M%S)"',
}

SCALE_COMMANDS = {
    "kubernetes": "kubectl scale deployment/$APP_NAME --replicas=$REPLICA_COUNT",
    "fly": "fly scale count $REPLICA_COUNT --app $APP_NAME",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --desired-count $REPLICA_COUNT",
    "heroku": "heroku ps:scale web=$REPLICA_COUNT --app $APP_NAME",
    "docker-compose": "docker-compose -f docker-compose.prod.yml up -d --scale web=$REPLICA_COUNT",
}


def load_service_definition(input_path):
    """Load and validate a JSON service definition from file or stdin."""
    try:
        if input_path == "-":
            data = json.load(sys.stdin)
        else:
            with open(input_path, "r") as f:
                data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found — {input_path}", file=sys.stderr)
        sys.exit(1)

    required = ["name"]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"Error: Missing required fields — {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    data.setdefault("stack", {})
    data.setdefault("dependencies", [])
    data.setdefault("endpoints", [])
    data.setdefault("contacts", {})
    data["stack"].setdefault("hosting", "kubernetes")
    data["stack"].setdefault("database", "postgresql")
    data["stack"].setdefault("ci_cd", "github-actions")
    data["stack"].setdefault("framework", "unknown")

    return data


def build_deployment_runbook(svc):
    """Build a deployment runbook markdown string."""
    hosting = svc["stack"]["hosting"].lower()
    db = svc["stack"]["database"].lower()
    today = date.today().isoformat()

    deploy_cmd = DEPLOY_COMMANDS.get(hosting, f"# Deploy using {hosting}")
    rollback_cmd = ROLLBACK_COMMANDS.get(hosting, f"# Rollback using {hosting}")

    health_checks = ""
    for ep in svc.get("endpoints", []):
        url = ep if isinstance(ep, str) else ep.get("url", ep.get("path", "/health"))
        health_checks += f"curl -sf {url} | jq .\n"
    if not health_checks:
        health_checks = "curl -sf https://$APP_HOST/api/health | jq .\n"

    contacts_table = _build_contacts_table(svc.get("contacts", {}))
    deps_list = "\n".join(f"- {d}" for d in svc.get("dependencies", [])) or "- None documented"
    config_files = svc.get("config_files", ["vercel.json", ".github/workflows/deploy.yml"])
    staleness_rows = "\n".join(
        f"| {cf} | `git log -1 --format=%ci -- {cf}` | Deploy |"
        for cf in config_files
    )

    return textwrap.dedent(f"""\
    # Deployment Runbook — {svc['name']}

    **Stack:** {svc['stack']['framework']} + {db} + {hosting}
    **Last verified:** {today}
    **Owner:** {svc.get('contacts', {}).get('owner', 'FILL IN')}
    **Estimated total time:** 15-25 minutes

    ---

    ## Staleness Check

    | Config File | Last Modified | Affects Steps |
    |-------------|--------------|---------------|
    {staleness_rows}

    If any config was modified after the "Last verified" date, review affected steps.

    ---

    ## Dependencies

    {deps_list}

    ## Pre-Deployment Checklist

    - [ ] All PRs merged to main
    - [ ] CI passing on main branch
    - [ ] Database migrations tested in staging
    - [ ] Rollback plan confirmed
    - [ ] On-call engineer notified

    ## Step 1: Verify CI Status (2 min)

    ```bash
    gh run list --branch main --limit 3
    ```

    VERIFY: Latest run shows green checkmark. If red, do not proceed.

    ## Step 2: Apply Database Migrations (5 min)

    ```bash
    DATABASE_URL=$STAGING_DB_URL pnpm db:migrate
    DATABASE_URL=$STAGING_DB_URL pnpm db:migrate status
    ```

    VERIFY: Output shows "All migrations applied" with today's date.

    ```bash
    DATABASE_URL=$PROD_DB_URL pnpm db:migrate
    ```

    VERIFY: Same output as staging. If error, see Rollback section.

    ## Step 3: Deploy to Production (5 min)

    ```bash
    {deploy_cmd}
    ```

    VERIFY: Deployment dashboard shows new version in progress.

    ## Step 4: Smoke Test (5 min)

    ```bash
    {health_checks.strip()}
    ```

    VERIFY: Health returns `{{"status": "ok"}}`. Error rate < 1%.

    ## Step 5: Monitor (10 min)

    Watch metrics for 10 minutes:
    - Error rate: < 1%
    - P95 latency: < 200ms
    - DB connections: < 80% of max

    ---

    ## Rollback

    ```bash
    {rollback_cmd}
    ```

    VERIFY: Previous version serving traffic. Re-run smoke tests.

    ---

    ## Escalation

    {contacts_table}
    """)


def build_incident_runbook(svc):
    """Build an incident response runbook."""
    contacts_table = _build_contacts_table(svc.get("contacts", {}))
    return textwrap.dedent(f"""\
    # Incident Response Runbook — {svc['name']}

    **Severity:** P1 (down), P2 (degraded), P3 (minor)
    **Last verified:** {date.today().isoformat()}
    **Owner:** {svc.get('contacts', {}).get('owner', 'FILL IN')}

    ---

    ## Phase 1: Triage (5 min)

    ```bash
    curl -sw "%{{http_code}}" https://$APP_HOST/api/health -o /dev/null
    ```

    VERIFY: 200 = app is up. 5xx or timeout = incident confirmed.

    | Condition | Severity | Action |
    |-----------|----------|--------|
    | Site completely unreachable | P1 | Page L2/L3 immediately |
    | Partial degradation | P2 | Notify team channel |
    | Single feature broken | P3 | Create ticket |

    ## Phase 2: Diagnose (10-15 min)

    ```bash
    git log --oneline -10
    ```

    Check for recent deployments and correlate with incident start time.

    ## Phase 3: Mitigate

    Apply the first applicable fix:
    1. Rollback last deployment
    2. Kill runaway database queries
    3. Scale up replicas
    4. Enable circuit breaker for failing external dependency

    ## Phase 4: Resolve and Postmortem

    Within 24 hours:
    1. Write incident timeline
    2. Identify root cause (5 Whys)
    3. Define action items with owners
    4. Update this runbook

    ---

    ## Escalation

    {contacts_table}
    """)


def build_database_runbook(svc):
    """Build a database maintenance runbook."""
    db = svc["stack"]["database"].lower()
    backup_cmd = DB_BACKUP_COMMANDS.get(db, f"# Backup command for {db}")
    return textwrap.dedent(f"""\
    # Database Maintenance Runbook — {svc['name']}

    **Database:** {db}
    **Schedule:** Weekly vacuum (automated), monthly manual review
    **Last verified:** {date.today().isoformat()}

    ---

    ## Step 1: Backup (5 min)

    ```bash
    {backup_cmd}
    ```

    VERIFY: Backup file exists and size > 0.

    ## Step 2: Check Bloat (3 min)

    ```bash
    psql $PROD_DB_URL -c "
    SELECT tablename,
           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
           n_dead_tup,
           ROUND(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1) AS dead_pct
    FROM pg_stat_user_tables
    ORDER BY n_dead_tup DESC
    LIMIT 10;"
    ```

    VERIFY: Identify tables with dead_pct > 5%.

    ## Step 3: Vacuum (5 min)

    ```bash
    psql $PROD_DB_URL -c "VACUUM ANALYZE <table_name>;"
    ```

    VERIFY: dead_pct drops below 5% after vacuum.

    ## Step 4: Reindex (10 min)

    ```bash
    psql $PROD_DB_URL -c "REINDEX INDEX CONCURRENTLY <index_name>;"
    ```

    VERIFY: Index size reduced. Query performance stable.

    ## Rollback

    Restore from backup if vacuum or reindex causes issues:
    ```bash
    pg_restore --dbname=$PROD_DB_URL backup-*.dump
    ```
    """)


def build_scaling_runbook(svc):
    """Build a scaling operations runbook."""
    hosting = svc["stack"]["hosting"].lower()
    scale_cmd = SCALE_COMMANDS.get(hosting, f"# Scale command for {hosting}")
    return textwrap.dedent(f"""\
    # Scaling Runbook — {svc['name']}

    **Hosting:** {hosting}
    **Last verified:** {date.today().isoformat()}

    ---

    ## When to Scale

    - CPU utilization > 70% sustained for 5+ minutes
    - Memory utilization > 80%
    - Request queue depth increasing
    - P95 latency > 500ms

    ## Step 1: Assess Current State (2 min)

    Check current replica count and resource utilization before scaling.

    ## Step 2: Scale Up (3 min)

    ```bash
    {scale_cmd}
    ```

    VERIFY: New replicas are running and receiving traffic.

    ## Step 3: Monitor (10 min)

    Watch metrics for 10 minutes to confirm scaling resolved the issue.

    ## Scale Down

    After the load subsides, scale back to baseline to control costs.

    ```bash
    {scale_cmd.replace('$REPLICA_COUNT', '$BASELINE_COUNT')}
    ```
    """)


def build_monitoring_runbook(svc):
    """Build a monitoring setup runbook."""
    endpoints = svc.get("endpoints", [])
    ep_checks = ""
    for ep in endpoints:
        url = ep if isinstance(ep, str) else ep.get("url", ep.get("path", "/health"))
        ep_checks += f"    - URL: {url}\n"
    if not ep_checks:
        ep_checks = "    - URL: https://$APP_HOST/api/health\n"

    return textwrap.dedent(f"""\
    # Monitoring Runbook — {svc['name']}

    **Last verified:** {date.today().isoformat()}

    ---

    ## Health Check Endpoints

{ep_checks}
    ## Key Metrics

    | Metric | Warning Threshold | Critical Threshold |
    |--------|------------------|-------------------|
    | Error rate | > 1% | > 5% |
    | P95 latency | > 200ms | > 1000ms |
    | CPU utilization | > 70% | > 90% |
    | Memory utilization | > 75% | > 90% |
    | DB connections | > 60% of max | > 80% of max |

    ## Alert Configuration

    Configure alerts for each critical threshold. Ensure PagerDuty integration
    is active for P1-level alerts.

    ## Dashboard Links

    - Application dashboard: FILL IN
    - Database dashboard: FILL IN
    - Infrastructure dashboard: FILL IN

    ## On-Call Rotation

    Ensure the on-call schedule is current. Review monthly.
    """)


def _build_contacts_table(contacts):
    """Build a markdown escalation table from contacts dict."""
    if not contacts:
        return (
            "| Level | Who | When | Contact |\n"
            "|-------|-----|------|---------|\n"
            "| L1 | On-call engineer | First responder | PagerDuty rotation |\n"
            "| L2 | Platform lead | Escalation | FILL IN |\n"
            "| L3 | VP Engineering | Production down > 30 min | FILL IN |"
        )
    rows = ["| Level | Who | When | Contact |", "|-------|-----|------|---------|"]
    level_map = {"l1": "First responder", "l2": "Escalation", "l3": "Production down > 30 min"}
    for level in ["l1", "l2", "l3"]:
        info = contacts.get(level, {})
        if isinstance(info, str):
            rows.append(f"| {level.upper()} | {info} | {level_map.get(level, '')} | FILL IN |")
        elif isinstance(info, dict):
            rows.append(
                f"| {level.upper()} | {info.get('name', 'FILL IN')} "
                f"| {level_map.get(level, '')} | {info.get('contact', 'FILL IN')} |"
            )
        else:
            rows.append(f"| {level.upper()} | FILL IN | {level_map.get(level, '')} | FILL IN |")
    return "\n".join(rows)


BUILDERS = {
    "deployment": build_deployment_runbook,
    "incident": build_incident_runbook,
    "database": build_database_runbook,
    "scaling": build_scaling_runbook,
    "monitoring": build_monitoring_runbook,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate runbook markdown templates from JSON service definitions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Example service definition JSON:
              {
                "name": "my-api",
                "stack": {"hosting": "kubernetes", "database": "postgresql",
                          "ci_cd": "github-actions", "framework": "FastAPI"},
                "dependencies": ["redis", "stripe-api", "sendgrid"],
                "endpoints": ["/api/health", "/api/v1/users"],
                "contacts": {
                  "owner": "Platform Team",
                  "l1": {"name": "On-call", "contact": "PagerDuty"},
                  "l2": {"name": "Platform Lead", "contact": "#platform-lead"}
                },
                "config_files": ["k8s/deployment.yaml", ".github/workflows/deploy.yml"]
              }
        """),
    )
    parser.add_argument("--input", "-i", required=True, help="Path to JSON service definition (use - for stdin)")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--type", "-t", default="deployment", choices=RUNBOOK_TYPES,
                        help="Runbook type to generate (default: deployment)")
    parser.add_argument("--json", action="store_true", help="Output as JSON with metadata")

    args = parser.parse_args()
    svc = load_service_definition(args.input)
    builder = BUILDERS[args.type]
    content = builder(svc)

    if args.json:
        result = {
            "service": svc["name"],
            "runbook_type": args.type,
            "generated_date": date.today().isoformat(),
            "stack": svc["stack"],
            "content": content,
        }
        output = json.dumps(result, indent=2)
    else:
        output = content

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Runbook written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
