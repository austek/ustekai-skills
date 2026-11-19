---
name: java-tooling
description: Java development tooling configuration and best practices for Gradle/Maven builds, static analysis, CI quality gates, dependency management, and lint/formatting. Use when setting up a Java project, configuring build tools, static analyzers, or CI gates, or when editing pom.xml or build.gradle(.kts).
paths:
  - "**/*.java"
  - "pom.xml"
  - "build.gradle"
  - "build.gradle.kts"
---

# Java Tooling

A comprehensive guide to Java development tooling. Configuration best practices for build systems, static analysis, CI quality gates, dependency management, and formatting.

## Categories

Build configuration and dependency management rules are JVM-wide and live in [jvm-tooling](../jvm-tooling/SKILL.md). Apply them together with this skill.

### Static Analysis [HIGH]
Catch defects and boundary violations at build time with static analysis tools.

| Rule | Description |
|------|-------------|
| [static-analysis-archunit-boundary-tests](rules/static-analysis-archunit-boundary-tests.md) | Enforce package and layer boundaries with ArchUnit tests |
| [static-analysis-error-prone-compiler-plugin](rules/static-analysis-error-prone-compiler-plugin.md) | Run error prone as a javac plugin, not a separate analysis pass |
| [static-analysis-nullaway](rules/static-analysis-nullaway.md) | Enforce default non-null with NullAway, not just Objects.requireNonNull |
| [static-analysis-spotbugs-ci-gate](rules/static-analysis-spotbugs-ci-gate.md) | Fail the build on SpotBugs findings, don't just report them |

### CI Quality Gates [MEDIUM]
Gate CI on build cache, coverage, warnings, and mutation testing so it enforces real quality.

| Rule | Description |
|------|-------------|
| [ci-quality-gates-build-cache](rules/ci-quality-gates-build-cache.md) | Enable a shared remote build cache so CI time tracks what changed |
| [ci-quality-gates-coverage-threshold](rules/ci-quality-gates-coverage-threshold.md) | Gate CI on a deliberately scoped coverage threshold, not a blunt global percentage |
| [ci-quality-gates-fail-on-warnings](rules/ci-quality-gates-fail-on-warnings.md) | Treat compiler warnings as errors in CI |
| [ci-quality-gates-mutation-testing](rules/ci-quality-gates-mutation-testing.md) | Use PITest to verify tests actually assert something, not just execute lines |

### Lint & Formatting [MEDIUM]
Enforce consistent formatting and import order without relying on human review.

| Rule | Description |
|------|-------------|
| [lint-format-checkstyle-config](rules/lint-format-checkstyle-config.md) | Scope Checkstyle to structural checks, not formatting |
| [lint-format-javadoc-tool-alignment](rules/lint-format-javadoc-tool-alignment.md) | Configure Javadoc linters to match the documentation rules |
| [lint-format-google-java-format](rules/lint-format-google-java-format.md) | Adopt google-java-format for zero-config, deterministic formatting |
| [lint-format-import-order](rules/lint-format-import-order.md) | Enforce deterministic import order, ban wildcard imports |
| [lint-format-spotless-apply-check](rules/lint-format-spotless-apply-check.md) | Gate CI on spotlessCheck, reserve spotlessApply for local hooks |

## Quick Reference

### Static Analysis
```java
@AnalyzeClasses(packages = "com.example")
class ArchitectureTest {

    @ArchTest
    static final ArchRule domainStaysFree = noClasses()
        .that().resideInAPackage("..domain..")
        .should().dependOnClassesThat().resideInAnyPackage("..infrastructure..", "org.springframework..");
}
```

### CI Quality Gates
```kotlin
tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.addAll(listOf("-Xlint:all", "-Werror"))
}
```

### Lint & Formatting
```kotlin
tasks.check {
    dependsOn(tasks.spotlessCheck) // CI verifies, never rewrites
}
```

## See Also

- [jvm-tooling](../jvm-tooling/SKILL.md) - Gradle/Maven build and dependency rules shared by Java, Kotlin and Scala
- [java-coding-standards](../java-coding-standards/SKILL.md) - General Java coding standards and best practices
- [java-testing](../java-testing/SKILL.md) - Test-writing best practices for JUnit 5, AssertJ, Mockito, and Testcontainers
