---
title: Register the Jackson Kotlin Module or Use kotlinx.serialization Consistently
impact: HIGH
impactDescription: prevents missing-constructor failures and silent null or default mismatches in JSON
tags: [serialization, jackson, kotlinx-serialization]
---

# Register the Jackson Kotlin Module or Use kotlinx.serialization Consistently [HIGH]

## Description
Jackson cannot construct Kotlin data classes without the Kotlin module: defaults and nullability are ignored or fail at runtime. Pick one serializer per service and configure it explicitly (see `reflection-serialization-jackson-explicit-config`). Jackson 3 (Spring Boot 4's default) moved to the `tools.jackson` group and package, so the module is `tools.jackson.module:jackson-module-kotlin` and mappers are immutable and built with a builder. Jackson 2 keeps `com.fasterxml.jackson.module`. In Ktor and multiplatform code, `kotlinx.serialization` with `@Serializable` is the usual choice.

## Bad Example
```kotlin
val mapper = ObjectMapper() // no Kotlin module
val dto: UserDto = mapper.readValue(json) // fails: no default constructor
```

## Good Example
```kotlin
// Jackson 3
val mapper: JsonMapper = jsonMapper {
    addModule(kotlinModule())
    enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
}

// kotlinx.serialization
@Serializable
data class UserDto(val id: String, val name: String = "")
val dto = Json { ignoreUnknownKeys = true }.decodeFromString<UserDto>(json)
```

## Notes
- Jackson 2 projects: `jacksonObjectMapper()` registers the module.
- Spring Boot 4 auto-configures a `JsonMapper`; a Boot issue reported the Kotlin module not being picked up automatically. Add a test that deserializes a data class with a default value so a missing module fails the build.
- The `com.fasterxml.jackson.annotation` package (annotations) is unchanged in Jackson 3.
- Declare DTO properties non-null where the contract guarantees them so a missing field fails fast.

## References
- [jackson-module-kotlin](https://github.com/FasterXML/jackson-module-kotlin)
- [Introducing Jackson 3 support in Spring](https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/)
- [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization)
