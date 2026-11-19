# Ktor Standards

Ktor 3 server standards for Kotlin services, designed for AI agents and LLMs. The current line is 3.6; plugins are separate artifacts.

## Overview

This skill provides 8 rules across 8 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Coroutines | `coroutines-` | CRITICAL | 1 |
| Configuration | `config-` | HIGH | 1 |
| Errors | `errors-` | HIGH | 1 |
| Serialization | `serialization-` | HIGH | 1 |
| Observability | `observability-` | HIGH | 1 |
| Testing | `testing-` | HIGH | 1 |
| Structure | `structure-` | MEDIUM | 1 |
| Dependency Injection | `di-` | MEDIUM | 1 |

## Rules

### Request Handling (CRITICAL/HIGH)
- `coroutines-no-blocking-in-handlers` - Never block the event loop in route handlers
- `errors-status-pages-and-validation` - Map errors centrally with StatusPages and validate bodies with RequestValidation
- `serialization-content-negotiation-explicit-json` - Install ContentNegotiation with an explicitly configured kotlinx Json

### Configuration, Observability, Testing (HIGH)
- `config-typed-application-config` - Read configuration once into a typed object from ApplicationConfig
- `observability-call-id-and-structured-logging` - Add CallId, CallLogging with MDC and JSON output
- `testing-test-application` - Test routes with testApplication and the real module

### Structure & Dependency Injection (MEDIUM)
- `structure-module-extension-functions` - Structure a Ktor app as Application.module extensions per feature
- `di-constructor-injection-with-koin-modules` - Inject dependencies through constructors; confine Koin to the composition root

## Structure

```
ktor-standards/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Related

- [spring-standards](../spring-standards/SKILL.md), [kotlin-coding-standards](../kotlin-coding-standards/SKILL.md), [jvm-coding-standards](../jvm-coding-standards/SKILL.md)
