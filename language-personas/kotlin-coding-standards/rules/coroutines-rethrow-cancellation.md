---
title: Rethrow CancellationException When Catching Broad Exceptions
impact: CRITICAL
impactDescription: swallowing cancellation makes a cancelled coroutine keep running
tags: [coroutines, cancellation, errors]
---

# Rethrow CancellationException When Catching Broad Exceptions [CRITICAL]

## Description
Coroutine cancellation is delivered as a `CancellationException`. A `catch (e: Exception)` or `runCatching` around a suspend call catches it, so the coroutine ignores cancellation, timeouts stop working, and scopes hang on shutdown. Catch specific exception types, or rethrow cancellation first.

## Bad Example
```kotlin
suspend fun refresh() {
    try {
        api.fetch()
    } catch (e: Exception) {
        log.warn("refresh failed", e) // also swallows cancellation
    }
}
val result = runCatching { api.fetch() } // same problem
```

## Good Example
```kotlin
suspend fun refresh() {
    try {
        api.fetch()
    } catch (e: CancellationException) {
        throw e
    } catch (e: IOException) {
        log.warn("refresh failed", e)
    }
}
```

## Notes
- Prefer catching the narrowest type (`IOException`, a domain exception) so the cancellation branch is unnecessary.
- `withTimeout` throws `TimeoutCancellationException`; `withTimeoutOrNull` returns null instead.

## References
- [Cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
