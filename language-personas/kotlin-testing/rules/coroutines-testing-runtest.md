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
@Test
fun retries() = runBlocking {
    val result = client.fetchWithRetry() // real delays: slow and flaky
    assertEquals("ok", result)
}
```

## Good Example
```kotlin
@Test
fun retries() = runTest {
    val client = RetryingClient(fake, io = StandardTestDispatcher(testScheduler))
    val result = client.fetchWithRetry()
    assertEquals("ok", result)
    assertEquals(3_000, currentTime) // virtual time consumed by backoff
}
```

## Notes
- Inject the dispatcher (see `coroutines-inject-dispatchers`) and build it from `testScheduler`.
- Use `backgroundScope` for collectors that run for the test's lifetime.

## References
- [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
