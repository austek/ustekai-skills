# Kotlin Coding Standards

Idiomatic, coroutine-safe Kotlin for server-side and library code, designed for AI agents and LLMs. Load together with [jvm-coding-standards](../jvm-coding-standards/SKILL.md).

## Overview

This skill provides 17 rules across 10 categories:

| Category | Prefix | Impact | Rules |
|----------|--------|--------|-------|
| Null Safety | `null-safety-` | CRITICAL | 2 |
| Coroutines | `coroutines-` | CRITICAL | 5 |
| Error Handling | `error-handling-` | HIGH | 1 |
| Immutability | `immutability-` | HIGH | 2 |
| Sealed Types | `sealed-` | HIGH | 1 |
| Serialization | `serialization-` | HIGH | 1 |
| Idioms | `idioms-` | MEDIUM | 2 |
| API Design | `api-design-` | MEDIUM | 1 |
| Java Interop | `interop-` | LOW | 1 |
| Documentation | `docs-` | LOW | 1 |

## Rules

### Null Safety (CRITICAL)
- `null-safety-no-bang-bang` - Never use the non-null assertion !!
- `null-safety-no-platform-type-leak` - Declare nullability explicitly on values from Java

### Coroutines (CRITICAL)
- `coroutines-flow-hot-vs-cold` - Expose cold Flow for streams and StateFlow for state
- `coroutines-inject-dispatchers` - Inject dispatchers instead of hard-coding them
- `coroutines-no-globalscope` - Never launch coroutines in GlobalScope
- `coroutines-no-runblocking-in-production` - Do not call runBlocking in production code
- `coroutines-rethrow-cancellation` - Rethrow CancellationException when catching broad exceptions

### Error Handling (HIGH)
- `error-handling-sealed-errors-over-exceptions` - Model expected failures as values, not exceptions

### Immutability (HIGH)
- `immutability-read-only-collections-in-api` - Expose read-only collection types in public APIs
- `immutability-val-and-data-classes` - Default to val, immutable data classes and copy()

### Sealed Types (HIGH)
- `sealed-when-exhaustive-no-else` - Use exhaustive when over sealed types with no else branch

### Serialization (HIGH)
- `serialization-jackson-kotlin-module` - Register the Jackson Kotlin module or use kotlinx.serialization consistently

### Idioms, API Design, Interop, Documentation (MEDIUM/LOW)
- `idioms-limit-scope-function-nesting` - Do not nest or chain scope functions
- `idioms-named-arguments-for-flags` - Use named arguments for booleans and same-typed parameters
- `api-design-explicit-api-mode` - Enable explicit API mode for libraries and shared modules
- `interop-jvm-annotations-only-when-needed` - Add @Jvm annotations only when a Java caller needs them
- `docs-kdoc-avoid-param-return-tags` - Write KDoc as prose and avoid @param and @return tags

## Structure

```
kotlin-coding-standards/
├── SKILL.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── <prefix>-<name>.md
```

## Sources

Rules follow the Kotlin coding conventions, the kotlinx.coroutines guide and the Kotlin release notes.

## Related

- [kotlin-testing](../kotlin-testing/SKILL.md), [kotlin-tooling](../kotlin-tooling/SKILL.md), [spring-standards](../spring-standards/SKILL.md), [ktor-standards](../ktor-standards/SKILL.md)
