# JVM Testing

Integration-test rules shared by Java, Kotlin and Scala, designed for AI agents and LLMs.

## Overview

This skill provides 3 rules in 1 category:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Testcontainers | `testcontainers-` | HIGH | 3 |

## Rules

### Testcontainers (HIGH)
- `testcontainers-container-reuse` - Reuse containers across a test run instead of restarting per class
- `testcontainers-lifecycle-scope` - Match container lifecycle scope to what the container represents
- `testcontainers-wait-strategy-explicit` - Declare an explicit wait strategy for every container

## Structure

```
jvm-testing/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── testcontainers-*.md
```

## Applicability

Apply to any JVM test that starts a container. Framework wiring (Spring `@ServiceConnection`, Ktor `testApplication`) belongs in the framework skills.

## Related

- [java-testing](../java-testing/SKILL.md), [scala-testing](../scala-testing/SKILL.md)
