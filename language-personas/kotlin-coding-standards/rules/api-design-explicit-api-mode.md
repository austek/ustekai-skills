---
title: Enable Explicit API Mode for Libraries and Shared Modules
impact: MEDIUM
impactDescription: every public declaration states its visibility and type deliberately
tags: [api-design, visibility, libraries]
---

# Enable Explicit API Mode for Libraries and Shared Modules [MEDIUM]

## Description
Kotlin declarations are `public` by default and return types are inferred, so an implementation detail or an inferred type can become API by accident. Turn on `explicitApi()` in modules others depend on. The compiler then requires explicit visibility and return types on public declarations. Mark everything else `internal`.

## Bad Example
```kotlin
class HttpClientFactory { // public by accident
    fun create() = buildClient() // inferred public return type
}
```

## Good Example
```kotlin
kotlin { explicitApi() }
```
```kotlin
public class HttpClient internal constructor()

internal fun buildClient(): HttpClient = HttpClient()

public class HttpClientFactory internal constructor() {
    public fun create(): HttpClient = buildClient()
}
```

## Notes
- Use `explicitApiWarning()` first when migrating an existing module.
- Pair with the binary-compatibility-validator plugin to catch accidental API breaks.

## References
- [Explicit API mode](https://github.com/Kotlin/KEEP/blob/master/proposals/explicit-api-mode.md)
