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
tasks.withType<io.gitlab.arturbosch.detekt.Detekt>().configureEach {
    jvmTarget = "21"
}
tasks.check { dependsOn("detekt", "detektMain", "detektTest") }
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
- The plain `detekt` task runs without type resolution and `check` does not run the type-resolved `detektMain`/`detektTest` on its own. Depend on them explicitly, or rules that need type resolution never gate the build.
- Detekt inherits `jvmTarget` from the Kotlin toolchain but accepts targets only up to a JDK cap that trails the newest releases, so a latest-JDK toolchain can fail `check` before analysis. Pin `jvmTarget` on the detekt tasks as shown (the analysis target does not change your build output).
- The plain baseline does not cover type-resolved findings such as `SuspendFunSwallowedCancellation`. Generate it with `./gradlew detektBaseline detektBaselineMain detektBaselineTest` and commit the generated baseline files, in a dedicated PR.
- Suppress a single finding with `@Suppress("RuleName")` plus a reason in the commit, never a blanket disable.

## References
- [detekt](https://detekt.dev/docs/gettingstarted/gradle)
