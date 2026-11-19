---
name: spring-standards
description: Spring Boot standards for Java and Kotlin services covering typed configuration properties, transaction boundaries, request DTO validation, Problem Details error handling, JPA open-in-view and fetching, virtual threads, structured logging and actuator exposure, slice and Testcontainers tests, and the Kotlin Spring/JPA compiler plugins. Use when writing, reviewing, or configuring a Spring Boot application, or when the user asks about Spring best practices.
paths:
  - "**/src/main/resources/application*.yml"
  - "**/src/main/resources/application*.yaml"
  - "**/src/main/resources/application*.properties"
  - "**/*Controller.java"
  - "**/*Controller.kt"
  - "**/*Service.java"
  - "**/*Service.kt"
---

# Spring Standards

Framework rules for Spring Boot 4.x (Spring Framework 7). Language rules come from the language skills ([java-coding-standards](../java-coding-standards/SKILL.md) or [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md)) and runtime rules from [jvm-coding-standards](../jvm-coding-standards/SKILL.md). Constructor injection is covered by `reflection-serialization-avoid-field-injection` in the Java skill.

## Categories

### Configuration & Data [HIGH]
| Rule | Description |
|------|-------------|
| [config-typed-configuration-properties](rules/config-typed-configuration-properties.md) | Bind configuration to typed, validated @ConfigurationProperties |
| [transactions-service-boundary](rules/transactions-service-boundary.md) | Put @Transactional on service methods, not controllers or repositories |
| [data-disable-open-in-view](rules/data-disable-open-in-view.md) | Disable open session in view and fetch explicitly |

### Web [HIGH]
| Rule | Description |
|------|-------------|
| [serialization-jackson-3-migration](rules/serialization-jackson-3-migration.md) | Use Jackson 3 packages and customizers on Spring Boot 4 |
| [web-dto-validation-at-boundary](rules/web-dto-validation-at-boundary.md) | Validate request DTOs at the boundary and never expose JPA entities |
| [web-problem-details-error-handling](rules/web-problem-details-error-handling.md) | Return RFC 9457 Problem Details from a central @RestControllerAdvice |

### Runtime & Observability [HIGH]
| Rule | Description |
|------|-------------|
| [concurrency-virtual-threads-property](rules/concurrency-virtual-threads-property.md) | Enable virtual threads with the Boot property |
| [observability-structured-logging-and-actuator](rules/observability-structured-logging-and-actuator.md) | Use Boot structured logging and expose only needed actuator endpoints |

### Testing & Kotlin [HIGH]
| Rule | Description |
|------|-------------|
| [testing-slices-and-service-connection](rules/testing-slices-and-service-connection.md) | Test with slices and @ServiceConnection Testcontainers |
| [kotlin-compiler-plugins-spring-jpa](rules/kotlin-compiler-plugins-spring-jpa.md) | Apply the kotlin-spring and kotlin-jpa compiler plugins in Kotlin projects |

## See Also
- [ktor-standards](../ktor-standards/SKILL.md), [jvm-testing](../jvm-testing/SKILL.md)
