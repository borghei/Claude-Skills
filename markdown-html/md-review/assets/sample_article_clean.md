---
title: Rotating service credentials
description: How to rotate the widget service credentials on the ninety-day cycle.
author: Docs Team
date: 2026-07-14
tags:
  - security
  - operations
---

# Rotating service credentials

Every widget service credential expires after ninety days. This guide shows how
to rotate one before it expires. Plan for about ten minutes of work.

## Before you start

You need console access and a filed change record. Ask the platform team if you
are missing either one. Both take a day to arrange, so start early.

## Rotate the credential

Install the client first. Then run the rotate command against the target
environment.

```bash
npm install --global widget-cli
widget-cli auth login
widget-cli creds rotate --env production
```

The command prints a new secret. Copy it into the vault right away. The old
secret stays valid for one hour, which gives you time to update consumers.

![Terminal output showing a rotated credential and its new expiry date](sample_review_config.json)

## Verify the change

Check that every consumer picked up the new secret. The dashboard lists each
consumer and the secret version it holds.

| Consumer | Expected version | Check interval |
| --- | --- | --- |
| API gateway | v4 | 60 seconds |
| Job runner | v4 | 5 minutes |
| Reporting job | v4 | 1 hour |

If a consumer still holds the old version after an hour, restart it. See the
[rotate the credential](#rotate-the-credential) steps above to confirm you
copied the right secret.

## If something breaks

Roll back with the previous secret from the vault. The vault keeps the last
three versions. File an incident note and tell the on-call engineer.

Full reference material lives in the
[review configuration file](sample_review_config.json) and on the
[public documentation site](https://example.com/docs).
