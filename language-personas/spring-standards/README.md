# Spring Standards

Spring Boot 4.x (Spring Framework 7) standards for Java and Kotlin services, designed for AI agents and LLMs. Boot 4 requires Java 17+ and Kotlin 2.2+; JDK 21+ is recommended. Notes mark where Boot 3.x differs.

## Overview

This skill provides 10 rules across 9 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Configuration | `config-` | HIGH | 1 |
| Transactions | `transactions-` | HIGH | 1 |
| Data | `data-` | HIGH | 1 |
| Web | `web-` | HIGH | 2 |
| Serialization | `serialization-` | HIGH | 1 |
| Concurrency | `concurrency-` | MEDIUM | 1 |
| Observability | `observability-` | HIGH | 1 |
| Testing | `testing-` | HIGH | 1 |
| Kotlin | `kotlin-` | HIGH | 1 |

## Rules

### Configuration, Transactions, Data (HIGH)
- `config-typed-configuration-properties` - Bind configuration to typed, validated @ConfigurationProperties
- `transactions-service-boundary` - Put @Transactional on service methods, not controllers or repositories
- `data-disable-open-in-view` - Disable open session in view and fetch explicitly

### Web & Serialization (HIGH)
- `web-dto-validation-at-boundary` - Validate request DTOs at the boundary and never expose JPA entities
- `web-problem-details-error-handling` - Return RFC 9457 Problem Details from a central @RestControllerAdvice
- `serialization-jackson-3-migration` - Use Jackson 3 packages and customizers on Spring Boot 4

### Runtime, Observability, Testing, Kotlin
- `concurrency-virtual-threads-property` - Enable virtual threads with the Boot property on JDK 21+ (MEDIUM)
- `observability-structured-logging-and-actuator` - Use Boot structured logging and expose only needed actuator endpoints (HIGH)
- `testing-slices-and-service-connection` - Test with slices and @ServiceConnection Testcontainers (HIGH)
- `kotlin-compiler-plugins-spring-jpa` - Apply the kotlin-spring and kotlin-jpa compiler plugins in Kotlin projects (HIGH)

## Structure

```
spring-standards/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Sources

Rules follow the Spring Boot 4.1 reference, the Boot 4.0 migration guide and the Spring Framework reference. Package names and starters changed in Boot 4; re-check against the version you run.

## Related

- [ktor-standards](../ktor-standards/SKILL.md), [jvm-coding-standards](../jvm-coding-standards/SKILL.md), [jvm-testing](../jvm-testing/SKILL.md)
