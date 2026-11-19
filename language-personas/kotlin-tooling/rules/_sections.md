# Section Definitions

## Compiler (compiler)
**Impact:** HIGH

**Rules:**
- `compiler-all-warnings-as-errors` - Treat Kotlin compiler warnings as errors in CI

## Static Analysis (static-analysis)
**Impact:** HIGH

**Rules:**
- `static-analysis-detekt-ci-gate` - Fail the build on detekt findings with a committed baseline

## Lint & Formatting (lint-format)
**Impact:** MEDIUM

**Rules:**
- `lint-format-ktlint-or-spotless-check` - Gate CI on a Kotlin formatter check and reserve auto-format for local use

## CI Quality Gates (ci-quality-gates)
**Impact:** MEDIUM

**Rules:**
- `ci-quality-gates-kover-coverage` - Gate coverage with Kover on changed logic, not a global percentage
