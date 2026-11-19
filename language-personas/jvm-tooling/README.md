# JVM Tooling

Gradle and Maven build and dependency rules shared by Java, Kotlin and Scala projects, designed for AI agents and LLMs.

## Overview

This skill provides 9 rules across 3 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Build Configuration | `build-` | HIGH | 4 |
| Toolchain | `toolchain-` | HIGH | 1 |
| Dependency Management | `dependency-management-` | MEDIUM | 4 |

## Rules

### Build Configuration (HIGH)
- `build-api-vs-implementation-scope` - Treat api vs implementation as a compile-avoidance lever, not just encapsulation
- `build-gradle-version-catalogs` - Centralize dependency versions in a Gradle version catalog
- `build-maven-dependency-management-bom` - Import a BOM in dependencyManagement instead of pinning every version
- `build-reproducible-builds` - Ban dynamic version ranges and non-deterministic archive output

### Toolchain (HIGH)
- `toolchain-pin-jdk` - Pin the JDK with a Gradle toolchain and release target

### Dependency Management (MEDIUM)
- `dependency-management-lockfile-or-bom` - Pick one source of truth — dependency lockfile or BOM, not neither
- `dependency-management-minimal-transitive-exposure` - Exclude unneeded transitive dependencies instead of accepting the full graph
- `dependency-management-version-catalog-single-source` - Make the version catalog the only place a version number can appear
- `dependency-management-vulnerability-scanning` - Scan dependencies for known CVEs on every build, not at release time

## Structure

```
jvm-tooling/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Applicability

Written for Gradle and Maven. Scala projects on sbt or Mill get the principles (single version source, reproducible builds, dependency scanning, a pinned JDK) but not the syntax.

## Related

- [java-tooling](../java-tooling/SKILL.md), [kotlin-tooling](../kotlin-tooling/SKILL.md), [scala-tooling](../scala-tooling/SKILL.md)
