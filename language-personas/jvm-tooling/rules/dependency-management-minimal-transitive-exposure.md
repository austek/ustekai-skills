---
title: Exclude Unneeded Transitive Dependencies Instead of Accepting the Full Graph
impact: MEDIUM
impactDescription: shrinks both the vulnerability-scan surface and the version-conflict surface of the resolved classpath
tags: [transitive-dependencies, dependency-management, gradle, attack-surface]
---

# Exclude Unneeded Transitive Dependencies Instead of Accepting the Full Graph [MEDIUM]

## Description
Every declared dependency pulls its own transitive graph onto the classpath by default, whether or not your code — or even the code paths of the direct dependency you actually wanted — uses any of it. `./gradlew :module:dependencies --configuration compileClasspath` (or `mvn dependency:tree`) makes that graph visible; `dependencyInsight --dependency X` explains why a specific transitive is present and which direct dependency pulled it in, which is usually the faster starting point when investigating an unexpected classpath entry.

Unused transitives aren't free. Each one is additional surface area for `dependency-management-vulnerability-scanning.md` to flag a CVE against, additional potential for a version conflict with some other dependency's own transitive requirement, and additional bytes in a deployed artifact or additional classes for a classloader to index. `exclude group: "...", module: "..."` on a direct dependency's declaration removes a specific transitive precisely — but it needs re-verification whenever that direct dependency's own version changes, since a new release can restructure its transitive graph and either make the exclusion redundant or, worse, remove something the exclusion was never meant to touch.

This is a distinct concern from the `api`/`implementation` visibility question in `build-api-vs-implementation-scope.md`: visibility controls what's exposed to *consumers* of your module, exclusion controls what's on *your own* classpath at all. A transitive can be correctly scoped `implementation` and still be pure dead weight nobody asked for.

## Bad Example
```kotlin
dependencies {
    implementation("com.example:some-client:4.2.0")
    // pulls in a concrete logging implementation transitively that this
    // project already binds elsewhere — nobody noticed the duplicate binding
}
```

## Good Example
```kotlin
dependencies {
    implementation("com.example:some-client:4.2.0") {
        exclude(group = "org.slf4j", module = "slf4j-simple")
    }
}
```

## Notes
- `dependencyInsight` output showing one transitive requested at three different versions by three unrelated direct dependencies is worth investigating on its own — that's exactly where Gradle's conflict resolution silently picks one version and discards the others' compatibility assumptions.
- Exclude at the narrowest scope — the specific direct dependency pulling the unwanted transitive — rather than a blanket per-configuration exclude, so a legitimate future need for that transitive via a different dependency isn't also blocked.
- This is a build-time optimization as much as a security one: fewer classes to resolve, download, and index is a smaller, faster classpath regardless of any CVE angle.

## References
- [Gradle User Guide — Excluding Transitive Dependencies](https://docs.gradle.org/current/userguide/dependency_downgrade_and_exclude.html)
- [Gradle User Guide — Viewing and Debugging Dependencies](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html)
