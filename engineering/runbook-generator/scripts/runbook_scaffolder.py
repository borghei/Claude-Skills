#!/usr/bin/env python3
"""Runbook Scaffolder: generate a runbook markdown draft from a JSON service definition.

Commands are derived from the stack (hosting, database, CI/CD, framework or
stack.migrate_command). Every type has timed numbered steps with VERIFY lines, a
Rollback section, an escalation table and Owner / Last verified fields, so a
draft passes runbook_validator.py; what the tool cannot know is left as FILL IN.

Usage:
    python runbook_scaffolder.py --input service.json --type incident --output runbook.md

Exit codes: 0 = runbook written, 2 = unusable input (missing file, bad JSON, wrong shape).
"""

import argparse
import json
import sys
from datetime import date

RUNBOOK_TYPES = ["deployment", "incident", "database", "scaling", "monitoring"]

DEPLOY = {
    "vercel": "vercel --prod",
    "fly": "fly deploy --app $APP_NAME",
    "kubernetes": "kubectl apply -f k8s/deployment.yaml\nkubectl rollout status deployment/$APP_NAME --timeout=5m",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --force-new-deployment",
    "heroku": "git push heroku main",
    "docker-compose": "docker compose -f docker-compose.prod.yml up -d",
}
ROLLBACK = {
    "vercel": "vercel rollback $PREVIOUS_DEPLOYMENT_URL",
    "fly": "fly releases --app $APP_NAME\nfly deploy --app $APP_NAME --image $PREVIOUS_IMAGE",
    "kubernetes": "kubectl rollout undo deployment/$APP_NAME\nkubectl rollout status deployment/$APP_NAME",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --task-definition $PREV_TASK_DEF",
    "heroku": "heroku rollback --app $APP_NAME",
    "docker-compose": "docker compose -f docker-compose.prod.yml up -d --no-build  # with the previous image tag pinned",
}
SCALE = {
    "kubernetes": "kubectl scale deployment/$APP_NAME --replicas=$REPLICA_COUNT",
    "fly": "fly scale count $REPLICA_COUNT --app $APP_NAME",
    "aws-ecs": "aws ecs update-service --cluster $CLUSTER --service $SERVICE --desired-count $REPLICA_COUNT",
    "heroku": "heroku ps:scale web=$REPLICA_COUNT --app $APP_NAME",
    "docker-compose": "docker compose -f docker-compose.prod.yml up -d --scale web=$REPLICA_COUNT",
}
REPLICAS = {
    "kubernetes": "kubectl get deployment/$APP_NAME\nkubectl top pods -l app=$APP_NAME",
    "fly": "fly status --app $APP_NAME",
    "aws-ecs": "aws ecs describe-services --cluster $CLUSTER --services $SERVICE",
    "heroku": "heroku ps --app $APP_NAME",
    "docker-compose": "docker compose -f docker-compose.prod.yml ps",
}
CI_STATUS = {
    "github-actions": "gh run list --branch main --limit 3",
    "gitlab-ci": "glab ci list --branch main",
}
MIGRATE = {  # by framework; override with stack.migrate_command
    "fastapi": "alembic upgrade head", "flask": "flask db upgrade", "django": "python manage.py migrate",
    "rails": "bin/rails db:migrate", "laravel": "php artisan migrate --force",
    "nextjs": "npx prisma migrate deploy", "express": "npx prisma migrate deploy", "nestjs": "npx prisma migrate deploy",
}
BACKUP = {
    "postgresql": 'pg_dump "$PROD_DB_URL" --format=custom --file="backup-$(date +%Y%m%d-%H%M%S).dump"',
    "mysql": 'mysqldump --single-transaction -h "$DB_HOST" -u "$DB_USER" -p "$DB_NAME" > "backup-$(date +%Y%m%d-%H%M%S).sql"',
    "mongodb": 'mongodump --uri="$MONGO_URI" --out="backup-$(date +%Y%m%d-%H%M%S)"',
}
RESTORE = {
    "postgresql": 'pg_restore --clean --dbname="$PROD_DB_URL" "$BACKUP_FILE"',
    "mysql": 'mysql -h "$DB_HOST" -u "$DB_USER" -p "$DB_NAME" < "$BACKUP_FILE"',
    "mongodb": 'mongorestore --uri="$MONGO_URI" --drop "$BACKUP_DIR"',
}
MAINTAIN = {  # (inspect command, maintenance command, what to verify)
    "postgresql": ('psql "$PROD_DB_URL" -c "SELECT relname, n_dead_tup, n_live_tup FROM pg_stat_user_tables '
                   'ORDER BY n_dead_tup DESC LIMIT 10;"',
                   'psql "$PROD_DB_URL" -c "VACUUM (ANALYZE) $TABLE_NAME;"\n'
                   'psql "$PROD_DB_URL" -c "REINDEX INDEX CONCURRENTLY $INDEX_NAME;"',
                   "n_dead_tup for the table drops; p95 query latency is unchanged or better."),
    "mysql": ('mysql -h "$DB_HOST" -u "$DB_USER" -p -e "SELECT table_name, data_free FROM information_schema.tables '
              'WHERE table_schema=\'$DB_NAME\' ORDER BY data_free DESC LIMIT 10;"',
              'mysqlcheck -h "$DB_HOST" -u "$DB_USER" -p --analyze "$DB_NAME"',
              "mysqlcheck reports OK for every table."),
    "mongodb": ('mongosh "$MONGO_URI" --eval "db.stats()"',
                'mongosh "$MONGO_URI" --eval "db.runCommand({compact: \'$COLLECTION\'})"',
                "compact returns ok: 1; storage size for the collection falls."),
}


def fail(msg):
    """Print a one-line error and exit 2 (unusable input)."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def load_service_definition(path):
    """Load and validate the service definition JSON (file path or '-' for stdin)."""
    try:
        data = json.load(sys.stdin) if path == "-" else json.load(open(path, encoding="utf-8"))
    except OSError as e:
        fail(f"cannot read {path}: {e.strerror}")
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON: {e}")
    if not isinstance(data, dict) or not data.get("name"):
        fail("service definition must be a JSON object with a non-empty 'name'")
    stack = data.setdefault("stack", {})
    if not isinstance(stack, dict) or not isinstance(data.setdefault("contacts", {}), dict):
        fail("'stack' and 'contacts' must be objects")
    for key, default in (("hosting", "kubernetes"), ("database", "postgresql"),
                         ("ci_cd", "github-actions"), ("framework", "unknown")):
        stack[key] = str(stack.get(key) or default).lower()
    data.setdefault("dependencies", [])
    data.setdefault("endpoints", [])
    return data


def code(cmd):
    """Fence a shell command."""
    return f"```bash\n{cmd.strip()}\n```"


def step(n, title, minutes, cmd, verify):
    body = [f"## Step {n}: {title} ({minutes} min)", ""] + ([code(cmd), ""] if cmd else [])
    return "\n".join(body + [f"VERIFY: {verify}", ""])


def urls(svc):
    out = []
    for ep in svc["endpoints"]:
        u = ep if isinstance(ep, str) else (ep.get("url") or ep.get("path") or "/health")  # str or {url|path}
        out.append(u if u.startswith("http") else f"https://$APP_HOST{u}")
    return out or ["https://$APP_HOST/health"]


def header(svc, kind, extra=()):
    s = svc["stack"]
    lines = [f"# {kind} Runbook: {svc['name']}", "",
             f"**Stack**: {s['framework']} + {s['database']} + {s['hosting']} (CI: {s['ci_cd']})",
             f"**Owner**: {svc['contacts'].get('owner') or 'FILL IN'}",
             f"**Last verified**: {date.today().isoformat()} (scaffolded; re-date after a staging dry run)",
             *extra, "", "---", ""]
    deps = "\n".join(f"- {d}" for d in svc["dependencies"]) or "- None documented"
    return "\n".join(lines + ["## Dependencies", "", deps, ""])


def escalation(svc):
    c = svc["contacts"]
    when = {"l1": "First responder", "l2": "No mitigation in 15 min", "l3": "Production down > 30 min"}
    default = {"l1": ("On-call engineer", "Paging rotation"), "l2": ("Service lead", "FILL IN"),
               "l3": ("Engineering manager", "FILL IN")}
    rows = ["## Escalation", "", "| Level | Who | When | Contact |", "|-------|-----|------|---------|"]
    for lvl in ("l1", "l2", "l3"):
        info = c.get(lvl)
        who, contact = default[lvl]
        if isinstance(info, str):
            who = info
        elif isinstance(info, dict):
            who, contact = info.get("name", who), info.get("contact", contact)
        rows.append(f"| {lvl.upper()} | {who} | {when[lvl]} | {contact} |")
    return "\n".join(rows) + "\n"


def staleness(svc):
    files = svc.get("config_files") or []
    if not files:
        return ""
    rows = "\n".join(f"| `{f}` | `git log -1 --format=%ci -- {f}` |" for f in files)
    return ("## Staleness Check\n\nIf any file below changed after Last verified, re-check the steps that use it.\n\n"
            "| Config file | Last modified |\n|-------------|---------------|\n" + rows + "\n")


def rollback(cmd, verify):
    return f"## Rollback\n\n{code(cmd)}\n\nVERIFY: {verify}\n"


def build_deployment(svc):
    s = svc["stack"]
    host = s["hosting"]
    migrate = s.get("migrate_command") or MIGRATE.get(s["framework"], f"# FILL IN: migration command for {s['framework']}")
    ci = CI_STATUS.get(s["ci_cd"], f"# FILL IN: check the latest main build in {s['ci_cd']}")
    smoke = "\n".join(f"curl -fsS {u}" for u in urls(svc))
    checklist = "\n".join(f"- [ ] {i}" for i in (
        "Change merged to main and CI green", "Migrations dry-run in staging", "Previous release id noted for rollback",
        "On-call engineer aware of the deploy window"))
    return "\n".join([
        header(svc, "Deployment", ["**Estimated total time**: 20-30 minutes", "**Dashboard**: FILL IN"]),
        staleness(svc), "## Pre-Deployment Checklist", "", checklist, "",
        step(1, "Confirm CI status", 2, ci, "The latest main run is green. If not, stop."),
        step(2, "Apply migrations in staging", 5, f'DATABASE_URL="$STAGING_DB_URL" {migrate}',
             "Command exits 0 and staging still serves traffic."),
        step(3, "Apply migrations in production", 5, f'DATABASE_URL="$PROD_DB_URL" {migrate}',
             "Command exits 0. If it fails, stop and use Rollback; do not retry blindly."),
        step(4, "Deploy", 5, DEPLOY.get(host, f"# FILL IN: deploy command for {host}"),
             "The new version is live on every instance."),
        step(5, "Smoke test", 5, smoke, "Every endpoint returns 2xx; error rate stays under 1% for 10 minutes."),
        rollback(ROLLBACK.get(host, f"# FILL IN: rollback command for {host}"),
                 "The previous version serves traffic; re-run Step 5. Schema changes need their own down migration."),
        escalation(svc)])


def build_incident(svc):
    first = urls(svc)[0]
    host = svc["stack"]["hosting"]
    severity = ("| Condition | Severity | Action |\n|-----------|----------|--------|\n"
                "| Service unreachable | P1 | Page L2 now |\n| Partial degradation | P2 | Notify the team channel |\n"
                "| One feature broken | P3 | Open a ticket |")
    return "\n".join([
        header(svc, "Incident Response", ["**Severity scale**: P1 (down), P2 (degraded), P3 (minor)",
                                          "**Dashboard**: FILL IN"]),
        "## Response Checklist", "", "- [ ] Incident channel opened", "- [ ] Incident lead named", "",
        step(1, "Triage", 5, f'curl -s -o /dev/null -w "%{{http_code}}\\n" {first}',
             "200 means the service is up; 5xx or a timeout confirms the incident."),
        severity, "",
        step(2, "Diagnose", 15, "git log --oneline --since='6 hours ago'\n" + REPLICAS.get(host, ""),
             "You can name the change or dependency that lines up with the start time, or you have ruled out deploys."),
        step(3, "Mitigate", 10, ROLLBACK.get(host, f"# FILL IN: rollback command for {host}"),
             "Error rate is back under 1%. If a rollback is not the cause, scale up or disable the failing dependency."),
        step(4, "Resolve and write the postmortem", 30, "",
             "Timeline, root cause and owned action items are written within 24 hours, and this runbook is updated."),
        rollback(ROLLBACK.get(host, f"# FILL IN: rollback command for {host}"),
                 "If a mitigation made things worse, return to the last known-good release."),
        escalation(svc)])


def build_database(svc):
    db = svc["stack"]["database"]
    inspect, maintain, verify = MAINTAIN.get(db, (f"# FILL IN: inspect {db}", f"# FILL IN: maintain {db}",
                                                   "The maintenance command succeeds."))
    return "\n".join([
        header(svc, "Database Maintenance", [f"**Database**: {db}", "**Dashboard**: FILL IN"]),
        "## Pre-Maintenance Checklist", "", "- [ ] Low-traffic window agreed", "- [ ] Restore tested this quarter", "",
        step(1, "Backup", 10, BACKUP.get(db, f"# FILL IN: backup command for {db}"),
             "The backup exists, is larger than zero bytes, and its name is recorded as $BACKUP_FILE."),
        step(2, "Inspect", 3, inspect, "You have the list of tables or collections that need work."),
        step(3, "Run maintenance", 15, maintain, verify),
        rollback(RESTORE.get(db, f"# FILL IN: restore command for {db}"),
                 "Row counts on key tables match the pre-maintenance values."),
        escalation(svc)])


def build_scaling(svc):
    host = svc["stack"]["hosting"]
    scale = SCALE.get(host, f"# FILL IN: scale command for {host}")
    return "\n".join([
        header(svc, "Scaling", [f"**Hosting**: {host}", "**Dashboard**: FILL IN"]),
        "## When to Scale", "", "- [ ] CPU above 70% for 5+ minutes", "- [ ] Memory above 80%",
        "- [ ] p95 latency above the SLO", "",
        step(1, "Record the current state", 2, REPLICAS.get(host, f"# FILL IN: show replicas for {host}"),
             "Current replica count is written down as $BASELINE_COUNT."),
        step(2, "Scale up", 3, scale, "New replicas are running and receiving traffic."),
        step(3, "Watch", 10, "", "CPU, memory and p95 latency fall back under their thresholds."),
        rollback(scale.replace("$REPLICA_COUNT", "$BASELINE_COUNT"),
                 "Replica count equals $BASELINE_COUNT once load subsides."),
        escalation(svc)])


def build_monitoring(svc):
    checks = "\n".join(f"curl -fsS {u}" for u in urls(svc))
    metrics = ("| Metric | Warning | Critical |\n|--------|---------|----------|\n| Error rate | > 1% | > 5% |\n"
               "| p95 latency | > 200 ms | > 1000 ms |\n| CPU | > 70% | > 90% |\n| DB connections | > 60% of max | > 80% of max |")
    return "\n".join([
        header(svc, "Monitoring", ["**Dashboard**: FILL IN"]),
        "## Coverage Checklist", "", "- [ ] Every endpoint below has an uptime check",
        "- [ ] Every critical threshold pages someone", "", metrics, "",
        step(1, "Check health endpoints", 2, checks, "Each endpoint returns 2xx."),
        step(2, "Fire a test alert", 5, "# Trigger your alerting tool's test notification for this service",
             "The on-call engineer receives the page within 2 minutes."),
        rollback("# Revert the alert rule change in the monitoring config repo and redeploy it",
                 "Alert rules match the last known-good version."),
        escalation(svc)])


BUILDERS = {"deployment": build_deployment, "incident": build_incident, "database": build_database,
            "scaling": build_scaling, "monitoring": build_monitoring}


def main():
    p = argparse.ArgumentParser(description="Generate a runbook markdown draft from a JSON service definition.",
                                epilog="Example input: assets/sample_service.json. Exit codes: 0 ok, 2 bad input.")
    p.add_argument("--input", "-i", required=True, help="JSON service definition (use - for stdin)")
    p.add_argument("--output", "-o", help="Output file (default: stdout)")
    p.add_argument("--type", "-t", default="deployment", choices=RUNBOOK_TYPES, help="Runbook type")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    p.add_argument("--json", action="store_true", help="Same as --format json")
    args = p.parse_args()

    svc = load_service_definition(args.input)
    content = BUILDERS[args.type](svc).replace("\n\n\n", "\n\n")
    if args.json or args.format == "json":
        content = json.dumps({"service": svc["name"], "runbook_type": args.type,
                              "generated_date": date.today().isoformat(), "stack": svc["stack"],
                              "content": content}, indent=2)
    if not args.output:
        return print(content)
    try:
        open(args.output, "w", encoding="utf-8").write(content + "\n")
    except OSError as e:
        fail(f"cannot write {args.output}: {e.strerror}")
    print(f"Runbook written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
