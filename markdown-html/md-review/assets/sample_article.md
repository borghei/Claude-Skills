---
title: Deploying The Widget Service To Production Using Our Standard Pipeline
description: A walkthrough of the deployment pipeline.
author: Docs Team
date: 2026-07-14
---

# Deploying the widget service

The widget service is deployed by the release pipeline whenever a tag is pushed
to the default branch. This guide explains the pipeline stages and the manual
approval gate.

### Prerequisites

Before you begin, it should be confirmed by the reader that access has been
granted to the deployment console, that the required credentials were rotated
within the last ninety days, and that the change record was filed with the
platform team at least one full business day before the intended release window
so that the on-call rotation can be notified in advance of any disruption.

Access is requested through the internal portal. See
[click here](https://internal.example.com/access) to open a request.

## Installation

Install the command line client on your workstation.

```bash
npm install --global widget-cli
widget-cli auth login
```

The client is written in Javascript and talks to the backend over gRPC. The
frontend console is a separate application and is not required for deployment.

![](../assets/pipeline-overview.png)

## Pipeline Stages

The pipeline has four stages. Each stage is gated by the previous one.

| Stage | Owner | Duration |
| Build | Platform | 4 min |
| Test | QA | 11 min |
| Stage | Platform | 6 min |
| Deploy | Release manager | 3 min |

![screenshot](../assets/stage-timings.png)

Detailed timings are maintained in the
[pipeline runbook](./missing-runbook.md).

## rollback procedure

If a deploy fails, the previous revision is restored automatically by the
controller within ninety seconds, and an e-mail is sent to the release channel,
but if the automatic rollback is itself unsuccessful because the previous
revision has already been garbage collected by the registry retention policy
then a manual restore must be performed by the on-call engineer using the
archived image bundle stored in cold storage.

Read the [prerequisites](#missing-prerequisites) again before retrying.

See the [installation section](#installation) for client setup, and the
[review configuration](./sample_review_config.json) for gate thresholds.

# Appendix

Additional notes are published on the [project web site](https://example.com/docs)
and mirrored on our Github organisation page.
