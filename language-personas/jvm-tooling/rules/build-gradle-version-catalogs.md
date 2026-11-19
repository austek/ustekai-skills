---
title: Centralize Dependency Versions in a Gradle Version Catalog
impact: HIGH
impactDescription: one file changes a version everywhere instead of editing N build.gradle.kts files
tags: [gradle, version-catalog, dependency-management, build-configuration]
---

# Centralize Dependency Versions in a Gradle Version Catalog [HIGH]

## Description
A Gradle version catalog (`gradle/libs.versions.toml`, stable since Gradle 7.4) is a single TOML file with `[versions]`, `[libraries]`, `[bundles]`, and `[plugins]` tables that Gradle turns into type-safe accessors — `libs.jackson.databind`, `libs.bundles.testing`, `libs.plugins.spotless` — available in every subproject's build script without an extra `apply` or import. Without a catalog, each subproject's `build.gradle.kts` hardcodes its own coordinate-and-version string, so bumping a shared library means grepping the whole tree for `"2.17.0"` and hoping every occurrence is the same dependency and not a coincidental version match on something else.

The catalog also closes a class of silent typo bugs: `libs.jackson.databind` is a generated property that fails at configuration time (with a clear "unresolved reference" from the IDE) if the alias is wrong, whereas a hand-typed string like `"com.fasterxml.jakson:jakson-databind:2.17.0"` resolves to nothing and fails much later, deep in dependency resolution, with a less obvious error. Because the accessors are generated, IDEs autocomplete them, which surfaces the full set of approved dependencies as you type rather than requiring a trip to another file to copy-paste a coordinate.

`[bundles]` groups dependencies that are always added together — a `testing` bundle bundling JUnit 5, AssertJ, and Mockito means adding one line (`testImplementation(libs.bundles.testing)`) instead of three, and removing a library from the bundle definition removes it from every module that uses the bundle in one edit.

## Bad Example
```kotlin
// app/build.gradle.kts
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.0")
}

// billing/build.gradle.kts
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.1") // drifted, nobody noticed
}
```

## Good Example
```toml
# gradle/libs.versions.toml
[versions]
jackson = "2.17.0"

[libraries]
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }

[bundles]
testing = ["junit-jupiter", "assertj-core", "mockito-core"]
```
```kotlin
// any subproject build.gradle.kts
dependencies {
    implementation(libs.jackson.databind)
    testImplementation(libs.bundles.testing)
}
```

## Notes
- Declare the catalog via `dependencyResolutionManagement { versionCatalogs { ... } }` in `settings.gradle.kts`, or drop the file at the conventional `gradle/libs.versions.toml` path and Gradle picks it up automatically.
- `version.ref` points at a `[versions]` entry so multiple libraries can share one version number (e.g. all Jackson modules tracking the same release train).
- A catalog can be published as a standalone artifact and consumed by multiple repositories, giving an organization one source of truth for approved versions across projects, not just within one build.

## References
- [Gradle User Guide — Version Catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html)
- [Gradle User Guide — Sharing dependency versions between projects](https://docs.gradle.org/current/userguide/platforms.html)
