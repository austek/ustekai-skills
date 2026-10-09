---
description: Budgeted, sharded repo audit: report, file issues, fix in worktrees, or open PRs
argument-hint: "[path] [--act report|issues|fix|pr] [--budget 2M|30%|$5] [--lanes ci,docs,deps,security,arch,tests|all] [--since REF] [--max-shards N] [--with skill=args] [--resume] [--schedule CRON] (all optional; defaults: report, 25% of plan ceiling else 2M tokens, deps lane)"
allowed-tools: Bash, Read, Glob, Grep, Skill, Agent
---

Invoke the `audit` skill with these arguments: $ARGUMENTS
