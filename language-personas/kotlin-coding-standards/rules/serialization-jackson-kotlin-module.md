---
title: Register the Jackson Kotlin Module or Use kotlinx.serialization Consistently
impact: HIGH
impactDescription: prevents missing-constructor failures and silent null or default mismatches in JSON
tags: [serialization, jackson, kotlinx-serialization]
---

# Register the Jackson Kotlin Module or Use kotlinx.serialization Consistently [HIGH]

## Description
Jackson cannot construct Kotlin data classes without the Kotlin module: defaults and nullability are ignored or fail at runtime. Pick one serializer per service and configure it explicitly (see `reflection-serialization-jackson-explicit-config`). Jackson uses the `tools.jackson` group and package, so the module is `tools.jackson.module:jackson-module-kotlin` and mappers are immutable and built with a builder. In Ktor and multiplatform code, `kotlinx.serialization` with `@Serializable` is the usual choice.

## Bad Example
```kotlin
val mapper = ObjectMapper() // no Kotlin module
val dto: UserDto = mapper.readValue(json) // fails: no default constructor
```

## Good Example
```kotlin
// Jackson
import tools.jackson.databind.DeserializationFeature
import tools.jackson.databind.json.JsonMapper
import tools.jackson.module.kotlin.jsonMapper
import tools.jackson.module.kotlin.kotlinModule

val mapper: JsonMapper = jsonMapper {
    addModule(kotlinModule())
    enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
}
```
```kotlin
// kotlinx.serialization
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json

@Serializable
data class UserDto(val id: String, val name: String = "")

val json = """{"id": "42"}"""
val dto = Json { ignoreUnknownKeys = true }.decodeFromString<UserDto>(json)
```

## Notes
- Spring Boot auto-configures a `JsonMapper`. Add a test that deserializes `{"id": "42"}` into `data class UserDto(val id: String, val name: String = "")` and asserts both `id` and `name`; the required parameter forces the Kotlin module, so a missing module fails the build.
- The `com.fasterxml.jackson.annotation` package (annotations) keeps its name; only databind, modules and core moved to `tools.jackson`.
- Declare DTO properties non-null where the contract guarantees them so a missing field fails fast.
- `DeserializationFeature.FAIL_ON_NULL_FOR_PRIMITIVES` turns a JSON `null` for a primitive such as `Int` into an error instead of `0`. Jackson enables it by default; keep a test with null and missing primitive fields.

## References
- [jackson-module-kotlin](https://github.com/FasterXML/jackson-module-kotlin)
- [Introducing Jackson 3 support in Spring](https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/)
- [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization)
