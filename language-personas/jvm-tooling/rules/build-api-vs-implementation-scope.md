---
title: Treat api vs implementation as a Compile-Avoidance Lever, Not Just Encapsulation
impact: HIGH
impactDescription: a leaf-module change that should recompile one module can instead trigger a full-project rebuild
tags: [gradle, build-performance, incremental-compilation, java-library]
---

# Treat api vs implementation as a Compile-Avoidance Lever, Not Just Encapsulation [HIGH]

## Description
Gradle's `java-library` plugin tracks each module's ABI (its public method and field signatures) separately from its implementation, and uses that distinction to decide whether a downstream consumer needs recompiling. When a module changes only internals — private method bodies, non-public classes — and its `api` surface is byte-for-byte unchanged, Gradle's compile avoidance skips recompiling every module that depends on it, because their compile classpath's observable contents haven't changed. A dependency declared `api`, by contrast, is treated as part of the consumer's own compile classpath transitively; any new release of that dependency — even a patch touching only its internals — can invalidate the consumer's up-to-date check, since Gradle can't assume a third-party jar's ABI is stable across versions the way it can for your own module.

`modules-api-vs-implementation-gradle-config` (java-coding-standards) covers why over-declaring `api` leaks encapsulation to consumers; this is the build-performance consequence of the same decision, and on a large multi-module reactor it's often the more expensive one. A shared "commons" module that declares its logging library or JSON mapper as `api` "for convenience" turns every consumer into something that recompiles whenever that library moves — including transitively, through anyone who depends on the commons module at all — even though none of those consumers reference the library directly.

Minimizing the `api` set is the fix: only types that actually appear in this module's own public method signatures, fields, or supertypes belong there. Everything used purely inside method bodies is `implementation`, and stays invisible to Gradle's consumer-invalidation logic.

## Bad Example
```kotlin
// commons/build.gradle.kts
dependencies {
    api("com.fasterxml.jackson.core:jackson-databind:2.17.0") // only used inside method bodies
}
```
Every module depending on `commons` recompiles whenever Jackson's version changes, even though none of them reference Jackson types.

## Good Example
```kotlin
// commons/build.gradle.kts
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.0")
}
```
Consumers of `commons` recompile only when `commons`'s own public API changes, not when its internal dependencies do.

## Notes
- Annotation processors that read arbitrary classpath resources (not just annotated sources) can disable compile avoidance for the module using them — check the processor's documentation before assuming avoidance still applies.
- A Gradle build scan (`--scan`) shows which tasks were skipped by compile avoidance versus which triggered full recompilation, useful for diagnosing an unexpectedly slow incremental build.
- See `../../java-coding-standards/rules/modules-api-vs-implementation-gradle-config.md` for the encapsulation rationale behind the same `api`/`implementation` choice.

## References
- [Gradle User Guide — Compile Avoidance](https://docs.gradle.org/current/userguide/java_library_plugin.html#sec:java_library_compile_avoidance)
- [Gradle User Guide — The Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html)
