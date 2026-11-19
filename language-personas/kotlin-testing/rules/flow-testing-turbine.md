---
title: Assert Flow Emissions With Turbine
impact: HIGH
impactDescription: deterministic, timeout-bounded assertions on each emission, completion and error
tags: [flow, testing, turbine]
---

# Assert Flow Emissions With Turbine [HIGH]

## Description
Collecting a flow into a list with `toList()` hangs on infinite flows and cannot assert ordering against other events. Turbine's `test { }` collects into a channel, lets you `awaitItem()`, `awaitComplete()` and `awaitError()` one step at a time, and fails on unconsumed events.

## Bad Example
```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class PricesTest {
    private val prices = MutableSharedFlow<Int>() // hot flow: never completes

    @Test
    fun emitsPrices() = runTest {
        val collected = prices.toList() // never returns
        assertEquals(listOf(1, 2), collected)
    }
}
```

## Good Example
```kotlin
import app.cash.turbine.test
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class PricesTest {
    private val prices = flowOf(1, 2)

    @Test
    fun emitsPrices() = runTest {
        prices.test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }
    }
}
```

## Notes
- `test { }` fails if unconsumed events remain when the block ends, so unexpected extra emissions fail the test.
- Call `awaitComplete()` for a finite flow. Turbine cancels collection when the block ends, so a late extra item is otherwise missed. For a hot flow, assert the intended observation window (for example `expectNoEvents()`) before the block ends.
- Use `StateFlow.value` for a quick assertion on current state.

## References
- [Turbine](https://github.com/cashapp/turbine)
