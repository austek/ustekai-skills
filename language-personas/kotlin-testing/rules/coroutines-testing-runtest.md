---
title: Test Suspend Code With runTest and Virtual Time
impact: HIGH
impactDescription: tests of delays and timeouts finish in milliseconds and never flake on real time
tags: [coroutines, testing, runTest]
---

# Test Suspend Code With runTest and Virtual Time [HIGH]

## Description
`runTest` from `kotlinx-coroutines-test` runs the body on a `TestScope` with a virtual clock, so `delay(5_000)` returns instantly and `advanceTimeBy` moves time explicitly. It also fails the test on leaked coroutines and uncaught exceptions. `runBlocking` and `Thread.sleep` use real time and hide failures.

## Bad Example
```kotlin
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlin.test.Test
import kotlin.test.assertEquals

fun interface Remote { suspend fun call(): String? }

class RetryingClient(
    private val remote: Remote,
    private val io: CoroutineDispatcher,
    private val backoffMs: Long = 1_000,
) {
    suspend fun fetchWithRetry(): String = withContext(io) {
        repeat(3) {
            remote.call()?.let { return@withContext it }
            delay(backoffMs)
        }
        "ok"
    }
}

class RetryTest {
    private val fake = Remote { null }

    @Test
    fun retries() = runBlocking {
        val client = RetryingClient(fake, io = kotlinx.coroutines.Dispatchers.IO)
        val result = client.fetchWithRetry() // real delays: slow and flaky
        assertEquals("ok", result)
    }
}
```

## Good Example
```kotlin
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.currentTime
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class RetryTest {
    private val fake = Remote { null }

    @Test
    fun retries() = runTest {
        val client = RetryingClient(fake, io = StandardTestDispatcher(testScheduler))
        val result = client.fetchWithRetry()
        assertEquals("ok", result)
        assertEquals(3_000, currentTime) // virtual time consumed by backoff
    }
}
```

## Notes
- Inject the dispatcher (see `coroutines-inject-dispatchers`) and build it from `testScheduler`.
- Use `backgroundScope` for collectors that run for the test's lifetime.

## References
- [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
