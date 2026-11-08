"""Scenario stems for question_bank_generator.py.

Each competency has concrete stems that are filled with the role and a
level-appropriate scope, so a "senior frontend engineer / react" bank asks about
a real situation instead of "describe your experience with react". Stems are
starting points: the interviewer should still swap in the team's own product,
stack and constraints.

Placeholders: {role} (e.g. "Frontend Engineer"), {scope} (what someone at this
level owns), {scale} (a level-appropriate size), {horizon} (planning horizon).
"""

from __future__ import annotations

from typing import Dict, List, Optional

LEVEL_CONTEXT: Dict[str, Dict[str, str]] = {
    "junior": {"scope": "the feature you work on", "scale": "a few thousand users", "horizon": "a sprint"},
    "mid": {"scope": "the component your team owns", "scale": "tens of thousands of users", "horizon": "a quarter"},
    "senior": {"scope": "the service you own", "scale": "hundreds of thousands of users",
               "horizon": "two quarters"},
    "staff": {"scope": "a system several teams depend on", "scale": "millions of users", "horizon": "a year"},
    "principal": {"scope": "an organisation-wide platform", "scale": "tens of millions of users",
                  "horizon": "several years"},
}

ALIASES = {
    "ts": "typescript", "js": "javascript", "k8s": "kubernetes", "system_architecture": "system_design",
    "architecture": "system_design", "sql": "databases", "database": "databases", "data_modeling": "databases",
    "ci_cd": "devops", "cicd": "devops", "infrastructure": "devops", "aws": "cloud", "gcp": "cloud", "azure": "cloud",
    "ml": "machine_learning", "ai": "machine_learning", "ux": "user_research", "ui": "frontend",
    "people_management": "leadership", "mentorship": "mentoring", "stakeholders": "stakeholder_management",
    "strategy": "product_strategy", "product_sense": "product_strategy", "metrics": "analytics",
    "data_analysis": "analytics", "monitoring": "observability", "reliability": "observability",
    "a11y": "accessibility", "teamwork": "collaboration", "api": "api_design", "apis": "api_design",
    # role-mapping competencies from question_bank_generator.py
    "advanced_coding": "coding_fundamentals", "python_r": "python", "html_css_js": "frontend",
    "react_vue_angular": "frontend", "basic_frameworks": "frontend", "frontend_development": "frontend",
    "frontend_architecture": "frontend", "state_management": "frontend", "responsive_design": "frontend",
    "backend_development": "backend", "server_side_programming": "backend", "api_consumption": "api_design",
    "database_basics": "databases", "database_design": "databases", "security_basics": "security",
    "performance_optimization": "performance", "caching": "system_design", "distributed_systems": "system_design",
    "microservices": "system_design", "platform_design": "system_design", "automation": "devops",
    "scripting": "devops", "infrastructure_as_code": "devops", "ci_cd_basics": "devops", "basic_cloud": "cloud",
    "container_orchestration": "kubernetes", "reliability_engineering": "observability",
    "mentoring_basics": "mentoring", "team_leadership": "leadership", "cross_functional_collaboration": "collaboration",
    "cross_functional_work": "collaboration", "cross_functional_leadership": "collaboration",
    "stakeholder_communication": "stakeholder_management", "advanced_ml": "machine_learning",
    "basic_ml": "machine_learning", "ml_systems": "machine_learning", "model_evaluation": "statistics",
    "statistical_analysis": "statistics", "experiment_design": "statistics", "basic_analytics": "analytics",
    "data_visualization": "analytics", "user_testing": "user_research", "user_empathy": "user_research",
    "troubleshooting": "debugging", "learning_agility": "adaptability", "innovation": "adaptability",
    "product_roadmap": "product_delivery", "feature_specification": "product_delivery",
    "user_stories": "product_delivery", "design_process": "design", "design_tools": "design",
    "visual_design": "design", "visual_communication": "design", "ui_ux_understanding": "design",
    "design_systems": "design", "design_vision": "strategy", "design_strategy": "strategy",
    "frontend_strategy": "strategy", "technology_strategy": "strategy", "technology_vision": "strategy",
    "architectural_vision": "strategy", "platform_strategy": "strategy", "data_strategy": "strategy",
    "ai_strategy": "strategy", "business_strategy": "strategy", "organizational_strategy": "strategy",
    "strategic_thinking": "strategy", "organizational_design": "organization",
    "organizational_impact": "organization", "organizational_infrastructure": "organization",
    "cross_team_influence": "organization", "strategic_influence": "organization",
    "business_acumen": "business", "business_impact": "business", "p&l_responsibility": "business",
    "market_creation": "business", "market_research": "business", "portfolio_management": "business",
}

# (stem, type, focus areas)
STEMS: Dict[str, List[tuple]] = {
    "react": [
        ("A page in {scope} re-renders on every keystroke and typing lags on low-end phones. How do you find the cause and what do you change?", "technical", ["profiling", "memoization", "state_placement"]),
        ("You are asked to move data fetching for {scope} from useEffect calls to a server or query-cache approach. What do you migrate first, and how do you avoid regressions?", "technical", ["data_fetching", "incremental_migration"]),
        ("A shared React component library is used by five teams and a breaking prop change is needed. How do you ship it?", "situational", ["api_evolution", "deprecation", "communication"]),
    ],
    "typescript": [
        ("An API response type in {scope} is `any` everywhere and bugs reach production. How do you introduce real types without stopping feature work?", "technical", ["gradual_typing", "runtime_validation"]),
        ("Design the types for a form library where each field's value type depends on its config. Walk me through the generics.", "technical", ["generics", "conditional_types"]),
        ("A teammate wants `strict: true` turned on this week across the codebase for {scope}. What is your plan?", "situational", ["migration_strategy", "prioritisation"]),
    ],
    "javascript": [
        ("A memory leak makes a long-lived browser tab for {scope} slow after an hour. How do you find and fix it?", "technical", ["memory_profiling", "event_listeners", "closures"]),
        ("Explain what happens, step by step, when a promise rejects inside an async function nobody awaits, and how you would catch it in production.", "technical", ["event_loop", "error_handling"]),
    ],
    "python": [
        ("A data job in {scope} went from 5 to 50 minutes after a dependency bump. How do you find the regression?", "technical", ["profiling", "dependency_management"]),
        ("You need to make a synchronous Python service for {scale} handle 10x the concurrent requests. What options do you weigh?", "technical", ["concurrency", "async", "trade_offs"]),
    ],
    "go": [
        ("A Go service in {scope} leaks goroutines under load. How do you confirm it and fix the pattern that causes it?", "technical", ["goroutines", "context_cancellation", "pprof"]),
        ("Design the error handling for a Go library that other teams will import. What do callers need to be able to do?", "technical", ["error_wrapping", "api_design"]),
    ],
    "java": [
        ("GC pauses in a Java service in {scope} spike p99 latency. Walk me through diagnosis and the fix.", "technical", ["gc_tuning", "allocation_profiling"]),
        ("You inherit a Spring service with 40-second startup. Where do you look first?", "technical", ["startup_profiling", "dependency_injection"]),
    ],
    "system_design": [
        ("Design the notification system for {scope}: email, push and in-app, at {scale}. What fails first and how do you degrade?", "technical", ["queues", "fan_out", "failure_modes"]),
        ("Design an audit log for {scope} that compliance can query for seven years. How do you store, index and protect it?", "technical", ["storage_tiering", "immutability", "query_patterns"]),
        ("Your design for {scope} needs a database choice today and you are not sure of the read/write mix. How do you decide and keep the option to change?", "situational", ["decision_under_uncertainty", "reversibility"]),
    ],
    "coding_fundamentals": [
        ("Given a log of (user_id, timestamp) events, return each user's longest streak of consecutive active days. Talk through edge cases before coding.", "coding", ["hash_maps", "sorting", "edge_cases"]),
        ("Implement a rate limiter allowing N requests per rolling minute per key. What data structure and why?", "coding", ["sliding_window", "data_structures"]),
    ],
    "frontend": [
        ("The largest contentful paint for the main page of {scope} is 4.5 s on mobile. How do you get it under 2.5 s?", "technical", ["web_vitals", "asset_loading", "rendering"]),
        ("Design and explain the state management for a multi-step checkout that must survive a page reload.", "technical", ["state_management", "persistence"]),
    ],
    "backend": [
        ("An endpoint in {scope} times out when one downstream service is slow. How do you stop one dependency from taking the whole service down?", "technical", ["timeouts", "circuit_breakers", "bulkheads"]),
        ("Two requests update the same order at the same moment and one change is lost. How do you prevent it?", "technical", ["concurrency_control", "idempotency"]),
    ],
    "api_design": [
        ("Design the public API for {scope} so that mobile clients released two years ago keep working. How do you version and deprecate?", "technical", ["versioning", "backward_compatibility"]),
        ("A partner needs bulk export of 10 million records from your API. What do you offer instead of paging through a list endpoint?", "technical", ["async_jobs", "pagination", "rate_limits"]),
    ],
    "databases": [
        ("A query in {scope} that ran in 50 ms now takes 8 s after the table grew. Walk me through the diagnosis.", "technical", ["query_plans", "indexing"]),
        ("You must add a NOT NULL column to a 500-million-row table with no downtime. What is the migration plan?", "technical", ["online_migrations", "backfills"]),
    ],
    "testing": [
        ("The test suite for {scope} takes 40 minutes and 5% of runs fail randomly. What do you do first?", "situational", ["flaky_tests", "test_pyramid", "prioritisation"]),
        ("Which tests would you write for a pricing calculator with discounts, taxes and currency rounding, and which bugs would each catch?", "technical", ["test_design", "boundary_cases"]),
    ],
    "devops": [
        ("Deploys of {scope} fail one time in ten and people re-run them until they pass. How do you fix the process?", "situational", ["pipeline_reliability", "root_cause"]),
        ("Design a rollout for a risky config change that lets you stop and roll back within five minutes.", "technical", ["progressive_delivery", "rollback"]),
    ],
    "kubernetes": [
        ("Pods for {scope} are OOM-killed only during peak hours. How do you investigate and set requests and limits?", "technical", ["resource_management", "capacity"]),
        ("A node pool upgrade must happen without dropping traffic. What do you check and in what order?", "technical", ["pod_disruption_budgets", "draining"]),
    ],
    "cloud": [
        ("The cloud bill for {scope} doubled in a month and nobody knows why. How do you find the cause and stop it recurring?", "situational", ["cost_attribution", "tagging", "budgets"]),
        ("Design multi-region failover for {scope}. What does it cost and what would you leave single-region?", "technical", ["disaster_recovery", "trade_offs"]),
    ],
    "security": [
        ("A dependency used by {scope} has a critical CVE disclosed this morning. Walk me through the next 24 hours.", "situational", ["vulnerability_response", "prioritisation"]),
        ("Design authentication and authorisation for an internal admin tool that can change customer data.", "technical", ["least_privilege", "audit_logging"]),
    ],
    "observability": [
        ("Users report {scope} is 'slow sometimes' but dashboards look fine. How do you find what they are seeing?", "technical", ["tracing", "percentiles", "slo"]),
        ("Define SLOs for {scope}. Which user journeys, which indicators, and what happens when the error budget runs out?", "technical", ["slo_design", "error_budgets"]),
    ],
    "performance": [
        ("p99 latency of {scope} doubled after a release but p50 is unchanged. How do you find the cause?", "technical", ["tail_latency", "profiling"]),
    ],
    "accessibility": [
        ("An audit finds that the main flow of {scope} cannot be completed with a keyboard. How do you fix it and keep it fixed?", "technical", ["keyboard_navigation", "regression_testing"]),
    ],
    "machine_learning": [
        ("A model in {scope} looked great offline but conversion dropped after launch. How do you find out why?", "technical", ["offline_online_gap", "data_drift", "experimentation"]),
        ("How would you decide between fine-tuning a model and improving retrieval for a support-answer feature?", "technical", ["evaluation", "trade_offs"]),
    ],
    "analytics": [
        ("Weekly active users fell 8% overnight. How do you tell a real drop from a tracking bug?", "technical", ["data_quality", "segmentation"]),
        ("Design the metrics for a new onboarding flow in {scope}. What is the north star and what are the guardrails?", "technical", ["metric_design", "guardrails"]),
    ],
    "product_strategy": [
        ("Usage of {scope} has plateaued for two quarters. What would you investigate, and how would you decide what to build next?", "situational", ["diagnosis", "prioritisation"]),
        ("Sales wants a feature for one large customer that does not fit the roadmap for {horizon}. How do you decide?", "situational", ["trade_offs", "stakeholder_alignment"]),
    ],
    "user_research": [
        ("You have two weeks to find out why trial users of {scope} do not convert. What research do you run?", "situational", ["research_planning", "method_choice"]),
    ],
    "design": [
        ("Walk me through a design decision in {scope} where research and stakeholder opinion disagreed. What did you ship?", "behavioral", ["evidence", "influence"]),
    ],
    "leadership": [
        ("Tell me about a time {scope} was off track. What did you notice first, what did you change, and what happened?", "behavioral", ["ownership", "course_correction"]),
        ("Two senior engineers on your team disagree on an architecture choice and work has stalled for a week. What do you do?", "situational", ["decision_making", "conflict_resolution"]),
    ],
    "mentoring": [
        ("Tell me about someone you helped grow into a bigger role. What did you do differently for them than for others?", "behavioral", ["coaching", "feedback"]),
    ],
    "collaboration": [
        ("Describe a time a dependency on another team blocked {scope}. How did you get it unblocked without escalating first?", "behavioral", ["cross_team_work", "influence"]),
    ],
    "communication": [
        ("Explain a technical trade-off from {scope} to me as if I were the finance lead who has to approve the cost.", "situational", ["audience_adaptation", "clarity"]),
    ],
    "stakeholder_management": [
        ("A stakeholder keeps adding requirements to {scope} after sign-off. How do you handle it over the next {horizon}?", "situational", ["expectation_setting", "scope_control"]),
    ],
    "debugging": [
        ("A bug in {scope} only reproduces in production, about once a day. How do you narrow it down without a debugger?", "technical", ["hypothesis_testing", "instrumentation"]),
    ],
    "adaptability": [
        ("Tell me about the last time a technology or process you relied on in {scope} was replaced. How did you get productive again, and how long did it take?", "behavioral", ["learning", "ownership"]),
    ],
    "technical_leadership": [
        ("Your team owns {scope} and has three competing technical proposals for its next {horizon}. How do you get to one decision that the team will commit to?", "situational", ["decision_records", "consensus"]),
        ("Tell me about a technical standard you introduced across {scope}. How did you get adoption without mandating it?", "behavioral", ["influence", "change_management"]),
    ],
    "technology_evaluation": [
        ("A team wants to adopt a new framework for {scope}. What evaluation would you run before saying yes, and what would make you say no?", "situational", ["evaluation_criteria", "proof_of_concept"]),
    ],
    "strategy": [
        ("What should {scope} look like at the end of {horizon}? Name the two bets you would make and the one thing you would stop doing.", "situational", ["vision", "focus", "trade_offs"]),
        ("Tell me about a strategy you set for {scope} that turned out wrong. How did you notice, and what did you change?", "behavioral", ["feedback_loops", "course_correction"]),
    ],
    "organization": [
        ("Two teams working on {scope} keep blocking each other. How would you change ownership or structure, and how would you know it worked?", "situational", ["org_design", "team_topology"]),
        ("Tell me about a change you drove across several teams without having authority over them.", "behavioral", ["influence", "alignment"]),
    ],
    "business": [
        ("Leadership asks whether {scope} is worth more investment next {horizon}. What numbers would you bring and how would you frame the decision?", "situational", ["unit_economics", "business_case"]),
        ("Estimate the market for {scope} in a new region. Walk me through your assumptions and which one you would test first.", "technical", ["market_sizing", "assumption_testing"]),
    ],
    "product_delivery": [
        ("You have a roadmap for {scope} over {horizon} and engineering capacity just dropped by a third. What do you cut and how do you tell stakeholders?", "situational", ["prioritisation", "communication"]),
        ("Write the acceptance criteria for 'users can export their data'. What edge cases do you include?", "technical", ["specification", "edge_cases"]),
    ],
    "statistics": [
        ("An A/B test on {scope} shows +3% conversion with p = 0.04 after the team peeked daily. Would you ship? What would you check?", "technical", ["peeking", "multiple_comparisons", "power"]),
        ("How would you evaluate a churn model for {scope} before anyone acts on its scores?", "technical", ["model_evaluation", "calibration", "business_metrics"]),
    ],
    "data_platform": [
        ("Analysts on {scope} get different numbers for the same metric from two dashboards. How do you fix it at the platform level?", "technical", ["semantic_layer", "data_contracts"]),
    ],
    "problem_solving": [
        ("Tell me about the hardest production problem you solved in {scope}: how you narrowed it down, and what you would do faster now.", "behavioral", ["debugging_method", "reflection"]),
    ],
}


def canonical(competency: str) -> str:
    key = competency.strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(key, key)


def scenario_questions(competency: str, role: str, level: str) -> Optional[List[dict]]:
    """Concrete questions for a competency, or None if no stems exist for it."""
    stems = STEMS.get(canonical(competency))
    if not stems:
        return None
    ctx = dict(LEVEL_CONTEXT.get(level, LEVEL_CONTEXT["senior"]), role=role or "this role")
    return [{"question": stem.format(**ctx), "competency": competency, "type": qtype,
             "focus_areas": focus, "generic": False} for stem, qtype, focus in stems]


def main() -> int:
    """List the competencies (and aliases) with scenario stems, or preview one filled in."""
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(description="List or preview the scenario stems used by question_bank_generator.py")
    p.add_argument("--competency", help="Print the filled-in questions for this competency")
    p.add_argument("--role", default="Software Engineer")
    p.add_argument("--level", default="senior", choices=sorted(LEVEL_CONTEXT))
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()
    if args.competency:
        qs = scenario_questions(args.competency, args.role, args.level)
        if qs is None:
            print(f"error: no stems for '{args.competency}'", file=sys.stderr)
            return 2
        print(json.dumps(qs, indent=2) if args.format == "json" else "\n".join(f"- {q['question']}" for q in qs))
        return 0
    data = {"competencies": sorted(STEMS), "aliases": dict(sorted(ALIASES.items()))}
    print(json.dumps(data, indent=2) if args.format == "json" else
          "Competencies: " + ", ".join(data["competencies"]) + f"\nAliases: {len(ALIASES)} (see --format json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
