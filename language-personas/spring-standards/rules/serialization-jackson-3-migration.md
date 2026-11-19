---
title: Use Jackson 3 Packages and Customizers on Spring Boot 4
impact: HIGH
impactDescription: mixing Jackson 2 and 3 types causes missing-bean, ClassNotFound and silent configuration drift
tags: [spring, boot4, jackson, serialization]
---

# Use Jackson 3 Packages and Customizers on Spring Boot 4 [HIGH]

## Description
Spring Boot 4 auto-configures Jackson 3 (`tools.jackson`) and deprecates Jackson 2 support, which stays available through `spring-boot-jackson2` for migration only. Group ids and packages moved from `com.fasterxml.jackson` to `tools.jackson`; the annotations (`com.fasterxml.jackson.annotation`, `jackson-annotations`) keep their old names. Boot's `@JsonComponent` became `@JacksonComponent`, `@JsonMixin` became `@JacksonMixin`, and `Jackson2ObjectMapperBuilderCustomizer` became `JsonMapperBuilderCustomizer`. Customize through the builder customizer rather than creating a second mapper.

## Bad Example
```java
import com.fasterxml.jackson.databind.ObjectMapper;

@Bean ObjectMapper objectMapper() { return new ObjectMapper(); } // Jackson 2 type; Boot 4 auto-configures a JsonMapper
```

## Good Example
```java
import tools.jackson.databind.DeserializationFeature;

@Bean
JsonMapperBuilderCustomizer strictJson() {
    return builder -> builder.enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
}
```

## Notes
- Set `spring.jackson.use-jackson2-defaults=true` temporarily if the migration changes JSON output; remove it once tests pass.
- Jackson 3 changes defaults (for example dates are no longer written as timestamps by default). Pin the contract in tests.
- Kotlin projects need `tools.jackson.module:jackson-module-kotlin`; see `serialization-jackson-kotlin-module` in kotlin-coding-standards.

## References
- [Spring Boot 4.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- [Introducing Jackson 3 support in Spring](https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/)
