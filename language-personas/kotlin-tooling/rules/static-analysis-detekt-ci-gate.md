---
title: Fail the Build on detekt Findings With a Committed Baseline
impact: HIGH
impactDescription: new smells and complexity fail CI while legacy findings are tracked, not ignored
tags: [detekt, static-analysis, ci]
---

# Fail the Build on detekt Findings With a Committed Baseline [HIGH]

## Description
Run detekt in `check` with `buildUponDefaultConfig = true` and a committed `config/detekt/detekt.yml`. Generate a baseline once for existing findings and commit it; new findings then fail the build. Use Spotless or the `detekt-formatting` plugin for style. Detekt ships a built-in `coroutines` ruleset; `GlobalCoroutineUsage` and `SuspendFunSwallowedCancellation` are off by default, so enable them in `detekt.yml`. They back `coroutines-no-globalscope` and `coroutines-rethrow-cancellation`.

## Bad Example
```kotlin
detekt {
    ignoreFailures = true // report only, never blocks
}
```

## Good Example
```kotlin
detekt {
    buildUponDefaultConfig = true
    allRules = false
    config.setFrom(files("config/detekt/detekt.yml"))
    baseline = file("config/detekt/baseline.xml")
}
dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:${libs.versions.detekt.get()}")
}
tasks.check { dependsOn(tasks.detekt) }
```

```yaml
# config/detekt/detekt.yml
coroutines:
  GlobalCoroutineUsage:
    active: true
  SuspendFunSwallowedCancellation:
    active: true
```

## Notes
- The snippets use the stable detekt 1.23.x coordinates (`io.gitlab.arturbosch.detekt`). Detekt 2.0 is still in alpha and uses the `dev.detekt` plugin id and group; migrate when it is stable.
- Regenerate the baseline with `./gradlew detektBaseline` only in a dedicated PR.
- Suppress a single finding with `@Suppress("RuleName")` plus a reason in the commit, never a blanket disable.

## References
- [detekt](https://detekt.dev/docs/gettingstarted/gradle)
