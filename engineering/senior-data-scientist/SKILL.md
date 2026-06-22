---
name: senior-data-scientist
description: 
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-science
  updated: 2026-06-17
  tags: [data-science, ml, statistics, experimentation, python, mlops]
---
# Senior Data Scientist

Expert data science for statistical modeling, experimentation, ML deployment, and data-driven decision making — A/B test design and analysis, feature engineering, model training/evaluation, production deployment, and causal inference.

## Keywords

data-science, machine-learning, statistics, a-b-testing, causal-inference,
feature-engineering, mlops, experiment-design, model-deployment, python,
scikit-learn, pytorch, tensorflow, spark, airflow

## Core Capabilities

- **Experiment design & analysis** — hypothesis framing, power analysis and sample sizing, randomization, SRM monitoring, and post-hoc significance testing.
- **Feature engineering** — profiling, candidate generation (temporal/aggregation/interaction/text), selection (variance, correlation, SHAP/RFE), and leakage validation.
- **Model training & evaluation** — stratified/temporal splits, baselines, hyperparameter tuning, cross-validation, calibration, and fairness checks.
- **Production deployment** — containerized serving, input/output drift monitoring (KS/PSI), canary rollouts, and latency/error SLAs.
- **Causal inference** — propensity score matching, difference-in-differences, regression discontinuity, instrumental variables, and assumption/placebo testing.

## When to Use

- Designing or analyzing an A/B test.
- Building a feature engineering pipeline.
- Training, evaluating, or deploying an ML model.
- Estimating treatment effects from observational data.

## Clarify First

Before running an analysis or pipeline, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — A/B test design / feature engineering / model evaluation / causal inference (selects the script and workflow)
- [ ] **Dataset & target variable** — what you are modeling or measuring (drives feature generation and leakage validation)
- [ ] **Decision metric & minimum effect** — the metric and the smallest effect worth detecting (drives power analysis and sample size)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/experiment_designer.py` | A/B test design, power analysis, sample size calculation |
| `scripts/feature_engineering_pipeline.py` | Automated feature generation, correlation analysis, feature selection |
| `scripts/statistical_analyzer.py` | Hypothesis testing, causal inference, regression analysis |
| `scripts/model_evaluation_suite.py` | Model comparison, cross-validation, deployment readiness checks |

> `statistical_analyzer.py` is referenced but not yet present in the repo — see the note in [references/ds-operations.md](references/ds-operations.md). Use inline scipy/statsmodels in the meantime.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/ds-workflows.md](references/ds-workflows.md)** — quick-start commands, tech stack, the five end-to-end workflows (A/B testing, feature pipeline, train/evaluate, deploy, causal inference) with Python snippets, performance targets, and common commands. Read when executing any data-science task.
- **[references/ds-operations.md](references/ds-operations.md)** — troubleshooting table, success criteria, and the full CLI flag reference for each script. Read when diagnosing issues or running the tools.
- **[references/statistical_methods_advanced.md](references/statistical_methods_advanced.md)** — advanced statistical methods reference (hypothesis testing, causal inference, regression). Read for statistical depth.
- **[references/experiment_design_frameworks.md](references/experiment_design_frameworks.md)** — experiment design frameworks and power-analysis foundations. Read when designing rigorous experiments.
- **[references/feature_engineering_patterns.md](references/feature_engineering_patterns.md)** — feature engineering patterns and selection techniques. Read when building features.

## Scope & Limitations

**This skill covers:**
- End-to-end experiment design including power analysis, randomization, and post-hoc analysis
- Feature engineering pipelines with profiling, generation, selection, and validation
- Model training evaluation including cross-validation, calibration, and fairness checks
- Production model deployment with monitoring, drift detection, and canary rollouts

**This skill does NOT cover:**
- Data engineering infrastructure (ETL orchestration, pipeline scheduling, data lake management) -- see `senior-data-engineer`
- Deep learning model architecture design and training at scale (distributed GPU training, custom layers) -- see `senior-ml-engineer`
- Prompt engineering, RAG systems, and LLM fine-tuning workflows -- see `senior-prompt-engineer`
- Computer vision pipelines (object detection, segmentation, video processing) -- see `senior-computer-vision`

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-data-engineer` | Feature pipeline ingests data from ETL outputs; shares data quality validation patterns | Raw data stores --> feature engineering pipeline --> feature store |
| `senior-ml-engineer` | Trained models handed off for MLOps deployment; shares model registry and serving configs | Evaluated model artifacts --> deployment pipeline --> production serving |
| `senior-prompt-engineer` | Embedding features from LLMs feed into ML pipelines; experiment frameworks apply to prompt A/B tests | LLM embeddings --> feature vectors; experiment designs --> prompt evaluation |
| `senior-architect` | Model serving architecture reviewed for scalability; data platform design aligned with training infrastructure | Architecture specs --> deployment topology --> monitoring dashboards |
| `senior-backend` | Model inference endpoints integrated into backend services; API contracts defined for prediction requests | REST/gRPC model API --> backend service layer --> client applications |
| `senior-devops` | CI/CD pipelines extended for model retraining triggers; containerized model images deployed via infrastructure-as-code | Docker images --> Kubernetes manifests --> production clusters |
