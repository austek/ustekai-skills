---
title: Install ContentNegotiation With an Explicitly Configured kotlinx Json
impact: HIGH
impactDescription: JSON handling is deterministic: unknown keys, defaults and nulls behave as the contract says
tags: [ktor, serialization, json]
---

# Install ContentNegotiation With an Explicitly Configured kotlinx Json [HIGH]

## Description
Install `ContentNegotiation` with `json(Json { ... })` and set every option that affects the contract: `ignoreUnknownKeys`, `encodeDefaults`, `explicitNulls`. Annotate DTOs with `@Serializable` and keep them separate from domain types. Relying on defaults makes request tolerance and response shape drift between versions.

## Bad Example
```kotlin
install(ContentNegotiation) { json() } // default Json: strict on unknown keys, omits defaults
```

## Good Example
```kotlin
install(ContentNegotiation) {
    json(Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
        explicitNulls = false
    })
}

@Serializable
data class OrderView(val id: String, val status: String, val note: String? = null)
```

## Notes
- With `explicitNulls = false`, a nullable property that has a non-null default (`val note: String? = "n/a"`) encodes `null` as an absent field and decodes back to the default, not `null`. Keep `explicitNulls = true` (the default) for such DTOs.
- Use `@SerialName` for wire names that must not change when a property is renamed.
- Prefer `Instant` with `kotlinx-datetime` and a serializer over `String` for timestamps.

## References
- [Ktor ContentNegotiation](https://ktor.io/docs/server-serialization.html)
