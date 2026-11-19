---
title: Expose Cold Flow for Streams and StateFlow for State
impact: CRITICAL
impactDescription: prevents duplicated upstream work and lost or stale emissions
tags: [coroutines, flow]
---

# Expose Cold Flow for Streams and StateFlow for State [CRITICAL]

## Description
A cold flow (one built with `flow { }` or a flow operator chain) re-runs the producer for each collector. A value typed `Flow` is not necessarily cold, because `SharedFlow` and `StateFlow` also implement `Flow`. Use a cold flow for query results and event streams. Use `StateFlow` for current state with a value (always has one, conflates), and `SharedFlow` for events that must reach all collectors. Share an expensive cold flow with `shareIn`/`stateIn` and `SharingStarted.WhileSubscribed`. Never expose `MutableStateFlow` publicly.

## Bad Example
```kotlin
import kotlinx.coroutines.flow.MutableStateFlow

data class Price(val cents: Long) { companion object { val ZERO = Price(0) } }

class Prices {
    val state = MutableStateFlow(Price.ZERO) // callers can write to it
}
```

## Good Example
```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.shareIn
import kotlinx.coroutines.flow.stateIn

data class Price(val cents: Long) { companion object { val ZERO = Price(0) } }
data class Quote(val price: Price)
interface PriceSource { fun quotes(): Flow<Quote> }

class Prices(source: PriceSource, scope: CoroutineScope) {
    val shared: SharedFlow<Quote> = source.quotes()
        .shareIn(scope, SharingStarted.WhileSubscribed(5_000), replay = 0)

    val latest: StateFlow<Price> = source.quotes()
        .map { it.price }
        .stateIn(scope, SharingStarted.WhileSubscribed(5_000), Price.ZERO)
}
```

## Notes
- `StateFlow` drops intermediate values; use `SharedFlow` or a `Channel` when every event matters.
- `SharedFlow` with `replay = 0` loses events emitted while no collector is subscribed, and a late collector sees only the replay cache. It is not durable delivery: use a `Channel` or a persisted queue when every event must be retained.
- Collect with a lifecycle-bound scope; do not `launch` an endless collector without an owner.

## References
- [Flow](https://kotlinlang.org/docs/flow.html)
