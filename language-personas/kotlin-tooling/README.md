# Kotlin Tooling

Kotlin build, lint and CI configuration, designed for AI agents and LLMs. Gradle scoping, version catalogs, toolchains and dependency rules are in [jvm-tooling](../jvm-tooling/SKILL.md).

## Overview

This skill provides 4 rules across 4 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Compiler | `compiler-` | HIGH | 1 |
| Static Analysis | `static-analysis-` | HIGH | 1 |
| Lint & Formatting | `lint-format-` | MEDIUM | 1 |
| CI Quality Gates | `ci-quality-gates-` | MEDIUM | 1 |

## Rules

### Compiler & Static Analysis (HIGH)
- `compiler-all-warnings-as-errors` - Treat Kotlin compiler warnings as errors in CI
- `static-analysis-detekt-ci-gate` - Fail the build on detekt findings with a committed baseline

### Formatting & Coverage (MEDIUM)
- `lint-format-ktlint-or-spotless-check` - Gate CI on a Kotlin formatter check and reserve auto-format for local use
- `ci-quality-gates-kover-coverage` - Gate coverage with Kover on changed logic, not a global percentage

## Structure

```
kotlin-tooling/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Related

- [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [kotlin-testing](../kotlin-testing/SKILL.md)
