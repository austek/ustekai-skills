---
title: Do Not Call runBlocking in Production Code
impact: CRITICAL
impactDescription: blocks a thread inside code that exists to avoid blocking, causing starvation and deadlocks
tags: [coroutines, blocking]
---

# Do Not Call runBlocking in Production Code [CRITICAL]

## Description
`runBlocking` parks the calling thread until the coroutine finishes. On a dispatcher thread or a server request thread it can starve the pool or deadlock. Keep it to `main()` entry points and test bridges, and make callers `suspend` instead. On Spring MVC with virtual threads, blocking is acceptable and coroutines are optional.

## Bad Example
```kotlin
import kotlinx.coroutines.runBlocking

data class Money(val cents: Long)
interface Client { suspend fun fetchPrice(sku: String): Money }

fun price(client: Client, sku: String): Money = runBlocking { client.fetchPrice(sku) }
```

## Good Example
```kotlin
data class Money(val cents: Long)
interface Client { suspend fun fetchPrice(sku: String): Money }

suspend fun price(client: Client, sku: String): Money = client.fetchPrice(sku)
```

## Notes
- Wrap unavoidable blocking calls with `withContext(Dispatchers.IO) { ... }`, never the reverse.
- Use `runTest` in tests, not `runBlocking`.

## References
- [runBlocking](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/run-blocking.html)
