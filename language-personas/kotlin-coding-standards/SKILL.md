---
name: kotlin-coding-standards
description: Kotlin coding standards covering null safety, errors as values, coroutines and Flow, immutability, sealed types and exhaustive when, scope functions, explicit API mode, Java interop and JSON serialization. Use when writing, reviewing, or refactoring Kotlin code, or when the user asks about Kotlin style, coroutines, or best practices.
paths:
  - "**/*.kt"
  - "**/*.kts"
---

# Kotlin Coding Standards

Idiomatic, coroutine-safe Kotlin for server-side and library code. Builds on [jvm-coding-standards](../jvm-coding-standards/SKILL.md) (virtual threads, logging, Jackson, pools); load both. Target Kotlin 2.2 or later (Spring Boot 4 requires 2.2+; the current stable is 2.4) on JDK 21+.

## Categories

### Null Safety [CRITICAL]
| Rule | Description |
|------|-------------|
| [null-safety-no-bang-bang](rules/null-safety-no-bang-bang.md) | Never use the non-null assertion !! |
| [null-safety-no-platform-type-leak](rules/null-safety-no-platform-type-leak.md) | Declare nullability explicitly on values from Java |

### Coroutines [CRITICAL]
| Rule | Description |
|------|-------------|
| [coroutines-no-globalscope](rules/coroutines-no-globalscope.md) | Never launch coroutines in GlobalScope |
| [coroutines-rethrow-cancellation](rules/coroutines-rethrow-cancellation.md) | Rethrow CancellationException when catching broad exceptions |
| [coroutines-no-runblocking-in-production](rules/coroutines-no-runblocking-in-production.md) | Do not call runBlocking in production code |
| [coroutines-inject-dispatchers](rules/coroutines-inject-dispatchers.md) | Inject dispatchers instead of hard-coding them |
| [coroutines-flow-hot-vs-cold](rules/coroutines-flow-hot-vs-cold.md) | Expose cold Flow for streams and StateFlow for state |

### Error Handling [HIGH]
| Rule | Description |
|------|-------------|
| [error-handling-sealed-errors-over-exceptions](rules/error-handling-sealed-errors-over-exceptions.md) | Model expected failures as values, not exceptions |

### Immutability [HIGH]
| Rule | Description |
|------|-------------|
| [immutability-val-and-data-classes](rules/immutability-val-and-data-classes.md) | Default to val, immutable data classes and copy() |
| [immutability-read-only-collections-in-api](rules/immutability-read-only-collections-in-api.md) | Expose read-only collection types in public APIs |

### Sealed Types [HIGH]
| Rule | Description |
|------|-------------|
| [sealed-when-exhaustive-no-else](rules/sealed-when-exhaustive-no-else.md) | Use exhaustive when over sealed types with no else branch |

### Serialization [HIGH]
| Rule | Description |
|------|-------------|
| [serialization-jackson-kotlin-module](rules/serialization-jackson-kotlin-module.md) | Register the Kotlin module or use kotlinx.serialization consistently |

### Idioms & API Design [MEDIUM]
| Rule | Description |
|------|-------------|
| [idioms-limit-scope-function-nesting](rules/idioms-limit-scope-function-nesting.md) | Do not nest or chain scope functions |
| [idioms-named-arguments-for-flags](rules/idioms-named-arguments-for-flags.md) | Use named arguments for booleans and same-typed parameters |
| [api-design-explicit-api-mode](rules/api-design-explicit-api-mode.md) | Enable explicit API mode for libraries and shared modules |
| [interop-jvm-annotations-only-when-needed](rules/interop-jvm-annotations-only-when-needed.md) | Add @Jvm annotations only when a Java caller needs them |
| [docs-kdoc-avoid-param-return-tags](rules/docs-kdoc-avoid-param-return-tags.md) | Write KDoc as prose and avoid @param and @return tags |

## Quick Reference
```kotlin
suspend fun loadAll(ids: List<Id>): List<Item> = coroutineScope {
    ids.map { async { repository.load(it) } }.awaitAll()
}

fun label(state: UiState): String = when (state) {
    UiState.Loading -> "loading"
    is UiState.Success -> "ready"
    is UiState.Failure -> "failed"
}
```

## See Also
- [kotlin-testing](../kotlin-testing/SKILL.md), [kotlin-tooling](../kotlin-tooling/SKILL.md)
- [spring-standards](../spring-standards/SKILL.md), [ktor-standards](../ktor-standards/SKILL.md)
