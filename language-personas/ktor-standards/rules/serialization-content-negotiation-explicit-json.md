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
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation

fun Application.module() {
    install(ContentNegotiation) { json() } // default Json: strict on unknown keys, encodes defaults
}
```

## Good Example
```kotlin
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@OptIn(ExperimentalSerializationApi::class)
fun Application.module() {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            encodeDefaults = true
            explicitNulls = false
        })
    }
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
