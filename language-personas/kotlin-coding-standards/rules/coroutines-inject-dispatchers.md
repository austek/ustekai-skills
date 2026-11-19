---
title: Inject Dispatchers Instead of Hard-Coding Them
impact: CRITICAL
impactDescription: tests control scheduling deterministically and run without real threads
tags: [coroutines, testing, dispatchers]
---

# Inject Dispatchers Instead of Hard-Coding Them [CRITICAL]

## Description
A hard-coded `Dispatchers.IO` makes a class impossible to test deterministically. Accept a `CoroutineDispatcher` (default `Dispatchers.IO`) in the constructor and pass a `StandardTestDispatcher` in tests.

## Bad Example
```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface Repo { fun loadAll(): List<String> }

class ReportService(private val repo: Repo) {
    suspend fun build() = withContext(Dispatchers.IO) { repo.loadAll() }
}
```

## Good Example
```kotlin
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface Repo { fun loadAll(): List<String> }

class ReportService(
    private val repo: Repo,
    private val io: CoroutineDispatcher = Dispatchers.IO,
) {
    suspend fun build() = withContext(io) { repo.loadAll() }
}
```

## Notes
- Suspend functions that are main-safe should switch dispatcher themselves, so callers never choose.
- `Dispatchers.Default` is for CPU-bound work, `Dispatchers.IO` for blocking calls.

## References
- [Testing coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
