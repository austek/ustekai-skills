---
title: Treat Kotlin Compiler Warnings as Errors in CI
impact: HIGH
impactDescription: deprecations, unchecked casts and unused code cannot accumulate unnoticed
tags: [compiler, warnings, k2]
---

# Treat Kotlin Compiler Warnings as Errors in CI [HIGH]

## Description
Enable `allWarningsAsErrors` for the Kotlin compiler (K2; K1 and `-language-version=1.9` are gone in Kotlin 2.4) so a new warning fails the build. Gate it on CI or a `-PwarningsAsErrors` property if local work needs flexibility. Kotlin 2.1+ enforces JSpecify annotations strictly, which covers Spring Framework 7's own API. Keep `-Xjsr305=strict` for libraries that still use JSR-305 annotations.

## Bad Example
```kotlin
kotlin {
    compilerOptions { /* warnings scroll past */ }
}
```

## Good Example
```kotlin
kotlin {
    jvmToolchain(25)
    compilerOptions {
        allWarningsAsErrors = providers.gradleProperty("warningsAsErrors").map(String::toBoolean).orElse(true)
        freeCompilerArgs.add("-Xjsr305=strict")
    }
}
```

## Notes
- Fix deprecations when they appear; do not add `@Suppress("DEPRECATION")` as a habit.

## References
- [Kotlin compiler options](https://kotlinlang.org/docs/gradle-compiler-options.html)
