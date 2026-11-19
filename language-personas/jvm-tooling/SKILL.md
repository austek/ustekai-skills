---
name: jvm-tooling
description: Gradle and Maven build tooling shared by Java, Kotlin and Scala projects covering Gradle version catalogs, api vs implementation scopes, Maven BOMs, reproducible builds, lockfiles, transitive dependency control and vulnerability scanning. Use when setting up or editing Gradle or Maven builds for any JVM project, or when managing dependencies.
paths:
  - "pom.xml"
  - "build.gradle"
  - "build.gradle.kts"
  - "settings.gradle.kts"
  - "gradle/libs.versions.toml"
---

# JVM Tooling

Build and dependency rules written for Gradle and Maven, shared by Java, Kotlin and Scala projects built with those tools. Scala projects on sbt or Mill get the principles but not the syntax. Load together with the language tooling skill (`java-`, `kotlin-` or `scala-tooling`).

## Categories

### Build Configuration [HIGH]
| Rule | Description |
|------|-------------|
| [build-api-vs-implementation-scope](rules/build-api-vs-implementation-scope.md) | Treat api vs implementation as a compile-avoidance lever, not just encapsulation |
| [build-gradle-version-catalogs](rules/build-gradle-version-catalogs.md) | Centralize dependency versions in a Gradle version catalog |
| [build-maven-dependency-management-bom](rules/build-maven-dependency-management-bom.md) | Import a BOM in dependencyManagement instead of pinning every version |
| [build-reproducible-builds](rules/build-reproducible-builds.md) | Ban dynamic version ranges and non-deterministic archive output |

### Dependency Management [MEDIUM]
| Rule | Description |
|------|-------------|
| [dependency-management-lockfile-or-bom](rules/dependency-management-lockfile-or-bom.md) | Pick one source of truth — dependency lockfile or BOM, not neither |
| [dependency-management-minimal-transitive-exposure](rules/dependency-management-minimal-transitive-exposure.md) | Exclude unneeded transitive dependencies instead of accepting the full graph |
| [dependency-management-version-catalog-single-source](rules/dependency-management-version-catalog-single-source.md) | Make the version catalog the only place a version number can appear |
| [dependency-management-vulnerability-scanning](rules/dependency-management-vulnerability-scanning.md) | Scan dependencies for known CVEs on every build, not at release time |

### Toolchain [HIGH]
| Rule | Description |
|------|-------------|
| [toolchain-pin-jdk](rules/toolchain-pin-jdk.md) | Pin the JDK with a Gradle toolchain and release target |

## Quick Reference
```toml
# gradle/libs.versions.toml
[versions]
jackson = "2.17.0"

[libraries]
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
```
```bash
# same PR that bumps the BOM version
./gradlew dependencies --write-locks
git add gradle.lockfile
```

## See Also
- [java-tooling](../java-tooling/SKILL.md), [scala-tooling](../scala-tooling/SKILL.md)
