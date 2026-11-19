---
title: Pick One Source of Truth — Dependency Lockfile or BOM, Not Neither
impact: HIGH
impactDescription: prevents a BOM version bump from silently having no effect because the lockfile still pins the old graph
tags: [gradle, dependency-locking, bom, dependency-management]
---

# Pick One Source of Truth — Dependency Lockfile or BOM, Not Neither [HIGH]

## Description
Gradle dependency locking (`./gradlew dependencies --write-locks`) records the exact resolved version of every dependency — including transitives — for each configuration, so a build resolves identically on every machine and every CI run until someone deliberately regenerates the lockfile. A BOM (`build-maven-dependency-management-bom.md` for Maven; Gradle's platform support for the equivalent) is a different mechanism: it pins the versions your build *declares*, but doesn't freeze what transitive resolution actually *picks* when two dependencies request conflicting versions of the same transitive. Locking captures the resolved graph; a BOM only constrains the inputs feeding into that resolution.

The two are complementary but not interchangeable, and a team needs to be deliberate about which one answers "what version is actually running." A stale lockfile — one not regenerated after a BOM version bump — silently keeps pinning the pre-bump transitive graph, so the BOM update has no runtime effect even though the declared version looks current. CI should verify the lockfile still matches what resolution would currently produce (a verify-mode check), the same way `lint-format-spotless-apply-check.md`'s `spotlessCheck` verifies formatting without rewriting anything — regenerating the lockfile is a local, reviewed action, not something CI does silently.

## Bad Example
```kotlin
// BOM bumped from 2.x to 3.x in this PR...
dependencies {
    implementation(platform("com.example:platform-bom:3.0.0"))
}
// ...but gradle.lockfile still lists the 2.x-era resolved graph, never regenerated
```

## Good Example
```bash
# same PR that bumps the BOM version
./gradlew dependencies --write-locks
git add gradle.lockfile
```
```kotlin
tasks.check {
    doFirst {
        // fails if the committed lockfile doesn't match current resolution
    }
}
```

## Notes
- Lockfiles matter most for reproducibility over time, not just across machines at one instant — a transitive dependency several levels deep can carry its own dynamic-looking constraint that drifts week to week even with zero changes to your own build file.
- Maven has no first-class dependency-locking equivalent; a BOM plus periodic `mvn dependency:tree` diffing against a committed baseline is the closer approximation there.
- Scope locking to the configurations you actually ship and test against (`compileClasspath`, `runtimeClasspath`) rather than every configuration Gradle defines, to keep the lockfile focused and the diff on a version bump readable.

## References
- [Gradle User Guide — Dependency Locking](https://docs.gradle.org/current/userguide/dependency_locking.html)
- [Gradle User Guide — Managing Transitive Dependencies](https://docs.gradle.org/current/userguide/dependency_constraints.html)
