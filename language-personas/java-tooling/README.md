# Java Tooling

A comprehensive guide to Java development tools, designed for AI agents and LLMs to configure and use modern Java tooling effectively.

## Overview

This skill provides 13 rules across 3 categories (build and dependency rules live in `jvm-tooling`):

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Static Analysis | `static-analysis-` | HIGH | 4 |
| CI Quality Gates | `ci-quality-gates-` | MEDIUM | 4 |
| Lint & Formatting | `lint-format-` | MEDIUM | 5 |

## Structure

```
skills/java-tooling/
├── SKILL.md              # Skill overview with all rule summaries
├── metadata.json         # Metadata (version, description)
├── README.md             # This file
└── rules/
    ├── _sections.md      # Section definitions
    ├── _template.md      # Rule template
    ├── static-analysis-*.md # Static Analysis rules
    ├── ci-quality-gates-*.md # CI Quality Gates rules
    └── lint-format-*.md    # Lint & Formatting rules
```

## Rules

Build configuration and dependency management rules moved to `jvm-tooling`.

### Static Analysis (HIGH)
- `static-analysis-archunit-boundary-tests` - Enforce package and layer boundaries with ArchUnit tests
- `static-analysis-error-prone-compiler-plugin` - Run error prone as a javac plugin, not a separate analysis pass
- `static-analysis-nullaway` - Enforce default non-null with NullAway, not just Objects.requireNonNull
- `static-analysis-spotbugs-ci-gate` - Fail the build on SpotBugs findings, don't just report them

### CI Quality Gates (MEDIUM)
- `ci-quality-gates-build-cache` - Enable a shared remote build cache so CI time tracks what changed
- `ci-quality-gates-coverage-threshold` - Gate CI on a deliberately scoped coverage threshold, not a blunt global percentage
- `ci-quality-gates-fail-on-warnings` - Treat compiler warnings as errors in CI
- `ci-quality-gates-mutation-testing` - Use PITest to verify tests actually assert something, not just execute lines

### Lint & Formatting (MEDIUM)
- `lint-format-javadoc-tool-alignment` - Configure Javadoc linters to match the documentation rules
- `lint-format-checkstyle-config` - Scope Checkstyle to structural checks, not formatting
- `lint-format-google-java-format` - Adopt google-java-format for zero-config, deterministic formatting
- `lint-format-import-order` - Enforce deterministic import order, ban wildcard imports
- `lint-format-spotless-apply-check` - Gate CI on spotlessCheck, reserve spotlessApply for local hooks

## Related

- [java-coding-standards](../java-coding-standards/README.md) - General Java coding standards and best practices
- [java-testing](../java-testing/README.md) - Test-writing best practices for JUnit 5, AssertJ, Mockito, and Testcontainers

## Usage

This skill is automatically applied when working with Java files (`**/*.java`) and Java build files (`pom.xml`, `build.gradle`, `build.gradle.kts`).
