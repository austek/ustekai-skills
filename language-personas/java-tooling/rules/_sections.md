# Section Definitions

## Static Analysis (static-analysis)
**Impact:** HIGH

Catch defects and boundary violations at build time with static analysis tools.

**Rules:**
- `static-analysis-archunit-boundary-tests` - Enforce package and layer boundaries with ArchUnit tests
- `static-analysis-error-prone-compiler-plugin` - Run error prone as a javac plugin, not a separate analysis pass
- `static-analysis-nullaway` - Enforce default non-null with NullAway, not just Objects.requireNonNull
- `static-analysis-spotbugs-ci-gate` - Fail the build on SpotBugs findings, don't just report them

## CI Quality Gates (ci-quality-gates)
**Impact:** MEDIUM

Gate CI on build cache, coverage, warnings, and mutation testing so it enforces real quality.

**Rules:**
- `ci-quality-gates-build-cache` - Enable a shared remote build cache so CI time tracks what changed
- `ci-quality-gates-coverage-threshold` - Gate CI on a deliberately scoped coverage threshold, not a blunt global percentage
- `ci-quality-gates-fail-on-warnings` - Treat compiler warnings as errors in CI
- `ci-quality-gates-mutation-testing` - Use PITest to verify tests actually assert something, not just execute lines

## Lint & Formatting (lint-format)
**Impact:** MEDIUM

Enforce consistent formatting and import order without relying on human review.

**Rules:**
- `lint-format-javadoc-tool-alignment` - Configure Javadoc linters to match the documentation rules
- `lint-format-checkstyle-config` - Scope Checkstyle to structural checks, not formatting
- `lint-format-google-java-format` - Adopt google-java-format for zero-config, deterministic formatting
- `lint-format-import-order` - Enforce deterministic import order, ban wildcard imports
- `lint-format-spotless-apply-check` - Gate CI on spotlessCheck, reserve spotlessApply for local hooks
