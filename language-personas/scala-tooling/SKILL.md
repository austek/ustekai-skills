---
name: scala-tooling
description: Scala development tooling configuration and best practices for sbt, Mill, compiler flags, Scalafix, Scalafmt, Scalastyle, and Wartremover. Use when setting up a Scala project, configuring the build, compiler warnings, linters, or formatters, or when editing build.sbt or build.mill.
paths:
  - "**/*.scala"
  - "build.sbt"
  - "build.mill"
---

# Scala Tooling

A comprehensive guide to Scala development tools. Configuration best practices for build systems, compiler flags, Scalafix, Scalafmt, Scalastyle, and Wartremover.

## Categories

### Build [HIGH]
Configure sbt and Mill builds for correct module layout, cross-building, and centralized dependency versions.

| Rule | Description |
|------|-------------|
| [build-cross-scala-version-support](rules/build-cross-scala-version-support.md) | Cross-build with crossScalaVersions and the + command, not duplicated modules |
| [build-dependency-version-management](rules/build-dependency-version-management.md) | Centralize dependency versions in project/Dependencies.scala |
| [build-mill-build-definition](rules/build-mill-build-definition.md) | Define Mill modules with ScalaModule and moduleDeps |
| [build-sbt-multi-module-layout](rules/build-sbt-multi-module-layout.md) | Structure a multi-module sbt build with aggregate and dependsOn |

### Compiler Flags [HIGH]
Turn on the Scala compiler's warning and strictness flags deliberately, and gate CI on them without an all-or-nothing switch.

| Rule | Description |
|------|-------------|
| [compiler-flags-deprecation-and-feature-warnings](rules/compiler-flags-deprecation-and-feature-warnings.md) | Always enable -deprecation and -feature, not just the warning count |
| [compiler-flags-scala3-strict-mode](rules/compiler-flags-scala3-strict-mode.md) | Assemble a strict Scala 3 flag profile beyond the defaults |
| [compiler-flags-unused-imports-error](rules/compiler-flags-unused-imports-error.md) | Fail the build on unused imports with -Wunused, not the retired 2.13 flag name |
| [compiler-flags-xfatal-warnings](rules/compiler-flags-xfatal-warnings.md) | Pair -Xfatal-warnings with -Wconf instead of an all-or-nothing switch |

### Scalafix [HIGH]
Run Scalafix's syntactic and semantic rules in CI check mode to keep the codebase free of unused code and stale patterns.

| Rule | Description |
|------|-------------|
| [scalafix-ci-check-mode](rules/scalafix-ci-check-mode.md) | Compile first, then run scalafixAll --check on CI |
| [scalafix-explicitresulttypes-rule](rules/scalafix-explicitresulttypes-rule.md) | Add explicit result types with the ExplicitResultTypes rule |
| [scalafix-removeunused-rule](rules/scalafix-removeunused-rule.md) | Prune unused imports and locals with the RemoveUnused rule |
| [scalafix-semantic-rules-require-semanticdb](rules/scalafix-semantic-rules-require-semanticdb.md) | Enable SemanticDB before running Scalafix's semantic rules |

### Scalafmt [HIGH]
Commit a pinned Scalafmt config and enforce it in CI check mode, never write mode.

| Rule | Description |
|------|-------------|
| [scalafmt-ci-check-mode](rules/scalafmt-ci-check-mode.md) | Run Scalafmt in check mode on CI, never in write mode |
| [scalafmt-config-committed](rules/scalafmt-config-committed.md) | Commit .scalafmt.conf with a pinned version key |
| [scalafmt-import-sorting](rules/scalafmt-import-sorting.md) | Sort and group imports with the Imports rewrite rule |
| [scalafmt-max-column-consistency](rules/scalafmt-max-column-consistency.md) | Pick one maxColumn value and keep the IDE reading the same config |

### Wartremover [HIGH]
Ban unsafe patterns at compile time with Wartremover, scoped and baselined so it doesn't block legacy code.

| Rule | Description |
|------|-------------|
| [wartremover-ban-null-var-any](rules/wartremover-ban-null-var-any.md) | Ban Wart.Null, Wart.Var, and Wart.Any at compile time |
| [wartremover-ci-integration](rules/wartremover-ci-integration.md) | Scope Wartremover to compile, not test, and let it fail via errors not warnings |
| [wartremover-scalastyle-baseline-for-legacy-code](rules/wartremover-scalastyle-baseline-for-legacy-code.md) | Baseline Wartremover and Scalastyle instead of enforcing everywhere on day one |

### Scalastyle [LOW]
Gate line length and naming style with a committed scalastyle-config.xml.

| Rule | Description |
|------|-------------|
| [scalastyle-line-length-and-style-checks](rules/scalastyle-line-length-and-style-checks.md) | Gate line length and naming style with scalastyle-config.xml |

## Quick Reference

### Build
```scala
// build.sbt
lazy val commonSettings = Seq(
  scalaVersion := "3.3.3",
  organization := "com.example"
)

lazy val core = (project in file("core"))
  .settings(commonSettings)
  .settings(name := "myapp-core")

lazy val api = (project in file("api"))
  .dependsOn(core)
  .settings(commonSettings)
  .settings(name := "myapp-api")

lazy val root = (project in file("."))
  .aggregate(core, api)
  .settings(publish / skip := true)
```

### Compiler Flags
```scala
// build.sbt — fatal by default, with a deliberate, visible carve-out
scalacOptions ++= Seq(
  "-Xfatal-warnings",
  "-Wconf:cat=deprecation:s"
)
```

### Scalafix
```yaml
# CI
- run: sbt compile
- run: sbt "scalafixAll --check"
```

### Scalafmt
```yaml
# CI job — fails the build if anything would change
- run: sbt scalafmtCheckAll scalafmtSbtCheck
```

### Wartremover
```scala
final class Cache(entries: Map[String, String]) {
  def get(key: String): Option[String] =
    entries.get(key)
}
```

### Scalastyle
```xml
<!-- scalastyle-config.xml -->
<scalastyle>
  <check level="error" class="org.scalastyle.file.FileLineLengthChecker" enabled="true">
    <parameters><parameter name="maxLineLength">120</parameter></parameters>
  </check>
  <check level="error" class="org.scalastyle.scalariform.ClassNamesChecker" enabled="true">
    <parameters><parameter name="regex">[A-Z][A-Za-z0-9]*</parameter></parameters>
  </check>
</scalastyle>
```

## See Also

- [scala-coding-standards](../scala-coding-standards/SKILL.md) - General Scala coding standards and best practices
- [scala-testing](../scala-testing/SKILL.md) - Test-writing best practices for MUnit, ScalaTest, ScalaCheck, and mocking discipline
- [jvm-tooling](../jvm-tooling/SKILL.md) - Applies only when Gradle or Maven builds the Scala project; the rules are written for those tools, not sbt or Mill. The principles (single version source, reproducible builds, dependency scanning, pinned JDK) carry over.
