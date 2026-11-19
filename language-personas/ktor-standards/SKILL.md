---
name: ktor-standards
description: Ktor server standards for Kotlin services covering module structure, typed ApplicationConfig, StatusPages and RequestValidation, non-blocking handlers, constructor injection with Koin, explicit kotlinx.serialization JSON, CallId and structured logging, and testApplication tests. Use when writing, reviewing, or configuring a Ktor application, or when the user asks about Ktor best practices.
paths:
  - "**/src/main/resources/application*.conf"
  - "**/src/main/resources/application*.yaml"
  - "**/Application.kt"
  - "**/*Routes.kt"
---

# Ktor Standards

Framework rules for Ktor 3 servers in Kotlin (plugin artifacts such as `ktor-server-call-id` and `ktor-server-test-host` are separate dependencies). Language rules come from [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md) (especially coroutines and sealed types) and runtime rules from [jvm-coding-standards](../jvm-coding-standards/SKILL.md).

## Categories

### Structure & Configuration [HIGH/MEDIUM]
| Rule | Description |
|------|-------------|
| [structure-module-extension-functions](rules/structure-module-extension-functions.md) | Structure a Ktor app as Application.module extensions per feature |
| [config-typed-application-config](rules/config-typed-application-config.md) | Read configuration once into a typed object from ApplicationConfig |
| [di-constructor-injection-with-koin-modules](rules/di-constructor-injection-with-koin-modules.md) | Inject dependencies through constructors; confine Koin to the composition root |

### Request Handling [CRITICAL/HIGH]
| Rule | Description |
|------|-------------|
| [coroutines-no-blocking-in-handlers](rules/coroutines-no-blocking-in-handlers.md) | Never block the event loop in route handlers |
| [errors-status-pages-and-validation](rules/errors-status-pages-and-validation.md) | Map errors centrally with StatusPages and validate bodies with RequestValidation |
| [serialization-content-negotiation-explicit-json](rules/serialization-content-negotiation-explicit-json.md) | Install ContentNegotiation with an explicitly configured kotlinx Json |

### Observability & Testing [HIGH]
| Rule | Description |
|------|-------------|
| [observability-call-id-and-structured-logging](rules/observability-call-id-and-structured-logging.md) | Add CallId, CallLogging with MDC and JSON output |
| [testing-test-application](rules/testing-test-application.md) | Test routes with testApplication and the real module |

## See Also
- [spring-standards](../spring-standards/SKILL.md), [kotlin-testing](../kotlin-testing/SKILL.md), [jvm-testing](../jvm-testing/SKILL.md)
