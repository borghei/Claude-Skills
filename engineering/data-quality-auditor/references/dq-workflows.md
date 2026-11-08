# End-to-End DQ Workflows

Read this when executing a concrete DQ task: adding DQ to a new dataset, detecting/responding to schema drift, monitoring freshness SLAs, auditing existing pipelines, or hardening after an incident.

## Workflow: Add DQ to a new dataset

1. **Profile** the data — export a sample to CSV/JSON, then `scripts/dq_check_runner.py --profile --data mytable.json` reports row count, null rate, distinct count, a few sample values and min/max/mean for numeric columns.
2. **Pick check thresholds** based on the profile and product knowledge.
3. **Write the checks** — as a `checks.yaml` for `dq_check_runner.py --data mytable.json --checks checks.yaml` (see `assets/checks.yaml`), or in your tool of choice (Great Expectations / dbt tests / Soda / custom SQL).
4. **Wire into pipeline** — checks run on every load. Failures fail the pipeline (with alerting), don't silently produce bad data downstream.
5. **Document the DQ contract** in the data catalog: what does this table guarantee?

## Workflow: Detect and respond to schema drift

1. **Snapshot baseline schema** — `scripts/schema_drift_detector.py --snapshot mytable.json --output baseline.json` infers one from exported rows; or export `information_schema.columns` as `{"columns": [{"name", "type", "nullable", "ordinal"}]}`.
2. **Schedule the detector** — `scripts/schema_drift_detector.py --baseline baseline.json --current current.json --fail-on warning` before every consumer pipeline (or hourly); exit 1 means drift at or above the gate.
3. **On drift detection** — alert + block pipeline; investigate whether the change was intentional (upstream renamed a column) or accidental (data corruption).
4. **If intentional**: update consumer pipelines + baseline. If accidental: roll back upstream or fix.

## Workflow: Monitor freshness SLAs

1. **Define SLA per table** — e.g., `events_table` must be updated within 1 hour; `daily_revenue` within 24 hours.
2. **Wire freshness checks** — `scripts/freshness_monitor.py --data events.json --column event_time --max-age-min 60 --table-name events_table` (exit 1 on breach).
3. **Alert on SLA breach** — via pager/Slack.
4. **Triage** — pipeline failure? upstream delay? logic bug?

## Workflow: Audit existing pipelines

1. **Inventory** all production tables (typically from data catalog).
2. **Score per table** — for each, what % of dimensions have at least one check? There is no catalog scanner here: list each table's existing checks against the six dimensions by hand (or from your dbt/GX manifest), then run `dq_check_runner.py` on a sample of each table to confirm the checks pass today.
3. **Prioritize** — start with customer-facing + Sev1-impact tables.
4. **Schedule remediation** — add missing checks per priority.

## Workflow: Post-incident DQ improvement

1. After a DQ incident, ask: would an automated check have caught this?
2. If yes: add it. The check becomes regression prevention.
3. Document the incident → check mapping. Over time, DQ check inventory reflects organizational pain history.
