---
description: Alias for /audit with every lane enabled (report only unless --act is given)
argument-hint: "[path] [--act report|issues|fix|pr] [--budget 2M|30%|$5] [--lanes LIST] [--since REF] [--max-shards N] [--with skill=args] [--resume] [--schedule CRON] (--lanes defaults to all)"
allowed-tools: Bash, Read, Glob, Grep, Skill, Agent
---

Invoke the `audit` skill with these arguments: `--lanes all --act report $ARGUMENTS`

Arguments later in the list override the defaults placed before them.
