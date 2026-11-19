---
name: kotlin-tooling
description: Kotlin development tooling covering Gradle Kotlin DSL builds, compiler warnings as errors, detekt static analysis, ktlint or Spotless formatting, and Kover coverage gates. Use when setting up a Kotlin project, configuring build tools, static analyzers or CI gates, or editing build.gradle.kts.
paths:
  - "**/*.kt"
  - "build.gradle.kts"
  - "settings.gradle.kts"
  - "config/detekt/**"
  - ".editorconfig"
---

# Kotlin Tooling

Kotlin-specific build, lint and CI configuration. Build, version-catalog, toolchain and dependency rules are shared and live in [jvm-tooling](../jvm-tooling/SKILL.md); apply both.

## Categories

### Compiler & Static Analysis [HIGH]
| Rule | Description |
|------|-------------|
| [compiler-all-warnings-as-errors](rules/compiler-all-warnings-as-errors.md) | Treat Kotlin compiler warnings as errors in CI |
| [static-analysis-detekt-ci-gate](rules/static-analysis-detekt-ci-gate.md) | Fail the build on detekt findings with a committed baseline |

### Formatting & Coverage [MEDIUM]
| Rule | Description |
|------|-------------|
| [lint-format-ktlint-or-spotless-check](rules/lint-format-ktlint-or-spotless-check.md) | Gate CI on a Kotlin formatter check and reserve auto-format for local use |
| [ci-quality-gates-kover-coverage](rules/ci-quality-gates-kover-coverage.md) | Gate coverage with Kover on changed logic, not a global percentage |

## See Also
- [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [kotlin-testing](../kotlin-testing/SKILL.md)
