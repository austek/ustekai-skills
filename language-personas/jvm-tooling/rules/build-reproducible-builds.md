---
title: Ban Dynamic Version Ranges and Non-Deterministic Archive Output
impact: CRITICAL
impactDescription: the same commit produces a byte-different artifact on every build without it, defeating hash-based verification
tags: [reproducibility, build-configuration, gradle, maven, supply-chain]
---

# Ban Dynamic Version Ranges and Non-Deterministic Archive Output [CRITICAL]

## Description
A reproducible build produces the same artifact — or at least behaviorally identical output — from the same source and declared inputs, regardless of which machine or day it runs. Two things routinely break that guarantee in a JVM build. First, dynamic version selectors (`2.+`, `[2.0,3.0)`, `latest.release`) let the *same declared dependency* resolve to a *different jar* depending on what's been published since the last build; a build that passed yesterday can pull in a different (possibly vulnerable, possibly incompatible) transitive dependency today with zero change to source control. Second, archive tasks (`Jar`, `Zip`, `Tar`) embed non-deterministic metadata by default — file timestamps and filesystem-order entry sequencing — so two builds of identical source produce byte-different output, which breaks any workflow that verifies artifacts by content hash.

Exact version pins fix the first problem directly: `"2.17.0"`, never `"2.+"`. The second requires explicit Gradle archive-task configuration, since `preserveFileTimestamps` and unordered entries are the historical default.

Reproducibility is a supply-chain security property, not just a hygiene one: if you can rebuild a given commit and get a byte-identical artifact, you can verify that what's deployed actually came from that source and wasn't tampered with on a compromised build runner. Dynamic ranges defeat that because the "same" build description legitimately produces different bytes over time, so a hash mismatch tells you nothing.

## Bad Example
```kotlin
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.+") // resolves differently every day
}
```

## Good Example
```kotlin
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.17.0")
}

tasks.withType<Jar>().configureEach {
    isPreserveFileTimestamps = false
    isReproducibleFileOrder = true
}
```

## Notes
- `+` and Ivy-style ranges are convenient locally but must never ship to a committed build file — CI resolving a different transitive version than what a developer tested is a recurring source of "works on my machine."
- Combine exact pins with dependency locking or checksum verification (see the dependency-management rules) to also detect when a *repository* silently serves different bytes for the same coordinate.
- Reproducible archive output also makes build caching more effective: a cache keyed on task inputs/outputs only hits reliably when identical inputs produce identical output bytes.

## References
- [Reproducible Builds project](https://reproducible-builds.org/)
- [Gradle User Guide — Declaring Versions](https://docs.gradle.org/current/userguide/dependency_versions.html)
