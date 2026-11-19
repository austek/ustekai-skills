---
title: Assert Flow Emissions With Turbine
impact: MEDIUM
impactDescription: deterministic, timeout-bounded assertions on each emission, completion and error
tags: [flow, testing, turbine]
---

# Assert Flow Emissions With Turbine [MEDIUM]

## Description
Collecting a flow into a list with `toList()` hangs on infinite flows and cannot assert ordering against other events. Turbine's `test { }` collects into a channel, lets you `awaitItem()`, `awaitComplete()` and `awaitError()` one step at a time, and fails on unconsumed events.

## Bad Example
```kotlin
@Test
fun emitsPrices() = runTest {
    val prices = source.prices().toList() // never returns for a hot flow
    assertEquals(listOf(1, 2), prices)
}
```

## Good Example
```kotlin
@Test
fun emitsPrices() = runTest {
    source.prices().test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

## Notes
- `test { }` fails if unconsumed events remain when the block ends, so unexpected extra emissions fail the test.
- Use `StateFlow.value` for a quick assertion on current state.

## References
- [Turbine](https://github.com/cashapp/turbine)
