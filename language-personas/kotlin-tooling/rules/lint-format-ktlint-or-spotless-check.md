---
title: Gate CI on a Kotlin Formatter Check and Reserve Auto-Format for Local Use
impact: MEDIUM
impactDescription: style disputes leave review and CI never rewrites code
tags: [ktlint, spotless, formatting]
---

# Gate CI on a Kotlin Formatter Check and Reserve Auto-Format for Local Use [MEDIUM]

## Description
Use one formatter: ktlint through Spotless (`spotlessKotlin`) or the ktlint Gradle plugin, with an `.editorconfig` as the single source of style. CI runs the check task; developers run the apply task or a pre-commit hook. Do not run both ktlint and the IDE's own style settings with different options.

## Bad Example
```kotlin
// CI step: ./gradlew spotlessApply && git commit  -- CI rewrites code
```

## Good Example
```kotlin
spotless {
    kotlin {
        ktlint()
        target("src/**/*.kt")
    }
    kotlinGradle { ktlint() }
}
tasks.check { dependsOn(tasks.spotlessCheck) }
```
```ini
# .editorconfig
[*.{kt,kts}]
indent_size = 4
max_line_length = 120
```

## Notes
- Do not use wildcard imports; ktlint's `no-wildcard-imports` enforces it.
- Pin the ktlint version in the version catalog so formatting does not change on upgrade.

## References
- [Spotless Gradle plugin](https://github.com/diffplug/spotless/tree/main/plugin-gradle)
- [ktlint](https://pinterest.github.io/ktlint/)
