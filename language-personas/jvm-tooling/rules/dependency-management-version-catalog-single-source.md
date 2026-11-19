---
title: Make the Version Catalog the Only Place a Version Number Can Appear
impact: MEDIUM
impactDescription: closes the drift path where one subproject quietly hardcodes a version the catalog already manages
tags: [gradle, version-catalog, governance, multi-module]
---

# Make the Version Catalog the Only Place a Version Number Can Appear [MEDIUM]

## Description
`build-gradle-version-catalogs.md` covers the mechanics of `libs.versions.toml`; this rule is the governance policy that makes a catalog actually function as a single source of truth across a multi-module build. No subproject `build.gradle.kts` may declare a hardcoded coordinate-and-version string for any dependency the catalog already manages — not even as a "temporary" override for one module under deadline pressure. A catalog that coexists with scattered hardcoded versions elsewhere isn't a single source of truth, it's an additional, easily-forgotten place to look; the moment one subproject pins its own version alongside the catalog, the codebase has two answers to "what version of X do we use," and nothing but discipline keeps them from drifting apart.

Enforcing this mechanically, rather than relying on review vigilance, closes the gap: a CI check — a custom task, or a `grep` for a literal Maven-coordinate-with-version pattern across `build.gradle.kts` files outside the catalog itself — fails the build if any subproject declares a version for a coordinate the catalog already defines. This catches the realistic regression path: someone adds a new dependency under time pressure, hardcodes the version to unblock themselves immediately, means to move it into the catalog "later," and later never arrives without something forcing the issue.

## Bad Example
```kotlin
// billing/build.gradle.kts — catalog manages jackson at 2.17.0
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0") // silently diverges
}
```

## Good Example
```kotlin
// billing/build.gradle.kts
dependencies {
    implementation(libs.jackson.databind) // only source of the version is the catalog
}
```

## Notes
- The same discipline applies to a shared, published catalog consumed across multiple repositories — a repo that locally overrides a version "just this once" reintroduces the exact drift the shared catalog exists to prevent.
- Add new dependencies to the catalog first, then reference them — never declare inline as a shortcut, even for a spike; the small friction of adding a catalog entry is the point, not an obstacle to route around.
- Pairs with `dependency-management-lockfile-or-bom.md`: the catalog is the single source for what version is *requested*; a lockfile, where used, is the single source for what version is actually *resolved*.

## References
- [Gradle User Guide — Version Catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html)
- [Gradle User Guide — Sharing Dependency Versions Between Projects](https://docs.gradle.org/current/userguide/platforms.html)
