---
title: Gate Coverage With Kover on Changed Logic, Not a Global Percentage
impact: MEDIUM
impactDescription: coverage gates track tested behavior without rewarding trivial tests
tags: [kover, coverage, ci]
---

# Gate Coverage With Kover on Changed Logic, Not a Global Percentage [MEDIUM]

## Description
Kover measures Kotlin coverage, including inline functions and coroutines, which JaCoCo misreports. Set a minimum on domain and service packages and exclude generated code, configuration classes and DTOs. Pair it with mutation testing (Pitest with the Kotlin plugin) for the core domain.

## Bad Example
```kotlin
kover { reports { verify { rule { minBound(95) } } } } // global, rewards getters
```

## Good Example
```kotlin
kover {
    reports {
        filters {
            includes { classes("com.example.domain.*", "com.example.service.*") }
            excludes { classes("*.config.*", "*Dto", "*\$\$serializer") }
        }
        verify {
            rule("domain") { minBound(80) }
        }
    }
}
tasks.check { dependsOn(tasks.koverVerify) }
```

## Notes
- The Kover docs show `filters` at `reports` scope or per variant, and they apply to every `verify` rule in that scope; a variant-level `filters` block replaces the common one. `*` matches any characters, dots included, so `com.example.domain.*` covers subpackages.
- `minBound` gates the aggregate coverage of the rule's class scope, not the lines a change adds; 100 untested new lines can pass beside 900 covered ones. Add a CI step that fails on changed-line coverage, by running a diff-coverage tool on the `koverXmlReport` output. Kover has no built-in diff gate.
- Do not exclude a class just to pass the gate.

## References
- [Kotlin Kover](https://kotlin.github.io/kotlinx-kover/gradle-plugin/)
